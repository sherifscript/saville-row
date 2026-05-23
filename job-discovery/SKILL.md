---
name: job-discovery
description: Search job boards (Indeed, Apify-LinkedIn, and adapter-configured platforms), score roles against the candidate, deduplicate, and append to an append-only Excel job log with backup-before-touch safety.
metadata:
  version: 1.1.0
  last_updated: 2026-05-23
---

# job-discovery

## When to activate

- User says "find jobs in [X]", "Run [Country/City]", "search [location]"
- User says "Run Remote", "search remote", "find remote roles", "run the workflow remote"
- `Run Request: [URL]` shortcut (single-role variant)
- `Run Blacklist: add/remove` (blacklist sub-action)

## What it does

1. Reads the candidate's career file and the target geography from the prompt.
2. Searches configured connectors. Indeed and Apify-LinkedIn are primary; others are adapter-configured. See [`references/connector-routing.md`](./references/connector-routing.md).
3. Filters out blacklisted companies. See [`references/deduplication-rules.md`](./references/deduplication-rules.md) (blacklist is loaded at session start).
4. Scores each role against the candidate (Match Score, 0–10).
5. Deduplicates against the existing job log.
6. Appends non-duplicate results to the append-only Excel job log, routed to the correct country sheet. See [`references/regional-sheet-mapping.md`](./references/regional-sheet-mapping.md) and [`references/append-only-safety.md`](./references/append-only-safety.md).

## Connectors

Indeed and Apify-LinkedIn are the primary connectors — the two largest job platforms worldwide. Additional platforms are adapter-configured in `connectors.yaml`:

| Connector | Platform | Notes |
| --- | --- | --- |
| `indeed` | Indeed | Primary. Direct connector. |
| `apify-linkedin` | LinkedIn (via Apify) | Primary. LinkedIn is login-gated; always scrape via Apify, never a browser. |
| `apify-wuzzuf` | Wuzzuf | Egypt-focused adapter. |
| `apify-stepstone` | StepStone | DACH-region adapter. |
| `apify-seek` | Seek | Australia/NZ adapter. |
| `apify-hiringcafe` | HiringCafe | Remote board (`remote_board: true`). `Run Remote` only. |
| `apify-weworkremotely` | We Work Remotely | Remote board. `Run Remote` only. |
| `apify-remoteok` | Remote OK | Remote board. `Run Remote` only. |
| `apify-workingnomads` | Working Nomads | Remote board. `Run Remote` only. |
| `apify-generic` | other | Pick a highly-rated active Apify scraper by judgment. |

The first time job-discovery runs and finds no `connectors.yaml`, it prompts the user to enable connectors and provides the default config. Setup, the Apify account flow, and the plug-and-play pattern for adding any new board are in [`references/connector-setup.md`](./references/connector-setup.md).

## Remote searches

A `Run Remote` search (any of: "Run Remote", "search remote", "find remote roles", "run the workflow remote") is a geography of its own. It invokes every enabled `remote_board` connector plus the primary connectors with their remote filter applied, and routes globally-remote results to the **Remote** sheet. Country-fenced remote roles ("Remote, US only") still route to the country sheet. See [`references/connector-routing.md`](./references/connector-routing.md) and [`references/regional-sheet-mapping.md`](./references/regional-sheet-mapping.md).

## Results table

Present results in a table with these columns: `# | Job Title | Company | Location | Job Type | Match Score | Match Justification | Skill Gap | Salary Range | Apply Link`.

Generate two tables: one for direct-connector (Indeed) results, one for Apify results. See [`references/connector-routing.md`](./references/connector-routing.md) for the partial-results and failure rules.

## Match Score

0–10, alignment with the career file. The score is a quick triage signal; the Match Justification column gives a one-sentence reason. Roles below a configurable threshold (`config.yaml > discovery.min_match_score`) can be filtered out before the CV-tailoring stage.

## The job log — append-only

The job log is `data/job-log/Job Listings.xlsx`. It is a **permanent record**. All writes are additive. Before any access (including read-only), back it up to `data/job-log/Backup/Job Listings — [DD.MM.YY HH.MM].xlsx`.

The full safety rules — never overwrite, never use a backup as a working base, hard-stop on a locked file in interactive sessions, separate-file fallback in unattended sessions — are in [`references/append-only-safety.md`](./references/append-only-safety.md). This is the single most important file in the skill. Read it.

Sheets are named by country, never by city. Routing rules in [`references/regional-sheet-mapping.md`](./references/regional-sheet-mapping.md).

Column order: `Source, Selected, Timestamp, #, Job Title, Company, Location, Job Type, Match Score, Match Justification, Skill Gap, Salary Range, Apply Link`. Selected rows get a green fill (`E2EFDA`). Apply Link is a clickable hyperlink. Implementation in [`scripts/excel_ops.py`](./scripts/excel_ops.py).

## Blacklist

`data/Blacklist.txt`. Loaded at session start. Any company matching an entry is excluded from results, the table, the job log, and all downstream processing. `Run Blacklist: add/remove [Company]` edits the file and confirms — no other workflow steps run.

## Files referenced

- [`references/connector-setup.md`](./references/connector-setup.md) — one-time setup + the plug-and-play pattern for adding boards
- [`references/connector-routing.md`](./references/connector-routing.md)
- [`references/regional-sheet-mapping.md`](./references/regional-sheet-mapping.md)
- [`references/deduplication-rules.md`](./references/deduplication-rules.md)
- [`references/append-only-safety.md`](./references/append-only-safety.md)
- [`scripts/excel_ops.py`](./scripts/excel_ops.py)
- [`scripts/safety_checks.py`](./scripts/safety_checks.py)
