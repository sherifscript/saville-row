# Changelog

All notable changes to saville-row are recorded here. Format loosely
follows [Keep a Changelog](https://keepachangelog.com/).

## Unreleased

### Fixed

- **Contact hyperlink targets leaked the template author** (privacy). The OPUS
  template was built from a finished personal CV, so its two contact
  hyperlinks kept that person's site and LinkedIn as relationship targets in
  `word/_rels/document.xml.rels`. docxtpl rewrites the visible `<w:t>` and
  never the relationship, so every CV rendered from the template *displayed*
  the candidate's URLs and *clicked through* to the template author's —
  invisible on screen, read by ATS parsers that follow relationships instead
  of display text. Both gates that should have caught it were counting rather
  than checking: audit check 5(e) passed on ">= 2 hyperlink rels" and
  `test_hyperlinks_survive_roundtrip` asserted the same count, so the leak
  satisfied both. `postprocess_cv` now binds each contact link by `r:id` and
  sets its target from the content map (never from the old target); check 5(e)
  joins `document.xml` to `document.xml.rels` by `r:id` and compares each label
  against its own target; `personal_site` and `linkedin_url` became required
  content-map keys. Unsupported URL schemes are rejected.

### Added

- `tests/test_contact_links.py` — two-candidate regression asserting
  *positively* that each rendered CV's targets are its own, plus
  cross-contamination absence. Absence alone passes trivially when a renderer
  leaves both candidates on neutral placeholders.
- `tests/test_tracked_docx_privacy.py` — fails the build if a tracked `.docx`
  points anywhere but an RFC 2606 reserved domain, or if a private workspace
  directory becomes tracked. Deliberately identifier-free: a denylist of the
  removed values would write them permanently into a public repository in
  order to remove them from it, and would only ever catch the known leak.

### Changed

- `templates/OPUS/full_template.docx` and the showcase CV neutralized to
  reserved example domains, labels and targets moved together.
- Test fixtures no longer use the maintainer's real employers and
  affiliations. The incident post-mortems in `skills/cv-tailor/references/`
  keep their named specifics — per CLAUDE.md those worked examples are the
  instructional mechanism, and abstracting them degrades what works.
- `SECURITY.md` rewritten for the current directory layout; now separates Git
  privacy from model-provider, connector, and employer disclosure, and
  documents how to inspect a `.docx` for hidden hyperlink targets.
- `settings.json` no longer pre-authorizes `pip` or blanket `python`
  execution.

## v2.0.0 — 2026-07-19

The lean-core rebuild. Diagnosis of the recurring "thin CV" failure showed
three compounding causes that v1.7.0 and v1.9.0 had patched around without
closing: (1) ~4,000 lines of instruction text diluted the authoring task the
skills exist for; (2) every richness rule was prose or a bullet-COUNT floor —
nothing programmatic ever checked bullet LENGTH, so a 12-word fragment
carrying one number passed all 13 checks (the committed showcase CV itself
shipped this way: one bullet per role, every quantified win dropped); (3) the
model-graded editorial verdicts were rubber-stamped in every batch, giving
false assurance. This release deletes process and adds one mechanical gate.

### Added

- **Bullet length floors** in `validate_content_map` (the one new gate):
  every experience bullet's substance clause >= 12 words (label lead-in
  excluded in labeled mode) and the section-wide average >= 20. Calibrated on
  the strongest shipped CVs (2026-05-06 Mastercard ~30 avg, 2026-05-18 Tabby
  ~22 avg) so rich CVs pass with margin and category-noun rewrites (~16 avg)
  fail. Fails at authoring time, before render.
- **Batch chunking** in the pipeline: no single authoring context writes
  more than 5 CVs. Quality decay with batch size is measured across BOTH the
  plugin era and the pre-plugin workflow (rich sessions were 1–2 CVs; the
  thin Cairo/Berlin batches were 10 straight in one context). Volume is
  preserved — job search is a numbers game — by running each chunk of <= 5
  in a fresh subagent context (or a fresh session via a Session Notes
  queue), never by cutting the day's roles.
- **Student-search rules** in job-discovery: localized query terms per
  market ("Werkstudent" is a German-market institution — Belgium needs
  jobstudent / job étudiant, NL werkstudent/bijbaan, US/UK student
  assistant/placement) and a full-time filter — a student search that
  returns unmarked full-time roles discards them and reports the count
  (the 2026-07 Belgium run logged full-time positions from a
  Werkstudent-style query).

