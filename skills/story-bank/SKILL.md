---
name: story-bank
description: Maintain a library of STAR+R behavioral interview stories drawn from the candidate's career file. Refresh extracts new stories without duplicating or inventing. Read by interview-prep.
metadata:
  version: 1.4.1
  last_updated: 2026-06-11
---

# story-bank

## When to activate

- User says "refresh the story bank", "Run Story Bank Refresh"
- User asks to add a story manually
- `interview-prep` reports the story bank is empty or thin and the user opts to refresh

## What it does

Maintains `paths.assets_dir`/Interview Story Bank.txt — the single source of structured behavioral interview stories. Stories are seeded from the candidate's career file and maintained either via `Run Story Bank Refresh` or manual additions.

The story bank is **not** read at session start. It is only loaded when `interview-prep` runs or `story-bank` is explicitly invoked.

## Run Story Bank Refresh

1. Read the candidate's career file in full.
2. Extract every moment strong enough for a behavioral interview — moments of decision, impact, failure, leadership, or insight.
3. For each story **not already present** in `paths.assets_dir`/Interview Story Bank.txt, add it in STAR+R format.
4. Do not duplicate existing entries.
5. Do not invent or embellish any detail not present in the career file.

See [`references/refresh-protocol.md`](./references/refresh-protocol.md).

## STAR+R format

Every story uses the format defined in [`references/star-plus-r.md`](./references/star-plus-r.md):

```
=====================================
Theme: [e.g. Stakeholder Management, Ambiguous Data, Cross-functional Delivery]
Strength: [e.g. analytical rigor, influence without authority]
Branch fit: [Research & Analytics / Product Management / General / etc.]
-------------------------------------
S:
T:
A:
R:
Reflection:
=====================================
```

## The no-invention rule

The story bank is factual. Every S, T, A, R, and Reflection line must be grounded in the career file. The framework does not invent a quantified result, does not embellish a role, does not add a decision the candidate did not describe.

If a career-file moment is genuinely a good story but lacks a key detail (e.g., no quantified result), the story is still banked, with the missing detail flagged: `R: [outcome described qualitatively; no metric in career file — candidate to confirm]`. The candidate fills the gap from memory; the framework does not fill it from imagination.

## Manual additions

The user can add a story directly: *"Add a story about the time I turned around the failing vendor relationship."* The skill interviews the user briefly to get all five STAR+R parts, then appends the entry. Manual additions are still subject to the no-invention rule — the framework writes down what the user says, structured, without embellishing.

## Save location

```
paths.assets_dir/Interview Story Bank.txt
```

## Files referenced

- [`references/star-plus-r.md`](./references/star-plus-r.md) — the format (shared with interview-prep)
- [`references/refresh-protocol.md`](./references/refresh-protocol.md) — the refresh procedure
- [`templates/story-entry.txt.tmpl`](./templates/story-entry.txt.tmpl)
