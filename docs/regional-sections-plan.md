# Deferred plan: region-aware section toggling

Status: **IMPLEMENTED in v1.8.0** — via the `cv.region_section_overrides`
config block (the "upgrade" option below), not the diagnosis-emitted list.
The user's config already carried the key (`EU: {summary: false}`,
`Denmark: {summary: false}`); v1.8.0 made it real:
`render_cv.effective_sections()` resolves it and `postprocess_cv()` removes
the disabled sections from the rendered file. Setup Step 6 now offers it.
Precedence: per-application diagnosis override > region overrides > global
`cv.sections`. See `skills/cv-tailor/references/modular-sections.md`.
Kept for the historical rationale below. Last updated 2026-06-25.

## Goal

Drop the `summary` section automatically for European CVs, without a per-region
schema field. European here means the EU branch plus the country branches carved
out of it for their own settings (currently Germany, Denmark). May later extend to
US and Gulf.

## Why not the obvious options

- **Global `cv.sections`** is all-or-nothing. Can't scope to a region.
- **Per-application `disable: summary`** in a Diagnosis is one-off. Doesn't make a
  standing rule.
- A region-conditional rule therefore has to live in plugin source, at the step
  that already knows the region: `role-diagnosis`.

## The build (one section, current scope)

In `role-diagnosis`, emit `disable: summary` whenever the resolved branch is a
European one. Do NOT hardcode `EU/Germany/Denmark` inline in the conditional.

1. Define one list, single source of truth, e.g. `european_branches: [EU, Germany,
   Denmark]`, in one place.
2. The rule tests branch membership against that list.
3. Adding a European country later = append one name to the list, not edit the rule.
4. Leave a comment marking the list as the thing to extend:
   `# ponytail: european_branches is the single source of truth for "European";
   extend this list, not the conditional. Promote to a regional_sections config
   block only if a SECOND section starts varying by region.`

This reuses the existing `disable: <section>` override mechanism that `cv-tailor`
already honors. No schema change, no wizard change.

### Confirm before writing the list

- Which branch keys count as European? EU-only (EU + Germany + Denmark) or
  geographic Europe (also UK, Switzerland, Norway, ...)? This changes the
  enumeration. Make the agent show its list before baking it in.
- Confirm the rule applies to the Germany and Denmark branches too, not just the
  generic EU branch. The membership list is exactly what guarantees that.

## Extending to US / Gulf

Still one section, more regions. Just add the region keys to `european_branches`
(or rename it to something like `summary_off_branches` once it's no longer
European-only). No schema needed.

Inversion check: if `summary` ends up off for Europe AND US AND Gulf, ask what
regions keep it. If it's down to one or two, flip it — drop `summary` from the
global default and enable it for the exceptions instead. Fewer rules.

## Upgrade trigger: when the schema field becomes worth it

Promote to an optional `regional_sections:` config block ONLY when MULTIPLE
sections vary by region (a matrix), e.g. summary off in EU, core_skills off in
Gulf, publications on for academic-EU. One section across many regions does NOT
justify it; the list above is lazier and does the same job.

When you do build it:

- Optional, defaults to empty, so existing setups behave identically. No wizard
  question needed (keep the default question set and CV structure as-is).
- The one real cost is precedence. Define the resolution order once and test it:
  **per-application override > regional_sections > global `cv.sections`.**
- Document it in `cv-tailor/references/modular-sections.md` and `content-map-schema.md`.
