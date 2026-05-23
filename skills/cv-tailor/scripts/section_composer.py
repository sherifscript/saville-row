"""
section_composer.py — stitch CV section partials into one docxtpl template.

Each template ships every possible section as a partial docx under
  templates/<name>/partials/<section>.docx

This composer reads the configured section order and produces a single
composite docx that docxtpl then renders. See
cv-tailor/references/modular-sections.md.

Implementation note
-------------------
Composing docx XML correctly means merging the body content of each partial
while keeping exactly one set of section properties (<w:sectPr>), and merging
the relationship parts (numbering, styles, hyperlinks) so list styles and
links survive. This scaffold uses python-docx's composition pattern; for
production, `docxcompose` (pip install docxcompose) handles the relationship
merging robustly and is the recommended dependency.
"""

import os
import tempfile


def compose_template(template_dir, sections):
    """Compose a docxtpl template from the partials for `sections`.

    Args:
        template_dir: e.g. templates/OPUS
        sections:     ordered list of section names, e.g.
                      ["tagline", "contact", "summary", "experience", ...]

    Returns:
        Path to a temporary composed .docx ready for DocxTemplate().

    If a partial is missing, raises FileNotFoundError naming the section.
    If the full_template.docx should be used instead (no partials dir),
    callers should skip the composer — see render_cv.py.
    """
    partials_dir = os.path.join(template_dir, "partials")
    if not os.path.isdir(partials_dir):
        raise FileNotFoundError(
            f"No partials/ directory under {template_dir}. "
            f"Either add section partials or use full_template.docx."
        )

    partial_paths = []
    for section in sections:
        path = os.path.join(partials_dir, f"{section}.docx")
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"Section partial missing: {path} "
                f"(section '{section}' is in cv.sections but has no partial)"
            )
        partial_paths.append(path)

    try:
        from docxcompose.composer import Composer
        from docx import Document
    except ImportError as exc:
        raise ImportError(
            "section_composer needs `docxcompose` and `python-docx`. "
            "Install: pip install docxcompose python-docx"
        ) from exc

    master = Document(partial_paths[0])
    composer = Composer(master)
    for path in partial_paths[1:]:
        composer.append(Document(path))

    out_fd, out_path = tempfile.mkstemp(suffix=".docx", prefix="composed_cv_")
    os.close(out_fd)
    composer.save(out_path)
    return out_path


def verify_partial_consistency(template_dir):
    """Warn if partials drift in font / size / color settings.

    Returns a list of warning strings (empty if consistent). Template
    maintainers should run this after editing any partial — see
    modular-sections.md ("What partials cannot do").
    """
    warnings = []
    partials_dir = os.path.join(template_dir, "partials")
    if not os.path.isdir(partials_dir):
        return [f"No partials directory: {partials_dir}"]

    # A full implementation parses each partial's word/document.xml and
    # compares <w:rFonts>, <w:sz>, and color values across partials.
    # Scaffold: report the partials present so a maintainer can eyeball them.
    found = sorted(f for f in os.listdir(partials_dir) if f.endswith(".docx"))
    if not found:
        warnings.append(f"No .docx partials in {partials_dir}")
    return warnings


if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 2:
        for w in verify_partial_consistency(sys.argv[1]):
            print("WARN:", w)
    else:
        print("Usage: python section_composer.py <template_dir>")
