"""
Tests for the v1.8.0 render pipeline: plain-string render + postprocess bold
+ section removal. This is the architecture that makes the 2026-05-11 /
test5 corruption (RichText embedded inside <w:t> -> invisible bullets)
structurally impossible: bullets are plain strings at render time, and bold
is applied afterwards by cloning the rendered run.
"""
import zipfile

import pytest
from docx import Document
from docxtpl import DocxTemplate

from md_to_richtext import build_bold_plan
from postprocess import postprocess_cv, PostprocessError, _split_run_bold
from render_cv import render, effective_sections
from conftest import TEMPLATE, REPO_ROOT, minimal_content_map


def _render_plain(cm, out_path):
    """Render a content map (already marker-stripped) through the template."""
    tpl = DocxTemplate(TEMPLATE)
    tpl.render(cm, autoescape=True)
    tpl.save(str(out_path))
    return str(out_path)


def _para_with_text(doc, text):
    norm = " ".join(text.split())
    for p in doc.paragraphs:
        if " ".join(p.text.split()) == norm:
            return p
    raise AssertionError("paragraph not found: %r" % text[:60])


def test_labeled_bullet_bold_label_formatting_preserved(tmp_path):
    bullet = "**Pipeline automation:** built a Python pipeline cutting time 30%."
    cm = minimal_content_map(experiences=[{
        "title": "Senior Analyst", "dates": "2023-Present",
        "company": "Acme", "location": "City", "bullets": [bullet],
    }])
    cm, plan = build_bold_plan(cm, mode="labeled")
    path = _render_plain(cm, tmp_path / "labeled.docx")
    summary = postprocess_cv(path, plan)
    assert summary["bolded_runs"] == 1

    doc = Document(path)
    p = _para_with_text(
        doc, "Pipeline automation: built a Python pipeline cutting time 30%.")
    assert p.runs[0].text == "Pipeline automation:"
    assert p.runs[0].bold is True
    assert p.runs[1].bold is not True
    # Cloned runs inherit the template bullet run's explicit formatting.
    assert p.runs[0].font.name == "Calibri"
    assert p.runs[0].font.size.pt == 10.0
    assert p.runs[1].font.name == "Calibri"


def test_inline_two_spans_alternation(tmp_path):
    bullet = "Lifted **activation by 18%**, covered in **TechCrunch**."
    cm = minimal_content_map(experiences=[{
        "title": "T", "dates": "D", "company": "Acme", "location": "L",
        "bullets": [bullet],
    }])
    cm, plan = build_bold_plan(cm, mode="inline")
    path = _render_plain(cm, tmp_path / "inline.docx")
    postprocess_cv(path, plan)

    doc = Document(path)
    p = _para_with_text(
        doc, "Lifted activation by 18%, covered in TechCrunch.")
    texts = [r.text for r in p.runs]
    bolds = [bool(r.bold) for r in p.runs]
    assert texts == ["Lifted ", "activation by 18%", ", covered in ",
                     "TechCrunch", "."]
    assert bolds == [False, True, False, True, False]


def test_bold_and_ampersand_interaction(tmp_path):
    bullet = "**A & B:** rest & more."
    cm = minimal_content_map(experiences=[{
        "title": "T", "dates": "D", "company": "Acme", "location": "L",
        "bullets": [bullet],
    }])
    cm, plan = build_bold_plan(cm, mode="labeled")
    path = _render_plain(cm, tmp_path / "amp.docx")
    postprocess_cv(path, plan)

    doc = Document(path)
    p = _para_with_text(doc, "A & B: rest & more.")
    assert p.runs[0].bold is True
    assert p.runs[0].text == "A & B:"
    with zipfile.ZipFile(path) as z:
        xml = z.read("word/document.xml").decode("utf-8")
    assert "A &amp; B:" in xml  # ampersand escaped, not stripped


def test_split_survives_pre_split_paragraph(tmp_path):
    """Defensive: a bullet paragraph that arrives as multiple runs is merged
    before splitting, so text and spans stay correct."""
    import copy as _copy
    bullet = "**Label:** the rest of it."
    cm = minimal_content_map(experiences=[{
        "title": "T", "dates": "D", "company": "Acme", "location": "L",
        "bullets": [bullet],
    }])
    cm, plan = build_bold_plan(cm, mode="labeled")
    path = _render_plain(cm, tmp_path / "presplit.docx")

    # Artificially split the bullet's single run into two.
    doc = Document(path)
    p = _para_with_text(doc, "Label: the rest of it.")
    src = p.runs[0]
    full = src.text
    clone = _copy.deepcopy(src._r)
    src._r.addnext(clone)
    src.text = full[:7]
    from docx.text.run import Run
    Run(clone, p).text = full[7:]
    assert len(p.runs) == 2

    _split_run_bold(p, plan[0]["spans"])
    assert " ".join(p.text.split()) == "Label: the rest of it."
    assert p.runs[0].text == "Label:"
    assert p.runs[0].bold is True


