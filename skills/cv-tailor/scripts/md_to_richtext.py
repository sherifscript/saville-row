"""
md_to_richtext.py — convert **markdown bold** markers to docxtpl RichText runs.

The framework uses `**phrase**` markers inside CV bullets to indicate which
phrases should render bold. docxtpl does not interpret these — without
conversion they render as literal asterisks in Word.

`convert_content_map()` does two things:
  1. In allowed fields (experience bullets, msc_bullets, ba_bullets):
     converts **phrase** to RichText bold runs.
  2. In disallowed fields (tagline, summary, core_skills, additional):
     strips stray ** markers so a leaked marker cannot render literally.

Always call convert_content_map(cm) immediately before
    tpl.render(cm, autoescape=True)

See skills/cv-tailor/references/docxtpl-recipe.md for the rationale and the named
failure modes (2026-04-28 ampersand strip, 2026-05-11 empty-bold regression).
"""

import re
from docxtpl import RichText


def md_to_richtext(text):
    """Convert **phrase** markers in a string to docxtpl bold runs.

    Plain strings (no ** markers) pass through unchanged — docxtpl renders
    them normally via autoescape.
    """
    if not isinstance(text, str) or "**" not in text:
        return text
    rt = RichText("")
    for part in re.split(r"(\*\*[^*]+?\*\*)", text):
        if not part:
            continue
        if part.startswith("**") and part.endswith("**"):
            rt.add(part[2:-2], bold=True)
        else:
            rt.add(part)
    return rt


def _strip_markers(text):
    """Remove stray ** markers from a string. Non-strings pass through."""
    return text.replace("**", "") if isinstance(text, str) else text


def convert_content_map(cm):
    """Walk the content_map. Convert markdown-bold to RichText in the
    Experience and Education sections; strip stray ** markers everywhere else.

    Mutates and returns cm.
    """
    # --- Bolding ALLOWED: experience + education bullets -------------------
    for role in cm.get("experiences", []):
        if "bullets" in role:
            role["bullets"] = [md_to_richtext(b) for b in role["bullets"]]

    for key in ("msc_bullets", "ba_bullets"):
        if key in cm:
            cm[key] = [md_to_richtext(b) for b in cm[key]]

    # --- Bolding NOT ALLOWED: strip stray markers -------------------------
    for key in ("tagline", "summary", "contact_line_1", "contact_line_2_suffix"):
        if key in cm:
            cm[key] = _strip_markers(cm[key])

    for skill in cm.get("core_skills", []):
        if "description" in skill:
            skill["description"] = _strip_markers(skill["description"])

    for item in cm.get("additional", []):
        if "description" in item:
            item["description"] = _strip_markers(item["description"])

    return cm


if __name__ == "__main__":
    # Quick self-test
    sample = {
        "tagline": "Senior PM | Growth",
        "summary": "Plain prose, no **bold** here please.",
        "core_skills": [{"label": "PLG", "description": "no **bold** in skills"}],
        "experiences": [
            {"bullets": ["Lifted **activation by 18%**, covered in **TechCrunch**."]}
        ],
        "msc_bullets": ["MSc with **panel data econometrics** coursework."],
        "ba_bullets": ["BA in Cognitive Science."],
        "additional": [{"label": "Languages", "description": "English, **Korean**"}],
    }
    out = convert_content_map(sample)
    assert "**" not in out["summary"]
    assert "**" not in out["core_skills"][0]["description"]
    assert "**" not in out["additional"][0]["description"]
    assert isinstance(out["experiences"][0]["bullets"][0], RichText)
    assert isinstance(out["msc_bullets"][0], RichText)
    print("md_to_richtext self-test passed.")
