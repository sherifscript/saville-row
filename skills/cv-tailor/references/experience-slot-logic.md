# Experience slot logic — three slots, picked deliberately

The CV's Experience section contains **exactly N slots** (default N=3, configurable per user). The slots are picked deliberately, not greedily.

## Why a cap matters

A four-slot CV typically pushes onto a second page and dilutes the headline. The cap forces a choice: which three roles best speak to the diagnosed role? That choice is the editorial work of the CV.

## The default 3-slot structure

For most users with a continuous primary employer:

1. **Slot 1 — most recent / longest-tenure role.** Usually the senior version of the candidate's primary employer.
2. **Slot 2 — adjacent role at the same employer.** If the candidate was promoted within one company, the prior role goes here as a continuous block. Slot 1 and Slot 2 read as one career arc.
3. **Slot 3 — branch-driven choice.** From `branches.yaml`, the third-slot company for the diagnosed branch.

If the candidate's primary employer is a single role (no promotion / no continuous block), then Slots 1 and 2 are simply their two most recent roles, and Slot 3 is the branch-driven choice as above.

## Configuration

```yaml
cv:
  max_experience_slots: 3           # default 3, common alternatives: 2, 4
  continuous_employer_block: true   # if true, two adjacent same-employer roles count as a block in slots 1+2
  fallback_third_slot: null         # used if no branch is selected (Run CV only: General)
```

## When to use N=2

- Recent graduates with one substantial role
- Career changers where only two roles are relevant to the new track
- Junior candidates whose third role is too far back to be useful

The 2-slot CV is shorter and tighter. It works well when the candidate has strong education to fill the remaining space.

## When to use N=4

- Senior ICs with several short-tenure specialist roles
- Executives with multiple board / advisory roles that add credibility
- Career narratives where four chapters genuinely tell a different story than three

The 4-slot CV almost always runs onto a second page. Accept that or remove a non-experience section (often `additional` or `summary`) to compensate.

**Caution:** the cap exists to force editorial discipline. Bumping to 4 because all four roles "seem relevant" is exactly the failure mode the cap prevents. Be honest about whether the fourth slot is earning its place or just being included.

## The continuous-block rule

If the candidate held two adjacent roles at the same employer (e.g., promoted Analyst → Senior Analyst → Manager at one firm), those roles render as a **contiguous block** in chronological order. The block lives in Slots 1 and 2 by default. Inside the block:

- Slot 1 = the more recent (senior) role
- Slot 2 = the earlier (junior) role, anchored directly below Slot 1 with no separator

Both roles share the company name at the top of the block. Each has its own date range, title, and bullets. The visual effect: one career chapter, two phases.

The continuous block is opt-in via `cv.continuous_employer_block: true`. Default is true. Set false if the two roles at the same employer were really different jobs (e.g., promoted from Sales to Product — they share a company but not a narrative).

## Branch override of Slot 3

The diagnosis specifies which branch applies, and `branches.yaml` specifies the third-slot company for each branch:

```yaml
branches:
  - name: research-and-analytics
    third_slot_company: Acme Research
  - name: product-management
    third_slot_company: Beta Inc
```

When the diagnosis picks `product-management`, Slot 3 renders the Beta Inc role. When it picks `research-and-analytics`, Slot 3 renders Acme Research. The candidate's career file contains both; the framework picks one per CV.

## Slot 4 and beyond (when N>3)

For users with `max_experience_slots: 4`:

- Slot 4 is the second branch-eligible role (e.g., if the candidate has two relevant past roles in the branch's domain), or a transferable-skills role from outside the branch.
- The diagnosis specifies it.

For users with `max_experience_slots: 2`:

- Slot 2 is the branch-driven choice; no continuous block, no third slot.

## What never goes in the experience section

- Roles older than ~10 years (unless they are the only credential for the role being targeted)
- Internships, unless the candidate is within ~2 years of graduation
- Side projects, volunteer work, or community roles (those go in `additional` or `volunteering`)
- Education-adjacent positions (TA, RA) — those go under `education`

## What the diagnosis controls

The diagnosis can:
- Pick the branch → controls Slot 3
- Specify section overrides → controls which sections render
- Specify keywords → controls bullet wording
- Declare the Positioning mode → in `transition` mode only, unlocks the slot
  latitude below

The diagnosis cannot:
- Add an extra slot beyond `max_experience_slots` (the config wins) — except
  the single transition-mode allowance below
- Promote Slot 3 above Slot 1 or 2 (chronology is enforced; an ongoing side
  engagement below the block must be marked `concurrent: true` in the
  content map)
- Drop the continuous block in favor of a non-block third role (if continuous_employer_block is true, the block holds slots 1+2)

These constraints exist because they protect the structure that makes the CV scannable in 6 seconds.

## Transition-mode slot latitude

When the diagnosis's `## Positioning` declares `Mode: transition` (a
deliberate career change), the branch's default slot picks may not carry the
target-domain evidence — the roles that prove a Customer Success story can be
old client-facing jobs the branch logic would never select. In transition
mode ONLY, the diagnosis MAY:

- **(a) override the branch's third slot** with a target-relevant role from
  the career file, and/or
- **(b) add ONE slot beyond `cv.max_experience_slots`** when an older role
  carries direct target-domain evidence no in-cap slot can
  (`validate_content_map` accepts max+1 only in transition mode).

Both require an explicit **`Slot plan:`** line in the diagnosis naming every
slot and its one-line justification — the extra slot must be argued, not
assumed. Everything else survives unchanged: the continuous-employer block
still holds slots 1+2, reverse chronology is still enforced (Check 7;
ongoing side roles marked `concurrent: true`), and the ~10-year lookback
still applies unless the old role is the only credential for the target
domain (the existing exception). In `direct` and `adjacent` modes, slot
rules are exactly the defaults above — the latitude does not exist.

The cap's purpose (forced editorial choice) is preserved: a transition
diagnosis that wants slot latitude has to write down why each slot earns
its place.
