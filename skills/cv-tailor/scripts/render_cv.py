"""
render_cv.py — main entry point for the cv-tailor skill.

Pipeline:
  1. Load config.yaml, branches.yaml, regional-headers.yaml.
  2. Load the Diagnosis.md for the target role.
  3. Build the content_map (the model fills this — see content-map-schema.md).
  4. Resolve enabled/disabled sections for the target region
     (cv.sections + cv.region_section_overrides).
  5. Validate the content_map (pre-render verification).
  6. build_bold_plan() — strip ** markers, record bold spans. Bullets stay
     plain strings; RichText is banned from the render path (2026-05-11).
  7. tpl.render(content_map, autoescape=True)  <-- autoescape MANDATORY.
  8. Save the .docx.
  9. postprocess_cv() — apply bold from the plan as real runs; remove
     disabled sections. Raises if a bullet cannot be located.
  10. run_full_audit() — refuse to ship on any failure.
  11. Optional: convert to PDF via LibreOffice.

This script is the scaffold. The content_map itself is built by the model
from the diagnosis and the career file; this file enforces the mechanics
that must not vary: validation, autoescape, the bold plan, the postprocess
pass, the audit.
"""

import os
import re
import subprocess

import yaml
from docxtpl import DocxTemplate

from md_to_richtext import build_bold_plan
from postprocess import postprocess_cv
from audit import run_full_audit, _iter_strings

try:
    from section_composer import compose_template
except ImportError:
    compose_template = None


# Keys required in every content_map. `summary` is required only when the
# summary section is enabled for the target region — see validate_content_map.
BASE_REQUIRED_KEYS = (
    "candidate_name", "tagline", "contact_line_1",
    "core_skills", "experiences",
)

DEFAULT_SECTIONS = (
    "tagline", "contact", "summary", "core_skills",
    "experience", "education", "additional",
)

_LABELED_BULLET_RE = re.compile(r"^\*\*[^*\n]{2,60}:\*\*")


def load_yaml(path):
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def resolve_bold_mode(config):
    """Map config to the bold mode: 'labeled' | 'inline' | 'plain'."""
    cv_cfg = config.get("cv", {}) or {}
    if cv_cfg.get("bullet_style", "plain") == "labeled":
        return "labeled"
    if cv_cfg.get("inline_bold", False):
        return "inline"
    return "plain"


def effective_sections(config, region=None):
    """Resolve the section list for a render, honoring region overrides.

    Starts from cv.sections (or DEFAULT_SECTIONS when absent/None) and
    subtracts every section mapped to false in
    cv.region_section_overrides[region]. Returns (enabled, disabled).
    """
    cv_cfg = config.get("cv", {}) or {}
    sections = list(cv_cfg.get("sections") or DEFAULT_SECTIONS)
    overrides = {}
    if region:
        overrides = (cv_cfg.get("region_section_overrides") or {}).get(
            region, {}) or {}
    disabled = [name for name, enabled in overrides.items()
                if enabled is False and name in sections]
    enabled = [s for s in sections if s not in disabled]
    return enabled, disabled


def validate_content_map(cm, config, enabled_sections=None, mode="plain",
                         positioning_mode=None):
    """Pre-render verification. Raises ValueError on any failure."""
    errors = []

    required = list(BASE_REQUIRED_KEYS)
    if enabled_sections is None or "summary" in enabled_sections:
        required.append("summary")
    for key in required:
        if key not in cm or cm[key] in (None, "", [], {}):
            errors.append(f"missing or empty required key: {key}")

    # Slot count: exactly cv.max_experience_slots. A transition-positioned
    # diagnosis may add one slot (its Slot plan must justify it) — see
    # experience-slot-logic.md.
    max_slots = config.get("cv", {}).get("max_experience_slots", 3)
    allowed_counts = {max_slots}
    if positioning_mode == "transition":
        allowed_counts.add(max_slots + 1)
    if "experiences" in cm and len(cm["experiences"]) not in allowed_counts:
        errors.append(
            f"experiences has {len(cm['experiences'])} entries; "
            f"allowed: {sorted(allowed_counts)} "
            f"(cv.max_experience_slots is {max_slots})"
        )

    for i, role in enumerate(cm.get("experiences", [])):
        # end_year is mandatory: Check 7 (chronology + contiguous block) used
        # to self-skip when it was absent — the test5 driver exploited that.
        if not isinstance(role.get("end_year"), int):
            errors.append(
                f"experiences[{i}] ({role.get('company', '?')}) missing "
                f"integer end_year (use 9999 for Present) — required for the "
                f"Check 7 chronology gate"
            )
        # Bullet floors: a lead slot below 3 or any slot below 2 is an
        # under-written CV, not a style choice.
        n_bullets = len(role.get("bullets") or [])
        floor = 3 if i == 0 else 2
        if n_bullets < floor:
            errors.append(
                f"experiences[{i}] ({role.get('company', '?')}) has "
                f"{n_bullets} bullet(s); floor is {floor} "
                f"(lead slot >= 3, every other slot >= 2)"
            )
        if mode == "labeled":
            for b in role.get("bullets") or []:
                if isinstance(b, str) and not _LABELED_BULLET_RE.match(b):
                    errors.append(
                        f"labeled mode: bullet in slot {i + 1} lacks a "
                        f"'**Label:**' lead-in: {b[:50]!r}"
                    )

    # No employer name in the summary.
    summary = cm.get("summary") or ""
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

    # Em dashes are banned from all employer-facing output — fail before
    # render instead of at audit Check 6. See shared/conventions.md.
    for value in _iter_strings(cm):
        if "—" in value:
            errors.append(f"em dash in content_map value: {value[:60]!r}")
            break

    if errors:
        raise ValueError("Pre-render validation failed:\n  - " + "\n  - ".join(errors))


