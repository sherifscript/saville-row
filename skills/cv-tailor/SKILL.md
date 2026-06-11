---
name: cv-tailor
description: Render diagnosis-driven, ATS-optimized CVs as .docx via docxtpl. Modular section composition, region-aware headers, inline-bold helper, and a mandatory five-question post-render audit that catches named historical failure modes.
metadata:
  version: 1.4.1
  last_updated: 2026-06-11
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

Inline bold is controlled by `config.yaml > cv.inline_bold` (default: `false`).

- **When `inline_bold: false` (default):** `convert_content_map()` strips all `**` markers from every field before render. Nothing renders bold regardless of what the content map contains. This is the default because selective bold is increasingly read by recruiters as an AI tell.
- **When `inline_bold: true`:** `**phrase**` markers in the three allowed fields convert to bold runs; markers in disallowed fields are stripped.

| Field | Bold allowed (when inline_bold: true)? |
| --- | --- |
| `experiences[i].bullets` | Yes |
| `msc_bullets` | Yes |
| `ba_bullets` | Yes |
| `tagline` | No (styled by template) |
| `summary` | No (prose) |
| `core_skills[i].description` | No (label is bold; description plain) |
| `additional[i].description` | No (same pattern) |

### Experience section structure — HARD RULES

**Read `references/experience-slot-logic.md` before building any content map.** The rules below are the non-negotiable subset; the reference file has the full spec.

**The 3-slot structure (default):**

1. **Slot 1** — the candidate's most recent primary-employer role. This is the slot with the senior title.
2. **Slot 2** — the adjacent role at the same employer (the junior / earlier title). When `cv.continuous_employer_block: true` (the default), this slot is **mandatory and non-droppable** whenever a Slot 1 role has a preceding same-employer role in the career file. It is not "if applicable" — it is required. Dropping it creates a visible employment gap.
3. **Slot 3** — branch-driven choice from `branches.yaml > branches[n].third_slot_company`. The diagnosis picks the branch; the branch picks the company; the framework picks the role. The diagnosis cannot add a fourth slot, drop the Slot 1 / Slot 2 block, or reorder Slot 1 above Slot 2.

**The continuous-block rule in plain language:** if the candidate held two roles at the same primary employer (e.g., Statista Research Expert Aug 2023 – Oct 2025, and Statista Research Assistant Aug 2020 – Jul 2023), those two roles must appear as Slots 1 and 2 in every CV, in that order, with no other role between them. The Statista Assistant is not optional. Omitting it leaves a three-year gap (2020–2023) that a recruiter will notice. This rule was violated in the 2026-05-24 Cairo trial because the render script read only the soft one-liner in this file and never opened experience-slot-logic.md.

**Reverse chronology is enforced by construction.** Slot 1 has the highest end date. Slot 2 has the next. Slot 3 is always older. An ongoing role (end date = "Present") goes before a completed role. Do not place an ongoing role in Slot 2 below a completed role in Slot 1.

**The post-render audit's Check 7 enforces the structure programmatically.** A CV that fails Check 7 is not shipped.

User can override `cv.max_experience_slots` in config. See [`references/experience-slot-logic.md`](./references/experience-slot-logic.md).

### No em dashes in employer-facing content

Em dashes (—) are banned from all employer-facing output. This means every field in the content_map: tagline, summary, bullets, additional descriptions. Use commas, periods, or restructure the sentence. See `${CLAUDE_PLUGIN_ROOT}/shared/conventions.md`. The post-render audit's Check 6 enforces this programmatically.

### Pre-render verification (mandatory)

Before `tpl.render()`:

- Diagnosis exists for this Company/Job Title in the target folder ✓
- `content_map` contains every required key; no key is empty or None ✓
- No tailored company name appears in any bullet, summary, or skills line ✓
- No specific employer name appears in the professional summary ✓
- Correct third-slot company per the diagnosis's branch ✓
- `contact_line_1` and `contact_line_2_suffix` match the regional rule for the target region ✓
- Work Authorization item present in `additional` for Western/EU/EEA targets, absent for Egypt/Gulf ✓
- Experience list is in strict reverse-chronological order; Slots 1 + 2 share the primary employer ✓
- No em dashes in any content_map value ✓

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
paths.session_output_dir/[session-date]/[Country or City]/CV - [Company] - [Job Title].docx
```

For `Run CV only`:

```
paths.session_output_dir/[session-date]/[Branch] CV.docx
```

(no Company/Job Title in filename — no specific JD)

`[session-date]` is today's date formatted per `paths.session_date_format` (default `dd.mm.yy`, e.g. `11.06.26`).

### Scratch files stay out of the output folder

The render driver script and any content-map JSON/YAML dumps used to build a CV go in `.scratch/` at the workspace root, never in the session output folder. The session folder holds the rendered `.docx` and nothing else. See "Deliverables-only output folders" in `${CLAUDE_PLUGIN_ROOT}/shared/conventions.md`.

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
