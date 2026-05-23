# Changelog

All notable changes to saville-row are recorded here. Format loosely
follows [Keep a Changelog](https://keepachangelog.com/).

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