def _resolve_template(repo_root, template_name, enabled_sections):
    """Prefer composed partials when every partial exists; else the full
    template. The stub partials/ dir (PLACEHOLDER.md only) used to crash the
    composer, forcing drivers to null cv.sections — that workaround is dead.
    """
    template_dir = os.path.join(repo_root, "templates", template_name)
    full_path = os.path.join(template_dir, "full_template.docx")
    if compose_template and enabled_sections:
        partials = [os.path.join(template_dir, "partials", s + ".docx")
                    for s in enabled_sections]
        if partials and all(os.path.exists(p) for p in partials):
            return compose_template(template_dir, enabled_sections)
    return full_path


def render(diagnosis_path, content_map, config, repo_root, output_path,
           expected_keywords, career_file_path=None, region=None,
           positioning_mode=None):
    """Render one CV. Returns the AuditResult.

    Pass `career_file_path` (the workspace's `career_file`, e.g.
    `assets/career.txt`) to enable the Check 9 numeric-grounding gate.
    Pass `region` (a key of cv.region_section_overrides, e.g. "EU") so
    region-disabled sections are actually removed from the output.
    `positioning_mode` is the diagnosis's Positioning mode
    (direct | adjacent | transition); transition unlocks one extra slot.
    """
    cv_cfg = config.get("cv", {}) or {}
    template_name = cv_cfg.get("template", "OPUS")
    mode = resolve_bold_mode(config)
    enabled, disabled = effective_sections(config, region)

    # 1. Pre-render validation.
    validate_content_map(content_map, config, enabled_sections=enabled,
                         mode=mode, positioning_mode=positioning_mode)

    # 2. Resolve the template (composed partials or the full template).
    template_path = _resolve_template(repo_root, template_name, enabled)
    if not os.path.exists(template_path):
        raise FileNotFoundError(
            f"Template not found: {template_path}. "
            f"If the file is open in Word, close it and retry — do NOT "
            f"fall back to a copy or older version."
        )

    # A disabled summary still has a {{ summary }} placeholder in the full
    # template; render it empty, then postprocess removes the section.
    if "summary" in disabled:
        content_map.setdefault("summary", "")

    # 3. Strip ** markers and record the bold plan. Bullets stay plain
    #    strings — RichText is banned from the render path (2026-05-11).
    content_map, bold_plan = build_bold_plan(content_map, mode=mode)

    # 4. Render. autoescape=True is MANDATORY — see docxtpl-recipe.md.
    tpl = DocxTemplate(template_path)
    tpl.render(content_map, autoescape=True)
    tpl.save(output_path)

    # 5. Post-process: apply planned bold as real runs; remove disabled
    #    sections. Raises PostprocessError when a bullet cannot be located.
    postprocess_cv(output_path, bold_plan, disabled_sections=tuple(disabled))

    # 6. Post-render audit. Refuse to ship on any failure.
    expect_bold = mode != "plain" and any(spec["spans"] for spec in bold_plan)
    result = run_full_audit(
        rendered_docx_path=output_path,
        diagnosis_md_path=diagnosis_path,
        content_map=content_map,
        expected_keywords=expected_keywords,
        expect_bold=expect_bold,
        career_file_path=career_file_path,
        bold_plan=bold_plan,
    )
    return result


def to_pdf(docx_path):
    """Convert a .docx to a .pdf via LibreOffice headless. Requires libreoffice."""
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
