---
name: cv-tailor
description: Render diagnosis-driven, ATS-optimized CVs as .docx via docxtpl. Modular section composition, region-aware headers, inline-bold helper, and a mandatory post-render audit (tailoring coverage, numeric grounding, and named structural failure modes).
metadata:
  version: 1.9.0
  last_updated: 2026-07-14
---

# cv-tailor

The renderer. Takes a Diagnosis.md, a candidate's career file, and a chosen template; produces a tailored CV that an ATS will parse and a recruiter will scan correctly.

## When to activate

- User says "render a CV for [company]", "tailor a CV", "Run CV only"
- A Diagnosis.md exists in the target folder and no CV has been rendered yet
- Pipeline orchestrator invokes after role-diagnosis completes

## Hard gate

Before doing anything, check for `Diagnosis - [Company] - [Job Title].md` in the target folder. If absent, defer to the opinionation policy (warn-once-then-comply by default; strict mode refuses). See `role-diagnosis/SKILL.md`.

The diagnosis must also **pass lint**: `scripts/lint_diagnosis.py` validates its structure (sections present, 6–10 keywords, one `Slot N` angle line per experience slot, each with a real `proof point:` and enough substance). `render_cv.render()` runs the lint automatically and refuses to render from a diagnosis that fails — a thin diagnosis licenses a thin CV, so fix the diagnosis, not the CV.

Exception: `Run CV only` shortcut explicitly skips the diagnosis gate (and the lint). The CV is rendered against broad branch judgment instead. The shortcut skips the diagnosis, not the richness bar: with no JD to tailor against there is no reason to trim, so a CV-only render defaults to full career-file density — every bullet the career file gives each slot, light-edited, and every degree. The 2026-07-14 Werkstudent CV shipped thin (4/3/3, BA dropped) precisely because this path had no stated floor.

## What it does

1. Reads `Diagnosis.md` and extracts the content map (lead credential, keywords, branch, target region).
2. Loads `config.yaml` to determine output formats, template choice, default section toggles, opinionation.
3. Loads `branches.yaml` to get the third-slot company for the chosen branch.
4. Loads `regional-headers.yaml` to get the header for the target region.
5. Builds a `content_map` dict for docxtpl. See [`references/content-map-schema.md`](./references/content-map-schema.md).
6. Resolves the section list for the target region — `cv.sections` minus any `cv.region_section_overrides[region]` set to false (e.g. `EU: summary: false`). See [`references/modular-sections.md`](./references/modular-sections.md).
7. Strips `**markdown bold**` markers via `build_bold_plan()` and records which spans should be bold. Bullets stay **plain strings** — RichText is banned from the render path (the 2026-05-11 / test5 corruption rendered every bullet invisible). See [`references/docxtpl-recipe.md`](./references/docxtpl-recipe.md).
8. Renders via `docxtpl` with `autoescape=True` mandatory and saves the `.docx`. See [`references/docxtpl-recipe.md`](./references/docxtpl-recipe.md).
9. Runs `postprocess_cv()` on the saved file: applies the planned bold as real runs (cloning the template's own run formatting) and removes region-disabled sections. Raises if any bullet cannot be located.
10. Runs the post-render audit. See [`references/post-render-audit.md`](./references/post-render-audit.md). Refuses to ship the CV if any check fails — including Check 5, which re-opens the file with python-docx and fails any CV whose bullets are not actually readable.
11. (Optional) Converts to PDF via LibreOffice if `output_formats` includes `pdf`.

## Critical correctness rules

These exist because each one has shipped a broken CV in the past. Do not skip.

### Tailor every field to the diagnosis (facts vs angle)

Every content field is angled by the diagnosis, not just the lead slot. Build the
`content_map` from the diagnosis's "Section angles" block: each experience slot
(including the lower and branch slots), each degree's bullets, `core_skills`,
`additional`, and any enabled optional section gets phrasing written for *this*
role. The career file is the source of facts (dates, employers, what happened,
every number); the diagnosis decides which fact to surface and how to frame it.

Do not paste career-file phrasing *unchanged* across CVs. The shipped failure mode:
the lead slot was tailored and slots 2..N, education, and `additional` were pasted
from the career file untouched, so they came out byte-for-byte identical across
every CV in a batch (the 2026-06-14 Denmark batch shipped the same Atheneum slot in
all ten CVs). Check 8 of the post-render audit now fails a slot that ships un-angled.
The fix is to **light-edit per role** — reframe the wording and angle for *this*
diagnosis while keeping the bullet's concrete detail — not to rewrite it thin (see
"Write strong bullets" below). The angle re-frames a real fact; it never adds one.
Check 9 enforces that. See
[`references/content-map-schema.md`](./references/content-map-schema.md) "Facts vs angle".

