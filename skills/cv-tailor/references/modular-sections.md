# Modular sections — toggling CV sections per user, region, and application

**How it actually works today:** the full template renders whole, then
`postprocess_cv()` **removes** disabled sections (header paragraph through
the paragraph before the next section header). Partial-file composition is
designed but INACTIVE — no shipped template has real partials, and
`render_cv._resolve_template()` silently falls back to `full_template.docx`
until they exist. Toggling ON a section the full template lacks
(publications / certifications / volunteering on OPUS) has no render path;
surface that content as an `additional` item instead.

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
    - publications    # toggleable; default off (no OPUS render path yet)
    - certifications  # toggleable; default off (no OPUS render path yet)
    - volunteering    # toggleable; default off (no OPUS render path yet)
```

Required sections (`tagline`, `contact`, `experience`, `education`) can never
be disabled — the postprocess pass refuses and warns.

## Three layers of control (highest precedence first)

1. **Per-application override in the diagnosis** — e.g. an academic role
   enables `publications`, disables `additional`:

   ```markdown
   ## Section overrides (optional, in Diagnosis.md)
   - enable: publications
   - disable: additional
   ```

2. **Region override in config** — `cv.region_section_overrides`, honored
   for real since v1.8.0 (before that the key was silently ignored):

   ```yaml
   cv:
     region_section_overrides:
       EU:      {summary: false}   # European CVs commonly drop the summary
       Denmark: {summary: false}
   ```

3. **User default** — `cv.sections` in config.yaml, set once by
   `job-search-setup`.

`render_cv.effective_sections(config, region)` resolves layers 2–3; the
diagnosis override is applied on top by the model.

One reorder exists without partials: `cv.student_mode` (or a
`Student mode: on` diagnosis line) moves EDUCATION above PROFESSIONAL
EXPERIENCE in the postprocess pass.

## When partials ship (future)

Each template would carry `partials/<section>.docx` files stitched in
`cv.sections` order by `scripts/section_composer.py` — enabling section
reordering and per-section Word editing. Until then, everything above is the
operative mechanism.
