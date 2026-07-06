"""
Tests for the batch sameyness sweep — the 2026-06-14 detector (one slot
byte-identical across all ten Denmark CVs). Warn-only by design: cross-CV
reuse is sometimes legitimate; it must be a visible choice, not silent drift.
"""
from docxtpl import DocxTemplate

from audit import scan_batch_sameyness
from md_to_richtext import build_bold_plan
from postprocess import postprocess_cv
from conftest import TEMPLATE, minimal_content_map


def _render_cv(tmp_path, filename, bullets):
    cm = minimal_content_map(experiences=[{
        "title": "T", "dates": "D", "company": "Acme", "location": "L",
        "bullets": list(bullets),
    }])
    cm, plan = build_bold_plan(cm, mode="plain")
    tpl = DocxTemplate(TEMPLATE)
    tpl.render(cm, autoescape=True)
    out = tmp_path / filename
    tpl.save(str(out))
    postprocess_cv(str(out), plan)
    return str(out)


def test_shared_bullet_across_cvs_warned(tmp_path):
    shared = "Conducted expert interviews for regional market research."
    _render_cv(tmp_path, "CV - Alpha - Analyst.docx",
               [shared, "Alpha-only bullet about pipelines and dashboards."])
    _render_cv(tmp_path, "CV - Beta - Analyst.docx",
               [shared, "Beta-only bullet about competitive intelligence."])
    warnings = scan_batch_sameyness(str(tmp_path))
    assert len(warnings) == 1
    assert "Alpha" in warnings[0] and "Beta" in warnings[0]
    assert "expert interviews" in warnings[0]


def test_unique_bullets_clean(tmp_path):
    _render_cv(tmp_path, "CV - Alpha - Analyst.docx",
               ["Alpha bullet one about pipelines.",
                "Alpha bullet two about dashboards."])
    _render_cv(tmp_path, "CV - Beta - Analyst.docx",
               ["Beta bullet one about intelligence.",
                "Beta bullet two about interviews."])
    assert scan_batch_sameyness(str(tmp_path)) == []


def test_same_clause_different_labels_warned(tmp_path):
    clause = "built repeatable frameworks for market sizing across sectors."
    _render_cv(tmp_path, "CV - Alpha - Analyst.docx",
               ["Self-service analytics: " + clause])
    _render_cv(tmp_path, "CV - Beta - Analyst.docx",
               ["Repeatable methodology: " + clause])
    warnings = scan_batch_sameyness(str(tmp_path))
    assert len(warnings) == 1
    assert "clause shared" in warnings[0]
