"""
audit.py — post-render audit for tailored CVs.

Implements the programmatic checks of the post-render audit
(see skills/cv-tailor/references/post-render-audit.md). The editorial checks (#1, #3)
are run by the model, not here.

Programmatic checks:
  Check 2 — at least two JD keywords appear verbatim in the rendered CV.
  Check 4 — every & from the content_map survives into the rendered XML.
  Check 5 — rendered-text integrity: every authored bullet is readable via
            python-docx (the parser Word and ATS systems agree with), per-slot
            counts match, no raw markup in any paragraph text, planned bold
            spans are real bold runs, and the contact hyperlinks survive.
            Supersedes the old bold-run regex count, which could never fail
            on the OPUS template (its section headers are bold) and passed
            the 2026-05-11 / test5 corruption where every bullet rendered
            EMPTY (RichText embedded inside <w:t> is invisible to Word but
            visible to a regex).
  Check 6 — no em dashes in the rendered CV (employer-facing output; see
            shared/conventions.md).
  Check 7 — experience section is in strict reverse-chronological order and
            the primary employer's contiguous block occupies slots 1 + 2.
  Check 8 — tailoring coverage: every experience slot reflects the diagnosis
            (each slot's bullets carry at least one diagnosed keyword), so no
            slot ships as un-angled career-file boilerplate.
  Check 9 — grounding: every number/percentage/count in the rendered CV traces
            to the career file, catching invented or inflated metrics.
  Check 10 — bullet strength: no experience bullet hides behind a generic
            abstraction ("enterprise decision-makers", "global process owners")
            *while carrying no concrete proof of its own*. Grounding-aware: a
            bullet with a number or named entity may keep natural phrasing; only
            the thin, ungrounded bullet fails. Programmatic floor for the
            editorial "surface a concrete proof point, not a generic noun" bar.

A CV that fails any check is NOT shipped.
"""

import zipfile
import re
from dataclasses import dataclass, field

from docx import Document


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


def _bullet_text(bullet):
    """Return the plain text of a content_map bullet.

    Since v1.8.0 bullets are always plain strings (build_bold_plan strips
    the ** markers; RichText is banned from the render path). The RichText
    branch below is kept ONLY for forensics of files/content maps produced
    before v1.8.0 — do not rely on it for new renders.
    """
    if isinstance(bullet, str):
        return bullet
    xml = getattr(bullet, "xml", "") or str(bullet)
    return " ".join(re.findall(r"<w:t[^>]*>(.*?)</w:t>", xml, re.DOTALL))


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


def _norm_ws(text):
    return " ".join(text.split())


