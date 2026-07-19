---
name: cv-tailor
description: Render diagnosis-driven, ATS-optimized CVs as .docx via docxtpl. Modular section composition, region-aware headers, inline-bold helper, and a mandatory post-render audit (tailoring coverage, numeric grounding, and named structural failure modes).
metadata:
  version: 2.0.0
  last_updated: 2026-07-18
---

# cv-tailor

Takes a Diagnosis.md, the candidate's career file, and a template; produces a
tailored CV that an ATS parses and a recruiter reads as rich, specific, and true.

**The one rule that outranks every other rule in this file: the career file is
the CV.** Tailoring means choosing which of its facts to surface and reframing
their vocabulary for this role. It never means compressing, abstracting, or
rewriting them thinner. When any instruction below seems to pull toward
shorter or more generic writing, you have misread it.

## When to activate

- User says "render a CV for [company]", "tailor a CV", "Run CV only"
- A Diagnosis.md exists in the target folder and no CV has been rendered yet
- Pipeline orchestrator invokes after role-diagnosis completes

## Hard gate

`Diagnosis - [Company] - [Job Title].md` must exist in the target folder and
pass `scripts/lint_diagnosis.py` (structure, 6–10 keywords, per-slot angles
with proof points, a `Mode:` line). `render_cv.render()` lints automatically
and refuses a failing diagnosis — fix the diagnosis, not the CV. If the
diagnosis is absent, defer to the opinionation policy
(warn-once-then-comply by default; strict refuses).

Exception: `Run CV only` skips the diagnosis, not the richness bar. With no JD
there is no reason to trim: full career-file density, every degree.

## Author the content map (the writing — this is the whole job)

Everything else in this skill is mechanics. The CV's quality is decided here.

### Start from the career file, bullet by bullet

For each experience slot, put every career-file bullet for that role on the
table. Light-edit each one toward the diagnosis; keep its structure, its
numbers, its named clients and tools. Cutting a bullet is a deliberate
editorial decision — never silent drift. Validation enforces floors both ways:
**count** (lead slot ≥ 5, slot 2 ≥ 4, slot 3+ ≥ 3; `cv.bullet_floors`
overrides only when the career file itself has fewer) and **length** (no
bullet under 12 clause-words; section average ≥ 20 — career-file bullets run
25–40 words and the tailored bullet stays in that range).

### The bullet formula, with worked examples

`[career-file fact, concrete specifics kept] + [interpretive clause in the
JD's vocabulary]`. The interpretive clause appends the target-domain reading;
it never replaces the fact.

Career file says:
> Diagnosed a manual data entry bottleneck and built an automated Python
> pipeline that increased report publication speed by 30%.

For a **data analyst** JD (keywords: data quality, automation):
> Diagnosed a manual data entry bottleneck and built an automated Python
> pipeline that increased report publication speed by 30%, improving data
> quality and consistency across high-frequency publication cycles.

For a **customer success** JD (transition mode; keyword: time-to-value):
> Diagnosed a manual workflow bottleneck and built an automated Python
> pipeline that cut report delivery from weeks to days, directly optimizing
> client Time-to-Value (TTV).

The **banned** version — what a thin CV looks like:
> Automated data workflows, improving efficiency by 30%.

Same fact, same number, and it will still be rejected: the diagnosis, the
bottleneck, the tool, and the publication-cycle context all boiled off. If a
bullet carries fewer concrete nouns and numbers than the career-file bullet it
came from, put the detail back.

### The bar, in five lines

1. **Specifics survive.** Named clients, institutions, tools, and every number
   from the source bullet stay in the tailored bullet.
2. **Surface the named proof point.** Each slot's diagnosis angle assigns one
   (e.g. "40+ multinationals", "cited by Deloitte", "30% faster"); the audit
   checks it appears in that slot's bullets.
3. **Lead with ownership and scope.** A plain verb ("Built", "Managed",
   "Monitored") is fine when concrete scope follows it; the failure is the
   naked-duty bullet ("Coordinated with teams") that names no scope or result.
4. **Keywords are framing, not confetti.** Use the diagnosis's verbatim JD
   keywords as the vocabulary the fact is read through — every slot carries at
   least one, experience bullets carry at least two overall.
5. **Truth is absolute.** Every number traces to the career file (Check 9).
   Reframe wording; never invent a metric, tool, title, or upgrade
   "supported" to "led". A recruiter who feels bait-and-switched stops
   reading. This is what keeps every CV uploadable without re-checking.

Both historical failure modes are banned equally: the **un-tailored** CV
(career-file bullets pasted byte-identical across a batch — the 2026-06-14
Denmark batch) and the **thin** CV (bullets rewritten into short abstractions —
the 2026-06-25 Cairo batch, the v1.6-era "category-noun" CVs). The first is
caught by Check 8 and the sameyness sweep; the second by the length floors.

### Positioning mode drives the frame

