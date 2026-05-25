"""
md_to_richtext.py — convert **markdown bold** markers to docxtpl RichText runs.

The framework uses `**phrase**` markers inside CV bullets to indicate which
phrases should render bold. docxtpl does not interpret these — without
conversion they render as literal asterisks in Word.

`convert_content_map()` does two things:
  1. In allowed fields (experience bullets, msc_bullets, ba_bullets):
     converts **phrase** to RichText bold runs WHEN inline_bold is True.
     When inline_bold is False (the default), strips markers instead.
  2. In disallowed fields (tagline, summary, core_skills, additional):
     strips stray ** markers so a leaked marker cannot render literally.

The inline_bold parameter maps to config.yaml > cv.inline_bold (default false).
When false, ** markers in ALL fields are stripped — nothing renders bold.

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


def convert_content_map(cm, inline_bold=False):
    """Walk the content_map. Convert markdown-bold to RichText in the
    Experience and Education sections when inline_bold is True; strip stray
    ** markers everywhere else (and from ALL fields when inline_bold is False).

    inline_bold maps to config.yaml > cv.inline_bold (default false).
    Pass the value loaded from config; default is False (strip all markers).

    Mutates and returns cm.
    """
    # Determine converter for the boldable fields based on the toggle
    _convert = md_to_richtext if inline_bold else _strip_markers

    # --- Bolding ALLOWED fields (convert or strip based on toggle) ---------
    for role in cm.get("experiences", []):
        if "bullets" in role:
            role["bullets"] = [_convert(b) for b in role["bullets"]]

    for key in ("msc_bullets", "ba_bullets"):
        if key in cm:
            cm[key] = [_convert(b) for b in cm[key]]

    # --- Bolding NOT ALLOWED: always strip stray markers ------------------
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
    import copy

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

    # Test inline_bold=True (default old behavior)
    out_bold = convert_content_map(copy.deepcopy(sample), inline_bold=True)
    assert "**" not in out_bold["summary"]
    assert "**" not in out_bold["core_skills"][0]["description"]
    assert "**" not in out_bold["additional"][0]["description"]
    assert isinstance(out_bold["experiences"][0]["bullets"][0], RichText)
    assert isinstance(out_bold["msc_bullets"][0], RichText)
    print("md_to_richtext self-test (inline_bold=True): passed.")

    # Test inline_bold=False (new default): all ** stripped, no RichText objects
    out_plain = convert_content_map(copy.deepcopy(sample), inline_bold=False)
    assert "**" not in out_plain["summary"]
    assert isinstance(out_plain["experiences"][0]["bullets"][0], str)
    assert "**" not in out_plain["experiences"][0]["bullets"][0]
    assert isinstance(out_plain["msc_bullets"][0], str)
    print("md_to_richtext self-test (inline_bold=False): passed.")