def check_5_rendered_integrity(rendered_docx_path, content_map,
                               bold_plan=None, expect_bold=False):
    """Check 5: rendered-text integrity (supersedes the bold-run regex count).

    Opens the rendered docx with python-docx — the same parse Word and ATS
    systems perform — and asserts the authored content is actually visible:

      a. every authored experience bullet appears as a whole, non-empty
         paragraph, in order; per-slot readable counts match the content map;
      b. same for msc_bullets / ba_bullets;
      c. no paragraph text contains raw markup ('<w:') or leftover '**';
      d. when bold was planned: each planned span's text is covered by a run
         with run.bold True in its paragraph (real run inspection);
      e. the contact hyperlinks survived the postprocess round-trip
         (>= 2 hyperlink relationships — asherif.me + LinkedIn in OPUS).

    Why it exists: the old check counted <w:b/> in the raw XML. The OPUS
    template's own section headers are bold, so that count could never be
    zero — the check was unfailable — and it passed the 2026-05-11 / test5
    corruption where every bullet rendered EMPTY (RichText embedded inside
    <w:t> is invisible to Word but visible to a regex). This check reads
    what a recruiter reads.
    """
    problems = []
    doc = Document(rendered_docx_path)
    paras = doc.paragraphs

    def find(text, start):
        target = _norm_ws(text)
        for i in range(start, len(paras)):
            if _norm_ws(paras[i].text) == target:
                return i
        return None

    # a + b: every authored bullet is a readable paragraph, in order.
    expected_lists = []
    for si, role in enumerate(content_map.get("experiences", [])):
        label = "slot %d (%s)" % (si + 1, role.get("company", "?"))
        expected_lists.append((label, role.get("bullets", []) or []))
    for key in ("msc_bullets", "ba_bullets"):
        if content_map.get(key):
            expected_lists.append((key, content_map[key]))

    cursor = 0
    total_expected = 0
    total_found = 0
    for label, bullets in expected_lists:
        found = 0
        for b in bullets:
            btext = _bullet_text(b)
            if not btext.strip():
                continue
            total_expected += 1
            idx = find(btext, cursor)
            if idx is None:
                problems.append(
                    "%s: bullet NOT readable in rendered doc: %r"
                    % (label, btext[:60]))
                continue
            cursor = idx + 1
            found += 1
            total_found += 1
        expected = len([b for b in bullets if _bullet_text(b).strip()])
        if found != expected:
            problems.append(
                "%s: only %d/%d bullets readable" % (label, found, expected))

    # c: no raw markup or leftover markers in any visible paragraph.
    for i, p in enumerate(paras):
        if "<w:" in p.text or "**" in p.text:
            problems.append(
                "paragraph %d contains raw markup or ** markers: %r"
                % (i, p.text[:60]))

    # d: planned bold spans rendered as real bold runs.
    bold_checked = 0
    if expect_bold and bold_plan:
        cursor2 = 0
        for spec in bold_plan:
            spans = spec.get("spans") or []
            if not spans:
                continue
            idx = find(spec["text"], cursor2)
            if idx is None:
                continue  # already reported unreadable above
            cursor2 = idx + 1
            bold_text = _norm_ws(
                "".join(r.text for r in paras[idx].runs if r.bold))
            for s, e in spans:
                span_text = _norm_ws(spec["text"][s:e])
                if span_text and span_text not in bold_text:
                    problems.append(
                        "bold span not rendered bold: %r in %r"
                        % (span_text[:40], spec["text"][:40]))
                else:
                    bold_checked += 1
    elif expect_bold and not bold_plan:
        problems.append("expect_bold=True but no bold_plan was supplied")

    # e: contact hyperlinks survived the round-trip.
    with zipfile.ZipFile(rendered_docx_path) as z:
        rels = z.read("word/_rels/document.xml.rels").decode(
            "utf-8", errors="replace")
    n_links = rels.count("/relationships/hyperlink")
    if n_links < 2:
        problems.append(
            "hyperlink relationships: %d found, >= 2 expected (personal "
            "site + LinkedIn) — the postprocess round-trip may have dropped "
            "them" % n_links)

    ok = not problems
    if ok:
        note = ("%d/%d bullets readable via python-docx; %d bold span(s) "
                "verified; %d hyperlink rel(s) intact."
                % (total_found, total_expected, bold_checked, n_links))
    else:
        note = "; ".join(problems)
    return ok, note


def check_6_no_em_dashes(document_xml):
    """Check 6: no em dashes in the rendered CV.

    Em dashes (U+2014, —) are banned from all employer-facing output.
    See shared/conventions.md.
    """
    text = _visible_text(document_xml)
    em_dash_count = text.count("—")
    ok = em_dash_count == 0
    if ok:
        note = "No em dashes found."
    else:
        note = (str(em_dash_count) + " em dash(es) found in rendered CV. "
                "Replace with commas, periods, or restructure the sentence. "
                "See shared/conventions.md.")
    return ok, note


def check_7_experience_structure(experiences):
    """Check 7: experience list is reverse-chronological and the primary
    employer's contiguous block holds slots 1 + 2.

    `experiences` is the list of dicts from the content_map (before rendering).
    Each dict must have: company, title, end_year (int; use 9999 for 'Present').

    Returns (ok, note). Returns (True, skip-note) if experiences has fewer
    than 2 entries or if end_year keys are absent — those cases need manual
    review, not a hard fail.
    """
    if not experiences or len(experiences) < 2:
        return True, "Fewer than 2 experience entries; structure check skipped."

    if not all("end_year" in e for e in experiences):
        return True, ("end_year not present on all entries; "
                      "chronology check requires manual review.")

    # Check strict reverse-chronological order
    years = [e["end_year"] for e in experiences]
    if years != sorted(years, reverse=True):
        return False, (
            "Experience entries are not in strict reverse-chronological order. "
            "Order: " + str([str(e.get("company", "?")) + " " + str(e.get("end_year"))
                             for e in experiences]) + ". "
            "Most recent role (highest end_year) must be slot 1. "
            "Ongoing roles use end_year=9999."
        )

    # Check that slots 1 and 2 share the same employer (contiguous block rule)
    slot1_company = experiences[0].get("company", "")
    slot2_company = experiences[1].get("company", "") if len(experiences) > 1 else ""
    if slot1_company and slot2_company and slot1_company != slot2_company:
        return False, (
            "Slots 1 and 2 are different employers ("
            + str(slot1_company) + " vs " + str(slot2_company) + "). "
            "When the candidate has two adjacent roles at the same primary employer "
            "(e.g., Statista Expert + Statista Assistant), they must occupy slots "
            "1 + 2 as a contiguous block. See "
            "skills/cv-tailor/references/experience-slot-logic.md."
        )

    return True, ("Experience structure valid: reverse-chronological; "
                  "slots 1 + 2 share employer " + str(slot1_company) + ".")


