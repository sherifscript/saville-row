# OPUS template

The flagship template. One-page, research/consulting-leaning, with selective
inline bold in the Experience and Education sections and red accent section
headers. This is the default (`config.yaml > cv.template: OPUS`).

## Status

`full_template.docx` is **built and render-tested** — it renders cleanly via
`docxtpl` with `autoescape=True`. It is fully public: every personal field
(name, contact, every degree) is a placeholder.

## Placeholders in this template

```
{{ candidate_name }}        {{ degree.name }}
{{ tagline }}               {{ degree.date }}
{{ contact_line_1 }}        {{ degree.institution }}
{{ personal_site }}         {{ degree.location }}
{{ linkedin_url }}
{{ contact_line_2_suffix }}
{{ summary }}
```

Plus the paragraph loops: `core_skills`, `experiences` (with nested
`role.bullets`), `degrees` (with nested `degree.bullets` — since v1.9.0
education is a loop, so every degree in the career file renders; the old
fixed `msc_*`/`ba_*` pair silently dropped a third degree), `additional`.

See `../../skills/cv-tailor/references/content-map-schema.md` for the full content
map.

## Modular sections

`full_template.docx` contains every section. The `partials/` folder is for
the modular-composition path (`skills/cv-tailor/references/modular-sections.md`)
and is still a placeholder — the renderer uses `full_template.docx` whole.

Section toggling works via the **postprocess pass**, not by leaving
content-map keys empty (an empty key would still render the section header):
`postprocess_cv()` deletes a disabled section's header paragraph through the
paragraph before the next header. `cv.sections` and
`cv.region_section_overrides` (e.g. `EU: summary: false`) both feed it.
Sections the full template does not contain (publications, certifications,
volunteering) cannot be toggled ON until real partials exist — surface that
content as an `additional` item instead.

## Bullets and bold

Every bullet placeholder is plain `{{ bullet }}`. Bullets must therefore be
**plain strings** at render time — a docxtpl `RichText` value through a plain
placeholder embeds run-XML inside `<w:t>` and Word/ATS read the bullet as
EMPTY (the 2026-05-11 / test5 corruption). Bold (`inline_bold`, `labeled`)
is applied after render by `postprocess_cv()`, which clones the rendered
run so the template's Calibri/size/bold-pairing formatting is inherited
exactly. See `docxtpl-recipe.md` "RichText is banned from the render path".

## Editing this template

Structural edits (new placeholder, tab stop, color) are made directly to
`full_template.docx` via unpack/edit/repack — never as part of the daily CV
build. See `../../skills/cv-tailor/references/docxtpl-recipe.md` and
`../../skills/cv-tailor/scripts/build_template.py`.
