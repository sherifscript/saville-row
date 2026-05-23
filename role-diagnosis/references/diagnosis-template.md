# Diagnosis template — the full spec

The Diagnosis.md file is the only place in the framework where editorial judgment lives. Everything downstream is mechanical execution of the diagnosis. Get the diagnosis right; the CV and cover letter follow.

## Full template

```markdown
# Role Diagnosis — [Company] | [Job Title]

## What is this team actually hiring to fix?

2–3 sentences. Read past the JD's surface bullets. What is the underlying
pressure — a missing capability, a stalled initiative, a person who left,
scale they can't keep up with, a market they don't understand? If the JD
says "build dashboards," is the real ask "make our metrics legible to a
non-technical exec"? Name the real problem.

## What would a great hire deliver in their first 90 days?

1–2 sentences. Concrete outputs the team would point to and say "yes,
that was the win." Not aspirations — specific shipped deliverables.

## What is the actual bar?

1 sentence. Pick exactly one of:

- technical depth
- stakeholder gravity
- speed under chaos
- commercial instinct
- methodological rigor
- cross-cultural fluency
- design judgment
- domain expertise (specify which)
- something else (specify in one phrase)

There can only be one primary bar — secondary bars come second.

## Which of my credentials speaks loudest to that bar?

1–2 sentences. Pick the single strongest proof point from the candidate's
career file. This becomes the lead angle of the lead experience section.

Examples of credentials to consider:
- multi-year senior tenure at a recognized company
- quantified outcome (revenue, growth %, scale)
- citations in named publications
- delivered shipped artifacts the reader can point to
- cross-functional or cross-cultural depth
- methodology depth (specific technique, tool, or framework)

Pick one. Do not list three.

## Branch (if applicable)

Which branch from `branches.yaml` does this role belong to? Name it and
explain in one sentence why (the JD keyword overlap, the role title, the
team context, etc.). For single-branch users, this section is omitted.

## Keywords from the JD that must appear verbatim in the CV

A bulleted list of 6–10 phrases. These are the ATS terms — the exact
strings the JD uses, not paraphrases. They will be distributed across
the tagline, summary, core skills, and at least two experience bullets.

- [keyword 1]
- [keyword 2]
- ...
```

## How to write each section well

### Section 1 — "what is this team actually hiring to fix?"

The JD describes the role; this section describes the problem behind the role. Three diagnostic moves:

1. **Read the JD top-to-bottom once.** Resist taking notes the first read.
2. **Identify what is over-specified vs. under-specified.** Over-specified sections (long lists of nice-to-haves) usually signal the team doesn't know exactly who they want — they're hiring for a *type* not a problem. Under-specified sections (vague "drive impact") usually signal the team knows the problem but can't articulate the work.
3. **Look at the team name, the reporting line, and the company stage.** A "Senior Data Scientist" at a 50-person Series B is solving a different problem than the same title at a 5,000-person enterprise. The pressure is contextual.

The output is *what the team is solving*, expressed as a problem statement, not as a job description.

### Section 2 — 90-day deliverables

A great hire produces *artifacts* in the first 90 days. Name them. "Builds relationships across the org" is not an artifact. "Ships v1 of the onboarding redesign with measured activation lift" is an artifact.

This section sharpens the diagnosis by forcing concreteness. If you can't name the deliverable, you don't yet understand the role.

### Section 3 — the actual bar

The bar is what gets a candidate hired vs. rejected at the late stage of the interview process. It is rarely "all of the above." Teams hire for one thing and tolerate the rest.

Picking the bar requires reading between the lines:
- **Technical depth** → JD lists specific technologies, the interview will include a deep dive
- **Stakeholder gravity** → JD mentions "executive presence" or "C-suite," team is small and political
- **Speed under chaos** → JD mentions "startup", "0 to 1", "wear many hats"
- **Commercial instinct** → JD mentions revenue, deals, pipeline
- **Methodological rigor** → JD specifies methods (DiD, RCT, K-means, etc.)
- **Cross-cultural fluency** → role spans regions, JD requires multiple languages or regional context

If two bars seem equal, pick the one that overlaps most with the candidate's strongest credential. The diagnosis is also a strategic choice about which version of the candidate to show.

### Section 4 — the loudest credential

Exactly one credential. The mistake here is greedy listing — "I'm strong on X, Y, and Z." That's not a diagnosis, it's a generic CV. The diagnosis picks one credential to lead with, and accepts that the others will sit in support.

The chosen credential becomes:
- The opener of the tagline (e.g., "ML Engineer with production NLP shipped at scale")
- The first sentence of the summary
- The lead bullet of the lead experience section
- The opener of the cover letter (often)

If the diagnosis can't pick one, the resulting CV will be generic — every section optimized to look fine, none of them optimized to land.

### Section 5 — verbatim keywords

These are not your interpretation of the JD's themes. They are *the exact strings the JD uses*. If the JD says "experimentation platform," do not write "A/B testing infrastructure" in the diagnosis. Write "experimentation platform." The CV's keyword density is measured against these exact strings.

Distribute the keywords:
- 1–2 in the tagline
- 2–3 in the summary
- 1–2 per core skill row
- ≥2 in experience bullets (mandatory — checked by the post-render audit)

## What a good diagnosis is not

- A summary of the JD (it's a *reading* of the JD)
- A scoring of the candidate against the role (that's the Match Score in job-discovery)
- A pep talk about why the candidate is great (that's the cover letter)
- A list of every possible angle (it's the *one chosen* angle)
- More than one page (longer means less clear)

## How long should it take?

A good diagnosis takes 5–10 minutes to write. Less and it's surface-level; more and you're rewriting the JD. The discipline is intentional brevity — 5 sections, each short.
