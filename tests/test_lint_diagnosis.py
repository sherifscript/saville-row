"""
Tests for lint_diagnosis — the mechanical floor under the diagnosis spec.
A thin diagnosis licenses a thin CV; the lint refuses to let cv-tailor
render from one.
"""
from lint_diagnosis import lint_diagnosis, parse_positioning_mode


def _good_diagnosis():
    """Modeled on the real Helios Energy diagnosis shape from the a 2026-06 batch."""
    return """# Role Diagnosis — Helios Energy Europe | Market Research Analyst

## What is this team actually hiring to fix?

They need market intelligence on European solar markets that senior
management can act on, and nobody on the commercial team owns it.

## What would a great hire deliver in their first 90 days?

A competitive landscape read of the top European inverter markets.

## What is the actual bar?

Methodological rigor.

## Which of my credentials speaks loudest to that bar?

End-to-end coverage of 40+ multinationals with findings cited by Alpha Advisory.

## Branch

research-market-intelligence: keyword overlap on market research.

## Keywords from the JD that must appear verbatim in the CV

- market research
- competitive intelligence
- market trends
- quantitative
- reports and presentations
- strategic recommendations
- senior management

## Section angles — one line for every rendered part

- Slot 1 (Northwind Research Expert): end-to-end coverage of 40+ multinationals, competitive positioning and market sizing | proof point: cited by Alpha Advisory, Beacon Law Review, Meridian Institute | angled as competitive intelligence for senior management.
- Slot 2 (Northwind Research Assistant): tracked sectors and synthesized findings into publication-ready outputs | proof point: data used by institutions, governments, media | angled as quantitative market research under deadline.
- Slot 3 (Cobalt Expert Network, research/recency): conduct technical interviews with industry experts | proof point: regional expert interviews for global research | angled as primary research feeding strategic recommendations.
- Higher degree (MSc PEP): economics and quantitative methods | angled as analytical rigor.
- core_skills: market research & competitive intelligence, quantitative analysis, tools.

## Positioning

**Mode: direct**

This is the candidate's actual last job under a different logo; energy-sector
specificity is the only gap, learnable and not the bar.
"""


def test_good_diagnosis_passes():
    ok, errors = lint_diagnosis(_good_diagnosis(), expected_slots=3)
    assert ok, errors


def test_missing_section_fails():
    text = _good_diagnosis().replace(
        "## What is the actual bar?", "## Something else")
    ok, errors = lint_diagnosis(text)
    assert not ok
    assert any("actual bar" in e for e in errors)


def test_too_few_keywords_fails():
    text = _good_diagnosis()
    head, _, tail = text.partition(
        "## Keywords from the JD that must appear verbatim in the CV")
    kw_block, _, rest = tail.partition("## Section angles")
    trimmed = "\n".join(
        [ln for ln in kw_block.splitlines() if ln.strip().startswith("-")][:4])
    text = (head
            + "## Keywords from the JD that must appear verbatim in the CV\n\n"
            + trimmed + "\n\n## Section angles" + rest)
    ok, errors = lint_diagnosis(text)
    assert not ok
    assert any("keywords" in e for e in errors)


def test_missing_slot_line_fails():
    text = "\n".join(ln for ln in _good_diagnosis().splitlines()
                     if not ln.startswith("- Slot 3"))
    ok, errors = lint_diagnosis(text, expected_slots=3)
    assert not ok
    assert any("Slot" in e for e in errors)


def test_slot_line_without_proof_point_fails():
    text = _good_diagnosis().replace(
        "| proof point: regional expert interviews for global research ", "")
    ok, errors = lint_diagnosis(text)
    assert not ok
    assert any("proof point" in e for e in errors)


def test_thin_proof_point_fails_but_explicit_none_passes():
    text = _good_diagnosis().replace(
        "proof point: regional expert interviews for global research",
        "proof point: regional")
    ok, errors = lint_diagnosis(text)
    assert not ok
    assert any("too thin" in e for e in errors)

    text_none = _good_diagnosis().replace(
        "proof point: regional expert interviews for global research",
        "proof point: none — say so explicitly, do not invent one; the slot "
        "carries transferable primary-research framing instead")
    ok_none, errors_none = lint_diagnosis(text_none)
    assert ok_none, errors_none


def test_short_slot_angle_fails():
    text = _good_diagnosis().replace(
        "- Slot 3 (Cobalt Expert Network, research/recency): conduct technical interviews "
        "with industry experts | proof point: regional expert interviews for "
        "global research | angled as primary research feeding strategic "
        "recommendations.",
        "- Slot 3: research | proof point: regional expert interviews rock")
    ok, errors = lint_diagnosis(text)
    assert not ok
    assert any("chars" in e for e in errors)


def test_missing_positioning_fails():
    text = _good_diagnosis().split("## Positioning")[0]
    ok, errors = lint_diagnosis(text)
    assert not ok
    assert any("Positioning" in e for e in errors)


def test_parse_positioning_mode():
    assert parse_positioning_mode(_good_diagnosis()) == "direct"
    assert parse_positioning_mode(
        "## Positioning\n\n**Mode: transition** — career change.") == "transition"
    assert parse_positioning_mode("Mode: adjacent, did the work") == "adjacent"
    assert parse_positioning_mode("no positioning here") is None
