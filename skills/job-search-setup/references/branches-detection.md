# Branches detection — how the setup skill proposes career arcs

A **branch** is a distinct narrative the candidate can lead with for different role types. Most careers contain 1–4 plausible branches. Setup proposes them; the user confirms.

## Detection heuristic

Read the candidate's career file in full. For each entry (role, project, citation, degree, side venture), assign one or more tentative branch tags. A tag is justified when:

1. The activity could plausibly become the **lead angle** of a CV for a specific role type, AND
2. At least two distinct pieces of evidence support it, AND
3. It would substantially change which experience slot, summary sentence, or core skills row leads.

If a candidate has only research roles, do not invent a "product management" branch from one short product internship. A branch must be **defensible from the file**.

## Common branch patterns

These show up often enough to recognize:

| Pattern | Anchored on |
| --- | --- |
| Research & Analytics | Long analyst tenure, citations, methodology depth |
| Product Management | Cross-functional shipping, metrics outcomes, roadmap ownership |
| Policy & Governance | Public sector, regulator engagement, white papers |
| Music & Creative | Industry deals, streaming numbers, press coverage |
| Engineering / IC | Code commits, infra work, technical writeups |
| Sales & GTM | Quota attainment, deal sizes, pipeline ownership |
| Consulting | Multi-client engagements, frameworks delivered, named projects |
| Founder / Operator | Equity-bearing roles, P&L ownership, fundraising |
| Academic | Publications, teaching, grant funding |

## Output format

After detection, present to the user as:

```
I see [N] possible branches in your career:

1. [Name] — anchored on [evidence sentence].
2. [Name] — anchored on [evidence sentence].
3. [Name] — anchored on [evidence sentence].

Confirm, edit, add, or remove?
```

Then write to `branches.yaml`:

```yaml
branches:
  - name: research-and-analytics
    display_name: Research & Analytics
    third_slot_company: Acme Research    # default third slot for CVs targeting this branch
    voice_descriptor: rigorous, citation-led, methodology-first
    keyword_seeds:
      - "research"
      - "analyst"
      - "insights"
      - "data"
  - name: product-management
    display_name: Product Management
    third_slot_company: Beta Inc
    voice_descriptor: cross-functional, outcome-oriented, user-focused
    keyword_seeds:
      - "product"
      - "PM"
      - "roadmap"
      - "user research"
```

The `third_slot_company` field is the company whose role goes in the third CV experience slot when this branch is selected. The first two slots are typically the candidate's most recent and longest-tenure roles; the third varies by branch (see `../cv-tailor/references/experience-slot-logic.md`).

## Edge cases

**Single-branch careers.** If only one branch surfaces, do not pad. Write `branches.yaml` with one entry. The framework works fine with a single branch — diagnosis skill will skip the branch-resolution step entirely.

**Career changers.** If two branches share no evidence — e.g., 10 years in accounting followed by 1 year as a junior data scientist — flag this to the user: *"Your data science branch has thin evidence; CVs leading with it will under-sell. Consider waiting until you have more shipped work before targeting senior data roles."* Then write both branches if the user wants.

**Side projects.** A 6-month side project is not a branch unless it has visible outcomes (revenue, press, citations, user numbers). Pure resume padding is not a branch.

## Re-detection

The setup skill is normally run once. If the candidate's career file is substantially updated (new role, completed project, fresh citations), the user can re-run `job-search-setup` and the wizard will detect changes and propose `branches.yaml` updates as a diff rather than overwriting wholesale.
