# CV templates

Each template is a docxtpl-compatible `.docx` plus a `partials/` folder of section partials. The `cv-tailor` skill renders against whichever template is set in `config.yaml > cv.template`.

## The catalog

| Template | Best for | Distinguishing features |
| --- | --- | --- |
| **OPUS** (flagship) | research, consulting, analytics, policy | Selective inline bold in experience and education; tight one-page layout; red accent section headers |
| **modern-tech** | software, product, startup roles | Clean sans-serif, minimal ornament, skills-forward |
| **academic** | academia, research labs, PhD-track | Publications and presentations sections on by default; longer-form |
| **executive** | senior leadership, director+, C-suite | Summary-forward, fewer bullets, emphasis on scope and scale |
| **creative** | design, music, brand, creative roles | Room for a links/portfolio section; more visual breathing room |

OPUS is the default and the most thoroughly specified. The other four are alternates.

## What each template folder contains

```
templates/<name>/
├── README.md            # template-specific notes, the formatting constants
├── full_template.docx   # all sections, for reference + non-modular rendering
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

The `cv-tailor` skill composes `full_template.docx` on the fly from the partials listed in `config.yaml > cv.sections` (see `skills/cv-tailor/references/modular-sections.md`). If no partials are present, it falls back to `full_template.docx` whole.

## v1.0 status

**The `.docx` files are not yet in this scaffold.** Designing five styled, docxtpl-ready templates plus their section partials is real design work that comes after the skeleton. Each template folder currently holds only this catalog entry and a placeholder.

To populate a template:

1. Build (or bring) a finished CV `.docx` with the layout you want.
2. Run `skills/cv-tailor/scripts/build_template.py <source.docx> <full_template.docx>` to convert the variable regions to docxtpl placeholders.
3. Split the result into section partials, or keep `full_template.docx` whole if you don't need modular sections.
4. Run the acceptance test (`build_template.py <template.docx>`) and confirm the render matches the source layout.

See `skills/cv-tailor/references/docxtpl-recipe.md` and `skills/cv-tailor/SKILL.md` Appendix for the full procedure.

## Adding your own template

Drop a new folder under `templates/`, follow the structure above, and set `cv.template` to the folder name. The framework treats template names as opaque — anything with a valid `full_template.docx` (or a complete `partials/` set) works.
