# Conventions — naming, paths, folder structure

Shared conventions every skill follows. If a skill's behavior seems to conflict with this file, this file is authoritative for naming and paths.

## Repo root files

| File | Purpose | Committed? |
| --- | --- | --- |
| `config.yaml` | global settings | No (gitignored) |
| `branches.yaml` | career branches | No (gitignored) |
| `regional-headers.yaml` | header variants | No (gitignored) |
| `connectors.yaml` | job board connectors | No (gitignored) |
| `config.example.yaml` etc. (in `shared/`) | annotated templates | Yes |

The `.yaml` files contain personal data and are gitignored. The `.example.yaml` files in `shared/` are the committed templates.

## The data/ folder

Everything the user generates lives under `data/`, which is gitignored in full:

```
data/
├── career.md                       # the candidate's career file
├── Blacklist.txt                    # blacklisted companies
├── Session Notes.txt                # the running anomaly log
├── Interview Story Bank.txt          # STAR+R story library
├── voice/                            # voice reference files
├── job-log/
│   ├── Job Listings.xlsx             # the append-only job log
│   └── Backup/                       # timestamped backups
├── interview-prep/                   # interview prep documents
└── sessions/
    └── [dd.mm]/                      # one folder per working day
        ├── [Country or City]/        # per-geography subfolder
        │   ├── Diagnosis - [Company] - [Job Title].md
        │   ├── CV - [Company] - [Job Title].docx
        │   ├── Cover Letter - [Company] - [Job Title].docx
        │   └── LinkedIn Messages.txt
        └── Requests/                 # output of the Run Request command
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

A "Run Cairo" session puts its documents in `data/sessions/[dd.mm]/Cairo/` but routes job-log rows to the Egypt sheet. See `job-discovery/references/regional-sheet-mapping.md`.

## What is committed vs. what is not

**Committed (the framework):** all `SKILL.md` files, all `references/`, all `scripts/`, all `templates/`, `shared/*.example.yaml`, `shared/conventions.md`, the root `README.md`, `LICENSE`, `.claude/CLAUDE.md`, `examples/showcase/`.

**Never committed (the user's data):** `data/` in full, the live `config.yaml` / `branches.yaml` / `regional-headers.yaml` / `connectors.yaml`. All covered by `.gitignore`.

The dividing line: the framework is public and shareable; the user's career, applications, and config are private and stay on their machine.

## Skill cross-references

Skills reference each other and their own `references/` files by relative path. When editing a skill, keep the "Files referenced" section of its `SKILL.md` in sync with the actual files.
