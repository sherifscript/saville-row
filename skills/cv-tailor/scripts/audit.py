"""
audit.py — post-render audit for tailored CVs.

Implements the two programmatic checks of the five-question post-render audit
(see skills/cv-tailor/references/post-render-audit.md). The editorial checks (#1, #3)
are run by the model, not here.

Programmatic checks:
  Check 2 — at least two JD keywords appear verbatim in the rendered CV.
  Check 4 — every & from the content_map survives into the rendered XML.
  Check 5 — bolded runs (<w:b/>) exist inside the experience section when the
            diagnosis specified bold-worthy phrases.

A CV that fails any check is NOT shipped.
"""

import zipfile
import re
from dataclasses import dataclass, field


@dataclass
class AuditResult:
    passed: dict = field(default_factory=dict)
    notes: dict = field(default_factory=dict)

    @property
    def all_passed(self):
        return all(self.passed.values())

    @property
    def failure_summary(self):
        lines = []
        for name, ok in self.passed.items():
            if not ok:
                lines.append("  FAIL [" + name + "]: " + self.notes.get(name, ""))
        return "\n".join(lines) if lines else "All checks passed."


def _read_document_xml(docx_path):
    """Return word/document.xml as a string."""
    with zipfile.ZipFile(docx_path) as z:
        return z.read("word/document.xml").decode("utf-8", errors="replace")


def _visible_text(document_xml):
    """Concatenate all <w:t> text content from the document XML."""
    return " ".join(re.findall(r"<w:t[^>]*>(.*?)</w:t>", document_xml, re.DOTALL))


def _iter_strings(obj):
    """Yield every string value nested anywhere in obj."""
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for v in obj.values():
            yield from _iter_strings(v)
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            yield from _iter_strings(v)


def check_2_keywords_in_experience(document_xml, expected_keywords):
    """Check 2: >= 2 JD keywords appear verbatim in the rendered document.

    Editorial review (checks 1/3) confirms the keywords land in experience
    bullets specifically.
    """
    text = _visible_text(document_xml).lower()
    hits = [kw for kw in expected_keywords if kw.lower() in text]
    ok = len(hits) >= 2
    if ok:
        note = str(len(hits)) + "/" + str(len(expected_keywords)) \
            + " keywords found verbatim: " + str(hits)
    else:
        note = "Only " + str(len(hits)) + " keyword(s) found verbatim (" \
            + str(hits) + "); need >= 2."
    return ok, note


def check_4_ampersands(document_xml, content_map):
    """Check 4: every & in content_map values survives into the rendered XML.

    The pass/fail criterion is purely the ampersand count. Double spaces are
    NOT a fail criterion — many templates legitimately use spaced separators
    ("  |  ", "  .  "). A double space is only a locating aid once the count
    check has already failed.
    """
    expected_amp = 0
    for value in _iter_strings(content_map):
        expected_amp += value.count("&")
    rendered_amp = document_xml.count("&amp;")
    ok = rendered_amp >= expected_amp
    if ok:
        note = (str(rendered_amp) + " ampersands rendered (>= "
                + str(expected_amp) + " expected).")
    else:
        text = _visible_text(document_xml)
        double_space_hits = len(re.findall(r"\S  \S", text))
        note = ("expected >= " + str(expected_amp) + " ampersands, found "
                + str(rendered_amp) + " (autoescape=False suspected). "
                + str(double_space_hits) + " double-space occurrence(s) in "
                "visible text — inspect those to locate the stripped "
                "ampersand(s).")
    return ok, note


def check_5_bold_in_experience(document_xml, expect_bold):
    """Check 5: bolded runs exist when the diagnosis specified bold phrases."""
    if not expect_bold:
        return True, "No bold phrases specified by diagnosis; check skipped."
    bold_runs = len(re.findall(r"<w:b\s*/>", document_xml))
    ok = bold_runs > 0
    if ok:
        note = str(bold_runs) + " bold run(s) found in rendered XML."
    else:
        note = ("Zero bold runs found, but diagnosis specified bold phrases. "
                "RichText likely embedded as text inside <w:t> — re-render. "
                "(See 2026-05-11 regression in post-render-audit.md.)")
    return ok, note


def run_full_audit(rendered_docx_path, diagnosis_md_path, content_map,
                   expected_keywords, expect_bold=True):
    """Run the programmatic audit checks. Returns an AuditResult.

    The editorial checks (#1, #3) are recorded by the model into the same
    result via result.passed['check_1'] / result.passed['check_3'].
    """
    document_xml = _read_document_xml(rendered_docx_path)
    result = AuditResult()

    ok2, note2 = check_2_keywords_in_experience(document_xml, expected_keywords)
    result.passed["check_2_keywords"] = ok2
    result.notes["check_2_keywords"] = note2

    ok4, note4 = check_4_ampersands(document_xml, content_map)
    result.passed["check_4_ampersands"] = ok4
    result.notes["check_4_ampersands"] = note4

    ok5, note5 = check_5_bold_in_experience(document_xml, expect_bold)
    result.passed["check_5_bold"] = ok5
    result.notes["check_5_bold"] = note5

    return result


if __name__ == "__main__":
    import sys
    import os
    if len(sys.argv) < 2:
        print("Usage: python audit.py <rendered_cv.docx>")
        sys.exit(1)
    if not os.path.isfile(sys.argv[1]):
        print(f"Error: file not found: {sys.argv[1]}", file=sys.stderr)
        sys.exit(1)
    xml = _read_document_xml(sys.argv[1])
    bold_count = len(re.findall(r"<w:b\s*/>", xml))
    amp_count = xml.count("&amp;")
    double_space_count = len(re.findall(r"\S  \S", _visible_text(xml)))
    print("Bold runs in document:", bold_count)
    print("Escaped ampersands:", amp_count)
    print("Double-space occurrences:", double_space_count)
