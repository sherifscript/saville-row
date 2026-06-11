---
name: job-search-setup
description: First-run wizard for saville-row. Reads the candidate's career file, proposes branches, prompts for voice references and regions, writes config.yaml. Run once per repo before any other skill.
metadata:
  version: 1.4.1
  last_updated: 2026-06-11
---

# job-search-setup

## When to activate

- User says "set up saville-row", "first run", "I just cloned this", "configure saville-row"
- User invokes any other skill and `config.yaml` does not exist (checked at `config/config.yaml`, then repo root for v1.2.0 compatibility) → suggest setup first

## What it does

Walks the candidate through a single conversation that produces three files in `paths.config_dir`/ (default: `config/`):
- `config.yaml` — global settings (opinionation, output formats, voice reference paths, template choice, paths block)
- `branches.yaml` — career branches auto-detected from the career file, confirmed by the user
- `regional-headers.yaml` — header variants for each target region

After setup completes, all other skills become operable.

## The conversation, in order

### Step 0 — Preamble (say this before any question)

Before asking anything, tell the user what saville-row is and what it does:

> *"saville-row is a job-search pipeline that runs five stages from a single prompt: it searches job boards for you, scores each role against your career, writes a one-page role diagnosis before any CV is rendered, produces a tailored CV for each selected role, and writes a voice-anchored cover letter. The pipeline runs start to finish from one command — `Run [Country]` — and produces a complete session output folder.*
>
> *Setup takes about 5 minutes. I'll ask you a few questions about your career, which regions you're targeting, and a few preferences — then I'll write the config files and you're ready to search."*

This gives new users a frame before they answer questions whose purpose they would otherwise have to guess at.

### Step 1 — Locate the career file

Ask the user for the path to their career history file. Accept any format: `.txt`, `.md`, `.docx`, `.pdf`. Read it once. It will be the single source of truth for all factual content downstream.

If the user does not have one yet, point them at [`references/career-file-guide.md`](./references/career-file-guide.md) and offer to help them build it: *"I can interview you for 15 minutes and draft a starter career file. Want to do that now, or come back when you have one?"* The guide's short version: open a blank document and brain-dump everything you have ever done — the framework selects per application, so the file should be longer and rawer than any CV.

### Step 2 — Auto-detect branches

Read the career file and propose 2–4 candidate **branches** — distinct career arcs the candidate might emphasize for different roles. For each, write one sentence on what anchors it. Example output:

```
I see three possible branches in your career:

1. Research & Analytics — anchored on 5 years at Acme Research covering
   B2C consumer apps; the Forrester and TechCrunch citations; the MSc thesis
   on user behavior modeling.

2. Product Management — anchored on 3 years as Senior PM at Beta Inc
   shipping the onboarding redesign that lifted activation 18%; the
   cross-functional product launches.

3. Commercial Strategy — anchored on the partnership deals at Gamma Co
   ($2M ARR contribution); the GTM playbook you wrote.

Confirm, edit, add, or remove?
```

User accepts/edits. For each confirmed branch, ask one follow-up question:

> *"For [Branch name] roles, which past employer should appear as the third experience slot on the CV — the role that best proves this branch's credentials alongside your primary employer? This maps directly to `third_slot_company` in branches.yaml."*

