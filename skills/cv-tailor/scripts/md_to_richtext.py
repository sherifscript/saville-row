"""
md_to_richtext.py — strip **markdown bold** markers and build the bold plan.

(The module name is historical: until v1.8.0 it converted markers to docxtpl
RichText objects. RichText through the template's plain `{{ bullet }}`
placeholders embeds run-XML inside <w:t> — invalid OOXML that Word/python-docx/
ATS read as EMPTY bullets. That was the 2026-05-11 incident and the corruption
in every labeled-mode CV of the 2026-06-25/27 batches. RichText is now banned
from the render path; see docxtpl-recipe.md.)

The v1.8.0 pipeline:

  1. `build_bold_plan(cm, mode)` — called immediately before
     `tpl.render(cm, autoescape=True)`. Strips `**` markers from every field,
     and (when mode is "labeled" or "inline") records which character spans of
     each bullet should render bold. Bullets stay plain strings.
  2. `postprocess_cv(path, plan, ...)` (postprocess.py) — after `tpl.save()`,
     applies the recorded spans as real bold runs by cloning the rendered
     run (template formatting inherited exactly).

Marker rules are unchanged from the old design:
  - Boldable fields: experiences[i].bullets, msc_bullets, ba_bullets.
  - Never-bold fields (tagline, summary, contact lines, core_skills
    descriptions, additional descriptions): markers are stripped so a leaked
    `**` can never render literally.
"""

import re

_MARKER_RE = re.compile(r"(\*\*[^*]+?\*\*)")

BOLD_MODES = ("plain", "inline", "labeled")


def _strip_markers(text):
    """Remove stray ** markers from a string. Non-strings pass through."""
    return text.replace("**", "") if isinstance(text, str) else text


def _strip_and_spans(text):
    """Strip ** markers; return (stripped_text, spans).

    Spans are (start, end) character offsets into the STRIPPED string, one
    per **marked** phrase — the coordinates postprocess_cv bolds at.
    """
    spans = []
    out = []
    pos = 0
    for part in _MARKER_RE.split(text):
        if not part:
            continue
        if part.startswith("**") and part.endswith("**"):
            inner = part[2:-2]
            spans.append((pos, pos + len(inner)))
            out.append(inner)
            pos += len(inner)
        else:
            out.append(part)
            pos += len(part)
    return "".join(out), spans


def build_bold_plan(cm, mode="plain"):
    """Strip markers across the content_map; record the bold plan.

    mode: "plain"  — no bold anywhere; every marker stripped, spans empty.
          "inline" — bold the **phrase** spans in boldable fields.
          "labeled" — same span mechanics; the convention is a bold
                      `**Label:**` lead-in on every experience bullet
                      (validated by render_cv.validate_content_map).

    Returns (cm, plan). Mutates cm in place: after this call every bullet is
    a plain string with no markers — safe for `{{ bullet }}` placeholders.
    Plan entries are in document order (experience slots, then msc, then ba):

        {"section": "experience"|"msc"|"ba", "slot": int|None,
         "text": "<stripped bullet>", "spans": [(start, end), ...]}

    Every bullet gets an entry even in plain mode (spans empty) — the
    postprocess pass uses the entries to verify each bullet is actually
    present and readable in the rendered document.
    """
    if mode not in BOLD_MODES:
        raise ValueError("mode must be one of %s, got %r" % (BOLD_MODES, mode))
    record_spans = mode != "plain"
    plan = []

    def handle(bullets, section, slot=None):
        new = []
        for b in bullets:
            if not isinstance(b, str):
                raise TypeError(
                    "bullets must be plain strings; got %s. RichText is "
                    "banned from the render path (2026-05-11 corruption — "
                    "see docxtpl-recipe.md)." % type(b).__name__)
            stripped, spans = _strip_and_spans(b)
            plan.append({
                "section": section,
                "slot": slot,
                "text": stripped,
                "spans": spans if record_spans else [],
            })
            new.append(stripped)
        return new

    for i, role in enumerate(cm.get("experiences", [])):
        if "bullets" in role:
            role["bullets"] = handle(role["bullets"], "experience", i)

    for key, section in (("msc_bullets", "msc"), ("ba_bullets", "ba")):
        if cm.get(key):
            cm[key] = handle(cm[key], section)

    # Never-bold fields: strip stray markers so none can render literally.
    for key in ("tagline", "summary", "contact_line_1", "contact_line_2_suffix"):
        if key in cm:
            cm[key] = _strip_markers(cm[key])

    for skill in cm.get("core_skills", []):
        if "description" in skill:
            skill["description"] = _strip_markers(skill["description"])

    for item in cm.get("additional", []):
        if "description" in item:
            item["description"] = _strip_markers(item["description"])

    return cm, plan


def convert_content_map(cm, inline_bold=False):
    """DEPRECATED shim (pre-v1.8.0 API). Strips ** markers from every field.

    It no longer produces RichText — RichText through a plain `{{ bullet }}`
    placeholder was the 2026-05-11 / labeled-mode corruption. The
    `inline_bold` argument is accepted and ignored; bold now happens after
    render via build_bold_plan() + postprocess_cv(). Existing driver scripts
    that call this keep producing valid (plain) CVs.
    """
    cm, _ = build_bold_plan(cm, mode="plain")
    return cm


if __name__ == "__main__":
    import copy

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

    # inline mode: markers stripped everywhere, spans recorded for bullets.
    cm, plan = build_bold_plan(copy.deepcopy(sample), mode="inline")
    bullet = cm["experiences"][0]["bullets"][0]
    assert bullet == "Lifted activation by 18%, covered in TechCrunch."
    assert isinstance(bullet, str) and "**" not in bullet
    entry = plan[0]
    assert entry["section"] == "experience" and entry["slot"] == 0
    assert [bullet[s:e] for s, e in entry["spans"]] == [
        "activation by 18%", "TechCrunch"]
    assert "**" not in cm["summary"]
    assert "**" not in cm["core_skills"][0]["description"]
    assert "**" not in cm["additional"][0]["description"]
    # msc entry recorded after experience entries; ba has no spans.
    assert plan[1]["section"] == "msc" and len(plan[1]["spans"]) == 1
    assert plan[2]["section"] == "ba" and plan[2]["spans"] == []

    # plain mode: same stripping, no spans anywhere.
    cm_p, plan_p = build_bold_plan(copy.deepcopy(sample), mode="plain")
    assert all(e["spans"] == [] for e in plan_p)
    assert cm_p["experiences"][0]["bullets"][0] == bullet

    # labeled-style span at position 0.
    cm_l, plan_l = build_bold_plan(
        {"experiences": [{"bullets": ["**Pipeline automation:** built it."]}]},
        mode="labeled")
    text = cm_l["experiences"][0]["bullets"][0]
    s, e = plan_l[0]["spans"][0]
    assert text[s:e] == "Pipeline automation:" and s == 0

    # deprecated shim: strips, never converts.
    out = convert_content_map(copy.deepcopy(sample), inline_bold=True)
    assert isinstance(out["experiences"][0]["bullets"][0], str)
    assert "**" not in out["experiences"][0]["bullets"][0]

    print("md_to_richtext self-test: passed.")
