"""
postprocess.py — post-render pass over a rendered CV .docx.

Why this exists
---------------
docxtpl RichText passed through a plain `{{ bullet }}` placeholder embeds the
RichText's run-XML *inside* the placeholder's <w:t> element. That is invalid
OOXML: Word, python-docx, and ATS parsers all read the paragraph as EMPTY.
This was the 2026-05-11 incident and the corruption that shipped in every
labeled-mode CV of the 2026-06-25 (Cairo) and 2026-06-27 (Berlin) batches.

So RichText is banned from the render path. Bullets render as plain strings
(valid OOXML by construction, formatting inherited from the styled placeholder
run), and bold is applied HERE, after `tpl.save()`:

  1. `build_bold_plan()` (md_to_richtext.py) strips the `**` markers before
     render and records which character spans of each bullet should be bold.
  2. `postprocess_cv()` re-opens the saved .docx with python-docx, finds each
     bullet paragraph, and splits its single run at the span boundaries by
     CLONING the run element. The clone inherits the template run's full rPr
     (Calibri, sz 20, paired w:b/w:bCs) with zero re-declaration in code —
     the formatting constants in docxtpl-recipe.md stay template-owned.

The same pass removes disabled sections (config `cv.sections` /
`cv.region_section_overrides`, e.g. EU: summary: false) by deleting the
section's header paragraph through the paragraph before the next header.

Every bullet in the plan is located by exact (whitespace-normalized) text
match with a forward-moving cursor. A bullet that cannot be found raises
PostprocessError — a loud render-time failure instead of a silent blank CV.
"""

import copy

from docx import Document
from docx.text.run import Run


# Literal header-paragraph text per section in the OPUS template. A different
# template supplies its own mapping via the `section_headers` argument.
OPUS_SECTION_HEADERS = {
    "summary": "PROFESSIONAL SUMMARY",
    "core_skills": "CORE SKILLS",
    "experience": "PROFESSIONAL EXPERIENCE",
    "education": "EDUCATION",
    "additional": "ADDITIONAL",
}

# Sections that must never be removed, whatever the config says.
REQUIRED_SECTIONS = ("tagline", "contact", "experience", "education")


class PostprocessError(ValueError):
    """A bold-plan entry could not be matched to the rendered document."""


def _norm(text):
    return " ".join(text.split())


def _find_paragraph(paragraphs, text, start=0):
    """Index of the first paragraph (from `start`) whose normalized text
    equals `text` normalized, or None."""
    target = _norm(text)
    for i in range(start, len(paragraphs)):
        if _norm(paragraphs[i].text) == target:
            return i
    return None


def _merge_runs(paragraph):
    """Collapse the paragraph to a single run carrying all its text.

    docxtpl renders a `{{ placeholder }}` inside one run, so bullets arrive
    as a single run; this is defensive for a paragraph that arrives split
    (proofing marks, rsid edits in a future template).
    """
    runs = paragraph.runs
    if len(runs) <= 1:
        return
    runs[0].text = "".join(r.text for r in runs)
    for r in runs[1:]:
        r._r.getparent().remove(r._r)


def _segments(text, spans):
    """Split `text` into ordered (segment_text, bold) pairs from bold spans.

    Spans are clamped to the text, empties dropped, overlapping/adjacent
    spans merged.
    """
    cleaned = []
    for s, e in sorted((max(0, s), min(len(text), e)) for s, e in spans):
        if e <= s:
            continue
        if cleaned and s <= cleaned[-1][1]:
            cleaned[-1] = (cleaned[-1][0], max(cleaned[-1][1], e))
        else:
            cleaned.append((s, e))
    segments = []
    pos = 0
    for s, e in cleaned:
        if s > pos:
            segments.append((text[pos:s], False))
        segments.append((text[s:e], True))
        pos = e
    if pos < len(text):
        segments.append((text[pos:], False))
    return [seg for seg in segments if seg[0]]