Propose the most likely answer from the career file (the role that overlaps most with the branch's keyword seeds) and let the user confirm or override. This field is **required** in branches.yaml. Without it, cv-tailor cannot resolve Slot 3 and will free-hand it, producing inconsistent CVs.

Write the final list to `branches.yaml`. See [`references/branches-detection.md`](./references/branches-detection.md) for the detection heuristic.

### Step 3 — Regions

Ask which countries or regions the user targets. For each, draft a regional header:

```
Region: [name]
Location line: [city, country]
Phone: [number]
Work auth line: [if applicable — varies by region]
Citizenship line: [if applicable]
Trailing fields: [LinkedIn, personal site, etc.]
```

Smart defaults for US / UK / EU / Gulf / Egypt are shipped in `${CLAUDE_PLUGIN_ROOT}/shared/regional-headers.example.yaml`. The setup skill copies the relevant ones into `paths.config_dir`/regional-headers.yaml and asks the user to fill in personal details (their address, phone, etc.).

For regions not in the defaults (Singapore, Australia, Brazil, etc.), prompt the user for the convention and write a new entry.

### Step 4 — Voice references

For each generative document type, ask whether the candidate has writing samples in their own voice:

- **CV summary:** existing CVs, About sections, LinkedIn bios
- **Cover letter:** old cover letters, application essays, letters of motivation
- **Interview prep:** none typically; skip
- **LinkedIn nudge:** sent messages, posts

For each provided file, write the path into `config.yaml > voice_references`. The cover-letter skill **refuses to draft** if no voice reference is configured for cover letters. See [`references/voice-references.md`](./references/voice-references.md).

### Step 5 — Template

Show the template catalog (`${CLAUDE_PLUGIN_ROOT}/templates/README.md`) and ask the user to pick one:

- `OPUS` — flagship; research/consulting heavy; selective inline bold in experience and education
- `modern-tech` — clean, tech/startup
- `academic` — publications-heavy
- `executive` — senior leadership
- `creative` — design / music / creative roles

Default: `OPUS`. Write `cv.template: [choice]` to `config.yaml`.

### Step 6 — Section toggles

Ask: *"Which CV sections do you want by default? You can override per application."* Default-on: tagline, contact, summary, core_skills, experience, education, additional. Default-off: publications, certifications, volunteering. The user can toggle anything.

### Step 6b — Inline bold

Ask: *"Should selected phrases in your experience and education bullets appear in bold? Bold helps a recruiter's eye land on quantified outcomes (40+ clients, 30%) and recognizable credentials (Deloitte, Harvard Law Review) in a 6-second scan. But it's also increasingly read as an AI tell — many recruiters now treat heavy bold as a signal that the CV was AI-drafted.*

*Here's the difference on a single bullet:*

With bold:
> Delivered market-entry research for **40+ multinational corporations**, cited by **Deloitte** and **Freedom House** across technology and media sectors.

Without bold:
> Delivered market-entry research for 40+ multinational corporations, cited by Deloitte and Freedom House across technology and media sectors.

*Default is off. Turn it on if you want the emphasis."*

Write `cv.inline_bold: true/false` to `config.yaml`. When `inline_bold: false`, the `convert_content_map()` helper in cv-tailor strips all `**` markers from every bullet before render — including experience, education, and any other field — so nothing renders bold regardless of what the content map contains.

### Step 6c — Session date format

Ask: *"Session output is saved into dated folders, e.g. `applications/11.06.26/Denmark/`. Should the date be written day-month-year (`dd.mm.yy`, e.g. `11.06.26`) or month-day-year (`mm.dd.yy`, e.g. `06.11.26`, the American convention)?"*

Default: `dd.mm.yy`. Write `paths.session_date_format: [choice]` to `config.yaml`.

### Step 7 — Output formats

Ask: *"Output formats?"*
- `docx` only — default, fast, no extra dependencies
- `docx + pdf` — also renders PDF via LibreOffice. Warn: requires `libreoffice` on PATH, adds ~5 seconds per render, and runs an extra audit pass on the PDF (modest extra token cost).

### Step 8 — Quality gates

The framework has a few hard quality gates that protect output. The main one: it will not render a CV until it has written a one-page role diagnosis for that role first. If you try to skip the diagnosis, should the framework explain the gate once and then do it anyway, or refuse outright every time?

Ask: *"The pipeline has quality gates — the main one being that it diagnoses each role before rendering a CV, so the CV has a clear editorial brief behind every bullet. If you skip a gate, should I explain it the first time and then go ahead, or refuse every time?"*
- `warn-once-then-comply` — default. Explains each gate the first time you bypass it in a session, then complies without repeating itself.
- `strict` — refuses to bypass any gate. Worth choosing if you've shipped a broken or generic CV before and want the framework to hold the line even when you're in a hurry.

### Step 9 — Write, confirm, and orient

Show the user the contents of the three files before writing. Confirm. Create `paths.config_dir`/ (default: `config/`) if it does not exist, and write all three config files there. Create `paths.assets_dir`/ (default: `assets/`) and place the career file in it. Then give a complete orientation:

**The full command catalog** — present this as the closing message so the user knows the whole surface area, not just one entry point:

```
Full pipeline
  Run [Country/City]              Full search → diagnose → tailor → cover for that geography
  Run [Country] | [Branch]        Same, scoped to one career branch
  Run Remote                      Search remote boards; routes results to the Remote sheet
  Run Remote | [Branch]           Remote, scoped to a branch

Single document
  Run CV only: [Branch]           Skip discovery; render one untailored CV for a branch
  Run CV only: General            Skip discovery; broad-judgment CV with no branch
  Run Request: [URL], [URL]       Diagnose, tailor, and cover specific job posting URLs

Utilities
  Run Blacklist: add [Company]    Add a company to the skip list
  Run Blacklist: remove [Company] Remove a company from the skip list
  Run Interview Prep: [Co], [Title]   Build an interview prep document for a role
  Run Story Bank Refresh          Extract new STAR+R stories from your career file

See CHEATSHEET.md at the repo root for a one-page reference.
```

**A note on connectors** — job discovery searches Indeed and, for LinkedIn and regional job boards, an Apify web scraper. The first time you run a search, the pipeline will walk you through connecting Apify. To save time, you can create a free account at apify.com now and have your API token ready. The detailed connector setup guide is in `skills/job-discovery/references/connector-setup.md`.

**Where your output lives** — CVs, cover letters, and diagnoses are saved to `applications/[dd.mm.yy]/[Country]/` (`paths.session_output_dir`/[session-date]/[Country or City]/, by default dated folders under `applications/` at the repo root, date format per `paths.session_date_format`). The job log is at `paths.job_log_dir`/Job Listings.xlsx. Config files are in `paths.config_dir`/. Career file and voice references are in `paths.assets_dir`/. All paths are shown again at the end of every pipeline run and can be customized in `config.yaml > paths`.

## What this skill does not do

- Does not write a starter career file (yet — see Step 1).
- Does not validate that the user's voice reference files actually exist (the skill is permissive; cv-tailor and cover-letter will complain if a path is broken).
- Does not configure connectors (~~job board / ~~web scraper). That happens lazily — the first time `job-discovery` runs and finds no `connectors.yaml`, it prompts.

## Files referenced

- [`references/career-file-guide.md`](./references/career-file-guide.md) — what to put in the career file
- [`references/branches-detection.md`](./references/branches-detection.md)
- [`references/voice-references.md`](./references/voice-references.md)
- [`${CLAUDE_PLUGIN_ROOT}/shared/config.example.yaml`](${CLAUDE_PLUGIN_ROOT}/shared/config.example.yaml)
- [`${CLAUDE_PLUGIN_ROOT}/shared/branches.example.yaml`](${CLAUDE_PLUGIN_ROOT}/shared/branches.example.yaml)
- [`${CLAUDE_PLUGIN_ROOT}/shared/regional-headers.example.yaml`](${CLAUDE_PLUGIN_ROOT}/shared/regional-headers.example.yaml)
- [`${CLAUDE_PLUGIN_ROOT}/templates/README.md`](${CLAUDE_PLUGIN_ROOT}/templates/README.md)
