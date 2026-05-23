# Refresh protocol — Run Story Bank Refresh

The refresh extracts new behavioral stories from the candidate's career file and adds them to the story bank without duplicating or inventing.

## Procedure

1. **Read the career file in full.** Not a skim. Every role, project, and side venture.
2. **Read the existing story bank** (`data/Interview Story Bank.txt`) if it exists. Build a list of stories already present, keyed by their core event.
3. **Scan for story-worthy moments.** A moment qualifies when it has a decision point, a personal contribution, an outcome, and something learned. See `star-plus-r.md` ("What earns a place in the bank").
4. **For each qualifying moment not already banked**, write a STAR+R entry.
5. **Append** the new entries to the story bank. Never overwrite existing entries.
6. **Report** to the user: how many stories were added, their themes, and any moments that were close but skipped (with the reason).

## Deduplication

A moment is a duplicate if its core event matches an existing entry, even if the existing entry's wording differs. Match on the underlying event (the project, the decision, the incident), not on the phrasing.

If the career file has been updated with more detail about an already-banked story, do not create a second entry. Instead, note it: *"The career file now has a quantified result for the [X] story, which was banked without one. Want me to update that entry?"* Updating an entry is a deliberate, confirmed action — not part of the automatic refresh.

## The no-invention rule

Every line of every entry must trace to the career file. The refresh:

- Does not invent quantified results.
- Does not embellish the candidate's role or contribution.
- Does not add decisions, stakes, or context not in the source.
- Does not merge two separate events into one more dramatic story.

If a moment is story-worthy but missing a detail, bank it with the gap flagged: `R: [qualitative outcome; no metric in career file — candidate to confirm]`.

## Theme and branch tagging

For each new story, assign:

- **Theme** — the behavioral question category it answers best (Stakeholder Management, Ambiguous Data, Failure & Recovery, etc.).
- **Strength** — the underlying capability it demonstrates.
- **Branch fit** — which branch(es) from `branches.yaml` the story supports. A story can fit multiple branches or be General.

Tagging is what makes the bank useful to `interview-prep` — the story map pulls by theme and branch.

## After refresh

The refresh updates the index entry for the story bank if an index is maintained:

> "Structured STAR+R interview stories drawn from the career file, organized by theme and branch."

And reports the summary to the user. Example:

> Added 4 stories: "Pricing-page experiment" (Influence Without Authority), "The churn investigation" (Ambiguous Data), "Shipping the redesign late" (Failure & Recovery), "First PM hire onboarding" (Building From Zero). Skipped one moment — the Q3 launch — because the career file describes the outcome but no decision the candidate personally owned; it reads as a team success, not a story. The bank now holds 11 stories.

## How often to refresh

Refresh when the career file gains material: a completed project, a new role, a resolved incident. There is no value in refreshing against an unchanged career file — the refresh would find nothing new.