### Changed

- **cv-tailor SKILL.md rewritten around the writing, not the process**
  (437 → ~215 lines). Centerpiece: "the career file is the CV" — tailoring is
  light-editing + vocabulary reframing, never compression — with worked
  career-file-bullet → tailored-bullet examples including the banned thin
  version. The 25–40-word figure is now framed purely as the career file's
  own range backed by hard floors, not a target to write down to.
- **Diagnosis depth bar raised** (`diagnosis-template.md`): sections 1/2/4
  now specify 4–6 / 2–4 / 2–4 sentences with named specifics and benchmark
  examples from the strongest shipped diagnoses. The old "2–3 sentences …
  1 sentence … intentional brevity" spec mandated exactly the terseness that
  thinned every downstream artifact (the 2026-06-27 batch compressed
  diagnosis sections to 1–2 sentences and the CVs thinned with them).
- **Showcase regenerated at the real standard.** The committed example CV now
  carries all 8 career-file bullets (3/2/3) with every metric intact and the
  five bolded proof phrases its README always claimed; its diagnosis is
  rewritten to the current spec (Section angles, Positioning, lint-clean).

### Removed

- **Reference bloat**: `docxtpl-recipe.md` compressed 200 → ~100 lines (the
  scripts enforce its rules mechanically; the doc keeps rule + trigger +
  pointer); `modular-sections.md` 150 → ~65 (it mostly documented the
  INACTIVE partials system — now states the operative postprocess-removal
  mechanism first and demotes partials to a future note).
- **The editorial-verdict machinery** (`record_editorial`, seeded checks 1
  and 3, `require_editorial`): `run_full_audit()`'s verdict is now final.
  The judgment content moved to where it operates — the authoring bar in
  SKILL.md (read at writing time) and the programmatic length floors.

## v1.10.0 — 2026-07-18

### Added

- **Student mode.** `cv.student_mode: true` moves EDUCATION above
  PROFESSIONAL EXPERIENCE in the postprocess pass — the layout
  early-career/student CVs lead with. Default false. A diagnosis can
  override per application with a `Student mode: on/off` line (parsed like
  the positioning mode). Offered by the `job-search-setup` wizard when the
  career file reads early-career. Check 5 and the bold plan follow the
  moved section order.
- **Release automation.** `.github/workflows/release.yml` tags `vX.Y.Z`
  and creates a GitHub Release (notes sliced from this file) whenever the
  `plugin.json` version changes on `main`; idempotent when the tag already
  exists. CI now runs `bump_version.py --check` so version drift across
  `plugin.json` / `marketplace.json` / SKILL.md frontmatters fails the
  build.

### Changed

- **README slimmed.** Popularity badges and the star-history section are
  gone — metrics return when there's real traction to show.

## v1.9.0 — 2026-07-14

CV richness. The 2026-07-14 Werkstudent CV (test6) shipped thin — 10
experience bullets against a career file offering 6/6/3, the Hamburg MSc
compressed to one bullet, and the BA silently dropped — while passing every
gate. Near-full career-file density is now the contract, and education can
no longer lose a degree structurally.

### Changed

- **Bullet floors raised to 5/4/3** (lead / slot 2 / slot 3+), up from 3/2.
  `cv.bullet_floors` in config overrides them, but only for career files
  that genuinely have fewer bullets — trimming rich material now requires a
  deliberate config change (`render_cv.validate_content_map`).
- **Education is a `degrees` loop.** The OPUS template's fixed
  `msc_*`/`ba_*` two-slot education block forced a three-degree candidate to
  drop one; the template now loops over a `degrees` list (name, date,
  institution, location, 1–3 bullets each) exactly like experiences.
  Validation rejects the retired `msc_*`/`ba_*` keys with a migration hint.
- **`Run CV only` keeps the richness bar.** The shortcut skips the diagnosis
  and lint, not density: with no JD to tailor against, the CV defaults to
  every career-file bullet per slot, light-edited, and every degree.
- **Summary-off regions compensate with density.** When
  `region_section_overrides` disables the summary (EU/Denmark), the lead
  slot's default bullet count rises by one.

### Added