def check_8_slot_coverage(experiences, expected_keywords):
    """Check 8: every experience slot is angled to this role.

    The diagnosis now mandates that at least one diagnosed keyword/angle reaches
    every experience slot, not just the lead (see diagnosis-template.md
    "Section angles"). The programmatic floor: each slot's bullets must contain
    at least one diagnosed keyword verbatim. A slot with zero is the symptom of
    un-angled career-file boilerplate pasted across CVs.

    Skipped (manual review) when keywords or bullets are absent.
    """
    if not expected_keywords or not experiences:
        return True, "No keywords or no experiences; coverage check skipped."
    if not all(e.get("bullets") for e in experiences):
        return True, ("Not all slots carry bullets in the content_map; "
                      "coverage check requires manual review.")

    kws = [k.lower() for k in expected_keywords]
    uncovered = []
    for i, e in enumerate(experiences):
        text = " ".join(_bullet_text(b) for b in e.get("bullets", [])).lower()
        if not any(k in text for k in kws):
            uncovered.append("slot " + str(i + 1) + " ("
                             + str(e.get("company", "?")) + ")")
    ok = not uncovered
    if ok:
        note = "Every experience slot carries >= 1 diagnosed keyword."
    else:
        note = ("Un-angled slot(s) with zero diagnosed keywords: "
                + ", ".join(uncovered) + ". The diagnosis must give each slot a "
                "Section-angle; do not paste career-file phrasing verbatim. See "
                "references/content-map-schema.md 'Facts vs angle'.")
    return ok, note


def check_9_numeric_grounding(document_xml, career_file_text):
    """Check 9: every metric in the rendered CV traces to the career file.

    Catches invented/inflated numbers (e.g. a "30%" or "40+" the career file
    never states). Conservative: only flags percentages (\\d+%) and count
    claims (\\d+\\+), and only when the digit sequence appears nowhere in the
    career file — so a real number written slightly differently still passes.
    Semantic inflation ("supported" -> "led") is the editorial honesty
    companion, not this check.

    Skipped when no career file text is provided.
    """
    if not career_file_text:
        return True, "No career file provided; numeric grounding skipped."

    text = _visible_text(document_xml)
    metrics = re.findall(r"\d+%|\d+\+", text)
    career_digits = career_file_text
    ungrounded = []
    for m in metrics:
        digits = re.sub(r"\D", "", m)
        if digits and digits not in career_digits:
            ungrounded.append(m)
    # de-dup while keeping order
    seen = set()
    ungrounded = [m for m in ungrounded if not (m in seen or seen.add(m))]
    ok = not ungrounded
    if ok:
        note = (str(len(metrics)) + " metric(s) checked; all trace to the "
                "career file.")
    else:
        note = ("Metric(s) with no source in the career file: "
                + ", ".join(ungrounded) + ". A bullet may re-frame a real fact "
                "but may not invent a number. Remove or correct, or add the fact "
                "to the career file if it is real.")
    return ok, note


# Generic filler phrases that signal a weak, un-tailored bullet. Each one
# was an actual offender in the 2026-06-25 Cairo batch, where bullets said
# "enterprise decision-makers" while named proof points (Deloitte, Harvard
# Law Review, W3C) sat unused in the career file. High-precision by design:
# only multi-word abstractions. Bare "stakeholders" is deliberately NOT listed
# (it is a common, valid JD term).
#
# These phrases are flagged only when the bullet carrying them has NO concrete
# proof point of its own (no number, no named entity) — see _has_concrete_proof.
# A grounded bullet may legitimately contain one of these phrases ("managed
# analytical workstreams for 40+ multinationals across Technology and Telecom"
# is strong; the phrase is incidental). The unconditional substring ban was the
# v1.6.0 over-correction that pushed bullets toward thin paraphrase — it failed
# the same phrasing the rich benchmark CVs legitimately use.
WEAK_GENERIC_PHRASES = (
    "enterprise decision-makers",
    "enterprise decision makers",
    "global process owners",
    "analytical workstreams",
    "client-ready",
    "actionable insights",
    "actionable recommendations",
    "evidence-based reports",
)

