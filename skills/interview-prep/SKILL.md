---
name: interview-prep
description: Produce an interview prep document for a specific role — role snapshot, STAR+R story map, likely hard questions, and smart questions to ask back. Pulls from the story bank and the career file.
metadata:
  version: 1.4.0
  last_updated: 2026-06-11
---

# interview-prep

## When to activate

- User says "prep me for the [company] interview", "Run Interview Prep: [Company], [Job Title]"
- Pipeline orchestrator invokes after an interview is scheduled (manual trigger)

## What it does

Produces a single document:

```
[Company] - [Job Title] - Interview Prep.docx
```

saved to `paths.interview_prep_dir`/. It pulls the job description (from the apply link in the job log if available, or a fresh search), reads the candidate's story bank and career file, infers the branch, and assembles four sections.

## Inputs

1. **The job description.** From the job log's Apply Link column if the role is logged; otherwise search for it.
2. **The story bank** — `paths.assets_dir`/Interview Story Bank.txt. Structured STAR+R stories. See the `story-bank` skill.
3. **The career file** — the candidate's full career history.
4. **The branch** — inferred from the role, same logic as `role-diagnosis`.

## The four sections

### 1. Role snapshot

A diagnosis of the underlying problem or pressure driving this hire. Not a summary of the JD. What is the company actually trying to solve? This is the same diagnostic instinct as `role-diagnosis` section 1, applied to interview prep. See [`references/role-snapshot.md`](./references/role-snapshot.md).

### 2. Story map

For each of the 4–5 most likely behavioral question themes for this role, select the single best story from the story bank and show why it fits. Write each entry as:

- **Theme** — the behavioral question territory (e.g., Stakeholder Management, Ambiguous Data)
- **Story title and fit rationale** — one sentence on why this story is the strongest match
- **Full STAR+R** — each element (Situation, Task, Action, Result, Reflection) written in full paragraphs, not crammed onto a single line. The Action is the longest section; it must show the decision, not just a list of steps.

See [`references/story-mapping.md`](./references/story-mapping.md). The STAR+R format and quality bar are in [`references/star-plus-r.md`](./references/star-plus-r.md).

### 3. Likely hard questions

3 questions specific to this role or company that a sharp interviewer would ask — not generic behaviorals, but questions that probe the real gaps in this candidacy for this role. Each question carries two coaching paragraphs: **Why they're asking this** (what gap the interviewer is probing) and **How to approach it** (a framing for the honest, strongest answer — not a script, but a way in). See [`references/hard-questions.md`](./references/hard-questions.md).

### 4. Your ask

2–3 smart questions for the candidate to ask the interviewer, grounded in the role snapshot diagnosis. Questions that show the candidate has understood the real problem.

## Em dashes

Em dashes (—) are banned from the interview prep document. It is employer-facing. Use commas, periods, or restructure the sentence instead. See `${CLAUDE_PLUGIN_ROOT}/shared/conventions.md`.

## Render to .docx (mandatory)

The four sections are drafted as markdown, then rendered, never shipped as markdown:

1. Write the draft as markdown (a `.scratch/` working file, not `paths.interview_prep_dir`/ — see `${CLAUDE_PLUGIN_ROOT}/shared/conventions.md`).
2. Render it via `python ${CLAUDE_PLUGIN_ROOT}/shared/scripts/text_to_docx.py <draft> <output.docx>`, saving to the path in "Save location" below.
3. The `.docx` is the **only** deliverable. Never leave a `.md` prep document in `paths.interview_prep_dir`/.

If the render fails, that is a failed stage — apply the failure-recovery rules in `job-search-pipeline/references/failure-recovery.md`. A failed render is not a license to ship the markdown draft instead.

## Save location

```
paths.interview_prep_dir/[Company] - [Job Title] - Interview Prep.docx
```

Create the folder if it does not exist.

## Relationship to other skills

- Reads from `story-bank` (the STAR+R story library). If the story bank is empty or thin, interview-prep suggests running `Run Story Bank Refresh` first.
- Shares the role-diagnosis instinct but does not write a Diagnosis.md — the role snapshot lives inside the prep document.
- Does not require a CV to have been rendered. Interview prep can run standalone for any role.

## Files referenced

- [`references/role-snapshot.md`](./references/role-snapshot.md)
- [`references/story-mapping.md`](./references/story-mapping.md)
- [`references/star-plus-r.md`](./references/star-plus-r.md)
- [`references/hard-questions.md`](./references/hard-questions.md)
- [`${CLAUDE_PLUGIN_ROOT}/shared/scripts/text_to_docx.py`](${CLAUDE_PLUGIN_ROOT}/shared/scripts/text_to_docx.py) — markdown → .docx render