- **Audit Check 12 (education completeness):** fails a CV whose `degrees`
  count falls below `cv.expected_degree_count` (new config key,
  recorded by job-search-setup from the career file) or whose institutions
  are not visible in the rendered document. The batch sameyness sweep is
  renumbered to 13 in the docs.
- Tests: default floors, `cv.bullet_floors` override, retired-key rejection,
  degree field validation, Check 12 behavior, and a three-degree end-to-end
  render through the new template loop.

## v1.8.0 — 2026-07-06

Render integrity, audit teeth, first-class positioning. The 2026-06-27
Berlin batch exposed the worst defect in the plugin's history: **every
labeled-mode CV since v1.6.0 shipped with an invisible experience section.**
`convert_content_map()` turned bullets into docxtpl RichText, the OPUS
template's placeholders are plain `{{ bullet }}`, and docxtpl embedded the
run-XML inside `<w:t>` — invalid OOXML that Word, python-docx, and ATS
parsers read as EMPTY paragraphs. The audit passed anyway (its bold check
regex-counted `<w:b/>`, which the template's own bold headers always
satisfy), and the "empty `.text` is normal for RichText, read raw XML"
doctrine enshrined the corruption as a parser quirk. This release pins the
long-unpinned 2026-05-11 incident to that exact trigger and rebuilds the
render, the audit, and the positioning system.

### Fixed

- **RichText corruption (the blank-CV bug).** Bullets are now plain strings
  through the whole render; bold is applied after save by
  `scripts/postprocess.py`, which clones the rendered run so the template's
  formatting (Calibri, sz 20, paired `w:b`/`w:bCs`) is inherited exactly.
  RichText is banned from the render path (`build_bold_plan` raises on one).
  The corruption class is structurally impossible now.
- **Audit Check 5 superseded** by `check_5_rendered_integrity`: re-opens the
  rendered file with python-docx and fails any CV whose authored bullets are
  not readable, with real bold-run inspection and a hyperlink-rels guard.
- **`cv.region_section_overrides` finally works** (e.g. `EU: summary:
  false`): `effective_sections()` resolves it, the postprocess pass removes
  the section. The composer no longer crashes on the stub partials dir.
- **Doctrine reversed** in CLAUDE.md / docxtpl-recipe.md: an empty
  python-docx bullet paragraph IS a render failure.
- **cover-letter signature contradiction** — objections-and-close.md now
  matches SKILL.md: plain text, no bold on any part of the name.

### Added

- **Required `## Positioning` in every diagnosis** (`Mode: direct | adjacent
  | transition` + rationale; replaces the optional Honest assessment). The
  mode drives the tagline construction (transition gets an honest bridge
  tagline, never an unheld title), summary framing, domain-translation
  aggressiveness, transition-mode slot latitude (branch override and/or one
  extra slot via an explicit `Slot plan:`), and the cover letter's objection
  paragraph (sourced from the diagnosis, never re-derived).
- **Canonical bullet formula** in cv-tailor: `[career-file fact, specifics
  kept] + [interpretive clause in the JD's vocabulary]`, with worked
  examples ("mirroring an Executive Business Review (EBR) motion").
- **`scripts/lint_diagnosis.py`**, wired into `render()`: sections present,
  6–10 keywords, one `Slot N` angle line per slot with a real `proof point:`
  and enough substance, Positioning mode declared. A thin diagnosis refuses
  to render instead of licensing a thin CV.
- **Audit Check 11 (`check_11_proof_points`)**: each slot's diagnosis proof
  point must surface in its rendered bullets (parsed from Diagnosis.md).
- **Batch sameyness sweep** (`python audit.py --sameyness <dir>`, warn-only):
  duplicate bullets/clauses across a session's CVs, reported in the
  pipeline's closing summary.
- **Editorial verdicts are required**: `run_full_audit` seeds checks 1 and 3
  as failed; `all_passed` stays False until the model records both via
  `result.record_editorial(...)`. No more pass-by-omission.
- **Per-CV tailor checklist** in job-search-pipeline (batch effort decay is
  a named failure mode); bullet-count floors (lead slot ≥ 3, others ≥ 2).

### Changed

- Check 2 scoped to experience bullets (per its own spec). Check 7: missing
  `end_year` now fails (the skip-dodge is closed); ongoing side engagements
  are marked `concurrent: true`. Check 9 broadened to `$` amounts and K/M/B
  magnitudes. Check 10 upgraded to a proof-density floor per slot using a
  career-file whitelist minus a sector/language stoplist.

