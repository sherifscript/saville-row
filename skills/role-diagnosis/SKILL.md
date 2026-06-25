---
name: role-diagnosis
description: Produce a one-page Diagnosis.md for a target role before any CV or cover letter is rendered. Five sections — what the team is hiring to fix, 90-day deliverables, the real bar, strongest credential, verbatim JD keywords. Hard gate for cv-tailor and cover-letter.
metadata:
  version: 1.6.0
  last_updated: 2026-06-25
---

# role-diagnosis

The editorial gate. No diagnosis, no CV. No diagnosis, no cover letter.

## When to activate

- User says "diagnose this role", "what is this team actually hiring to fix", "read this JD"
- `cv-tailor` or `cover-letter` is invoked and no `Diagnosis - [Company] - [Job Title].md` exists in the target folder
- `Run Request: [URL]` shortcut command

## What it does

Reads a job description (from a URL, pasted text, or scraped data) and produces a file:

```
Diagnosis - [Company Name] - [Job Title].md
```

The file contains the five core sections plus a Section-angles block (and an optional honest-assessment). It is the editorial brief that drives every downstream choice — bullet order, lead angles, which experience to emphasize, what to drop, and how every part below the headline is framed. If a bullet does not serve the diagnosis, it does not belong on that CV.

## The five sections

See [`references/diagnosis-template.md`](./references/diagnosis-template.md) for the full template. The sections are:

1. **What is this team actually hiring to fix?** — 2–3 sentences. Read past the JD's surface bullets. Name the real problem.
2. **What would a great hire deliver in their first 90 days?** — 1–2 sentences. Concrete outputs.
3. **What is the actual bar?** — 1 sentence. Pick one: technical depth / stakeholder gravity / speed under chaos / commercial instinct / methodological rigor / cross-cultural fluency / something else.
4. **Which of my credentials speaks loudest to that bar?** — 1–2 sentences. The single strongest proof point from the career file. This becomes the lead angle of the lead experience section.
5. **Keywords from the JD that must appear verbatim in the CV.** — Bulleted list of 6–10 exact strings from the JD. ATS terms.

Plus a **Section angles** block: one line per rendered part (every experience slot, each degree, core_skills, additional, and any enabled optional section), each naming a real career-file fact and how it connects to the diagnosed problem. For every experience slot the line also names the **proof point** — the specific named credential, institution, client, platform, or number the slot's bullets must surface — so cv-tailor writes "cited by Deloitte and the Harvard Law Review" rather than a generic "enterprise decision-makers". Section 4 sets the headline; this block tailors everything below it so no part ships as career-file boilerplate. The angle re-frames a real fact, never invents one. See [`references/diagnosis-template.md`](./references/diagnosis-template.md).

## The anti-rigidity clause

There is no fixed "for FP&A roles, lead with X" rule. There is no "always include the Python pipeline for data roles" rule. The diagnosis selects the lead. The lead selects the bullet order. The JD's vocabulary selects the wording. Resist the temptation to pre-decide based on role category. See [`references/anti-rigidity.md`](./references/anti-rigidity.md).

## Branch resolution

If `branches.yaml` exists with more than one branch, the diagnosis must specify which branch applies to this role. The branch determines the third experience slot in the CV (see `../cv-tailor/references/experience-slot-logic.md`). If the branch is ambiguous from the JD, prompt the user to pick:

> *"This role could be diagnosed against your `research-and-analytics` branch or your `product-management` branch. The JD emphasizes stakeholder management and shipped outcomes, which leans PM, but it also asks for analytical rigor. Which branch should this CV speak to?"*

For unattended runs (scheduled, batch), pick the branch with the highest keyword overlap and note the choice in the diagnosis.

See [`references/branch-resolution.md`](./references/branch-resolution.md).

## Output

Always saved to the same folder the CV will be saved to:

```
paths.session_output_dir/[session-date]/[Country or City]/Diagnosis - [Company] - [Job Title].md
```

For the `Run Request` shortcut: `paths.session_output_dir`/[session-date]/Requests/Diagnosis - [Company] - [Job Title].md.

`[session-date]` is today's date formatted per `paths.session_date_format` (default `dd.mm.yy`, e.g. `11.06.26`).

For `Run CV only` (no specific JD): the diagnosis step is skipped entirely; cv-tailor uses broad branch judgment instead.

## Hard gate enforcement

When cv-tailor or cover-letter is invoked, they check for `Diagnosis - [Company] - [Job Title].md` in the target folder before doing anything. If absent:

- **opinionation: warn-once-then-comply (default)** — first time per session, explain the gate and offer to run role-diagnosis now. After confirmation, comply with the user's request to skip and render without a diagnosis. Output quality will be lower.
- **opinionation: strict** — refuse to proceed. Run role-diagnosis first.

## What this skill does not do

- Does not write CV bullets. That's cv-tailor.
- Does not write cover letter prose. That's cover-letter.
- Does not score the role against the candidate. That's `job-discovery`'s Match Score column.
- Does not decide whether to apply. That's the candidate's call. The diagnosis only sharpens the application if the candidate has decided to apply.

## Files referenced

- [`references/diagnosis-template.md`](./references/diagnosis-template.md) — the full template with all five sections
- [`references/anti-rigidity.md`](./references/anti-rigidity.md) — why no per-role-type defaults
- [`references/branch-resolution.md`](./references/branch-resolution.md) — branch picking when ambiguous
- [`templates/Diagnosis.md.tmpl`](./templates/Diagnosis.md.tmpl) — the literal file template
- [`examples/saas-pm-role.md`](./examples/saas-pm-role.md) — a worked example for the showcase candidate
