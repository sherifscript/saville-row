# docxtpl recipe — the rendering rules and their failure modes

This file documents the small set of hard rules that make the CV render reliably. Every rule here exists because skipping it has produced a broken CV at some point. The named incidents (2026-04-26, 2026-04-28, 2026-05-11) are real failures from the workflow this framework was extracted from.

## The minimum render

```python
from docxtpl import DocxTemplate
from md_to_richtext import build_bold_plan
from postprocess import postprocess_cv

content_map, bold_plan = build_bold_plan(content_map, mode=mode)  # MANDATORY
tpl = DocxTemplate("templates/OPUS/full_template.docx")
tpl.render(content_map, autoescape=True)          # autoescape=True is MANDATORY
tpl.save("CV - Company - Job Title.docx")
postprocess_cv("CV - Company - Job Title.docx", bold_plan)  # MANDATORY
```

(`mode` is `"labeled"` when `cv.bullet_style: labeled`, `"inline"` when
`cv.inline_bold: true`, else `"plain"` — `render_cv.resolve_bold_mode()`
derives it. Prefer calling `render_cv.render()`, which runs this whole
pipeline plus validation and the audit.)

Four things must be true: (1) you used `docxtpl`, not unpack/edit/repack;
(2) you called `build_bold_plan()` before rendering, so every bullet is a
**plain string** at render time; (3) you passed `autoescape=True`;
(4) you called `postprocess_cv()` after saving, so planned bold becomes real
runs and disabled sections are removed.

## Why `autoescape=True` is mandatory

docxtpl's default is `autoescape=False`. With that default, when content_map values contain `&`, `<`, or `>`, the rendered XML becomes malformed (`&` is a special XML character). Word and python-docx silently strip the malformed bytes — the resulting document opens fine, just with the `&` characters gone.

The failure mode looks like this:

```
content_map:
  "tagline": "Senior Analyst — Telecom & AI"
  "core_skills":
    - {"label": "Music Industry", "description": "Artist & Label partnerships..."}
  "additional":
    - {"label": "Roles", "description": "Co-Founder & Executive Producer..."}

rendered CV (with autoescape=False):
  Tagline:        "Senior Analyst — Telecom  AI"          ← double space
  Skill row:      "Music Industry: Artist  Label..."     ← double space
  Additional:     "Roles: Co-Founder  Executive Producer..."  ← double space
```

The recruiter sees the double space and assumes a typo. The CV looks unprofessional in the most subtle, hard-to-debug way possible.

**Incident 2026-04-28 (Believe CV batch):** every CV with an `&` in any field shipped with stripped ampersands. None of the CVs were caught before sending because the diff inspection was on `content_map` (which had the `&`) rather than the rendered docx. Audit check #4 was added in response.

**Fix:** pass `autoescape=True` to every `tpl.render()` call without exception. The escaping converts `&` to `&amp;` in the XML, which Word renders as `&` correctly.

## RichText is banned from the render path (the 2026-05-11 trigger, pinned)

The framework uses `**phrase**` markdown-style markers inside bullets to
indicate which phrases should render bold. docxtpl does not interpret these
markers. Until v1.8.0 the pipeline converted them to docxtpl `RichText`
objects before render. **That was the bug.**

**The pinned trigger:** the template's bullet placeholders are plain
`{{ bullet }}`, not the RichText form `{{r bullet }}`. When a `RichText`
value passes through a plain placeholder, docxtpl embeds the RichText's
run-XML **inside** the placeholder's `<w:t>` element (RichText's `__html__`
bypasses autoescape, so the markup is inserted raw). `<w:r>` nested inside
`<w:t>` is invalid OOXML: **Word, python-docx, and ATS parsers all read the
paragraph as EMPTY.** The text is still visible to a raw-XML regex — which
is why the old audit passed the corruption.

- **Incident 2026-05-11 (General CV regression):** every bullet containing
  `**markdown**` rendered as an empty bullet. The trigger above was not
  identified at the time; the old audit check #5 (a bold-run regex count)
  was added in response — and could never fail on OPUS, whose section
  headers are themselves bold.