def test_section_removal_summary_and_additional(tmp_path):
    cm = minimal_content_map()
    cm, plan = build_bold_plan(cm, mode="plain")
    path = _render_plain(cm, tmp_path / "sections.docx")
    summary = postprocess_cv(path, plan,
                             disabled_sections=("summary", "additional"))
    assert set(summary["removed_sections"]) == {"summary", "additional"}

    doc = Document(path)
    texts = [p.text.strip() for p in doc.paragraphs]
    assert "PROFESSIONAL SUMMARY" not in texts
    assert "ADDITIONAL" not in texts
    # Neighboring sections intact.
    assert "CORE SKILLS" in texts
    assert "EDUCATION" in texts
    assert any("Did a plain thing." in t for t in texts)


def test_required_sections_never_removed(tmp_path):
    cm = minimal_content_map()
    cm, plan = build_bold_plan(cm, mode="plain")
    path = _render_plain(cm, tmp_path / "required.docx")
    summary = postprocess_cv(path, plan, disabled_sections=("experience",))
    assert summary["removed_sections"] == []
    assert any("required" in w for w in summary["warnings"])
    doc = Document(path)
    assert "PROFESSIONAL EXPERIENCE" in [p.text.strip() for p in doc.paragraphs]


def test_hyperlinks_survive_roundtrip(tmp_path):
    cm = minimal_content_map()
    cm, plan = build_bold_plan(cm, mode="plain")
    path = _render_plain(cm, tmp_path / "links.docx")
    postprocess_cv(path, plan, disabled_sections=("summary",))
    with zipfile.ZipFile(path) as z:
        rels = z.read("word/_rels/document.xml.rels").decode("utf-8")
    assert rels.count("/relationships/hyperlink") >= 2


def test_plan_mismatch_raises(tmp_path):
    cm = minimal_content_map()
    cm, plan = build_bold_plan(cm, mode="plain")
    path = _render_plain(cm, tmp_path / "mismatch.docx")
    bad_plan = [{"section": "experience", "slot": 0,
                 "text": "a bullet that was never rendered", "spans": []}]
    with pytest.raises(PostprocessError):
        postprocess_cv(path, bad_plan)


# ---------------------------------------------------------------------------
# End-to-end through render(): validation -> render -> postprocess -> audit.
# ---------------------------------------------------------------------------

def _three_slot_map():
    return minimal_content_map(experiences=[
        {"title": "Senior Analyst", "dates": "2023 - Present",
         "company": "Acme", "location": "City", "end_year": 9999,
         "bullets": [
             "**Pipeline automation:** built a Python pipeline cutting "
             "publication time 30% across reporting.",
             "**Dashboard ownership:** owned Power BI dashboards used "
             "across departments for weekly reporting.",
             "**Executive interviews:** conducted interviews with "
             "executives, structuring input into decision evidence.",
         ]},
        {"title": "Analyst", "dates": "2020 - 2023",
         "company": "Acme", "location": "City", "end_year": 2023,
         "bullets": [
             "**Data quality:** cleaned and validated epidemiological "
             "data across high-frequency publication cycles.",
             "**Trial tracking:** tracked vaccine trials from Phase I "
             "to Phase III into structured reports.",
         ]},
        {"title": "Consultant", "dates": "2018 - 2020",
         "company": "Other Co", "location": "Town", "end_year": 2020,
         "bullets": [
             "**Primary research:** conducted expert interviews for "
             "market research projects across regions.",
             "**Cross-cultural delivery:** managed communication for "
             "research projects targeting regional markets.",
         ]},
    ])


KEYWORDS = ["pipeline", "dashboards", "data quality", "market research"]


def _record_editorial_pass(result):
    """Tests stand in for the model's required editorial verdicts."""
    result.record_editorial("check_1_lead_slots", True, "test fixture verdict")
    result.record_editorial("check_3_recruiter_fit", True, "test fixture verdict")


