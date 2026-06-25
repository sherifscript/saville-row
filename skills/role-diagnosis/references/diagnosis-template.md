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

## Section angles — one line for every rendered part

The lead angle (section 4) sets the headline. This section sets everything
else, so no part of the CV ships as untailored career-file boilerplate. List
every part the CV will actually render, given the user's `cv.sections` and
`cv.max_experience_slots`, and give each a one-line angle: which real fact
from the career file this part surfaces, and how it connects to the diagnosed
problem. This is the brief cv-tailor executes field by field.

Cover, at minimum:
- Each experience slot (1 .. max_experience_slots), including the lower slots
  and the branch slot — not just the lead. If a slot has nothing to say to
  this role, angle it to the nearest transferable fact rather than reusing the
  generic version.
- Each degree (higher / lower) — what about it speaks to this role.
- core_skills rows and additional items — which the role rewards.
- Any enabled optional section (certifications, publications, volunteering).

For every experience slot, the angle line must also name the **proof point**:
the specific named credential, institution, client, platform, or number from the
career file that the slot's bullets must surface. This is what stops a bullet
from defaulting to a generic noun ("enterprise decision-makers") when a concrete
proof point ("cited by Deloitte and the Harvard Law Review") is available. If the
slot genuinely has no named proof point or metric, say so explicitly so cv-tailor
does not invent one.

```
- Slot 1 (most recent): [fact] | proof point: [named credential / metric to surface] angled as [connection to the problem]
- Slot 2 (same-employer): [fact] | proof point: [named credential / metric] angled as [connection]
- Slot 3 (branch): [fact] | proof point: [named credential / metric] angled as [connection]
- Higher degree: [fact] angled as [connection]
- ...one line per remaining rendered part...
```

The angle re-frames a real fact, and the proof point must already exist in the
career file. Neither ever adds a fact, a number, or a title the career file does
not contain. See the grounding gate (Check 9) and the bullet-strength gate
(Check 10) in `../../cv-tailor/references/post-render-audit.md`.

## Honest assessment (optional)

One sentence. Is the candidacy a strong match, a stretch, or a reach?
Name the largest risk plainly. This section is for the candidate's eyes
only — it never enters the CV or cover letter. It is most useful on
stretch or borderline roles where the cover letter will need to address
an obvious objection.

Examples:
- "Strong match: the Statista tenure directly mirrors the core ask."
- "Stretch: seniority is right but no public-sector context; cover
  letter should address the gap head-on."
- "Reach: three of five required skills are absent from the career
  file; proceed only if the Match Score rationale is compelling."
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

Distribute the keywords across the whole document, not just the top:
- 1–2 in the tagline
- 2–3 in the summary
- 1–2 per core skill row
- ≥2 in experience bullets (mandatory — checked by the post-render audit)
- at least one diagnosed keyword or angle reaches *every* rendered experience
  slot, including the lower and branch slots (checked by the coverage audit)

The old failure mode was a top-weighted distribution: the lead slot got
tailored and the lower slots, education, and additional sections shipped as
identical career-file boilerplate across every CV. The "Section angles"
section above exists to prevent exactly that. A reader comparing two of your
CVs side by side should not find a paragraph that is word-for-word the same.

## What a good diagnosis is not

- A summary of the JD (it's a *reading* of the JD)
- A scoring of the candidate against the role (that's the Match Score in job-discovery)
- A pep talk about why the candidate is great (that's the cover letter)
- A list of every possible angle (it's the *one chosen* angle)
- More than one page (longer means less clear)

## How long should it take?

A good diagnosis takes 5–10 minutes to write. Less and it's surface-level; more and you're rewriting the JD. The discipline is intentional brevity — 5 sections, each short.
