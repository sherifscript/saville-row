"""
Guards the 2026-05-11 failure mode: experience bullets containing **bold**
markers rendering as empty bullets.

Root cause (pinned in v1.8.0): docxtpl RichText passed through the template's
plain `{{ bullet }}` placeholder embeds run-XML inside <w:t> — invalid OOXML
that Word/python-docx/ATS read as EMPTY. The old guard here counted <w:b/>
in the raw XML, which the template's own bold section headers always satisfy,
so it could never fail. The v1.8.0 pipeline renders bullets as plain strings
and applies bold afterwards (postprocess_cv); the guard now asserts what a
recruiter's parser actually reads.
"""
from docx import Document
from docxtpl import DocxTemplate

from md_to_richtext import build_bold_plan, convert_content_map
from postprocess import postprocess_cv
from conftest import TEMPLATE, minimal_content_map


def test_markers_become_real_bold_runs(tmp_path):
    cm = minimal_content_map(experiences=[{
        "title": "Senior Analyst", "dates": "2023-Present",
        "company": "Acme", "location": "City",
        "bullets": ["Lifted **activation by 18%**, covered in **TechCrunch**."],
    }])
    cm, plan = build_bold_plan(cm, mode="inline")

    # No RichText anywhere: every bullet is a plain string at render time.
    assert all(isinstance(b, str)
               for b in cm["experiences"][0]["bullets"])

    tpl = DocxTemplate(TEMPLATE)
    tpl.render(cm, autoescape=True)
    out = tmp_path / "bold.docx"
    tpl.save(str(out))
    postprocess_cv(str(out), plan)

    # The bullet is READABLE by python-docx (the 2026-05-11 corruption made
    # it empty) and the marked phrases are real bold runs.
    doc = Document(str(out))
    target = "Lifted activation by 18%, covered in TechCrunch."
    matches = [p for p in doc.paragraphs
               if " ".join(p.text.split()) == target]
    assert matches, "bullet paragraph is not readable — render corruption"
    p = matches[0]
    bold_text = "".join(r.text for r in p.runs if r.bold)
    assert "activation by 18%" in bold_text
    assert "TechCrunch" in bold_text
    assert "**" not in p.text


def test_plain_mode_strips_markers_no_bold(tmp_path):
    cm = minimal_content_map(experiences=[{
        "title": "T", "dates": "D", "company": "Acme", "location": "L",
        "bullets": ["Kept **markers** out of the plain render."],
    }])
    cm, plan = build_bold_plan(cm, mode="plain")
    assert plan[0]["spans"] == []
    assert cm["experiences"][0]["bullets"][0] == \
        "Kept markers out of the plain render."


def test_markers_stripped_from_disallowed_fields():
    """** markers in summary/skills are stripped, never rendered literally."""
    cm = minimal_content_map(
        summary="A summary with a stray **marker** in it.",
        core_skills=[{"label": "Skill", "description": "stray **marker** here"}],
    )
    cm, _ = build_bold_plan(cm, mode="labeled")
    assert "**" not in cm["summary"]
    assert "**" not in cm["core_skills"][0]["description"]


def test_deprecated_shim_strips_never_converts():
    """convert_content_map (pre-v1.8.0 API) keeps old drivers valid: it
    strips markers and never produces RichText, even with inline_bold=True."""
    cm = minimal_content_map(experiences=[{
        "title": "T", "dates": "D", "company": "Acme", "location": "L",
        "bullets": ["A bullet with **markers** inside."],
    }])
    out = convert_content_map(cm, inline_bold=True)
    bullet = out["experiences"][0]["bullets"][0]
    assert isinstance(bullet, str)
    assert "**" not in bullet