# ponytail: heuristic proof detector, not an NER. A digit or a mid-sentence
# proper noun is "concrete enough"; editorial check 3 is the real judge.
_PROPER_NOUN_RE = re.compile(r"\b([A-Z][a-zA-Z]+|[A-Z]{2,})\b")


def _has_concrete_proof(bullet_text):
    """True if the bullet carries a number or a named entity.

    A number (40+, 30%, $30K, 11M, a year) is unambiguous proof. For named
    entities we strip any leading `Label:` lead-in (labeled bullet_style) so the
    capability label's own capitalization does not count, then look for a
    capitalized token that is not the first word of the clause — Deloitte,
    Python, Power BI, US/Canadian, Statista. Crude but high-precision for the
    job: it only gates whether a WEAK_GENERIC_PHRASE is allowed to stand.
    """
    if any(ch.isdigit() for ch in bullet_text):
        return True
    # Strip a short leading "Label:" segment (labeled mode) before noun scan.
    clause = re.sub(r"^[^:]{0,40}:\s*", "", bullet_text).strip()
    if not clause:
        return False
    first_word = clause.split()[0]
    for m in _PROPER_NOUN_RE.finditer(clause):
        if m.group(0) != first_word:  # ignore a capitalized sentence start
            return True
    return False


def check_10_bullet_strength(experiences):
    """Check 10: no experience bullet hides behind a generic abstraction
    *without any concrete proof of its own*.

    Programmatic floor for the editorial bar "surface a concrete proof point,
    not a generic noun". A WEAK_GENERIC_PHRASE fails only when its bullet has no
    number and no named entity (_has_concrete_proof). This lets a grounded bullet
    keep natural phrasing while still catching the thin, abstract bullet the
    phrase list was written for. Needs no career file; only skips when there are
    no experiences at all.

    Reads bullet text via _bullet_text so it works whether bullets are plain
    strings or RichText (labeled / inline_bold mode).
    """
    if not experiences:
        return True, "No experiences; bullet-strength check skipped."

    hits = []
    for i, e in enumerate(experiences):
        for b in e.get("bullets", []):
            btext = _bullet_text(b)
            if _has_concrete_proof(btext):
                continue  # grounded bullet — phrase is incidental, allowed
            low = btext.lower()
            for phrase in WEAK_GENERIC_PHRASES:
                if phrase in low:
                    hits.append("slot " + str(i + 1) + " ("
                                + str(e.get("company", "?")) + "): '" + phrase
                                + "' in an ungrounded bullet")
    ok = not hits
    if ok:
        note = "No ungrounded generic-filler phrasing; bullets carry concrete proof."
    else:
        note = ("Generic filler in a bullet with no concrete proof: "
                + "; ".join(hits) + ". Either ground the bullet with the slot's "
                "named proof point / metric from the career file, or drop the "
                "abstraction. See the diagnosis's per-slot proof points.")
    return ok, note


