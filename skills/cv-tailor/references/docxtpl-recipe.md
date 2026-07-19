# docxtpl recipe — the rendering rules and their failure modes

Every rule here exists because skipping it shipped a broken CV. All of them
are enforced mechanically by `render_cv.render()` — prefer calling it over
hand-rolling this pipeline.

## The minimum render

```python
from docxtpl import DocxTemplate
from md_to_richtext import build_bold_plan
from postprocess import postprocess_cv

content_map, bold_plan = build_bold_plan(content_map, mode=mode)  # MANDATORY
tpl = DocxTemplate("templates/OPUS/full_template.docx")
tpl.render(content_map, autoescape=True)          # autoescape=True MANDATORY
tpl.save("CV - Company - Job Title.docx")
postprocess_cv("CV - Company - Job Title.docx", bold_plan)        # MANDATORY
```

(`mode` comes from `render_cv.resolve_bold_mode(config)`: `"labeled"` |
`"inline"` | `"plain"`.)

## `autoescape=True` (incident 2026-04-28, Believe batch)

docxtpl's default `autoescape=False` silently strips `&`, `<`, `>` from the
rendered XML: `Artist & Label` ships as `Artist  Label` — a recruiter-visible
typo in every field containing an ampersand. Audit Check 4 counts ampersands;
the fix is always the same: pass `autoescape=True` to every `tpl.render()`.

## RichText is banned from the render path (2026-05-11, pinned trigger)

The template's bullet placeholders are plain `{{ bullet }}`. A `RichText`
value through a plain placeholder embeds run-XML **inside** `<w:t>`
(RichText's `__html__` bypasses autoescape) — invalid OOXML that Word,
python-docx, and ATS parsers all read as an **EMPTY paragraph**, while a
raw-XML regex still sees the text (why the old audit passed it). This
corruption is deterministic and shipped every labeled-mode CV of the
2026-06-25 and 2026-06-27 batches blank.

The v1.8.0 rule: bullets are **plain strings** at render time, always.
`build_bold_plan()` strips every `**` marker pre-render (recording spans for
allowed fields: experience + degree bullets; stripping outright elsewhere);
`postprocess_cv()` applies the plan as real bold runs post-save by cloning
the rendered run (template rPr inherited exactly), and raises
`PostprocessError` when a planned bullet is missing. Audit Check 5 re-opens
the file with python-docx and refuses to ship unreadable bullets — the check
that keeps this corruption class unshippable.

## What to bold (plain mode)

Bold exists so a recruiter's 6-second scan lands on **proof**:

- **Bold-worthy:** quantified outcomes (`38%`, `$2M ARR`, `40+
  multinationals`); credential proper nouns (`TechCrunch`, `Deloitte`,
  `Harvard Law Review`); concrete superlatives (`second-most-used feature`).
- **Never bold:** JD keywords (they earn their *place* verbatim for ATS,
  never bold — bolding them is keyword theater), generic strength claims,
  any adjective without a number.
- **Per-CV budget:** roughly 4–8 bold items total, each phrase bolded at
  most once. A bullet with no outcome or credential stays plain. Bolding
  everything is the same as bolding nothing.

In `bullet_style: labeled`, every bullet's lead label is bold by design, so
the 4–8 ceiling is suspended for labels; inside the clause, bold at most one
quantified outcome. See `SKILL.md` "Bullet style and bold".

## Contact-line hyperlinks

The personal site and LinkedIn links must be **real hyperlink
relationships**, not plain text (corporate mail clients don't auto-link
.docx text). The OPUS template carries them pre-wired; the postprocess
round-trip must preserve them. Audit Check 5(e) fails a CV whose
`word/_rels/document.xml.rels` has fewer than two hyperlink relationships.

## Template handling

- **Unpack/edit/repack is never part of the daily build** — daily builds are
  docxtpl renders. It is allowed only for one-time structural edits to the
  template itself (new placeholder, tab stop, global font/color), committed
  back via [`../scripts/build_template.py`](../scripts/build_template.py).
- **Locked template = stop.** If the template (or the job log) is open in
  Word, do not fall back to a copy or older version — notify the user and
  wait.

## XML formatting constants (OPUS; template maintainers only)

- Font: Calibri declared explicitly on every `<w:rPr>` (never rely on
  document defaults). Body 10pt (`w:sz 20`), section headers 12pt bold
  C0392B with bottom border, job-title rows 11pt bold 1A1A1A, tab stop 9626
  DXA throughout.
- Always pair `<w:b/>`+`<w:bCs/>`, `<w:i/>`+`<w:iCs/>`, `<w:sz>`+`<w:szCs>`.

Other templates define their own constants.
