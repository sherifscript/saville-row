# Branch resolution — picking the right branch when the role is ambiguous

If `branches.yaml` has one entry, this is a no-op. The framework uses that branch for everything.

If `branches.yaml` has multiple entries, the diagnosis must pick one per role. This file describes how.

## The picking heuristic

For each role being diagnosed, score each configured branch against the JD on three dimensions:

1. **Keyword overlap.** Count how many of the branch's `keyword_seeds` appear in the JD (case-insensitive, whole-word match). More overlap → higher score.
2. **Role title alignment.** Does the role title match the branch's domain? "Senior PM" → product-management; "Research Manager" → research-and-analytics; "Director of Policy" → policy-and-governance.
3. **Team / company context.** A research role at a consultancy reads differently from a research role at a pharma company. Use any context from the JD about team size, reporting line, and company stage.

Pick the highest-scoring branch. If two branches tie within ~20%, the role is *ambiguous* and the user should pick.

## Ambiguity prompt

When ambiguous in an interactive session:

```
This role could be diagnosed against your [Branch A] branch or your
[Branch B] branch.

[Branch A]: [one-sentence reason it might fit — keyword overlap, title cue]
[Branch B]: [one-sentence reason it might fit]

Which branch should this CV speak to? You can also say "split" and I'll
generate two diagnoses and two CVs — useful when you want to try both
angles and decide later.
```

For unattended runs (scheduled, batch), pick the higher-scoring branch silently and note the choice in the diagnosis:

```markdown
## Branch

product-management (auto-selected: 6 keyword matches vs. 3 for
research-and-analytics; title "Senior PM" aligns)
```

## Branch override

The user can override the diagnosis's branch pick with a one-line edit to the Diagnosis.md file. The cv-tailor skill reads the branch field from the diagnosis when composing the experience section.

## When no branch fits

Occasionally a role doesn't match any configured branch — e.g., a "Chief of Staff" role for a candidate with no chief-of-staff branch. Two options:

1. **Skip the role.** If it's a stretch outside the configured branches, the candidate may not be a strong fit anyway. Note this and move on.
2. **Diagnose against the general profile.** If the candidate wants to apply, set `branch: general` in the diagnosis. The cv-tailor skill falls back to the default third-slot company from `config.yaml > cv.default_third_slot` (set during setup).

Adding a new branch mid-search is also fine — re-run `job-search-setup` and update `branches.yaml`. The framework picks up new branches on next invocation.

## What branch resolution does not do

- Does not change the first two experience slots. Those are always the candidate's primary employer / longest tenure / most recent role, in chronological order. See `cv-tailor/references/experience-slot-logic.md`.
- Does not change which keywords appear. Those come from the JD verbatim, regardless of branch.
- Does not change the regional header. That's purely region-based.

Branch only controls: third-slot company, secondary core-skills emphasis, and (sometimes) the cover letter opener angle.