def run_full_audit(rendered_docx_path, diagnosis_md_path, content_map,
                   expected_keywords, expect_bold=True, career_file_path=None,
                   bold_plan=None):
    """Run the programmatic audit checks. Returns an AuditResult.

    The editorial checks (#1, #3) are recorded by the model into the same
    result via result.passed['check_1'] / result.passed['check_3'].

    `bold_plan` is the plan returned by build_bold_plan(); Check 5 uses it
    to verify each planned bold span rendered as a real bold run.
    """
    document_xml = _read_document_xml(rendered_docx_path)
    result = AuditResult()

    ok2, note2 = check_2_keywords_in_experience(document_xml, expected_keywords)
    result.passed["check_2_keywords"] = ok2
    result.notes["check_2_keywords"] = note2

    ok4, note4 = check_4_ampersands(document_xml, content_map)
    result.passed["check_4_ampersands"] = ok4
    result.notes["check_4_ampersands"] = note4

    ok5, note5 = check_5_rendered_integrity(
        rendered_docx_path, content_map,
        bold_plan=bold_plan, expect_bold=expect_bold)
    result.passed["check_5_integrity"] = ok5
    result.notes["check_5_integrity"] = note5

    ok6, note6 = check_6_no_em_dashes(document_xml)
    result.passed["check_6_em_dashes"] = ok6
    result.notes["check_6_em_dashes"] = note6

    experiences = content_map.get("experiences", [])
    ok7, note7 = check_7_experience_structure(experiences)
    result.passed["check_7_structure"] = ok7
    result.notes["check_7_structure"] = note7

    ok8, note8 = check_8_slot_coverage(experiences, expected_keywords)
    result.passed["check_8_coverage"] = ok8
    result.notes["check_8_coverage"] = note8

    career_text = None
    if career_file_path:
        with open(career_file_path, encoding="utf-8", errors="replace") as f:
            career_text = f.read()
    ok9, note9 = check_9_numeric_grounding(document_xml, career_text)
    result.passed["check_9_grounding"] = ok9
    result.notes["check_9_grounding"] = note9

    ok10, note10 = check_10_bullet_strength(experiences)
    result.passed["check_10_bullet_strength"] = ok10
    result.notes["check_10_bullet_strength"] = note10

    return result


def _selftest():
    """Smallest check that fails if check_10 logic breaks (weak/strong split)."""
    weak = [{"company": "Statista", "bullets": [
        "Tracked competitive positioning for enterprise decision-makers."]}]
    strong = [{"company": "Statista", "bullets": [
        "Synthesized findings into reports cited by Deloitte and the "
        "Harvard Law Review, briefing global stakeholders."]}]
    ok_weak, _ = check_10_bullet_strength(weak)
    ok_strong, _ = check_10_bullet_strength(strong)
    assert not ok_weak, "check_10 should FAIL a generic-filler bullet"
    assert ok_strong, "check_10 should PASS a named-proof-point bullet"
    # Grounding-aware: a generic phrase is allowed when the bullet itself
    # carries concrete proof (a number or named entity).
    grounded = [{"company": "Statista", "bullets": [
        "Managed analytical workstreams for 40+ multinationals across "
        "Technology and Telecom, delivering client-ready outputs."]}]
    ok_grounded, _ = check_10_bullet_strength(grounded)
    assert ok_grounded, ("check_10 should PASS a grounded bullet even when it "
                         "contains a phrase from WEAK_GENERIC_PHRASES")
    assert _has_concrete_proof("Managed workstreams for 40+ corporations")
    assert not _has_concrete_proof("served enterprise decision-makers")
    # Works on labeled-style bullets too (bold label lead-in, plain string —
    # since v1.8.0 bullets are always plain strings by the time checks run).
    labeled_weak = [{"company": "X", "bullets": [
        "Coverage: served enterprise decision-makers."]}]
    ok_labeled, _ = check_10_bullet_strength(labeled_weak)
    assert not ok_labeled, "check_10 should FAIL filler behind a label lead-in"
    print("audit self-test (check_10): passed.")


if __name__ == "__main__":
    import sys
    import os
    if len(sys.argv) >= 2 and sys.argv[1] == "--selftest":
        _selftest()
        sys.exit(0)
    if len(sys.argv) < 2:
        print("Usage: python audit.py <rendered_cv.docx>  |  python audit.py --selftest")
        sys.exit(1)
    if not os.path.isfile(sys.argv[1]):
        print(f"Error: file not found: {sys.argv[1]}", file=sys.stderr)
        sys.exit(1)
    path = sys.argv[1]
    xml = _read_document_xml(path)
    doc = Document(path)
    paras = doc.paragraphs
    empty = sum(1 for p in paras if not p.text.strip())
    with zipfile.ZipFile(path) as z:
        rels = z.read("word/_rels/document.xml.rels").decode(
            "utf-8", errors="replace")
    print("Paragraphs (python-docx):", len(paras))
    print("Empty paragraphs:", empty,
          " <- empty bullets = the 2026-05-11/test5 corruption; investigate")
    print("Escaped ampersands:", xml.count("&amp;"))
    print("Hyperlink relationships:", rels.count("/relationships/hyperlink"))
    print("Em dashes:", _visible_text(xml).count("—"))