def test_render_end_to_end_labeled(tmp_path):
    config = {"cv": {"bullet_style": "labeled", "max_experience_slots": 3}}
    out = tmp_path / "cv.docx"
    result = render(
        diagnosis_path=None,
        content_map=_three_slot_map(),
        config=config,
        repo_root=REPO_ROOT,
        output_path=str(out),
        expected_keywords=KEYWORDS,
    )
    # all_passed is deliberately False until the editorial verdicts are
    # recorded — a CV can no longer pass by omission.
    assert not result.all_passed
    _record_editorial_pass(result)
    assert result.all_passed, result.failure_summary

    # Every bullet must be readable and the labels bold — what Word and an
    # ATS parser see, not what a raw-XML regex sees.
    doc = Document(str(out))
    p = _para_with_text(
        doc, "Pipeline automation: built a Python pipeline cutting "
             "publication time 30% across reporting.")
    assert p.runs[0].bold is True
    assert p.runs[0].text == "Pipeline automation:"


def test_render_region_override_removes_summary(tmp_path):
    config = {"cv": {
        "bullet_style": "labeled",
        "max_experience_slots": 3,
        "region_section_overrides": {"EU": {"summary": False}},
    }}
    cm = _three_slot_map()
    del cm["summary"]  # not required when the region disables the section
    out = tmp_path / "cv_eu.docx"
    result = render(
        diagnosis_path=None,
        content_map=cm,
        config=config,
        repo_root=REPO_ROOT,
        output_path=str(out),
        expected_keywords=KEYWORDS,
        region="EU",
    )
    _record_editorial_pass(result)
    assert result.all_passed, result.failure_summary
    texts = [p.text.strip() for p in Document(str(out)).paragraphs]
    assert "PROFESSIONAL SUMMARY" not in texts


def test_effective_sections_resolution():
    config = {"cv": {"region_section_overrides": {"EU": {"summary": False}}}}
    enabled, disabled = effective_sections(config, region="EU")
    assert "summary" in disabled and "summary" not in enabled
    enabled_us, disabled_us = effective_sections(config, region="US")
    assert disabled_us == [] and "summary" in enabled_us
    enabled_none, disabled_none = effective_sections(config, region=None)
    assert disabled_none == []


def test_validate_rejects_missing_end_year_and_thin_slots(tmp_path):
    from render_cv import validate_content_map
    config = {"cv": {"max_experience_slots": 3}}
    cm = _three_slot_map()
    del cm["experiences"][0]["end_year"]
    cm["experiences"][1]["bullets"] = cm["experiences"][1]["bullets"][:1]
    with pytest.raises(ValueError) as exc:
        validate_content_map(cm, config)
    msg = str(exc.value)
    assert "end_year" in msg
    assert "floor" in msg


def test_validate_rejects_unlabeled_bullet_in_labeled_mode():
    from render_cv import validate_content_map
    config = {"cv": {"max_experience_slots": 3}}
    cm = _three_slot_map()
    cm["experiences"][0]["bullets"][0] = "A bullet without any label lead-in."
    with pytest.raises(ValueError) as exc:
        validate_content_map(cm, config, mode="labeled")
    assert "labeled mode" in str(exc.value)


def test_validate_rejects_em_dash():
    from render_cv import validate_content_map
    config = {"cv": {"max_experience_slots": 3}}
    cm = _three_slot_map()
    cm["summary"] = "A summary with an em dash — banned."
    with pytest.raises(ValueError) as exc:
        validate_content_map(cm, config)
    assert "em dash" in str(exc.value)


def test_transition_mode_allows_one_extra_slot():
    from render_cv import validate_content_map
    config = {"cv": {"max_experience_slots": 3}}
    cm = _three_slot_map()
    cm["experiences"].append({
        "title": "Support Agent", "dates": "2016 - 2018",
        "company": "Old Co", "location": "Town", "end_year": 2018,
        "bullets": [
            "**Client escalations:** resolved technical escalations for "
            "enterprise accounts across three regions.",
            "**Onboarding:** trained new team members on the support "
            "playbook and CRM workflows.",
        ],
    })
    # 4 slots rejected in default/adjacent positioning...
    with pytest.raises(ValueError):
        validate_content_map(cm, config, mode="labeled")
    with pytest.raises(ValueError):
        validate_content_map(cm, config, mode="labeled",
                             positioning_mode="adjacent")
    # ...but allowed (max+1) in transition mode.
    validate_content_map(cm, config, mode="labeled",
                         positioning_mode="transition")
