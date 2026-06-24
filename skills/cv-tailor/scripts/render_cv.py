"""
render_cv.py — main entry point for the cv-tailor skill.

Pipeline:
  1. Load config.yaml, branches.yaml, regional-headers.yaml.
  2. Load the Diagnosis.md for the target role.
  3. Build the content_map (the model fills this — see content-map-schema.md).
  4. Validate the content_map (pre-render verification).
  5. Compose the section partials per cv.sections (section_composer.py).
  6. convert_content_map() — markdown bold -> RichText.
  7. tpl.render(content_map, autoescape=True)  <-- autoescape MANDATORY.
  8. Save the .docx.
  9. run_full_audit() — refuse to ship on any failure.
  10. Optional: convert to PDF via LibreOffice.

This script is the scaffold. The content_map itself is built by the model
from the diagnosis and the career file; this file enforces the mechanics
that must not vary: validation, autoescape, the helper, the audit.
"""

import os
import sys
import subprocess

import yaml
from docxtpl import DocxTemplate

from md_to_richtext import convert_content_map
from audit import run_full_audit

try:
    from section_composer import compose_template
except ImportError:
    compose_template = None


REQUIRED_KEYS = (
    "candidate_name", "tagline", "contact_line_1", "summary",
    "core_skills", "experiences",
)


def load_yaml(path):
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def validate_content_map(cm, config):
    """Pre-render verification. Raises ValueError on any failure."""
    errors = []

    for key in REQUIRED_KEYS:
        if key not in cm or cm[key] in (None, "", [], {}):
            errors.append(f"missing or empty required key: {key}")

    max_slots = config.get("cv", {}).get("max_experience_slots", 3)
    if "experiences" in cm and len(cm["experiences"]) != max_slots:
        errors.append(
            f"experiences has {len(cm['experiences'])} entries; "
            f"cv.max_experience_slots is {max_slots}"
        )

    # No employer name in the summary.
    summary = cm.get("summary", "")
    for role in cm.get("experiences", []):
        company = role.get("company", "")
        if company and company in summary:
            errors.append(f"employer name '{company}' appears in summary")

    # No company name in any bullet.
    for role in cm.get("experiences", []):
        for other in cm.get("experiences", []):
            company = other.get("company", "")
            for bullet in role.get("bullets", []):
                btext = bullet if isinstance(bullet, str) else ""
                if company and company in btext and company != role.get("company"):
                    errors.append(
                        f"company '{company}' referenced in a bullet under "
                        f"{role.get('company')}"
                    )

    if errors:
        raise ValueError("Pre-render validation failed:\n  - " + "\n  - ".join(errors))


def render(diagnosis_path, content_map, config, repo_root, output_path,
           expected_keywords, career_file_path=None):
    """Render one CV. Returns the AuditResult.

    Pass `career_file_path` (the workspace's `career_file`, e.g.
    `assets/career.txt`) to enable the Check 9 numeric-grounding gate. Without
    it, grounding is skipped.
    """
    template_name = config.get("cv", {}).get("template", "OPUS")
    sections = config.get("cv", {}).get("sections")

    # 1. Pre-render validation.
    validate_content_map(content_map, config)

    # 2. Compose the template from section partials (if composer available
    #    and a section list is configured); otherwise use the full template.
    template_dir = os.path.join(repo_root, "templates", template_name)
    if compose_template and sections:
        template_path = compose_template(template_dir, sections)
    else:
        template_path = os.path.join(template_dir, "full_template.docx")

    if not os.path.exists(template_path):
        raise FileNotFoundError(
            f"Template not found: {template_path}. "
            f"If the file is open in Word, close it and retry — do NOT "
            f"fall back to a copy or older version."
        )

    # 3. Detect whether the diagnosis specified bold phrases (for audit #5).
    expect_bold = any(
        isinstance(b, str) and "**" in b
        for role in content_map.get("experiences", [])
        for b in role.get("bullets", [])
    )

    # 4. Convert markdown bold -> RichText. MANDATORY before render.
    content_map = convert_content_map(content_map)

    # 5. Render. autoescape=True is MANDATORY — see docxtpl-recipe.md.
    tpl = DocxTemplate(template_path)
    tpl.render(content_map, autoescape=True)
    tpl.save(output_path)

    # 6. Post-render audit. Refuse to ship on any failure.
    result = run_full_audit(
        rendered_docx_path=output_path,
        diagnosis_md_path=diagnosis_path,
        content_map=content_map,
        expected_keywords=expected_keywords,
        expect_bold=expect_bold,
        career_file_path=career_file_path,
    )
    return result


def to_pdf(docx_path):
    """Convert a .docx to .pdf via LibreOffice headless. Requires libreoffice."""
    out_dir = os.path.dirname(docx_path)
    subprocess.run(
        ["libreoffice", "--headless", "--convert-to", "pdf",
         "--outdir", out_dir, docx_path],
        check=True,
    )
    return os.path.splitext(docx_path)[0] + ".pdf"


if __name__ == "__main__":
    print(
        "render_cv.py is a library scaffold. The model builds the content_map "
        "from the diagnosis and the career file, then calls render(). "
        "See skills/cv-tailor/references/content-map-schema.md for the content_map "
        "shape and skills/cv-tailor/SKILL.md for the full flow."
    )
