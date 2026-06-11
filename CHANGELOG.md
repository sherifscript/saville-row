# Changelog

All notable changes to saville-row are recorded here. Format loosely
follows [Keep a Changelog](https://keepachangelog.com/).

## v1.4.1 — 2026-06-11

### Changed

- **Plugin renamed `saville-row` → `saville-row`.** Some app surfaces
  (e.g. the Claude Desktop plugin directory) title-case the raw `name` field
  instead of honoring `displayName`, so the old `name` was rendering as
  "SavilleRow" in those UIs. The new `name` falls back to "SavilleRow".
  The GitHub repo slug is unchanged (`sherifscript/saville-row`); only the
  plugin/install name changed.
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
  symptom (plugin shows as raw "SavilleRow" or with empty skills) and the
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