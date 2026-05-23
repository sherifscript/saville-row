# Anti-rigidity — why there are no per-role-type defaults

A common request when extending this framework is to add rules like:

- "For data science roles, always lead with the Python pipeline"
- "For consulting roles, always emphasize stakeholder management"
- "For senior IC roles, always promote the longest-tenure technical position"

These rules feel useful. They aren't. The framework rejects them.

## Why

A diagnosis is the act of reading *this specific role at this specific company*. The moment a default like "for data roles, lead with Python" exists, the diagnosis stops being a reading and starts being a categorization. Two failure modes follow:

1. **Wrong lead for the role.** A "data science" role at a 12-person startup hiring its first DS is solving "give us the analyst we don't have yet"; the Python pipeline is irrelevant — the bar is generalist analytical instinct and the ability to write a Looker dashboard. The default would lead with the wrong thing.

2. **Generic CVs that look tailored.** When categorization replaces diagnosis, every CV for every "data role" gets the same lead. A recruiter reading three of them sees the same opener three times. The signal of tailoring is destroyed.

The original workflow this framework was extracted from hit this exact failure mode on 2026-04-26: a batch of CVs that "all looked tailored, none of them were." The cause was per-role-type defaults that had crept into the build script.

## The rule

The diagnosis selects the lead. The lead selects the bullet order. The JD's vocabulary selects the wording.

No category defaults. Ever.

## What is allowed

The framework can use categories as **hints** for the diagnosis-writer (Claude or the human) to *consider*, not as *defaults* to apply. For example:

```
ALLOWED: "This role is in the data science category. Common bars for data
roles include methodological rigor, production engineering depth, or
stakeholder-facing analytical communication. Read the JD to decide which
applies here."

NOT ALLOWED: "This is a data science role, so the CV defaults to leading
with the Python pipeline and the K-means model."
```

The first guides judgment. The second replaces it.

## Branch defaults are different — and allowed

`branches.yaml` configures which third-slot company appears for each branch. This is a *user-configured default per branch*, not a *framework-configured default per role category*. The user has chosen it deliberately, knowing their own career. The framework has not pre-decided for them.

The distinction matters: the branch default reflects the candidate's chosen narrative; a role-type default would override the candidate's narrative with a generic one.

## When you're tempted

If you find yourself adding a `if role_category == 'X' then lead_with(Y)` rule, stop. Write a `references/role-category-considerations.md` note instead, listing the *questions to ask* for that category. Let the diagnosis-writer do the picking.
