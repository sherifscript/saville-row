# Modular sections — composing the CV from partials

CVs are not monolithic. Different users want different sections; different roles want different sections within the same user. The framework treats sections as **partials** that get stitched in order at render time.

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

Each template (`templates/OPUS/`, `templates/modern-tech/`, etc.) ships every possible section as a partial docx file:

```
templates/OPUS/
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

1. Add the partial: `templates/[your-template]/partials/new_section.docx` with the desired styling and Jinja placeholders.
2. Add the section to the canonical list in `shared/config.example.yaml` with a default.
3. Update `scripts/section_composer.py` to recognize the new name (only if the name has special composition rules; otherwise the composer handles arbitrary names automatically).
4. Add content_map keys for the new section.
5. Update `references/content-map-schema.md`.