### Positioning drives the frame

The diagnosis's required `## Positioning` section (`Mode: direct | adjacent |
transition` + rationale) decides how every headline element is framed.
`render_cv.render()` reads the mode from the diagnosis automatically.

**Tagline construction per mode:**

- `direct`: open with the role title as the JD states it —
  `[Role Title]  |  [Pillar 1] · [Pillar 2] · [Pillar 3]`.
- `adjacent`: open with the candidate's real functional identity written in
  the JD's vocabulary. Claiming the role *family* is fair when the career
  file substantively supports it ("Data Analyst" for years of pipeline +
  dashboard + validation work), but never claim a seniority or exact title
  the career file cannot back ("Senior X" only when the seniority is real).
- `transition`: build the bridge tagline —
  `[Real capability identity]  |  Transitioning to [Target function]`
  (the benchmark pattern: "Client Engagement & Analytics Specialist |
  Transitioning to Customer Success"). A transition CV never states the
  target title as a held identity; the honest bridge is what makes the rest
  of the translation credible. A recruiter who feels bait-and-switched stops
  reading; one who sees an honest bridge keeps going.

**Summary framing per mode:**

- `direct`: sentence 1 states the matching scope in the JD's terms.
- `adjacent`: sentence 1 names the real background and reads it as the
  target capability ("five years [real work], operating as [JD concept]").
- `transition`: sentence 1 is the explicit bridge — "leveraging a background
  in [real domain] to transition into [target domain]" — then sentences 2–3
  carry the strongest transferable proof. Naming the transition IS the
  strategy.

**Slot latitude:** `transition` mode may re-pick slots beyond the branch
default — see `references/experience-slot-logic.md` "Transition-mode slot
latitude". `direct`/`adjacent` use today's slot rules exactly.

### Write strong bullets (the substance bar)

Tailoring decides *which* fact each bullet surfaces; this decides *how* it is
written. The benchmark is the candidate's own career-file bullet, **lightly
edited** — not a thin rewrite.

**The canonical bullet formula:** `[career-file fact, concrete specifics
kept] + [interpretive clause in the JD's vocabulary]`. The interpretive
clause *appends* the target-domain reading of the fact; it never replaces
the fact. Worked examples (transition-grade):

- "...structuring qualitative inputs into strategic deliverables used by
  enterprise clients, **mirroring an Executive Business Review (EBR)
  motion**"
- "...built an automated Python pipeline that increased publication speed by
  30%, **directly optimizing client Time-to-Value (TTV)**"

The fact half carries the specifics and the numbers; the interpretive half
names the concept this team hires for. One interpretive/ungrounded bullet
per 3-bullet slot is the pattern's natural ceiling (audit Check 10's density
floor allows exactly that).

There are two opposite failure modes, and both ship weak CVs:

- **Un-tailored:** a career-file bullet pasted byte-for-byte across every CV in a
  batch (the 2026-06-14 Denmark batch shipped the same lower slot in all ten).
