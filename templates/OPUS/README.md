# OPUS template

The flagship template. One-page, research/consulting-leaning, with selective
inline bold in the Experience and Education sections and red accent section
headers. This is the default (`config.yaml > cv.template: OPUS`).

## Status

`full_template.docx` is **built and render-tested** — it renders cleanly via
`docxtpl` with `autoescape=True`. It is fully public: every personal field
(name, contact, both degrees) is a placeholder.

## Placeholders in this template

```
{{ candidate_name }}        {{ msc_degree }}      {{ ba_degree }}
{{ tagline }}               {{ msc_date }}        {{ ba_date }}
{{ contact_line_1 }}        {{ msc_institution }} {{ ba_institution }}
{{ personal_site }}         {{ msc_location }}    {{ ba_location }}
{{ linkedin_url }}
{{ contact_line_2_suffix }}
{{ summary }}
```

Plus the paragraph loops: `core_skills`, `experiences` (with nested
`role.bullets`), `msc_bullets`, `ba_bullets`, `additional`.

See `../../skills/cv-tailor/references/content-map-schema.md` for the full content
map.

## Modular sections

`full_template.docx` contains every section. The `partials/` folder is for
the modular-composition path (`skills/cv-tailor/references/modular-sections.md`).
Splitting OPUS into partials is a v1.1 task — until then, the renderer uses
`full_template.docx` whole and section toggling is done by leaving the
relevant content-map keys empty.

## Editing this template

Structural edits (new placeholder, tab stop, color) are made directly to
`full_template.docx` via unpack/edit/repack — never as part of the daily CV
build. See `../../skills/cv-tailor/references/docxtpl-recipe.md` and
`../../skills/cv-tailor/scripts/build_template.py`.
