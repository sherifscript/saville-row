"""
lint_diagnosis.py — mechanical validation of a Diagnosis.md before any CV.

The diagnosis is "the only place in the framework where editorial judgment
lives" (diagnosis-template.md), yet until v1.8.0 nothing validated it: a thin
angle line ("Slot 3: research angled as analysis") licensed a thin CV that
then passed every downstream gate. This lint is the mechanical floor under
the diagnosis spec — structure and substance signals only; the editorial
quality of the angles remains the model's job.

Checks:
  1. The five core sections + Keywords + Section angles are present.
  2. The Keywords section lists 6-10 bullet lines (the ATS terms).
  3. At least `expected_slots` `- Slot N` angle lines exist.
  4. Every Slot line names a proof point: `proof point:` followed by >= 3
     words, or the explicit token `none` (so cv-tailor does not invent one).
  5. Every Slot line is >= 90 chars — a one-word abstraction in the angle
     gives cv-tailor nothing to preserve and licenses a thin bullet
     (the observed good angle lines run ~200 chars).

Wired into cv-tailor's gate: render_cv.render() runs this on the diagnosis
and refuses to render when it fails. CLI:

    python lint_diagnosis.py <Diagnosis.md> [--slots N]
"""

import re

# Substring probes (case-insensitive) for the required headings — tolerant of
# heading-punctuation drift between template versions.
REQUIRED_SECTIONS = (
    ("hiring to fix", "## What is this team actually hiring to fix?"),
    ("first 90 days", "## What would a great hire deliver in their first 90 days?"),
    ("actual bar", "## What is the actual bar?"),
    ("credentials speaks loudest", "## Which of my credentials speaks loudest to that bar?"),
    ("keywords from the jd", "## Keywords from the JD that must appear verbatim in the CV"),
    ("section angles", "## Section angles"),
)

_SLOT_LINE_RE = re.compile(r"^[-*]\s*Slot\s*\d", re.IGNORECASE)
_PROOF_POINT_RE = re.compile(r"proof point:\s*(.+?)(?:\||$)", re.IGNORECASE)
_HEADING_RE = re.compile(r"^#{2,3}\s+(.*)$")

MIN_KEYWORDS = 6
MAX_KEYWORDS = 10
MIN_SLOT_LINE_CHARS = 90


def _keyword_bullets(lines):
    """Bullet lines under the Keywords heading, up to the next heading."""
    bullets = []
    in_section = False
    for line in lines:
        m = _HEADING_RE.match(line.strip())
        if m:
            in_section = "keywords from the jd" in m.group(1).lower()
            continue
        if in_section and re.match(r"^[-*]\s+\S", line.strip()):
            bullets.append(line.strip())
    return bullets


def lint_diagnosis(md_text, expected_slots=3):
    """Validate a Diagnosis.md's structure. Returns (ok, errors)."""
    errors = []
    lower = md_text.lower()
    lines = md_text.splitlines()

    # 1. Required sections present.
    for probe, canonical in REQUIRED_SECTIONS:
        if probe not in lower:
            errors.append("missing section: %r" % canonical)

    # 2. Keyword count.
    kws = _keyword_bullets(lines)
    if not (MIN_KEYWORDS <= len(kws) <= MAX_KEYWORDS):
        errors.append(
            "keywords section has %d bullet(s); need %d-%d verbatim JD "
            "keywords" % (len(kws), MIN_KEYWORDS, MAX_KEYWORDS))

    # 3-5. Slot angle lines.
    slot_lines = [ln.strip() for ln in lines if _SLOT_LINE_RE.match(ln.strip())]
    if len(slot_lines) < expected_slots:
        errors.append(
            "Section angles has %d 'Slot N' line(s); need one per experience "
            "slot (%d)" % (len(slot_lines), expected_slots))
    for ln in slot_lines:
        preview = ln[:50] + ("..." if len(ln) > 50 else "")
        pp = _PROOF_POINT_RE.search(ln)
        if not pp:
            errors.append(
                "slot angle line lacks 'proof point:': %r" % preview)
        else:
            val = pp.group(1).strip().rstrip(".")
            if val.lower() != "none" and len(val.split()) < 3:
                errors.append(
                    "proof point too thin (%r) — name the credential/metric "
                    "or write 'none': %r" % (val, preview))
        if len(ln) < MIN_SLOT_LINE_CHARS:
            errors.append(
                "slot angle line under %d chars — a thin angle licenses a "
                "thin bullet; name the concrete career-file detail to carry: "
                "%r" % (MIN_SLOT_LINE_CHARS, preview))

    return (not errors), errors


if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("diagnosis", help="Path to a Diagnosis.md")
    parser.add_argument("--slots", type=int, default=3,
                        help="Expected experience slot count (default 3)")
    args = parser.parse_args()

    with open(args.diagnosis, encoding="utf-8") as f:
        text = f.read()
    ok, errs = lint_diagnosis(text, expected_slots=args.slots)
    if ok:
        print("Diagnosis lint: PASSED")
        sys.exit(0)
    print("Diagnosis lint: FAILED")
    for e in errs:
        print("  -", e)
    sys.exit(1)