- **Thin:** a bullet rewritten from scratch into a short, abstract fragment that
  boils off the concrete texture the career file gave it. The 2026-06-25 Cairo
  batch did this — "engineered Python data analysis workflows across
  high-frequency publication cycles" in place of the real, specific fact
  ("monitored COVID-19 incidence and vaccine-trial data across US and Canadian
  regions, used by international institutions, governments, and media").

Every bullet must clear this bar:

1. **Preserve the concrete specifics; reframe only the vocabulary.** The career
   file's named clients, exact numbers, and specific nouns *are* the substance —
   keep them. Reframing turns a fact's wording toward the role; it never dissolves
   the specifics into category-nouns. A real test: if a bullet carries fewer
   concrete nouns/numbers than the career-file bullet it came from, you
   over-compressed — put the detail back.
2. **Light-edit the source bullet; do not rewrite from scratch.** Start from the
   actual career-file bullet for the fact you are surfacing. Keep its structure
   and detail; change its wording to the role's language and fold in the JD's
   terms. Sameyness across a batch is prevented by the *diagnosis choosing
   different facts and angles per role* — never by stripping detail from a shared
   skeleton.
3. **Surface the named proof point, not a generic noun.** When the career file
   names the institutions that cited the work, the clients, the platforms, or a
   number (e.g. 40+ multinationals, 30% faster, $30K, 11M views), the bullet names
   it. The diagnosis's per-slot **proof points** (see
   `role-diagnosis/references/diagnosis-template.md`, "Section angles") tell you
   which one each slot carries.
4. **Lead with ownership and scope.** Open with a verb that carries ownership
   *and* is immediately followed by concrete scope, number, or outcome — "Managed
   analytical workstreams for 40+ multinationals across Technology and Telecom,
   delivering outputs under deadline" is strong even though it opens with
   "Managed." A plain verb is only weak when the bullet behind it is empty: the
   thing to avoid is the *naked duty* bullet ("Managed documentation workflows",
   "Coordinated with teams") that names no scope, number, or result. Do not
   contort around a natural verb to satisfy a blocklist — a grounded "Monitored /
   Conducted / Built" bullet beats an awkward synonym.
5. **Frame in the role's vocabulary (see "Domain translation" below).** Use the
   diagnosis's verbatim JD keywords as the *framing* of the bullet — the same real
   fact read as the thing this team is hiring for — not as tokens sprinkled to
   satisfy ATS.
6. **Shape, length, and count.** Scope + action + outcome with concrete detail,
   roughly 25–40 words — the substance and shape of the career file's own
   bullets. This is a floor on substance, not a hard cap; the diagnosis decides
   how much each slot needs, but a ~12-word fragment is almost always
   under-written. Put the metric where it lands (lead or terminal), not buried
   mid-clause behind filler. **Bullet counts per slot: near-full career-file
   density is the default.** Start from every bullet the career file gives the
   role and light-edit them all; cutting one is an editorial decision that must
   be named in the check_3 verdict, never silent. Hard floors enforced at
   validation: lead slot >= 5 bullets, slot 2 >= 4, slot 3 and later >= 3
   (`cv.bullet_floors` overrides them only when the career file itself has
   fewer — never to trim rich material). When the target region disables the
   summary (`region_section_overrides`, e.g. EU), the lead slot's default
   rises by one more bullet: the page has the room, and density is what
   replaces the summary's proof. The old 3/2 floors let the 2026-07-14
   Werkstudent CV ship at 4/3/3 while the career file offered 6/6/3 — thin by
   permission; the 2026-06-27 batch had already shown the same silent
   shrinkage. Floors make trimming a deliberate choice, not drift.

Everything stays grounded: the proof point and every number must already exist in
the career file (Checks 9, 10). Reframe what is true; invent nothing.

### Domain translation (frame real work in the JD's vocabulary)

The strongest tailoring does not just preserve specifics — it **renames the
candidate's real work in the target role's own vocabulary**, so a recruiter reads
the CV and thinks "even without the exact title, this covers what we need." The
source of that vocabulary is already in hand: the diagnosis's **verbatim JD
keywords** block. Today those keywords are mostly *sprinkled* to satisfy ATS (Check
2 only wants two of them to appear somewhere). Promote them to **framing**:

- **Capability labels (labeled mode), `core_skills` labels, and the `summary`** are
  written in the JD's concepts, not as literal restatements of the underlying work.
  A research-throughput fact reframed for a customer-facing role becomes a label
  like "Time-to-Value" or a skill like "Value Realization"; the same fact for a
  market-intelligence role becomes "Competitive Landscape Mapping." The label or
  skill name does the reframing; the clause underneath carries the grounded detail.
