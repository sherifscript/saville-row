# Security and privacy

`saville-row` is a public framework, but the data you run it on — your career
history, contact details, application history — is private. This file explains
what protects that data, what does not, and what you are responsible for.

## Where your data lives

All personal data lives in gitignored directories. Paths are configurable via
`config.yaml > paths`; these are the defaults:

- `config/` — `config.yaml`, `branches.yaml`, `regional-headers.yaml`,
  `connectors.yaml`. Contains your name, contact details, and connector
  settings.
- `assets/` — career file, voice references, blacklist, story bank, session
  notes.
- `job-log/` — `Job Listings.xlsx` and its backups.
- `applications/` — generated CVs, cover letters, and diagnoses, by date and
  country.
- `interview-prep/` — generated interview prep documents.
- `.scratch/` — ad-hoc helper scripts and temp files.

The committed `shared/*.example.yaml` files are templates. They contain
fictional values only.

## What Git protects, and what it does not

Being gitignored stops an ordinary `git add` / `commit` / `push` from
including these files. That is the whole of the guarantee. It does **not**
protect you against:

- `git add -f`, which overrides the ignore rule.
- Anything already committed in the past. Removing a file from the working
  tree does not remove it from history; that needs a history rewrite.
- Copies you make outside the ignored directories.
- Generated documents you deliberately send to employers.

`tests/test_tracked_docx_privacy.py` fails the build if any private directory
becomes tracked, or if a committed `.docx` points at a non-example domain.

## Where your data actually goes

"Stays on your machine" is true of Git and false of everything else. Four
distinct boundaries, and only the first is local:

1. **Local disk.** Config, career file, job log, and generated documents are
   written and read locally.
2. **The model provider.** Every skill works by sending your career data,
   diagnoses, and drafts to Claude. This is inherent to the framework — it is
   an LLM plugin — and is governed by your Anthropic account's terms, not by
   this repository.
3. **Connectors you enable.** `job-discovery` sends derived search inputs
   (titles, locations, filters) to whichever job board or scraper you have
   configured. It does not send your CV or career file. Review
   `CONNECTORS.md` and each connector's own privacy terms before enabling it.
4. **Employers and ATS vendors.** Everything in a submitted CV or cover letter
   is disclosed on purpose, to a third party whose retention you do not
   control.

## Hidden data in generated documents

A `.docx` is a ZIP archive, and some of it is not visible on screen. Two
places have historically carried data the author did not intend:

- **Hyperlink targets.** A hyperlink's display text and its destination live
  in different parts of the file (`word/document.xml` versus
  `word/_rels/document.xml.rels`). They can disagree, and many ATS parsers
  read the destination. `cv-tailor` now binds every contact link's target to
  its own visible text at render time, and audit check 5 refuses to ship a CV
  where they diverge.
- **Document properties.** `docProps/core.xml` carries author and
  last-modified-by fields.

To inspect any `.docx` before submitting it:

```
unzip -p "CV.docx" word/_rels/document.xml.rels | grep 'Target='
unzip -p "CV.docx" docProps/core.xml
```

Every target should match the contact detail printed beside it.

## What you are responsible for

- **Do not force-add ignored files.** `git add -f config/config.yaml`
  overrides the ignore rule.
- **Check before your first push.** `git status` should show nothing from the
  directories listed above.
- **Keep API tokens out of the repo.** The framework reads connector tokens
  from your MCP/connector configuration, never from a committed file.
- **The showcase is the deliberate exception.** `examples/showcase/` is
  committed on purpose — a fictional candidate (Jordan Park) using RFC 2606
  reserved domains. Never put your own data there.

## Reporting a security issue

If you find a problem in the framework itself — a script that writes outside
the configured paths, a path that could leak personal data into a commit, or
personal data embedded in a distributed artifact — open an issue describing
the problem. Do not include real personal data in the issue.

## The append-only job log

`job-log/Job Listings.xlsx` is treated as an irreplaceable record. The
framework backs it up before every access and never overwrites it. A
data-safety measure rather than a security one, but the same spirit: your
accumulated history is protected by default. See
`skills/job-discovery/references/append-only-safety.md`.
