---
name: cv-tailor
description: Render diagnosis-driven, ATS-optimized CVs as .docx via docxtpl. Modular section composition, region-aware headers, inline-bold helper, and a mandatory five-question post-render audit that catches named historical failure modes.
metadata:
  version: 1.2.0
  last_updated: 2026-05-24
---

# cv-tailor

The renderer. Takes a Diagnosis.md, a candidate's career file, and a chosen template; produces a tailored CV that an ATS will parse and a recruiter will scan correctly.

## When to activate

- User says "render a CV for [company]", "tailor a CV", "Run CV only"
- A Diagnosis.md exists in the target folder and no CV has been rendered yet
- Pipeline orchestrator invokes after role-diagnosis completes

## Hard gate

Before doing anything, check for `Diagnosis - [Company] - [Job Title].md` in the target folder. If absent, defer to the opinionation policy (warn-once-then-comply by default; strict mode refuses). See `role-diagnosis/SKILL.md`.

Exception: `Run CV only` shortcut explicitly skips the diagnosis gate. The CV is rendered against broad branch judgment instead.

## What it does

1. Reads `Diagnosis.md` and extracts the content map (lead credential, keywords, branch, target region).
2. Loads `config.yaml` to determine output formats, template choice, default section toggles, opinionation.
3. Loads `branches.yaml` to get the third-slot company for the chosen branch.
4. Loads `regional-headers.yaml` to get the header for the target region.
5. Builds a `content_map` dict for docxtpl. See [`references/content-map-schema.md`](./references/content-map-schema.md).
6. Composes sections per `cv.sections` order in config. Disabled sections are omitted; the template's partials are stitched together at render time. See [`references/modular-sections.md`](./references/modular-sections.md).
7. Renders via `docxtpl` with `autoescape=True` mandatory. See [`references/docxtpl-recipe.md`](./references/docxtpl-recipe.md).
8. Converts `**markdown bold**` markers in experience and education bullets to docxtpl `RichText` runs. See [`references/docxtpl-recipe.md`](./references/docxtpl-recipe.md).
9. Saves `.docx` to the target folder.
10. Runs the five-question post-render audit. See [`references/post-render-audit.md`](./references/post-render-audit.md). Refuses to ship the CV if any check fails.
11. (Optional) Converts to PDF via LibreOffice if `output_formats` includes `pdf`.

## Critical correctness rules

These exist because each one has shipped a broken CV in the past. Do not skip.

### `autoescape=True` is mandatory

Without it, `&` characters in content_map values are silently stripped from the rendered XML. `Artist & Label` becomes `Artist  Label`. Always pass `autoescape=True` to `tpl.render()`.

### `convert_content_map()` runs before render

The helper at `scripts/md_to_richtext.py`:
- Converts `**phrase**` markers to RichText bold runs in experience bullets and education bullets only.
- Strips stray `**` markers from all other fields (tagline, summary, core_skills descriptions, additional descriptions).

If you do not run it, leaked `**` markers render as literal asterisks in Word.

### Inline bold scope

| Field | Bold allowed? |
| --- | --- |
| `experiences[i].bullets` | Yes |
| `msc_bullets` | Yes |
| `ba_bullets` | Yes |
| `tagline` | No (styled by template) |
| `summary` | No (prose) |
| `core_skills[i].description` | No (label is bold; description plain) |
| `additional[i].description` | No (same pattern) |

### Experience section structure

By default: exactly 3 experience slots. Slot 1 = most recent / longest-tenure role. Slot 2 = adjacent role at the same employer if applicable (continuous block). Slot 3 = branch-driven choice. User can override `cv.max_experience_slots` in config. See [`references/experience-slot-logic.md`](./references/experience-slot-logic.md).

### Pre-render verification (mandatory)

Before `tpl.render()`:

- Diagnosis exists for this Company/Job Title in the target folder ✓
- `content_map` contains every required key; no key is empty or None ✓
- No tailored company name appears in any bullet, summary, or skills line ✓
- No specific employer name appears in the professional summary ✓
- Correct third-slot company per the diagnosis's branch ✓
- `contact_line_1` and `contact_line_2_suffix` match the regional rule for the target region ✓
- Work Authorization item present in `additional` for Western/EU/EEA targets, absent for Egypt/Gulf ✓

### Post-render audit (mandatory)

The five-question audit at [`references/post-render-audit.md`](./references/post-render-audit.md). Refuses to ship the CV if any check fails.

## Modular sections

CV sections are composable. Default order (configurable in `config.yaml`):

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
```

A user can disable any toggleable section globally in `config.yaml`. A diagnosis can also override per-application — e.g., a publications-heavy academic role can turn `publications: on` for that CV only.

The template (`${CLAUDE_PLUGIN_ROOT}/templates/[chosen]/`) ships every possible section as a partial docx file. `scripts/section_composer.py` reads the section order and stitches partials in order, then the result is rendered by docxtpl. See [`references/modular-sections.md`](./references/modular-sections.md).

## Output

```
data/sessions/[dd.mm]/[Country or City]/CV - [Company] - [Job Title].docx
```

For `Run CV only`:

```
data/sessions/[dd.mm]/[Branch] CV.docx
```

(no Company/Job Title in filename — no specific JD)

## Files referenced

- [`references/docxtpl-recipe.md`](./references/docxtpl-recipe.md) — the autoescape mandate, the RichText helper, named failure modes
- [`references/post-render-audit.md`](./references/post-render-audit.md) — the five checks
- [`references/modular-sections.md`](./references/modular-sections.md) — section composition
- [`references/regional-headers.md`](./references/regional-headers.md) — the regional header pattern
- [`references/experience-slot-logic.md`](./references/experience-slot-logic.md) — slot 1/2/3 rules
- [`references/content-map-schema.md`](./references/content-map-schema.md) — every key in the content_map
- [`scripts/render_cv.py`](./scripts/render_cv.py) — the main entry point
- [`scripts/md_to_richtext.py`](./scripts/md_to_richtext.py) — the bold-marker helper
- [`scripts/audit.py`](./scripts/audit.py) — the five-question audit as code
- [`scripts/section_composer.py`](./scripts/section_composer.py) — section partial stitching
- [`scripts/build_template.py`](./scripts/build_template.py) — one-time template-from-CV converter