- **Scale the aggressiveness to the diagnosis's Positioning mode, not to a
  vibe.** `direct` stays near the source wording — heavy translation on a true
  match reads as straining. `adjacent` translates the framing: capability
  labels, core-skill labels, the summary, and the lead bullets carry the JD's
  concepts while every clause keeps its career-file specifics. `transition`
  translates aggressively: every experience slot carries at least one
  interpretive clause reading the real work in the target domain's own motions
  and metrics ("mirroring an EBR motion", "optimizing Time-to-Value"), and
  every label is written in the target's vocabulary. The mode is declared in
  the diagnosis's `## Positioning` section; see "Positioning drives the frame".
- **Hard guardrail — vocabulary only.** Translation changes *wording and framing*,
  never the facts. It never invents a title, a number, a tool, or a responsibility,
  and never upgrades a contributor role to owner. A label is a lens on a real fact,
  not a new claim. Checks 9 (numeric grounding) and its honesty companion enforce
  this. This is the line that keeps every CV uploadable without re-checking.

### `autoescape=True` is mandatory

Without it, `&` characters in content_map values are silently stripped from the rendered XML. `Artist & Label` becomes `Artist  Label`. Always pass `autoescape=True` to `tpl.render()`.

### `build_bold_plan()` before render, `postprocess_cv()` after save

Bullets are **plain strings all the way through the render** — never RichText.
(RichText through the template's plain `{{ bullet }}` placeholders embeds
run-XML inside `<w:t>`; Word, python-docx, and ATS parsers read the bullet as
EMPTY. That corruption shipped every labeled-mode CV of the 2026-06-25 and
2026-06-27 batches blank. See `references/docxtpl-recipe.md`.)

The two mandatory helpers around `tpl.render()`:

- `build_bold_plan(cm, mode)` (`scripts/md_to_richtext.py`) — strips every
  `**` marker before render. In the boldable fields (experience bullets,
  degree bullets) it records the bold spans in a plan; in all other fields
  (tagline, summary, core_skills descriptions, additional descriptions) it
  strips outright so a leaked marker cannot render literally.
- `postprocess_cv(path, plan, disabled_sections)` (`scripts/postprocess.py`)
  — after `tpl.save()`, applies the plan as real bold runs by cloning the
  rendered run (template formatting inherited exactly), verifies every
  planned bullet is actually present, and removes region-disabled sections.

`render_cv.render()` runs both; drivers should call it rather than
hand-rolling the pipeline.

### Inline bold scope

Bold rendering is controlled by `config.yaml > cv.inline_bold` (default:
`false`) and `cv.bullet_style` (labeled mode turns bold on for labels).

- **When `inline_bold: false` (default):** all `**` markers are stripped and
  no spans are recorded. Nothing renders bold. This is the default because
  selective bold is increasingly read by recruiters as an AI tell.
- **When `inline_bold: true`:** `**phrase**` markers in the three allowed
  fields become recorded bold spans, applied by the postprocess pass;
  markers in disallowed fields are stripped.

| Field | Bold allowed (when inline_bold: true)? |
| --- | --- |
| `experiences[i].bullets` | Yes |
| `degrees[i].bullets` | Yes |
| `tagline` | No (styled by template) |
| `summary` | No (prose) |
| `core_skills[i].description` | No (label is bold; description plain) |
| `additional[i].description` | No (same pattern) |

### Bullet style: plain or labeled

`config.yaml > cv.bullet_style` (default `plain`) chooses how experience bullets
read. It is independent of the substance bar above — content is written the same
way in both modes; this is only the surface form.

- **`plain` (default):** bullets are prose. Bold follows `inline_bold` (default
  off). This is the conservative default; selective inline bold is increasingly
  read as an AI tell.
- **`labeled`:** each bullet opens with a 2–5 word **bold capability label** in
  the role's vocabulary, then a colon, then the outcome — the Gemini style
  (`**Pipeline automation:** built a Python pipeline that cut publication time
  30%`). The model writes the label as `**Label:**` at the start of each bullet.
  `labeled` turns bold rendering on for bullets regardless of `inline_bold`, so
  the labels render as real bold runs.

Two rules keep `labeled` mode from going thin:

- **The label is domain translation, not a literal restatement.** It names the
  fact in the JD's vocabulary (see "Domain translation") — "Time-to-Value
  Optimization", "Competitive Landscape Mapping" — not a flat paraphrase of the
  clause ("Methodology under deadline", "Structured under pressure" are the weak
  pattern to avoid).
