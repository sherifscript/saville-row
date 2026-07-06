# Modular sections — composing the CV from partials

CVs are not monolithic. Different users want different sections; different roles want different sections within the same user. The framework treats sections as **partials** that get stitched in order at render time.

> **Current state (v1.8.0): partial composition is INACTIVE.** No shipped
> template has real partials yet (`templates/OPUS/partials/` holds only a
> placeholder), so `render_cv._resolve_template()` uses partials **only when
> every needed partial actually exists** and otherwise falls back to
> `full_template.docx` silently — the composer can no longer crash a render.
> The *operative* toggle mechanism today is: render the full template, then
> `postprocess_cv()` **removes** disabled sections (header paragraph through
> the paragraph before the next section header). This honors
> `cv.region_section_overrides` (e.g. `EU: summary: false`) for real —
> before v1.8.0 that key was silently ignored. Toggling a section ON that
> the full template does not contain (publications, certifications,
> volunteering on OPUS) still has no render path; surface such content as an
> `additional` item until the partials are built.

## Region-aware section overrides

```yaml
cv:
  sections: [tagline, contact, summary, core_skills, experience, education, additional]
  region_section_overrides:
    EU:
      summary: false        # European CVs commonly drop the summary
    Denmark:
      summary: false
```

`render_cv.effective_sections(config, region)` resolves the final list per
render: it starts from `cv.sections` and subtracts every section a region
override maps to `false`. Precedence: per-application override in the
diagnosis > `region_section_overrides` > global `cv.sections`. Required
sections (`tagline`, `contact`, `experience`, `education`) can never be
disabled — the postprocess pass refuses and warns.

## The canonical section list

```yaml
cv:
  sections:
    - tagline         # required, always present
    - contact         # required
    - summary         # toggleable; default on
    - core_skills     # toggleable; default on
    - experience      # required
    - education       # required
    - additional      # toggleable; default on
    - publications    # toggleable; default off
    - certifications  # toggleable; default off
    - volunteering    # toggleable; default off
    - languages       # toggleable; default on (often inside `additional`)
```

`tagline`, `contact`, `experience`, `education` are required — every CV has them. Everything else is toggleable.

## Two layers of control

### Layer 1 — user default in `config.yaml`

```yaml
cv:
  template: OPUS
  sections:
    - tagline
    - contact
    - summary
    - core_skills
    - experience
    - education
    - additional
  # publications, certifications, volunteering not listed → not included by default
```

This is set during `job-search-setup`. The user picks once, and every CV uses this default.

### Layer 2 — per-application override in the diagnosis

The diagnosis can override sections for a specific role:

```markdown
## Section overrides (optional, in Diagnosis.md)

- enable: publications
- disable: additional
```

For an academic role at a research lab, the diagnosis enables `publications` because the institution will look for them; disables `additional` because the publications list takes the space.

The cv-tailor skill reads section overrides from the diagnosis after loading the user's defaults from config. Overrides take precedence.

## How partials work

Each template (`${CLAUDE_PLUGIN_ROOT}/templates/OPUS/`, `${CLAUDE_PLUGIN_ROOT}/templates/modern-tech/`, etc.) ships every possible section as a partial docx file:

```
${CLAUDE_PLUGIN_ROOT}/templates/OPUS/
├── README.md
├── full_template.docx       # all sections, for reference
└── partials/
    ├── tagline.docx
    ├── contact.docx
    ├── summary.docx
    ├── core_skills.docx
    ├── experience.docx
    ├── education.docx
    ├── additional.docx
    ├── publications.docx
    ├── certifications.docx
    └── volunteering.docx
```

Each partial is a docxtpl template containing only that section's variable region with the styling preserved. `scripts/section_composer.py` reads the `cv.sections` list, opens each requested partial, and composes them into a single docx in order. That composite is then rendered with the full content_map.

## Why partials, not conditionals

The naive approach is to put every section in one `full_template.docx` with `{% if include_publications %}...{% endif %}` blocks. This breaks for two reasons:

1. **docxtpl Jinja blocks inside Word XML are fragile.** Block boundaries on paragraph or section boundaries get clobbered when Word saves the file. Editing the template in Word becomes risky.
2. **Section ordering matters.** Some users want `publications` between `education` and `additional`; others want it at the end. Conditionals can't reorder; partials can.

Partials give clean ordering, clean toggling, and clean editability. Each partial can be opened and edited in Word without affecting any other.

## What partials cannot do

- **Cross-section formatting consistency.** If you edit `tagline.docx` to use a different font size from `contact.docx`, the composed CV will have inconsistent fonts. Template maintainers must keep partials visually aligned. The `build_template.py` script includes a verification step that compares font/size/color settings across partials and warns on drift.
- **Dynamic section ordering within a section.** The order of bullets *within* the experience section is still determined by the content_map (the `experiences` list order), not by partials.

## Default section sets by template

Each template ships with a recommended default section set:

| Template | Default sections |
| --- | --- |
| OPUS | tagline, contact, summary, core_skills, experience, education, additional |
| modern-tech | tagline, contact, summary, core_skills, experience, education |
| academic | tagline, contact, summary, experience, education, publications, presentations, additional |
| executive | tagline, contact, summary, experience, education, additional |
| creative | tagline, contact, summary, core_skills, experience, education, additional, links |

The setup wizard adopts the chosen template's default. The user can edit afterward.

## Adding a new section

1. Add the partial: `${CLAUDE_PLUGIN_ROOT}/templates/[your-template]/partials/new_section.docx` with the desired styling and Jinja placeholders.
2. Add the section to the canonical list in `${CLAUDE_PLUGIN_ROOT}/shared/config.example.yaml` with a default.
3. Update `scripts/section_composer.py` to recognize the new name (only if the name has special composition rules; otherwise the composer handles arbitrary names automatically).
4. Add content_map keys for the new section.
5. Update `references/content-map-schema.md`.