### Breaking

- `experiences[i].end_year` (int, 9999 = Present) is **required** in every
  content map — add it to driver scripts.
- `run_full_audit(...).all_passed` is False until both editorial verdicts
  are recorded — call `result.record_editorial(...)` twice after each audit.
- New diagnoses must carry `## Positioning` with a `Mode:` line; a pre-1.8
  diagnosis fails the lint until one line is added (e.g.
  `**Mode: adjacent** — did the work, not the title; risk: tool mismatch.`).
- `convert_content_map()` is a deprecated strip-only shim: it never produces
  RichText (that was the corruption); `inline_bold=True` is ignored. Use
  `build_bold_plan()` + `postprocess_cv()` — or simply `render_cv.render()`.

## v1.7.0 — 2026-06-27

Rich tailoring. v1.6.0 added a "bullet strength" bar to fix generic, un-tailored
bullets — but it over-corrected toward *punchy* and produced *thin*. Side-by-side
against the original-workflow benchmark CV and an external Gemini CV (same JD), the
plugin's bullets were ~16 words of category-nouns where the benchmarks were ~25–40
words that kept the concrete texture (named clients, exact numbers, "COVID-19
incidence and vaccine-trial data across US and Canadian regions"). Two spec defects
caused it: the substance bar told the model to compress and banned the natural verbs
that carry rich bullets, and the Check 10 blocklist failed grounded phrasing the
strong CVs legitimately use. This release rebalances toward rich + concrete + domain
translation, with factuality kept as a hard guardrail.

### Changed

- **Substance bar rewritten** (`cv-tailor/SKILL.md` "Write strong bullets"). Now
  leads with *preserve the concrete specifics* and *light-edit the source bullet
  (don't rewrite thin)*, adds a ~25–40-word substance floor, and drops the
  blanket ban on natural lead verbs (managed / monitored / conducted) — only the
  *naked duty* bullet with no scope or outcome is weak. Reconciles with the
  "don't paste verbatim" rule so it reads as *light-edit per role*, not *rewrite
  from scratch*.
- **Check 10 is grounding-aware** (`cv-tailor/scripts/audit.py`). A
  `WEAK_GENERIC_PHRASES` hit now fails a bullet only when that bullet carries no
  concrete proof of its own (no number, no named entity) via `_has_concrete_proof`.
  This stops the v1.6.0 ban from rejecting rich, grounded bullets that happen to
  contain a phrase like "client-ready" — including bullets that use a verbatim JD
  keyword.
- **Audit Check 3 given teeth** (`cv-tailor/references/post-render-audit.md`). The
  "feels like a generic version of my career?" editorial read now explicitly judges
  richness/substance and domain translation, not just keyword fit.

### Added

- **Domain translation** (`cv-tailor/SKILL.md` new section + `role-diagnosis`
  Section angles). Capability labels, `core_skills` labels, and the summary are
  framed in the JD's own vocabulary (sourced from the diagnosis's verbatim
  keywords), translating real work into the concepts the role hires for — the
  reproducible mechanism behind the strongest tailoring. Aggressiveness scales with
  the diagnosis's stretch read; a hard guardrail keeps translation vocabulary-only,
  never inventing a fact (Check 9 still enforces grounding).
- **Diagnosis Section angles carry concrete detail.** The per-slot angle must name
  the specific career-file texture to preserve and the JD-keyword framing for
  labels, so cv-tailor has rich source to light-edit instead of a thin abstraction.

## v1.6.1 — 2026-06-26

### Added

- **Setup wizard exposes `cv.bullet_style`.** `job-search-setup` Step 6b-ii now
  asks plain vs labeled (with a side-by-side example), so the v1.6.0 labeled-bullet
  style is a real setup choice instead of a hand-edit. Closes the gap found in the
  2026-06-25 test4 run, where the toggle existed in config and cv-tailor but the
  wizard only asked about `inline_bold`.

## v1.6.0 — 2026-06-25

Bullet strength. The 2026-06-25 Cairo batch passed every audit check and still
shipped weak, generic bullets ("tracked positioning for enterprise
decision-makers") while named proof points (cited by Deloitte, Harvard Law
Review, W3C) sat unused in the career file. Tailoring decided *which* fact a
bullet surfaced; nothing governed *how* it was written, so quality was
luck-of-the-draw. Benchmarked against an external Gemini CV that surfaced the
concrete credentials, the gap was clear.

### Added

- **Bullet-writing standard.** `cv-tailor/SKILL.md` "Write strong bullets" makes
  the substance bar explicit: surface the named proof point (not a generic noun),
  lead with the outcome/ownership verb, place the metric where it lands, reframe
  into JD vocabulary.
- **Per-slot proof points in the diagnosis.** `role-diagnosis` "Section angles"
  now names, for each experience slot, the specific credential/institution/number
  the bullets must surface, so cv-tailor has concrete material instead of
  defaulting to generic nouns.
- **Audit Check 10 (bullet strength).** Fails any bullet that hides behind a
  high-precision blocklist of generic fillers ("enterprise decision-makers",
  "global process owners", etc.). Reads RichText or plain-string bullets, so it
  works in both bullet styles. The editorial checks 1 and 3 were strengthened to
  demand a named proof point per lead slot.
- **`cv.bullet_style: plain | labeled`.** Opt-in Gemini-style bold capability
  lead-ins (`**Pipeline automation:** ...`); `plain` remains the default.

### Fixed

- **`render_cv.py` never rendered bold.** It called `convert_content_map()`
  without the config flag, so `inline_bold: true` (and now `labeled`) produced no
  bold runs and would fail audit Check 5. It now passes the resolved flag. The
  string-based audit checks (8, 10) read bullet text via a `_bullet_text` helper
  so they no longer break on RichText bullets in bold mode.

## v1.5.0 — 2026-06-25

Whole-CV tailoring. The 2026-06-14 Denmark trial showed tailoring effort decaying
down the page: the lead experience slot was rewritten per role, but the lower and
branch slots, education, and additional sections shipped as identical career-file
boilerplate across every CV (the Atheneum slot was byte-for-byte identical in all
ten CVs). Root cause: the diagnosis only ever angled the headline, and the audit
only checked the lead.

### Added

- **Diagnosis "Section angles" block.** `role-diagnosis` now emits one line per
  rendered part (every experience slot, each degree, core_skills, additional, and
  any enabled optional section), naming a real career-file fact and how it connects
  to the diagnosed problem. Keyword coverage is now whole-document, not top-weighted.
- **Audit Check 8 (tailoring coverage).** Fails any experience slot whose bullets
  carry zero diagnosed keywords, catching un-angled boilerplate before it ships.
- **Audit Check 9 (numeric grounding).** Fails any percentage or count in the
  rendered CV whose digits are absent from the career file, catching invented or
  inflated metrics. Paired with an editorial honesty companion for semantic
  inflation ("supported" must not become "led"). `render_cv.render()` gains a
  `career_file_path` argument to enable it.
- **Regression tests** for Checks 8 and 9 (`tests/test_tailoring_audit.py`).

### Changed

- **`cv-tailor` facts-vs-angle rule.** The career file is the source of facts; the
  diagnosis is the source of the angle of *every* field, not just the lead slot.
  Copying career-file phrasing verbatim into bullets is now explicitly forbidden.

## v1.4.1 — 2026-06-11

### Changed

- **Marketplace entry enriched.** The `.claude-plugin/marketplace.json`
  plugin entry now carries the same metadata as `plugin.json` —
  `version`, `author`, `homepage`, `repository`, `license`, `keywords` —
  plus `category` and `tags` for richer Directory listings.

## v1.4.0 — 2026-06-11

Workflow parity fixes from the first end-to-end trial with friends, plus the
remaining Life Assets-style workspace conveniences.

### Changed

- **Session output moved to `applications/`.** `paths.session_output_dir`
  defaults to `applications` (was `.`), so dated session folders no longer
  land at the repo root next to `config/` and `assets/`.
- **Session date folders now include the year and are configurable.** New
  `paths.session_date_format` (default `dd.mm.yy`, e.g. `11.06.26`; or
  `mm.dd.yy` for US-style dates, e.g. `06.11.26`). `shared/scripts/path_utils.py`
  gains `format_session_date()`. Every `[dd.mm]` reference across the skills
  is now `[session-date]`.
- **Cover letters: `.docx` render is now mandatory.** `cover-letter/SKILL.md`
  adds a "Render to .docx (mandatory)" step — draft as plain text, render via
  `text_to_docx.py`, ship the `.docx` only. A failed render is a failed stage,
  not a license to leave a `.md`/`.txt` letter in the session folder.
  `interview-prep/SKILL.md` gets the same explicit render step.

### Added

- **Scratch-script hygiene.** New "Deliverables-only output folders"
  convention in `shared/conventions.md`: session folders hold only
  `Diagnosis - *.md`, `CV - *.docx`, `Cover Letter - *.docx`, and
  `LinkedIn Messages.txt`. Render driver scripts and content-map dumps go to
  `.scratch/` (gitignored) and are cleaned up after the audit passes.
- **Deliverables-only sweep.** `job-search-pipeline`'s closing summary now
  checks session folders for stray non-deliverables and moves them to
  `.scratch/` before reporting done.
- **Assets index at session start.** `job-search-pipeline` now maintains
  `paths.assets_dir`/index.txt — scans `assets_dir`, reconciles additions and
  removals, and gives each file a one-line description, mirroring the
  original workflow's Life Assets index.
- **README Troubleshooting section** — covers the stale-marketplace-cache
  symptom (plugin shows as raw "Saville Row" or with empty skills) and the
  fix (`claude plugin marketplace update sherifscript` then reinstall).
- **`.gitignore` hardening** — `data/` (legacy v1.2.0 layout containing the
  PII workflow reference), `applications/`, `.scratch/`, and year-bearing
  `dd.mm.yy/` session folders are now ignored.
- **`tests/test_path_utils.py`** — covers default paths, user-config
  overrides, and `format_session_date()` for both formats.

## v1.3.0 — 2026-05-26

Workspace layout restructure and QA pass from the first end-to-end trial run.

### Changed

- **Workspace layout.** Config files (`config.yaml`, `branches.yaml`,
  `regional-headers.yaml`, `connectors.yaml`) now live under `config/`.
  Career file, voice references, `Blacklist.txt`, story bank, and session notes
  live under `assets/`. Job log lives under `job-log/`. Dated session output
  lands at the repo root (`[dd.mm]/`) instead of `data/sessions/[dd.mm]/`.
  The old `data/` folder is no longer used.
- **cv-tailor — seven-check post-render audit.** Two new checks added:
  check 6 scans all runs for em-dashes (banned from all employer-facing output);
  check 7 validates chronological order and contiguous-block structure. The
  contiguous-block rule is now hard (in SKILL.md directly) rather than soft
  ("if applicable").
- **cv-tailor — inline-bold toggle.** Bold runs are opt-in via `cv.inline_bold`
  (default false). Setup step 6b presents before/after examples so the user
  makes an informed choice before enabling.
- **job-search-setup — third-slot prompting.** Step 2 now prompts for
  `third_slot_company` per branch, closing the schema mismatch that allowed
  an unintended company into experience slot 3.
- **cover-letter — signature.** Last-name bolding removed from the signature.
- **Em-dash ban.** Documented in `shared/conventions.md` as the cross-skill
  rule for all employer-facing output (CV, cover letter, LinkedIn, interview
  prep). Referenced in interview-prep SKILL.md.

### Added

- **`config/` directory** — default location for all root-level YAML config
  files.
- **`assets/` directory** — default location for career file, voice references,
  `Blacklist.txt`, story bank, and session notes.
- **`job-log/` directory** — default location for the Excel job log.
- **`paths:` config block** in `config.yaml` — makes workspace layout a single
  config decision; every skill reads from it instead of hardcoding paths.
- **`shared/scripts/path_utils.py`** — single source of truth for resolving
  workspace paths; includes v1.2.0 backwards-compatible config file lookup.
- **`CHEATSHEET.md`** — one-page command reference at repo root.
- **job-discovery** — creates an empty `Blacklist.txt` on first run if absent.
- **role-diagnosis** — "Honest assessment" added as an optional section to
  the diagnosis template and `Diagnosis.md.tmpl`.
- **job-search-pipeline** — explicit no-mid-run-pause rule; closing summary
  always states session folder, job-log path, and output count.
- **Setup UX** — Step 0 preamble for new users; Step 8 (opinionation) rewritten
  with a concrete gate example; Step 9 presents the full 11-command catalog
  and Apify forward note.

### Migration from v1.2.0

1. `mkdir config assets job-log`
2. Move `config.yaml`, `branches.yaml`, `regional-headers.yaml`,
   `connectors.yaml` → `config/`
3. Move `data/career.md`, `data/voice/`, `data/Blacklist.txt`,
   `data/Interview Story Bank.txt`, `data/Session Notes.txt` → `assets/`
4. Move `data/job-log/` contents → `job-log/`
5. Existing `data/sessions/[dd.mm]/` folders can stay or be moved to the repo root.
6. Delete the now-empty `data/` folder if desired.
7. Add a `paths:` block to `config/config.yaml` only if you want non-default
   locations — the defaults match the new layout exactly.

---

## v1.2.0 — 2026-05-24

Plugin conversion.

### Changed

- **Plugin layout.** Skills moved from repo root to `skills/` directory.
  `.claude-plugin/plugin.json` manifest added; the repo is now installable
  via `claude plugin install saville-row@sherifscript`.
- **Router folded into pipeline.** The routing table and opinionation policy
  from `.claude/CLAUDE.md` are now self-contained inside
  `job-search-pipeline/SKILL.md`. The `.claude/` directory is removed.
- **Permissions migrated.** Python/pip permissions moved from
  `.claude/settings.json` to the plugin-level `settings.json`.
- **Connector placeholders.** Third-party platform names (Indeed, LinkedIn,
  Apify, Wuzzuf, StepStone, Seek, etc.) wrapped in `~~job board` and
  `~~web scraper` placeholders in body text. Frontmatter trigger descriptions
  are unchanged.

### Added

- `.claude-plugin/marketplace.json` — single-plugin marketplace so
  `claude plugin marketplace add sherifscript/saville-row` works.
- `CONNECTORS.md` — documents the `~~` placeholder system and lists all
  connector categories with their default options.
- `settings.json` (plugin root) — default Python/pip execution permissions.

### Removed

- `.claude/CLAUDE.md` — content folded into `job-search-pipeline/SKILL.md`.
- `.claude/settings.json` — replaced by plugin-level `settings.json`.

---

## v1.1.0 — 2026-05-23

Quality pass on the cover-letter and CV skills, plus first-class support for
remote roles.

### Changed

- **cv-tailor — tighter bold rule.** Bold is now reserved for quantified
  outcomes, credential proper nouns, and concrete superlative outcomes only.
  JD keyword phrases ("roadmap", "user research", "stakeholder management")
  are no longer bold-worthy — keywords earn their place in the CV for ATS,
  not bold. Added: each phrase is bolded at most once per CV, and a target of
  roughly 4–8 bolded items total. Updated `docxtpl-recipe.md`,
  `content-map-schema.md`, and post-render audit check 3.
- **cover-letter — recruitment-standard rewrite.** The quality standard
  expanded from five to eight requirements: a tight opener (25 words or
  fewer), the strongest proof as plain description, explicit handling of the
  candidacy's obvious objection (career change, industry switch, seniority
  jump, gap, short tenures), one genuine line of motivation, and a warm close
  with a concrete next step. New reference `objections-and-close.md`; the
  opener rule no longer permits a run-on; `voice-anchor.md` now distinguishes
  genuine warmth from flattery.
- **Showcase regenerated.** Jordan Park's CV re-rendered with the disciplined
  bolding (five bold phrases, all proof); the cover letter rewritten to the
  new eight-point standard (250 words, B2C-to-B2B objection named and
  resolved).

### Added

- **Remote-role support.** New `Run Remote` / `Run Remote | [Branch]`
  shortcut command; natural-language variants ("search remote", "run the
  workflow remote") route to it. Globally-remote roles route to a new
  **Remote** sheet — the one allowed non-country sheet; country-fenced remote
  roles still route to the country sheet.
- **Remote job boards as connectors.** HiringCafe, We Work Remotely, Remote
  OK, and Working Nomads ship as default `remote_board` connectors. A new
  `remote_board: true` connector field marks a board as remote-only; it fires
  for `Run Remote` searches and is silent for geo searches.

## v1.0.0 — initial release

First public release. Eight skills covering the full job-search pipeline.

### Skills

- **job-search-setup** — first-run wizard. Reads the career file, auto-detects
  c