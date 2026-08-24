"""
Guards the 2026-05-11 / test5 corruption class — for real this time.

The corruption: a docxtpl RichText value passed through the template's plain
`{{ bullet }}` placeholder embeds the RichText run-XML inside <w:t>. Word,
python-docx, and ATS parsers read the paragraph as EMPTY, while a raw-XML
regex still "sees" the text — which is exactly how all 10 CVs of the
2026-06-27 a 2026-06 batch shipped blank experience sections with a passing
audit.

check_5_rendered_integrity reads the rendered file with python-docx (the
parse a recruiter's tooling performs) and must FAIL that corruption.
"""
from docx import Document
from docxtpl import DocxTemplate, RichText

from audit import check_5_rendered_integrity
from md_to_richtext import build_bold_plan
from postprocess import postprocess_cv
from conftest import TEMPLATE, contact_links, minimal_content_map


BULLET_TEXT = "Label: the rest of the bullet with real substance in it."


def _save(tpl_cm, out_path):
    tpl = DocxTemplate(TEMPLATE)
    tpl.render(tpl_cm, autoescape=True)
    tpl.save(str(out_path))
    return str(out_path)


def test_integrity_fails_richtext_corruption(tmp_path):
    """Reproduce the test5 corruption honestly: RichText through {{ bullet }}."""
    rt = RichText("")
    rt.add("Label:", bold=True)
    rt.add(" the rest of the bullet with real substance in it.")
    cm = minimal_content_map()
    cm["experiences"][0]["bullets"] = [rt]
    path = _save(cm, tmp_path / "corrupt.docx")

    # The paragraph is EMPTY to python-docx (and Word, and ATS parsers).
    doc = Document(path)
    assert not any(BULLET_TEXT in p.text for p in doc.paragraphs)

    # The audit map carries what SHOULD be visible.
    audit_cm = {"experiences": [
        {"company": "Acme", "bullets": [BULLET_TEXT]}]}
    ok, note = check_5_rendered_integrity(path, audit_cm)
    assert ok is False
    assert "slot 1 (Acme)" in note
    assert "NOT readable" in note


def test_integrity_passes_healthy_postprocessed_render(tmp_path):
    cm = minimal_content_map(experiences=[{
        "title": "T", "dates": "D", "company": "Acme", "location": "L",
        "bullets": ["**Label:** the rest of the bullet with substance."],
    }])
    cm, plan = build_bold_plan(cm, mode="labeled")
    path = _save(cm, tmp_path / "healthy.docx")
    postprocess_cv(path, plan, contact_links=contact_links(cm))

    ok, note = check_5_rendered_integrity(
        path, cm, bold_plan=plan, expect_bold=True)
    assert ok is True, note
    assert "bold span(s) verified" in note


def test_integrity_fails_unbolded_planned_span(tmp_path):
    """Bold was planned but never applied (postprocess skipped) -> FAIL."""
    cm = minimal_content_map(experiences=[{
        "title": "T", "dates": "D", "company": "Acme", "location": "L",
        "bullets": ["**Label:** the rest of the bullet with substance."],
    }])
    cm, plan = build_bold_plan(cm, mode="labeled")
    path = _save(cm, tmp_path / "unbolded.docx")
    # postprocess_cv deliberately NOT called.

    ok, note = check_5_rendered_integrity(
        path, cm, bold_plan=plan, expect_bold=True)
    assert ok is False
    assert "bold span not rendered bold" in note


def test_integrity_fails_visible_markup(tmp_path):
    cm = minimal_content_map(experiences=[{
        "title": "T", "dates": "D", "company": "Acme", "location": "L",
        "bullets": ["a bullet carrying literal <w:fake/> markup text"],
    }])
    cm, plan = build_bold_plan(cm, mode="plain")
    path = _save(cm, tmp_path / "markup.docx")

    ok, note = check_5_rendered_integrity(path, cm)
    assert ok is False
    assert "raw markup" in note


def test_integrity_checks_hyperlink_targets_not_count(tmp_path):
    """Each contact link must POINT at its own label, not merely exist.

    The predecessor of this test asserted `>= 2 hyperlink rels`, which the
    2026-08 leak satisfied while both links pointed at the template author.
    """
    cm = minimal_content_map()
    cm, plan = build_bold_plan(cm, mode="plain")
    path = _save(cm, tmp_path / "rels.docx")
    postprocess_cv(path, plan, contact_links=contact_links(cm))
    ok, note = check_5_rendered_integrity(path, cm)
    assert ok is True, note
    assert "2 contact link(s) match their target" in note
