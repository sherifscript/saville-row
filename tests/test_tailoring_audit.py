"""
Guards the 2026-06-14 failure mode: tailoring effort decayed down the page.
The lead experience slot was tailored per role, but the lower and branch slots
shipped as byte-for-byte identical career-file boilerplate across every CV
(the Atheneum slot was identical in all ten CVs of the Denmark batch).

Check 8 fails any experience slot that carries zero diagnosed keywords.
Check 9 fails any metric in the CV that has no source in the career file.

Guards the 2026-06-25 failure mode: bullets passed every check and were still
weak, defaulting to generic nouns ("enterprise decision-makers") where named
proof points sat unused. Check 10 fails the generic-filler blocklist and
(with a career file) enforces a per-slot proof-density floor.

Guards the 2026-06-27 audit dodges: end_years=None self-skipped Check 7;
editorial checks silently unrecorded still produced all_passed=True.
"""
from audit import (check_2_keywords_in_experience, check_7_experience_structure,
                   check_8_slot_coverage, check_9_numeric_grounding,
                   check_10_bullet_strength, check_11_proof_points,
                   AuditResult, run_full_audit)


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


def test_check10_reads_labeled_bullets():
    """Labeled mode: bullets are plain strings with a bold-label lead-in
    (since v1.8.0 bullets are always plain strings by audit time)."""
    exp = [{"company": "X", "bullets": [
        "Coverage: served global process owners."]}]
    assert check_10_bullet_strength(exp)[0] is False


def test_check10_skips_without_experiences():
    assert check_10_bullet_strength([])[0] is True


# ---------------------------------------------------------------------------
# Check 2 — keywords must land in experience bullets, not just anywhere.
# ---------------------------------------------------------------------------

def test_check2_counts_experience_bullets_only():
    exp = [{"company": "Statista", "bullets": [
        "Built pricing models with shopper insights for retail clients."]}]
    ok, _ = check_2_keywords_in_experience(exp, KEYWORDS)
    assert ok is True  # "pricing" + "shopper insights" both in bullets

    generic = [{"company": "Statista", "bullets": [
        "Did some general research work for various teams."]}]
    ok2, note2 = check_2_keywords_in_experience(generic, KEYWORDS)
    assert ok2 is False
    assert "experience bullets" in note2


# ---------------------------------------------------------------------------
# Check 7 — end_year mandatory; concurrent side roles exempt from the sort.
# ---------------------------------------------------------------------------

def _block(**third):
    return [
        {"company": "Statista", "end_year": 2025},
        {"company": "Statista", "end_year": 2023},
        dict({"company": "Atheneum"}, **third),
    ]


def test_check7_missing_end_year_now_fails():
    exp = _block()
    exp[2] = {"company": "Atheneum"}  # no end_year at all
    ok, note = check_7_experience_structure(exp)
    assert ok is False
    assert "end_year" in note


def test_check7_concurrent_present_role_below_block_passes():
    exp = _block(end_year=9999, concurrent=True)
    ok, note = check_7_experience_structure(exp)
    assert ok is True, note


def test_check7_unmarked_present_role_below_block_fails():
    exp = _block(end_year=9999)  # ongoing but NOT marked concurrent
    ok, note = check_7_experience_structure(exp)
    assert ok is False
    assert "concurrent" in note


# ---------------------------------------------------------------------------
# Check 9 — broadened metric shapes.
# ---------------------------------------------------------------------------

CAREER_RICH = ("Generated $30,000 in revenue and 11M+ streams; built a "
               "pipeline that raised speed 30% across 40+ firms. German B2. "
               "Tracked Phase III trials through 2023.")


def test_check9_flags_invented_currency_and_magnitude():
    xml = ("<w:t>Generated $50K in revenue and 25 million downloads, "
           "raising speed 30%</w:t>")
    ok, note = check_9_numeric_grounding(xml, CAREER_RICH)
    assert ok is False
    assert "$50K" in note and "25 million" in note
    assert "30%" not in note


def test_check9_grounds_currency_through_comma_squash():
    xml = "<w:t>owning $30K in revenue and 11M streams</w:t>"
    ok, note = check_9_numeric_grounding(xml, CAREER_RICH)
    assert ok is True, note


def test_check9_ignores_years_and_language_levels():
    xml = "<w:t>German B2, Phase III trials, since 2023, in 2020</w:t>"
    ok, note = check_9_numeric_grounding(xml, CAREER_RICH)
    assert ok is True, note


# ---------------------------------------------------------------------------
# Check 10 — proof density with the career-file whitelist.
# ---------------------------------------------------------------------------

CAREER_WL = ("Synthesized reports cited by Deloitte and W3C. Built a Python "
             "pipeline, +30% speed, across Technology and Telecom sectors.")


