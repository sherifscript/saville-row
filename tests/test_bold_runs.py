"""
Guards the 2026-05-11 failure mode: experience bullets containing **bold**
markers rendering as empty bullets because the RichText was embedded as
text instead of as sibling runs.

A CV whose diagnosis specified bold phrases must contain real <w:b/> runs.
"""
import zipfile
import re

from docxtpl import DocxTemplate
from md_to_richtext import convert_content_map, md_to_richtext
from conftest import TEMPLATE, minimal_content_map


def test_markers_become_bold_runs(tmp_path):
    cm = minimal_content_map(experiences=[{
        "title": "Senior Analyst", "dates": "2023-Present",
        "company": "Acme", "location": "City",
        "bullets": ["Lifted **activation by 18%**, covered in **TechCrunch**."],
    }])
    cm = convert_content_map(cm)
    tpl = DocxTemplate(TEMPLATE)
    tpl.render(cm, autoescape=True)
    out = tmp_path / "bold.docx"
    tpl.save(str(out))

    with zipfile.ZipFile(str(out)) as z:
        xml = z.read("word/document.xml").decode("utf-8", errors="replace")
    bold_runs = len(re.findall(r"<w:b\s*/>", xml))
    assert bold_runs > 0, (
        "no bold runs in the rendered XML — RichText did not produce runs"
    )
    # The bolded phrases must not leak literal ** markers.
    assert "**" not in xml


def test_plain_string_passes_through():
    """A bullet with no markers is returned unchanged (a plain str)."""
    assert md_to_richtext("a plain bullet") == "a plain bullet"


def test_markers_stripped_from_disallowed_fields():
    """** markers in summary/skills are stripped, never rendered literally."""
    cm = minimal_content_map(
        summary="A summary with a stray **marker** in it.",
        core_skills=[{"label": "Skill", "description": "stray **marker** here"}],
    )
    cm = convert_content_map(cm)
    assert "**" not in cm["summary"]
    assert "**" not in cm["core_skills"][0]["description"]
