"""
Guards the 2026-06-14 failure mode: tailoring effort decayed down the page.
The lead experience slot was tailored per role, but the lower and branch slots
shipped as byte-for-byte identical career-file boilerplate across every CV
(the Atheneum slot was identical in all ten CVs of the Denmark batch).

Check 8 fails any experience slot that carries zero diagnosed keywords.
Check 9 fails any number in the CV that has no source in the career file.

Guards the 2026-06-25 failure mode: bullets passed every check and were still
weak, defaulting to generic nouns ("enterprise decision-makers") where named
proof points sat unused. Check 10 fails the generic-filler blocklist.
"""
from audit import (check_8_slot_coverage, check_9_numeric_grounding,
                   check_10_bullet_strength)


KEYWORDS = ["category strategies", "shopper insights", "data-driven", "pricing"]


def test_check8_flags_unangled_lower_slot():
    """Lead slot tailored, branch slot pasted verbatim -> fail, naming the slot."""
    exp = [
        {"company": "Statista", "bullets": [
            "Translated pricing and shopper insights into data-driven recommendations."]},
        {"company": "Atheneum", "bullets": [
            "Conduct technical interviews with SWANA-based experts for market research."]},
    ]
    ok, note = check_8_slot_coverage(exp, KEYWORDS)
    assert ok is False
    assert "slot 2" in note and "Atheneum" in note


def test_check8_passes_when_every_slot_angled():
    exp = [
        {"company": "Statista", "bullets": ["Built data-driven category strategies."]},
        {"company": "Atheneum", "bullets": ["Shopper insights from expert interviews."]},
    ]
    ok, _ = check_8_slot_coverage(exp, KEYWORDS)
    assert ok is True


def test_check8_skips_without_data():
    assert check_8_slot_coverage([], KEYWORDS)[0] is True
    assert check_8_slot_coverage([{"company": "X"}], KEYWORDS)[0] is True  # no bullets


CAREER = "increased publication speed by 30%; covered 40+ firms across 8+ industries."


def test_check9_flags_invented_metric():
    xml = "<w:t>Raised speed 30% across 40+ firms and lifted retention 55%</w:t>"
    ok, note = check_9_numeric_grounding(xml, CAREER)
    assert ok is False
    assert "55%" in note and "30%" not in note  # only the invented one is flagged


def test_check9_passes_when_all_grounded():
    xml = "<w:t>Raised speed 30% across 40+ firms in 8+ industries</w:t>"
    assert check_9_numeric_grounding(xml, CAREER)[0] is True


def test_check9_skips_without_career_file():
    xml = "<w:t>lifted retention 55%</w:t>"
    assert check_9_numeric_grounding(xml, None)[0] is True


def test_check10_flags_generic_filler():
    exp = [{"company": "Statista", "bullets": [
        "Tracked positioning for enterprise decision-makers."]}]
    ok, note = check_10_bullet_strength(exp)
    assert ok is False
    assert "enterprise decision-makers" in note and "Statista" in note


def test_check10_passes_named_proof_point():
    exp = [{"company": "Statista", "bullets": [
        "Synthesized findings into reports cited by Deloitte and the "
        "Harvard Law Review."]}]
    assert check_10_bullet_strength(exp)[0] is True


def test_check10_reads_richtext_bullets():
    """Labeled / inline_bold mode: bullets are RichText, not strings."""
    from md_to_richtext import md_to_richtext
    exp = [{"company": "X", "bullets": [
        md_to_richtext("**Coverage:** served global process owners.")]}]
    assert check_10_bullet_strength(exp)[0] is False


def test_check10_skips_without_experiences():
    assert check_10_bullet_strength([])[0] is True
