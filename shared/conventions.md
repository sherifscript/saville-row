# Conventions — naming, paths, folder structure

Shared conventions every skill follows. If a skill's behavior seems to conflict with this file, this file is authoritative for naming and paths.

## Config files

| File | Location | Committed? |
| --- | --- | --- |
| `config.yaml` | `config/` | No (gitignored) |
| `branches.yaml` | `config/` | No (gitignored) |
| `regional-headers.yaml` | `config/` | No (gitignored) |
| `connectors.yaml` | `config/` | No (gitignored) |
| `config.example.yaml` etc. (in `shared/`) | `shared/` | Yes |

The live `.yaml` files contain personal data and live in `config/`, which is gitignored. The `.example.yaml` files in `shared/` are the committed templates.

## Workspace layout

Everything the user generates lives in four gitignored directories at the repo root. Paths are configurable via `config.yaml > paths`; defaults are shown below:

```
config/                              # config.yaml, branches.yaml, regional-headers.yaml, connectors.yaml
assets/                              # career.md, voice/, Blacklist.txt, Interview Story Bank.txt, Session Notes.txt
job-log/                             # Job Listings.xlsx and Backup/
[dd.mm]/                             # dated session output at repo root
    [Country or City]/               # per-geography subfolder
        Diagnosis - [Company] - [Job Title].md
        CV - [Company] - [Job Title].docx
        Cover Letter - [Company] - [Job Title].docx
        LinkedIn Messages.txt
    Requests/                        # output of the Run Request command
interview-prep/                      # interview prep documents
```

## File naming

| Artifact | Name pattern |
| --- | --- |
| Diagnosis | `Diagnosis - [Company] - [Job Title].md` |
| Tailored CV | `CV - [Company] - [Job Title].docx` |
| Untailored CV (Run CV only) | `[Branch] CV.docx` or `General CV.docx` |
| Cover letter | `Cover Letter - [Company] - [Job Title].docx` |
| Interview prep | `[Company] - [Job Title] - Interview Prep.docx` |
| Job log backup | `Job Listings — [DD.MM.YY HH.MM].xlsx` |

Date folders use `dd.mm`. Timestamps in the job log use `H:MM AM/PM DD.MM.YY`. Backup timestamps use `DD.MM.YY HH.MM`.

## Sheets vs. folders

- **Job log sheets** are always country-named (Egypt, Denmark, ...). Never city-named.
- **Session folders** use whatever the prompt specified (Cairo, Copenhagen, ...).

A "Run Cairo" session puts its documents in `[dd.mm]/Cairo/` at the repo root (or wherever `paths.session_output_dir` points) but routes job-log rows to the Egypt sheet. See `skills/job-discovery/references/regional-sheet-mapping.md`.

## Em dashes in employer-facing output

**Em dashes (—) never appear in any candidate-facing or employer-facing output.** This covers CVs, cover letters, LinkedIn nudges, and interview-prep documents.

Use commas, periods, or parentheses instead, or restructure the sentence. Em dashes are a recognized AI-generation tell and a screening risk. This rule applies regardless of how naturally an em dash might read in the context.

Scope:
- ✅ Ban: CVs (tagline, summary, bullets, additional), cover letters, LinkedIn nudges, interview prep docs
- ✅ Allowed: internal artifacts — diagnosis files, session notes, SKILL.md documentation

Every skill that generates employer-facing output must enforce this rule and check it before shipping. The post-render audit (`cv-tailor/scripts/audit.py`) includes a programmatic em-dash check. The cover-letter skill already bans em dashes in its own rules. `interview-prep` and the LinkedIn nudge section of `cover-letter` must apply the same rule.

## What is committed vs. what is not

**Committed (the framework):** all `SKILL.md` files under `skills/`, all `references/`, all `scripts/`, all `templates/`, `shared/*.example.yaml`, `shared/conventions.md`, the root `README.md`, `LICENSE`, `.claude-plugin/`, `settings.json`, `CONNECTORS.md`, `examples/showcase/`.

**Never committed (the user's data):** `config/`, `assets/`, `job-log/`, `interview-prep/`, and dated `[dd.mm]/` session folders. All covered by `.gitignore`.

The dividing line: the framework is public and shareable; the user's career, applications, and config are private and stay on their machine.

## Skill cross-references

Skills live under `skills/` and reference each other by relative path (`../sibling-skill/references/file.md`). Assets outside `skills/` (shared scripts, CV templates) are referenced via `${CLAUDE_PLUGIN_ROOT}/shared/...` or `${CLAUDE_PLUGIN_ROOT}/templates/...`. When editing a skill, keep the "Files referenced" section of its `SKILL.md` in sync with the actual files.
