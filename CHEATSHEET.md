# saville-row — command cheatsheet

A one-page reference for all shortcut commands. Full docs in `skills/job-search-pipeline/references/shortcut-commands.md`.

---

## Full pipeline

| Command | What it does |
|---|---|
| `Run [Country/City]` | Full search → diagnose → tailor → cover for that geography |
| `Run [Country] \| [Branch]` | Full pipeline, scoped to one career branch |
| `Run Remote` | Search remote boards; results route to the Remote sheet |
| `Run Remote \| [Branch]` | Remote pipeline, scoped to a branch |

**Flow:** discover → select top 5 per connector → diagnose each → render CV → write cover letter → draft LinkedIn nudges → session notes. Runs start to finish with no pauses.

---

## Single document

| Command | What it does |
|---|---|
| `Run CV only: General` | One untailored CV; broad judgment; no discovery |
| `Run CV only: [Branch]` | One untailored CV; branch-scoped; no discovery |
| `Run Request: [URL], [URL], ...` | Diagnose + tailor + cover for specific job posting URLs |

---

## Utilities

| Command | What it does |
|---|---|
| `Run Blacklist: add [Company], ...` | Add companies to the skip list |
| `Run Blacklist: remove [Company], ...` | Remove companies from the skip list |
| `Run Interview Prep: [Company], [Job Title]` | Interview prep doc: role snapshot, story map, hard questions, your ask |
| `Run Story Bank Refresh` | Extract new STAR+R stories from your career file |

---

## Key locations

| What | Where |
|---|---|
| Session output (CVs, cover letters, diagnoses) | `[dd.mm]/[Country or City]/` (repo root, configurable via `paths.session_output_dir`) |
| Job log | `job-log/Job Listings.xlsx` |
| Blacklist | `assets/Blacklist.txt` |
| Story bank | `assets/Interview Story Bank.txt` |
| Career file | `assets/career.md` |
| Config | `config/config.yaml` (gitignored) |
| Branches | `config/branches.yaml` (gitignored) |
| Regional headers | `config/regional-headers.yaml` (gitignored) |

---

## Pipeline gates

| Gate | Rule |
|---|---|
| Diagnosis before CV | No `Diagnosis - [Company] - [Job Title].md` → no CV (except `Run CV only`) |
| Audit before ship | CV fails any of the 7 audit checks → not shipped |
| Voice ref for cover letter | No voice reference → warn-once-then-comply (or refuse in strict mode) |
| Append-only job log | Never overwrite; back up before every access |
