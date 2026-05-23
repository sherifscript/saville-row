---
name: job-search-setup
description: First-run wizard for saville-row. Reads the candidate's career file, proposes branches, prompts for voice references and regions, writes config.yaml. Run once per repo before any other skill.
metadata:
  version: 1.0.0
  last_updated: 2026-05-20
---

# job-search-setup

## When to activate

- User says "set up saville-row", "first run", "I just cloned this", "configure saville-row"
- User invokes any other skill and `config.yaml` does not exist at the repo root → suggest setup first

## What it does

Walks the candidate through a single conversation that produces three files at the repo root:
- `config.yaml` — global settings (opinionation, output formats, voice reference paths, template choice)
- `branches.yaml` — career branches auto-detected from the career file, confirmed by the user
- `regional-headers.yaml` — header variants for each target region

After setup completes, all other skills become operable.

## The conversation, in order

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

User accepts/edits. Write the final list to `branches.yaml`. See [`references/branches-detection.md`](./references/branches-detection.md) for the detection heuristic.

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

Smart defaults for US / UK / EU / Gulf / Egypt are shipped in `${CLAUDE_PLUGIN_ROOT}/shared/regional-headers.example.yaml`. The setup skill copies the relevant ones into `regional-headers.yaml` and asks the user to fill in personal details (their address, phone, etc.).

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

### Step 7 — Output formats

Ask: *"Output formats?"*
- `docx` only — default, fast, no extra dependencies
- `docx + pdf` — also renders PDF via LibreOffice. Warn: requires `libreoffice` on PATH, adds ~5 seconds per render, and runs an extra audit pass on the PDF (modest extra token cost).

### Step 8 — Opinionation

Ask: *"How strict do you want the framework to be?"*
- `warn-once-then-comply` — default. Hard gates explain themselves on first bypass, then get out of the way.
- `strict` — hard gates refuse outright. Recommended for users who have shipped broken outputs before and trust the framework's audit more than their own judgment.

### Step 9 — Write and confirm

Show the user the contents of the three files before writing. Confirm. Write. Done. Suggest a next command:

> *"Setup complete. Try `Run [your_primary_region]` to do a first job search, or `Run CV only: General` to render an untailored CV against your default template."*

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
