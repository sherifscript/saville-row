---
name: job-search-pipeline
description: Orchestrator for saville-row. Chains discover → diagnose → tailor → cover → audit. Owns the shortcut-command DSL (Run [Country], Run CV only, Run Request, Run Blacklist, Run Interview Prep, Run Story Bank Refresh).
metadata:
  version: 1.10.0
  last_updated: 2026-07-06
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

1. Confirm `config.yaml` exists (check `config/config.yaml` first, then repo root for v1.2.0 backwards compatibility). If not, route to `job-search-setup`.
2. Load `config.yaml`, `branches.yaml`, `regional-headers.yaml`, `connectors.yaml` from `config.yaml > paths.config_dir`.
3. Load `config.yaml > paths` block — all downstream skills read workspace paths from this block instead of hardcoding them.
4. Load `paths.assets_dir`/Blacklist.txt into memory.
5. Read `paths.assets_dir`/Session Notes.txt if it exists — use prior findings (market-specific yield issues, connector flakiness) as context.
6. Maintain `paths.assets_dir`/index.txt: scan `assets_dir` recursively, create the index if it does not exist, and reconcile it against the current contents — add entries for new files, remove entries for deleted ones. For each new file, write a one-line description (read just enough of the file to describe it when the filename isn't self-evident). Don't re-read files that are already indexed. Use the index as the session's reference to `assets_dir`, and only open a file from it when something in the session needs it.

## The full pipeline

For a `Run [Country/City]` command, the pipeline runs start to finish from one prompt — no mid-run pauses, no confirmation checkpoints between stages:

```
1. job-discovery   — search, blacklist filter, score, dedup, append to job log
2. role-diagnosis  — for each top-N selected role, write Diagnosis.md   [GATE]
3. cv-tailor       — per-CV checklist (below), one role at a time
4. cover-letter    — write a cover letter per role (Western markets; multinationals only in Egypt/Gulf)
5. cover-letter    — draft LinkedIn nudges where a recruiter was identified
6. session notes   — log anything unexpected
```

Each stage gates the next: no diagnosis means no CV; a failed audit means the CV is not shipped.

**The cv-tailor stage is a per-CV checklist, not a loop to rush.** Batch
effort decay is a named failure mode (2026-06-14: the tenth CV got a fraction
of the first CV's attention; 2026-06-27: bullet counts silently shrank down
the batch). For EACH selected role, in order:

1. Lint the diagnosis (`lint_diagnosis.py` — `render()` also enforces it).
2. Author the content map fresh from THIS role's diagnosis — every slot from
   its Section angle, at the full substance bar. Define batch constants
   (contact lines, education facts, the Languages string) ONCE in the driver
   and reference them; never re-type them per role (the 2026-06-27 batch
   shipped two different Languages strings from two drivers).
3. Render via `render_cv.render()` (validation → render → postprocess →
   programmatic audit).
4. Ship only on `all_passed`; a failure means fix and re-render, not skip.

**Chunk big batches; never cut them.** Job search is a numbers game — a
10-role day across ~~job board (Indeed) and ~~job board (LinkedIn) is a
legitimate target and the pipeline must deliver it. But quality decay with
batch size is measured, not hypothetical, in BOTH eras of this workflow (the
rich 2026-05-04/06 sessions were 1–2 CVs; the thin 2026-05-18 Cairo and
2026-06-27 Berlin batches were 10 straight in one context). The cap is
therefore per **authoring context**, not per day: no single context authors
more than 5 CVs.

For selections above 5: split into chunks of <= 5 and run each chunk's
diagnose → tailor → audit in a **fresh subagent context** (give it only the
config, the career file, and that chunk's JDs — not the transcript of the
chunks before it). If subagents are unavailable, ship the first 5, write the
remaining roles as a queue into Session Notes, and tell the user to start a
fresh session with `Run Request` for the queue — same-day volume, fresh
attention. No instruction survives contact with the tenth consecutive CV;
a fresh context does.

After the last CV, run the batch sameyness sweep
(`python audit.py --sameyness <session folder>`) and carry any warnings into
the closing summary — duplicated bullets across CVs must be a visible choice,
not silent drift.

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

When any stage fails, do not silently fall back. Stop, log to `paths.assets_dir`/Session Notes.txt, notify the user. The failure-recovery rules per stage are in [`references/failure-recovery.md`](./references/failure-recovery.md).

## Session notes

After any session where something unexpected happened — low yield, language barriers, connector failures, market-specific limitations — append an entry to `paths.assets_dir`/Session Notes.txt and tell the user one line about what was logged. Format in [`references/session-notes.md`](./references/session-notes.md).

## Closing summary (after every full pipeline run)

Before reporting done, run the **deliverables-only sweep**: check each session output folder for anything that isn't `Diagnosis - *.md`, `CV - *.docx`, `Cover Letter - *.docx`, or `LinkedIn Messages.txt` (stray `.py` scripts, content-map dumps, `.md` cover letters from a failed render, etc.) and move it to `.scratch/`. See "Deliverables-only output folders" in `${CLAUDE_PLUGIN_ROOT}/shared/conventions.md`.

After a pipeline run completes, tell the user in plain text:

1. **Session output folder** — the exact path where CVs, cover letters, and diagnoses were saved (e.g., `paths.session_output_dir`/11.06.26/Cairo/).
2. **Job log location** — `paths.job_log_dir`/Job Listings.xlsx, and which sheet was updated.
3. **What was produced** — a one-line count: "5 diagnoses, 5 CVs, 4 cover letters, 1 LinkedIn nudge file."
4. **Any exceptions** — low yield, connector failures, or skipped cover letters (Egypt/Gulf local companies), stated in one sentence each.
5. **Sweep result** — one line: either "Output folders are clean" or what was moved to `.scratch/` and why.
6. **Sameyness sweep** — one line from `python audit.py --sameyness <session folder>`: either "no duplicate bullets across CVs" or each shared bullet named with the CVs that share it.

This summary makes it easy to find the output without hunting through folders, and gives a quick sanity-check on what the pipeline completed.

## Opinionation

The pipeline respects `config.yaml > opinionation`. Default is `warn-once-then-comply`: hard gates (diagnosis-first; voice reference for cover letters; max experience slots; append-only Excel) emit a one-time explanation on the first bypass per session, then comply silently. Track which gates have been warned about in session memory.

`strict` mode (`opinionation: strict` in `config.yaml`) reverts to the original behavior: refuses to proceed when a gate is bypassed.

## Files referenced

- [`references/shortcut-commands.md`](./references/shortcut-commands.md) — the full DSL
- [`references/session-notes.md`](./references/session-notes.md) — the session notes format
- [`references/failure-recovery.md`](./references/failure-recovery.md) — per-stage failure rules