- **Incidents 2026-06-25 (Cairo, v1.6.0) and 2026-06-27 (Berlin, v1.7.0):**
  the same corruption shipped in *every* labeled-mode CV of both batches —
  three job titles, zero visible bullets — with a passing audit. It is
  deterministic, not intermittent: any render where bullets are RichText
  through a plain placeholder corrupts (renders whose bullets carried no
  `**` markers, like the 2026-05-06 BMG CV, stayed plain strings and were
  fine — that is why the failure looked random).

**The v1.8.0 rule:** bullets are **plain strings** at render time, always.
`build_bold_plan()` ([`../scripts/md_to_richtext.py`](../scripts/md_to_richtext.py))
strips every `**` marker before render — allowed fields get their bold spans
recorded in a plan, disallowed fields (tagline, summary, core_skills
descriptions, additional descriptions) are stripped outright. After
`tpl.save()`, `postprocess_cv()`
([`../scripts/postprocess.py`](../scripts/postprocess.py)) applies the plan
as **real bold runs** by cloning the rendered run element — the clone
inherits the template run's full rPr (Calibri, sz 20, paired `w:b`/`w:bCs`),
so no formatting is re-declared in code. It also verifies every planned
bullet is actually present in the document and raises `PostprocessError`
if not — a loud render-time failure instead of a silent blank CV.

Audit Check 5 (`check_5_rendered_integrity`) then reads the rendered file
with python-docx and refuses to ship a CV whose bullets are not readable —
the check that makes this corruption class unshippable even if a future
driver script reintroduces RichText.

`convert_content_map()` still exists as a deprecated strip-only shim for
pre-v1.8.0 driver scripts; it never produces RichText.

## Editorial guidance — what to bold

Bold is signal. In a recruiter's 6-second scan their eye lands on the bold
phrases first. Bold exists to make them land on **proof** — so bold proof,
and nothing else.

**Bold-worthy — only these three things:**

- **Quantified outcomes.** A number tied to a result: `38%`, `cut opt-outs
  22%`, `$2M ARR`, `40+ multinationals`, `11M views`. The number is the proof.
- **Recognizable proper nouns that are themselves credentials.** Named press
  that covered the work (`TechCrunch`), named publications or bodies that
  cited it (`Deloitte`, `Harvard Law Review`, `Freedom House`), a marquee
  client, the institution name in an education bullet.
- **Concrete superlative outcomes** stated plainly — `second-most-used
  feature`, `first dedicated hire`. These are outcomes, not vocabulary.

**Never bold — this is the rule that was wrong before:**

- **JD keyword phrases.** "roadmap", "user research", "stakeholder
  management", "product-led growth" and the like belong in the CV verbatim —
  that is what the diagnosis's keyword list is for, and it matters for ATS.
  But an ATS parses plain text; bolding a keyword does nothing for the machine
  and reads as keyword theater to the human. Keywords earn their *place* in
  the CV. They do not earn *bold*. Bold is for what the candidate did, never
  for the words the job ad happened to use.
- Generic strength claims ("strong communicator", "team player").
- Any adjective with no number behind it.

**Each phrase is bolded at most once in the whole CV.** If a phrase would
qualify for bold in two places — an experience bullet and an education bullet,
say — bold the stronger instance and leave the other plain. A bolded phrase
appearing twice tells the reader the CV was not edited.

**Think per-CV, not per-bullet.** Before rendering, look at every bolded
phrase together. A well-bolded one-page CV has roughly **4 to 8 bolded items
total** — the handful of things the recruiter should carry away. If most
bullets contain a bold phrase, the CV is over-bolded; cut back to genuine
proof. A bullet with no quantified outcome and no credential proper noun has
nothing to bold — leave it plain. **Bolding everything is the same as bolding
nothing.**