def test_check10_sector_nouns_do_not_ground():
    exp = [{"company": "X", "bullets": [
        "Coverage: tracked positioning across Technology and Telecom.",
        "Sector reads: tracked more positioning across sectors broadly.",
        "Reporting: synthesized findings cited by Deloitte and W3C.",
    ]}]
    ok, note = check_10_bullet_strength(exp, CAREER_WL)
    assert ok is False  # only 1/3 proofed; Technology/Telecom stoplisted
    assert "floor" in note


def test_check10_density_floor_two_of_three_passes():
    exp = [{"company": "X", "bullets": [
        "Coverage: tracked positioning for 40+ multinationals.",
        "Sector reads: tracked more positioning across sectors broadly.",
        "Reporting: synthesized findings cited by Deloitte and W3C.",
    ]}]
    ok, note = check_10_bullet_strength(exp, CAREER_WL)
    assert ok is True, note  # one interpretive bullet per slot is the pattern


def test_check10_two_bullet_slot_needs_one_proofed():
    exp = [{"company": "X", "bullets": [
        "Coverage: tracked positioning across markets broadly.",
        "Sector reads: watched trends for teams and functions.",
    ]}]
    ok, _ = check_10_bullet_strength(exp, CAREER_WL)
    assert ok is False


# ---------------------------------------------------------------------------
# Check 11 — the diagnosis proof point must surface in its slot.
# ---------------------------------------------------------------------------

DIAGNOSIS_MD = """# Role Diagnosis — Test | Analyst

## Section angles — one line for every rendered part

- Slot 1 (Statista Research Expert): pipeline ownership | proof point: Python pipeline, +30% publication speed | angled as source-of-truth reporting.
- Slot 2 (Statista Research Assistant): pandemic data | proof point: none | angled as data quality at scale.
- Slot 3 (VOV Music): label operations | proof point: data used by institutions | angled as commercial reporting.
"""


def test_check11_flags_dropped_proof_point(tmp_path):
    d = tmp_path / "Diagnosis - Test - Analyst.md"
    d.write_text(DIAGNOSIS_MD, encoding="utf-8")
    exp = [
        {"company": "Statista", "bullets": [
            "Dashboards: owned reporting used across departments."]},  # 30%/Python dropped!
        {"company": "Statista", "bullets": ["Data quality: cleaned data."]},
        {"company": "VOV", "bullets": ["Reporting: ran label operations."]},
    ]
    ok, note = check_11_proof_points(exp, str(d))
    assert ok is False
    assert "slot 1" in note and "Python" in note


def test_check11_passes_when_any_token_surfaces(tmp_path):
    d = tmp_path / "Diagnosis - Test - Analyst.md"
    d.write_text(DIAGNOSIS_MD, encoding="utf-8")
    exp = [
        {"company": "Statista", "bullets": [
            "Pipeline automation: built a Python pipeline lifting speed 30%."]},
        {"company": "Statista", "bullets": ["Data quality: cleaned data."]},
        {"company": "VOV", "bullets": ["Reporting: ran label operations."]},
    ]
    ok, note = check_11_proof_points(exp, str(d))
    # Slot 1 surfaces its tokens; slot 2 is 'none'; slot 3's proof point has
    # no distinctive token -> skipped loudly, not failed.
    assert ok is True, note
    assert "Skipped" in note


def test_check11_skips_without_diagnosis():
    assert check_11_proof_points([], None)[0] is True


# ---------------------------------------------------------------------------
# Editorial seeding — no pass by omission.
# ---------------------------------------------------------------------------

def test_audit_passes_without_editorial_ceremony(tmp_path):
    """v2.0.0: run_full_audit's verdict is final — no editorial seeding.

    The retired model-graded verdicts (checks 1 and 3) were rubber-stamped
    in every batch; richness is now enforced pre-render by the
    validate_content_map length floors instead."""
    from docxtpl import DocxTemplate
    from md_to_richtext import build_bold_plan
    from postprocess import postprocess_cv
    from conftest import TEMPLATE, minimal_content_map

    cm = minimal_content_map(experiences=[{
        "title": "T", "dates": "D", "company": "Acme", "location": "L",
        "end_year": 2025,
        "bullets": ["Built pricing models with shopper insights for clients.",
                    "Shipped data-driven category strategies for retailers."],
    }])
    cm, plan = build_bold_plan(cm, mode="plain")
    tpl = DocxTemplate(TEMPLATE)
    tpl.render(cm, autoescape=True)
    out = tmp_path / "cv.docx"
    tpl.save(str(out))
    postprocess_cv(str(out), plan)

    result = run_full_audit(
        rendered_docx_path=str(out), diagnosis_md_path=None,
        content_map=cm, expected_keywords=KEYWORDS,
        expect_bold=False, bold_plan=plan)
    assert result.all_passed is True, result.failure_summary
    assert not any(k.startswith("check_1_") or k.startswith("check_3_")
                   for k in result.passed)