def _split_run_bold(paragraph, spans):
    """Rebuild the paragraph's run as bold/plain segments per `spans`.

    Each segment is a deep copy of the original run element, so the
    template's rPr (font, size, paired w:b/w:bCs attributes) is inherited
    exactly; only the bold flag differs. Returns the number of bold runs
    created.
    """
    _merge_runs(paragraph)
    if not paragraph.runs:
        raise PostprocessError(
            "bullet paragraph has no runs: " + repr(paragraph.text[:60]))
    src = paragraph.runs[0]
    segments = _segments(src.text, spans)
    if not any(bold for _, bold in segments):
        return 0

    prev_el = src._r
    bolded = 0
    for seg_text, seg_bold in segments:
        el = copy.deepcopy(src._r)
        prev_el.addnext(el)
        prev_el = el
        run = Run(el, paragraph)
        run.text = seg_text  # python-docx sets xml:space="preserve" as needed
        if seg_bold:
            run.font.bold = True
            run.font.cs_bold = True  # keep w:b / w:bCs paired (template rule)
            bolded += 1
    src._r.getparent().remove(src._r)
    return bolded


def _apply_bold(doc, bold_plan):
    """Locate every planned bullet in document order; bold its spans.

    Entries with no spans are still located — so this doubles as a
    render-time integrity assert: a bullet the plan expected but the
    document cannot show is a hard failure, not a silent blank.
    """
    if not bold_plan:
        return 0
    paras = doc.paragraphs
    cursor = 0
    bolded = 0
    for spec in bold_plan:
        idx = _find_paragraph(paras, spec["text"], start=cursor)
        if idx is None:
            raise PostprocessError(
                "bullet not found in rendered doc (order or text mismatch): "
                + repr(spec["text"][:60]))
        cursor = idx + 1
        if spec.get("spans"):
            bolded += _split_run_bold(paras[idx], spec["spans"])
    return bolded


def _remove_sections(doc, disabled, headers):
    """Delete each disabled section's paragraphs (header through the
    paragraph before the next known header). Collect-then-remove."""
    removed, warnings = [], []
    if not disabled:
        return removed, warnings

    paras = doc.paragraphs
    header_positions = {}
    for i, p in enumerate(paras):
        stripped = p.text.strip()
        for name, header_text in headers.items():
            if stripped == header_text:
                header_positions[name] = i
    header_indices = sorted(header_positions.values())

    ranges = []
    for name in disabled:
        if name in REQUIRED_SECTIONS:
            warnings.append(
                "section '%s' is required and was not removed" % name)
            continue
        if name not in headers:
            warnings.append(
                "section '%s' has no header mapping; not removed" % name)
            continue
        if name not in header_positions:
            warnings.append(
                "header for section '%s' not found in document; "
                "nothing removed" % name)
            continue
        start = header_positions[name]
        following = [i for i in header_indices if i > start]
        end = following[0] if following else len(paras)
        ranges.append((name, start, end))

    for name, start, end in ranges:
        for p in paras[start:end]:
            el = p._element
            parent = el.getparent()
            if parent is not None:
                parent.remove(el)
        removed.append(name)
    return removed, warnings


def postprocess_cv(docx_path, bold_plan, disabled_sections=(),
                   section_headers=OPUS_SECTION_HEADERS):
    """Post-render pass: remove disabled sections, apply planned bold.

    Opens the document once, saves in place. Returns a summary dict:
    {"removed_sections": [...], "bolded_runs": int, "warnings": [...]}.

    Raises PostprocessError when a planned bullet cannot be located —
    ship nothing rather than a CV whose bullets are not where the plan
    says they are.
    """
    doc = Document(docx_path)
    removed, warnings = _remove_sections(doc, disabled_sections,
                                         section_headers)
    bolded = _apply_bold(doc, bold_plan)
    doc.save(docx_path)
    return {
        "removed_sections": removed,
        "bolded_runs": bolded,
        "warnings": warnings,
    }


if __name__ == "__main__":
    # Smallest self-check: segments logic (the only branchy pure function).
    assert _segments("abcdef", [(1, 3)]) == [("a", False), ("bc", True),
                                             ("def", False)]
    assert _segments("abcdef", [(0, 2), (2, 4)]) == [("abcd", True),
                                                     ("ef", False)]
    assert _segments("abc", [(5, 9)]) == [("abc", False)]
    assert _segments("Label: rest", [(0, 6)]) == [("Label:", True),
                                                  (" rest", False)]
    print("postprocess self-test (_segments): passed.")