**This whole section governs `bullet_style: plain` (the default).** It does
*not* apply to `bullet_style: labeled`. In labeled mode every bullet opens with
a bold capability label by design (`**Pipeline automation:** ...`), so the
"4 to 8 items" ceiling and the "never bold a label" rule are deliberately
suspended for that lead label. The rules still hold for any *other* bold inside
a labeled bullet: bold the label and, if anything, a single quantified outcome,
nothing more. See `SKILL.md` "Bullet style: plain or labeled".

## Contact-line hyperlinks

The personal site and LinkedIn links in contact line 2 must render as **real clickable hyperlinks** in the .docx output — not plain text. The baseline OPUS CV carried these as Word hyperlink relationships; the plugin's render path must preserve or recreate them.

**How to add hyperlinks in docxtpl:** docxtpl does not natively produce hyperlink relationships from plain text. The two reliable approaches:

1. **Embed the hyperlinks in the template.** The OPUS_Template.docx should have the personal site and LinkedIn URLs pre-wired as hyperlink elements in contact line 2, with the display text as placeholders. docxtpl inherits them during render. Preferred — the template does the work once.

2. **Build them in `render_cv.py` via python-docx post-processing.** After `tpl.save()`, reopen the file with `python-docx`, locate the contact-line-2 paragraph, delete the plain-text URL runs, and inject hyperlink relationships. More fragile but works if the template cannot be modified.

**What "plain text URL" means to a recruiter:** a PDF viewer and Word both make clickable links from `https://` strings automatically, but a `.docx` attachment opened in a corporate email environment may not. A real hyperlink relationship ensures the link is clickable in every context.

**Post-render verification:** after rendering, check that `word/_rels/document.xml.rels` contains at least two `Relationship` entries with `Type=".../hyperlink"`. If it contains zero, the links are plain text and must be fixed before shipping. Audit Check 5(e) enforces this automatically — it also guards the `postprocess_cv()` save round-trip, which must preserve the relationships (python-docx keeps unknown parts and rels intact).

## When unpack/edit/repack is allowed

Never as part of the daily build. The daily build is always docxtpl render against a pre-built template.

Unpack/edit/repack is allowed for **structural edits to the template itself**:
- Adding a new placeholder (e.g., a new section variable)
- Fixing a misaligned tab stop
- Changing a color or font globally

These are one-time changes committed back to the template. The new template is then used by every subsequent render.

The build script for the template is at [`../scripts/build_template.py`](../scripts/build_template.py).

## When the template file is locked

If `OPUS_Template.docx` (or whichever template is configured) is open in Word, the render will fail. Do not fall back to a copy or an older version. Stop, notify the user that the file is open, and wait for it to be closed.

This rule extends to all template files. The user's `data/job-log/Job Listings.xlsx` has the same rule (see `job-discovery/references/append-only-safety.md`).

## XML formatting constants

These live in the template and are inherited automatically by docxtpl. They are documented here only so template maintainers know what to preserve when editing the template directly:

- **Font:** Calibri declared explicitly on every `<w:rPr>` as `<w:rFonts w:ascii="Calibri" w:cs="Calibri" w:eastAsia="Calibri" w:hAnsi="Calibri"/>`. Never rely on document-level defaults — Word does not reliably inherit them.
- **Body text size:** `<w:sz w:val="20"/><w:szCs w:val="20"/>` (10pt)
- **Section header size:** `<w:sz w:val="24"/><w:szCs w:val="24"/>` (12pt), bold, color C0392B, bottom border single sz=6 color C0392B space=2
- **Job title row size:** `<w:sz w:val="22"/><w:szCs w:val="22"/>` (11pt), bold, color 1A1A1A, indent left=120, right tab at pos=9626
- **Tab stop:** 9626 DXA throughout
- **Bold tags:** always pair `<w:b/>` with `<w:bCs/>`. Always pair `<w:i/>` with `<w:iCs/>`. Always pair `<w:sz>` with `<w:szCs>`.

These constants are template-specific. Each shipped template (OPUS, modern-tech, academic, etc.) defines its own and may differ.