- **The label is an addition, not a budget cut.** The clause after the colon still
  meets the full substance bar above — ~25–40 words, the named proof point, the
  concrete specifics. A label followed by a 6-word fragment is an under-written
  bullet wearing a hat.

The label re-frames a real fact in the JD's language; it never adds a fact. In
`labeled` mode the "what to bold" discipline (4–8 bold items, never bold a
generic label) applies to plain mode only — see `references/docxtpl-recipe.md`.

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

### Education structure — every degree renders

Education is a `degrees` loop (since v1.9.0), ordered most recent first, one
entry per degree in the career file — including an in-progress degree
("Expected [year]") and the undergraduate degree. Each degree carries 1–3
bullets at the same substance bar as experience bullets. Do not drop a degree
to fit a slot count: the old fixed two-slot template is what silently shipped
the 2026-07-14 Werkstudent CV without the BA. Validation requires the
`degrees` key (and rejects the retired `msc_*`/`ba_*` keys); the post-render
audit's Check 12 fails a CV whose rendered degree count falls below
`cv.expected_degree_count` or whose institutions are not visible in the
document.

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

The post-render audit at [`references/post-render-audit.md`](./references/post-render-audit.md). Refuses to ship the CV if any check fails.

**The two editorial checks must be explicitly recorded.** After
`run_full_audit()` returns, record a one-line verdict for each:
`result.record_editorial('check_1_lead_slots', ok, note)` (lead slots serve
the diagnosed problem with their proof points surfaced) and
`result.record_editorial('check_3_recruiter_fit', ok, note)` (richness vs
the career file, domain translation, no semantic inflation). The audit seeds
both as failed, so `all_passed` stays False until they are recorded — a CV
can no longer pass by omission. Recording the verdicts is authoring work,
not a pause; it never stops a batch run.

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

A user can disable any toggleable section globally in `config.yaml`, or per
region via `cv.region_section_overrides` (e.g. `EU: summary: false` — common
for European CVs). A diagnosis can also override per-application — e.g., a
publications-heavy academic role can turn `publications: on` for that CV only.

Mechanism today: partial composition is inactive (no template ships real
partials yet), so the full template renders whole and `postprocess_cv()`
**removes** disabled sections from the saved file. Toggling ON a section the
full template lacks (publications/certifications/volunteering on OPUS) has no
render path yet — surface that content as an `additional` item. See
[`references/modular-sections.md`](./references/modular-sections.md).

### Student mode

`cv.student_mode: true` moves EDUCATION above PROFESSIONAL EXPERIENCE — the
layout early-career/student CVs lead with. Default false. A diagnosis can
override it per application with a `Student mode: on` (or `off`) line, the
same way `Mode:` declares the positioning mode. The move happens in
`postprocess_cv()`; no template change.

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
- [`references/post-render-audit.md`](./references/post-render-audit.md) — the audit checks (programmatic 2,4,5,6,7,8,9,10,11,12 + editorial 1,3)
- [`references/modular-sections.md`](./references/modular-sections.md) — section composition
- [`references/regional-headers.md`](./references/regional-headers.md) — the regional header pattern
- [`references/experience-slot-logic.md`](./references/experience-slot-logic.md) — slot 1/2/3 rules
- [`references/content-map-schema.md`](./references/content-map-schema.md) — every key in the content_map
- [`scripts/render_cv.py`](./scripts/render_cv.py) — the main entry point
- [`scripts/md_to_richtext.py`](./scripts/md_to_richtext.py) — marker stripping + the bold plan (`build_bold_plan`)
- [`scripts/postprocess.py`](./scripts/postprocess.py) — post-render bold application + section removal
- [`scripts/audit.py`](./scripts/audit.py) — the audit checks as code (+ `--sameyness` batch sweep)
- [`scripts/lint_diagnosis.py`](./scripts/lint_diagnosis.py) — the diagnosis structure lint (the render gate's mechanical backstop)
- [`scripts/section_composer.py`](./scripts/section_composer.py) — section partial stitching (inactive until real partials ship)
- [`scripts/build_template.py`](./scripts/build_template.py) — one-time template-from-CV converter
