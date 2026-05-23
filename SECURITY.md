# Security and privacy

`saville-row` is a public framework, but the data you run it on — your
career history, contact details, application history — is private. This file
explains how the framework keeps the two separate, and what you are
responsible for.

## Your data never gets committed

Everything personal lives under `data/` and a handful of root config files.
All of it is listed in `.gitignore`:

- `data/` — your career file, voice references, job log, session notes,
  generated CVs and cover letters, interview prep docs.
- `config.yaml`, `branches.yaml`, `regional-headers.yaml`, `connectors.yaml`
  — your filled-in configuration, which contains your name, contact details,
  and (in `connectors.yaml`) connector settings.

Because these are gitignored, a normal `git add` / `git commit` / `git push`
will not include them. The framework's code is public; your data stays on
your machine.

## What you are responsible for

- **Do not force-add ignored files.** `git add -f config.yaml` overrides the
  ignore rule. Do not do it.
- **Check before your first push.** Run `git status` and confirm nothing
  under `data/` and none of the four config files are staged. If you see
  them, stop and fix `.gitignore` before pushing.
- **The showcase is the exception.** `examples/showcase/` is committed on
  purpose — it is a fictional candidate (Jordan Park) with invented data,
  and the `.gitignore` has explicit negation rules to keep it in. Never put
  your own data in `examples/showcase/`.
- **Your `connectors.yaml` may hold a ~~web scraper token reference (e.g. an Apify token).** Keep API
  tokens out of the committed repo. The framework reads tokens from your
  connector/MCP configuration, not from a committed file, but double-check.

## Reporting a security issue

If you find a security problem in the framework code itself — for example a
script that writes outside `data/`, or a path that could leak personal data
into a commit — open an issue describing the problem. Do not include any
real personal data in the issue.

## The append-only job log

`data/job-log/Job Listings.xlsx` is treated as an irreplaceable record. The
framework backs it up before every access and never overwrites it. This is a
data-safety measure, not a security one, but it lives in the same spirit:
your accumulated history is protected by default. See
`skills/job-discovery/references/append-only-safety.md`.
