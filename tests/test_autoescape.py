"""
Guards the 2026-04-28 failure mode: an `&` in a content_map value being
silently stripped from the rendered docx when autoescape is off.

A CV rendered with autoescape=True must keep every ampersand.
"""
import os
import zipfile

from docxtpl import DocxTemplate
from md_to_richtext import convert_content_map
from conftest import TEMPLATE, minimal_content_map


def _rendered_xml(path):
    with zipfile.ZipFile(path) as z:
        return z.read("word/document.xml").decode("utf-8", errors="replace")


def test_ampersand_survives_render(tmp_path):
    cm = minimal_content_map(
        tagline="Research & Analytics  |  Policy & Governance",
        core_skills=[{"label": "Telecom & AI", "description": "markets & trends"}],
    )
    cm = convert_content_map(cm)
    tpl = DocxTemplate(TEMPLATE)
    tpl.render(cm, autoescape=True)
    out = tmp_path / "amp.docx"
    tpl.save(str(out))

    xml = _rendered_xml(str(out))
    # Three ampersands went in; all three must come out (escaped as &amp;).
    assert xml.count("&amp;") >= 3, (
        "ampersands were stripped — render was not autoescaped"
    )


def test_no_double_space_smell(tmp_path):
    """An & that survived should not leave a double-space gap behind it."""
    cm = minimal_content_map(tagline="Data & Strategy")
    cm = convert_content_map(cm)
    tpl = DocxTemplate(TEMPLATE)
    tpl.render(cm, autoescape=True)
    out = tmp_path / "amp2.docx"
    tpl.save(str(out))
    xml = _rendered_xml(str(out))
    assert "Data &amp; Strategy" in xml
