"""
build_template.py — one-time conversion of a finished CV into a docxtpl template.

This is NOT part of the daily build. It runs once to turn a candidate's
visually-finished CV (.docx) into a docxtpl template by replacing the variable
text regions with Jinja placeholders. The daily CV build then renders that
template — see render_cv.py.

When to re-run: only when the underlying CV layout changes (new section, moved
tab stop, restyled header). Per-job CVs never re-run this.

Procedure
---------
1. Read the source CV .docx as a zip; pull word/document.xml.
2. Targeted string surgery: replace the inner text of <w:t> nodes for the
   tagline, contact lines, summary, and the variable title rows.
3. Replace ranges of bullet paragraphs with docxtpl paragraph loops:
       {%p for bullet in role.bullets %} <styled bullet> {%p endfor %}
4. Repack as the template .docx.

Run the acceptance test (below) before promoting a new template to daily use.
"""

import sys
import zipfile
import shutil
import os


PLACEHOLDER_MAP = {
    # source text fragment  ->  docxtpl placeholder
    # Fill these in for the specific source CV being converted. Examples:
    # "Senior Product Manager | Growth": "{{ tagline }}",
    # "Brooklyn, NY | +1 ...": "{{ contact_line_1 }}",
}


def convert(source_cv_path, template_out_path):
    """Convert a finished CV docx into a docxtpl template.

    This scaffold copies the source and documents the surgery points. The
    actual <w:t> replacements depend on the specific source CV and must be
    filled into PLACEHOLDER_MAP, plus the loop-block insertions done by hand
    or by extending this function.
    """
    if not os.path.exists(source_cv_path):
        raise FileNotFoundError(source_cv_path)

    # Work on a copy.
    shutil.copy(source_cv_path, template_out_path)

    with zipfile.ZipFile(template_out_path) as z:
        document_xml = z.read("word/document.xml").decode("utf-8")

    for source_text, placeholder in PLACEHOLDER_MAP.items():
        if source_text not in document_xml:
            print(f"WARN: source fragment not found, skipped: {source_text!r}")
            continue
        document_xml = document_xml.replace(source_text, placeholder)

    # NOTE: bullet-loop insertion ({%p for ... %}) is layout-specific and is
    # done by locating the bullet paragraph ranges in document_xml and
    # replacing them with: loop-open paragraph + one styled bullet paragraph
    # + loop-close paragraph. See skills/cv-tailor/references/docxtpl-recipe.md.

    _rewrite_zip_member(template_out_path, "word/document.xml", document_xml)
    print(f"Template written: {template_out_path}")
    print("Run the acceptance test before promoting to daily use.")


def _rewrite_zip_member(zip_path, member, new_content):
    """Replace one member inside a zip file with new text content."""
    tmp = zip_path + ".tmp"
    with zipfile.ZipFile(zip_path) as zin, \
         zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == member:
                data = new_content.encode("utf-8")
            zout.writestr(item, data)
    os.replace(tmp, zip_path)


def acceptance_test(template_path):
    """Render the template with recognizable dummy values and report.

    Open the result in Word: it must be visually identical to the source CV
    except for the placeholder text. If anything else changed, the template
    is broken — do not promote it.
    """
    from docxtpl import DocxTemplate
    dummy = {
        "tagline": "XXXX TAGLINE XXXX",
        "contact_line_1": "XXXX CONTACT 1 XXXX",
        "contact_line_2_suffix": "XXXX SUFFIX XXXX",
        "summary": "XXXX SUMMARY XXXX",
        "core_skills": [{"label": f"XXXX SKILL {i}", "description": "XXXX DESC"}
                        for i in range(1, 6)],
        "experiences": [
            {"title": f"XXXX TITLE {i}", "dates": "XXXX DATES",
             "company": f"XXXX COMPANY {i}", "location": "XXXX LOC",
             "bullets": [f"XXXX BULLET {i}.1", f"XXXX BULLET {i}.2"]}
            for i in range(1, 4)
        ],
        "msc_bullets": ["XXXX MSC BULLET"],
        "ba_bullets": ["XXXX BA BULLET"],
        "additional": [{"label": "XXXX ADD", "description": "XXXX ADD DESC"}],
    }
    tpl = DocxTemplate(template_path)
    tpl.render(dummy, autoescape=True)
    out = template_path.replace(".docx", " — ACCEPTANCE TEST.docx")
    tpl.save(out)
    print(f"Acceptance render saved: {out}")
    print("Open in Word and confirm it matches the source CV layout exactly.")


if __name__ == "__main__":
    if len(sys.argv) == 3:
        convert(sys.argv[1], sys.argv[2])
    elif len(sys.argv) == 2:
        acceptance_test(sys.argv[1])
    else:
        print("Usage:")
        print("  python build_template.py <source_cv.docx> <template_out.docx>")
        print("  python build_template.py <template.docx>   # acceptance test")
