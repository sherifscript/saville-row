---
name: job-search-pipeline
description: Orchestrator for saville-row. Chains discover → diagnose → tailor → cover → audit. Owns the shortcut-command DSL (Run [Country], Run CV only, Run Request, Run Blacklist, Run Interview Prep, Run Story Bank Refresh).
metadata:
  version: 1.2.0
  last_updated: 2026-05-24
---

# job-search-pipeline

The orchestrator. It does not do the work — it sequences the other skills and owns the shortcut-command grammar.

## Skill router

Match user intent to the correct skill before doing anything else:

| User says... | Skill |
| --- | --- |
| "set up saville-row" / "first run" / "I just cloned this" | `job-search-setup` |
| "find jobs in [X]" / "Run [Country]" / "search [city]" | `job-discovery` → `job-search-pipeline` |
| "Run Remote" / "search remote" / "find remote roles" / "run the workflow remote" | `job-search-pipeline` (`Run Remote` — routes to the Remote sheet) |
| "tailor a CV for [company]" / "render a CV" / "Run CV only" | `role-diagnosis` (gate) → `cv-tailor` |
| "diagnose this role" / "what is this team actually hiring to fix" | `role-diagnosis` |
| "write a cover letter for [company]" | `cover-letter` (after diagnosis) |
| "prep me for the [company] interview" / "Run Interview Prep" | `interview-prep` |
| "refresh the story bank" / "Run Story Bank Refresh" | `story-bank` |
| "blacklist [company]" / "Run Blacklist: add/remove" | `job-discovery` (blacklist sub-action) |
| Any `Run [shortcut]` command | `job-search-pipeline` (it owns the DSL) |

## When to activate

- Any `Run [...]` shortcut command
- User describes a multi-stage job-search task ("find me jobs in Berlin and tailor CVs for the best ones")

## Session start

At the start of every session in a saville-row repo:

1. Confirm `config.yaml` exists. If not, route to `job-search-setup`.
2. Load `config.yaml`, `branches.yaml`, `regional-headers.yaml`, `connectors.yaml`.
3. Load `data/Blacklist.txt` into memory.
4. Read `data/Session Notes.txt` if it exists — use prior findings (market-specific yield issues, connector flakiness) as context.

## The full pipeline

For a `Run [Country/City]` command, the pipeline runs start to finish from one prompt — no mid-run pauses, no confirmation checkpoints between stages:

```
1. job-discovery   — search, blacklist filter, score, dedup, append to job log
2. role-diagnosis  — for each top-N selected role, write Diagnosis.md   [GATE]
3. cv-tailor       — render a CV per diagnosis, run the post-render audit
4. cover-letter    — write a cover letter per role (Western markets; multinationals only in Egypt/Gulf)
5. cover-letter    — draft LinkedIn nudges where a recruiter was identified
6. session notes   — log anything unexpected
```

Each stage gates the next: no diagnosis means no CV; a failed audit means the CV is not shipped.

**No mid-run confirmation pauses.** Do not stop between stages to ask whether to proceed, whether to generate all CVs, or whether the selection looks right. Present the results table and the selected roles, then proceed immediately into diagnosis, CV rendering, and cover letters. The only interactive stop in a full-pipeline run is the branch-selection menu when a `Run [Country]` prompt names no branch — and only that.

If a configurable safety valve is needed, it lives in config.yaml as `pipeline.confirm_before_render` (default false). Without that key explicitly set to true, the pipeline runs uninterrupted.

## Shortcut command DSL

The full grammar is in [`references/shortcut-commands.md`](./references/shortcut-commands.md). Summary:

| Command | Effect |
| --- | --- |
| `Run [Country/City]` | Full pipeline for that geography |
| `Run [Country] \| [Branch]` | Full pipeline, scoped to a branch |
| `Run Remote` / `Run Remote \| [Branch]` | Full pipeline for location-independent roles; remote boards + remote-filtered primaries; rows route to the Remote sheet |
| `Run CV only: [Branch or General]` | Skip discovery and diagnosis; render one untailored CV |
| `Run Request: [URL], [URL], ...` | Per-URL: diagnose + tailor + cover for specific postings |
| `Run Blacklist: add/remove [Company], ...` | Edit the blacklist; no other steps |
| `Run Interview Prep: [Company], [Job Title]` | Build an interview prep document |
| `Run Story Bank Refresh` | Extract new STAR+R stories from the career file |

## Selection rule

From each results table, select the top 5 roles by Match Score (up to 10 total across both tables, fewer if a connector returned fewer). Aim for at least 10 results per table before applying the top-5 cut; retry once with alternative keywords if the first pass is thin — use broader synonyms of the primary job title (e.g., if "Product Manager" yields thin results, retry with "Product Lead" or "Program Manager") and the branch's keyword seeds from `branches.yaml`. A low yield after retry is acceptable — proceed with whatever was found.

Selected roles get `✓` in the job log's Selected column and a green row fill.

## Failure recovery

When any stage fails, do not silently fall back. Stop, log to `data/Session Notes.txt`, notify the user. The failure-recovery rules per stage are in [`references/failure-recovery.md`](./references/failure-recovery.md).

## Session notes

After any session where something unexpected happened — low yield, language barriers, connector failures, market-specific limitations — append an entry to `data/Session Notes.txt` and tell the user one line about what was logged. Format in [`references/session-notes.md`](./references/session-notes.md).

## Closing summary (after every full pipeline run)

After a pipeline run completes, tell the user in plain text:

1. **Session output folder** — the exact path where CVs, cover letters, and diagnoses were saved (e.g., `data/sessions/25.05/Cairo/`).
2. **Job log location** — `data/job-log/Job Listings.xlsx`, and which sheet was updated.
3. **What was produced** — a one-line count: "5 diagnoses, 5 CVs, 4 cover letters, 1 LinkedIn nudge file."
4. **Any exceptions** — low yield, connector failures, or skipped cover letters (Egypt/Gulf local companies), stated in one sentence each.

This summary makes it easy to find the output without hunting through folders, and gives a quick sanity-check on what the pipeline completed.

## Opinionation

The pipeline respects `config.yaml > opinionation`. Default is `warn-once-then-comply`: hard gates (diagnosis-first; voice reference for cover letters; max experience slots; append-only Excel) emit a one-time explanation on the first bypass per session, then comply silently. Track which gates have been warned about in session memory.

`strict` mode (`opinionation: strict` in `config.yaml`) reverts to the original behavior: refuses to proceed when a gate is bypassed.

## Files referenced

- [`references/shortcut-commands.md`](./references/shortcut-commands.md) — the full DSL
- [`references/session-notes.md`](./references/session-notes.md) — the session notes format
- [`references/failure-recovery.md`](./references/failure-recovery.md) — per-stage failure rules