The diagnosis's `## Positioning` section declares `Mode: direct | adjacent |
transition`; `render_cv.render()` reads it automatically.

- **direct** — tagline opens with the JD's role title
  (`[Role Title]  |  [Pillar 1] · [Pillar 2] · [Pillar 3]`); summary states
  the matching scope in the JD's terms; translation stays near the source
  wording (heavy translation on a true match reads as straining).
- **adjacent** — tagline opens with the candidate's real functional identity
  in the JD's vocabulary (claim the role *family* when the career file backs
  it; never a seniority it can't). Summary sentence 1 names the real
  background and reads it as the target capability. Labels, skills, and lead
  bullets carry the JD's concepts; clauses keep career-file specifics.
- **transition** — tagline is the honest bridge
  (`[Real capability identity]  |  Transitioning to [Target function]`);
  summary sentence 1 names the transition explicitly; every slot carries at
  least one interpretive clause reading the real work in the target domain's
  motions ("mirroring an EBR motion"). One interpretive/ungrounded bullet per
  3-bullet slot is the ceiling (Check 10's density floor allows exactly
  that). Transition mode may also re-pick slots beyond the branch default —
  see `references/experience-slot-logic.md`.

### Every section gets angled

Not just experience: `core_skills` labels, degree bullets, `additional`, the
summary (3 sentences), and the tagline are all written from the diagnosis's
"Section angles" block for *this* role. The career file supplies facts; the
diagnosis picks which fact each field surfaces and how it's framed. See
`references/content-map-schema.md` for every key.

## Render mechanics (non-negotiable; each rule has shipped a broken CV)

1. Build the `content_map`, then call `render_cv.render()` — it validates,
   renders, postprocesses, and audits in one call. Do not hand-roll.
2. **`autoescape=True` always** — without it `&` silently vanishes from the
   rendered XML.
3. **Bullets are plain strings end-to-end; RichText is banned.**
   `build_bold_plan()` strips `**` markers pre-render and records spans;
   `postprocess_cv()` applies them as real bold runs post-save and removes
   region-disabled sections. RichText through a plain `{{ bullet }}`
   placeholder renders EMPTY in Word/ATS (the 2026-05-11 corruption).
4. **The template file must not be open in Word** during render — docxtpl
   silently writes a corrupt file.
5. The post-render audit (`references/post-render-audit.md`) runs inside
   `render()`; a CV that fails any check is not shipped. Check 5 re-opens the
   file with python-docx — an empty bullet paragraph IS a render failure.
6. Optional PDF via LibreOffice when `output_formats` includes `pdf`.

Pre-render validation (`validate_content_map`) programmatically enforces:
required keys, `degrees` list (retired `msc_*`/`ba_*` keys rejected), slot
count = `cv.max_experience_slots` (+1 only in transition), integer `end_year`
per role, bullet count + length floors, labeled-mode lead-ins, no employer
name in the summary, no target-company name in any bullet, no em dashes
anywhere (see `${CLAUDE_PLUGIN_ROOT}/shared/conventions.md`), regional
contact lines.

## Structure rules

**Experience slots** (full spec: `references/experience-slot-logic.md`):
Slot 1 = most recent primary-employer role; Slot 2 = the adjacent same-employer
role — mandatory when the career file has one (`cv.continuous_employer_block:
true` default; dropping it creates a visible employment gap); Slot 3 =
branch-driven from `branches.yaml`. Strict reverse chronology by `end_year`
(9999 = Present); same-employer roles stay contiguous. Check 7 enforces this.

**Education**: a `degrees` loop, most recent first, one entry per career-file
degree including in-progress and undergraduate. Each degree carries 1–3
bullets at the same substance bar. Check 12 fails a dropped degree.

**Regional headers**: contact lines and work-authorization item per
`regional-headers.yaml` — see `references/regional-headers.md`.

## Bullet style and bold

`cv.bullet_style` (default `plain`): prose bullets; bold follows
`cv.inline_bold` (default false — selective bold reads as an AI tell).
`labeled`: each bullet opens `**Label:**` where the label is 2–5 words of
domain translation ("Time-to-Value Optimization", not "Methodology under
deadline"), then a clause meeting the full substance bar — the label is an
addition, never a budget cut, and the length floors count only the clause.
Bold markers are allowed in experience/degree bullets only; everywhere else
they are stripped.

## Sections, student mode, output

Sections are composable via `config.yaml > cv.sections` +
`cv.region_section_overrides` (e.g. `EU: summary: false`; a summary-off region
raises the lead slot's bullet default by one — density replaces the summary's
proof). Disabled sections are removed by `postprocess_cv()`; toggling ON a
section the template lacks surfaces as an `additional` item instead. See
`references/modular-sections.md`.

`cv.student_mode: true` (or a `Student mode: on` line in the diagnosis) moves
EDUCATION above EXPERIENCE in postprocess.

Output paths:

```
paths.session_output_dir/[session-date]/[Country or City]/CV - [Company] - [Job Title].docx
paths.session_output_dir/[session-date]/[Branch] CV.docx        # Run CV only
```

Driver scripts and content-map dumps go in `.scratch/`, never in the session
folder.

## Files referenced

- [`references/content-map-schema.md`](./references/content-map-schema.md) — every content_map key
- [`references/experience-slot-logic.md`](./references/experience-slot-logic.md) — slot rules, transition latitude
- [`references/post-render-audit.md`](./references/post-render-audit.md) — the audit checks
- [`references/docxtpl-recipe.md`](./references/docxtpl-recipe.md) — autoescape, bold plan, named failure modes
- [`references/modular-sections.md`](./references/modular-sections.md) — section composition
- [`references/regional-headers.md`](./references/regional-headers.md) — regional header pattern
- [`scripts/render_cv.py`](./scripts/render_cv.py) — entry point (validate → render → postprocess → audit)
- [`scripts/lint_diagnosis.py`](./scripts/lint_diagnosis.py) — diagnosis gate
- [`scripts/audit.py`](./scripts/audit.py) — audit checks as code (+ `--sameyness` sweep)
