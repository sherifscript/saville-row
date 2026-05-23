# Voice anchor — the operational test

The single biggest failure mode of AI-written cover letters is the template smell: prose that is grammatically perfect, professionally toned, and obviously not written by the person whose name is at the bottom. Recruiters in 2025–2026 are trained to spot it instantly, and it reads as low effort.

The framework defends against this with one operational test, applied per sentence.

## The test

> **Could this exact sentence appear in a cover letter for a different role at a different company?**

If yes, the sentence is generic. Cut it or rewrite it until the answer is no.

## Why this test and not "sound human"

"Sound more human" / "be more authentic" / "write naturally" are vague instructions. They do not give the writer a decision procedure. A sentence can be perfectly natural-sounding and still be generic ("I am excited about the opportunity to contribute to your team's mission").

The test is binary and concrete. You take a sentence, you imagine it pasted into a different application, and you ask whether it would still be true and still fit. If it would, the sentence is doing no work specific to this application — it is filler.

## Sentences that fail the test

These are real patterns. Every one of them could appear in any cover letter:

- "I am writing to express my strong interest in the [role] position."
- "I am confident that my skills and experience make me an ideal candidate."
- "Your company's commitment to innovation deeply resonates with me."
- "I thrive in fast-paced, collaborative environments."
- "I would welcome the opportunity to discuss how I can contribute to your team."
- "I am passionate about [field]."

Cut all of them. None survive the test.

## Sentences that pass the test

These cannot be moved to a different application because they reference specifics:

- "Northwind sits at the activation cliff every workflow-automation product hits when power users want more depth and new users churn before they get there." (specific to Northwind's stage and product)
- "The 18% activation lift I shipped at Beta Inc came from working that exact problem on a consumer surface." (specific quantified credential tied to the role's problem)
- "I noticed your changelog ships weekly, which tells me the experimentation loop is already tight, so the PM gap is probably prioritization, not velocity." (specific observation about this company)

A passing sentence is anchored to either the company's specific situation or the candidate's specific credential, and ideally connects the two.

## Using the voice reference

The voice reference files (configured in `config.yaml`) are samples of the candidate's own writing. Before drafting:

1. Read all voice reference files for cover letters.
2. Identify the candidate's voice markers:
   - **Sentence length** — do they write short and punchy, or longer and qualified?
   - **Openers** — how do they start paragraphs? Direct claim? Observation? Concession?
   - **Vocabulary** — words they use repeatedly; words they would never use (e.g., a candidate who never says "passionate" or "leverage").
   - **Rhetorical moves** — do they concede before claiming? Do they use plain declaratives? Do they ask questions?
3. Draft against those markers.

The voice reference does not dictate structure. It dictates *register* — the texture of the prose. A candidate who writes plainly should get a plain cover letter even if the "best practice" template is more elaborate.

## What good looks like

A good cover letter reads like the candidate sat down and wrote it in 30 minutes because they actually wanted this specific job. It is direct, it is specific, it does not perform. It tells the reader what the candidate has done in plain terms and trusts the reader to draw the conclusion.

It is not impressive-sounding. Impressive-sounding is the smell. Plain and specific is the goal.

## Warmth is not flattery

The voice test cuts generic enthusiasm. It must not also cut genuine sincerity, because the cover letter standard requires one real line of motivation and a warm close. These are not in tension — the distinction is specificity.

**Flattery** is praise of the company that could be pasted into any letter: "I admire your commitment to innovation", "your mission deeply resonates with me", "I have long respected your work". It fails the voice test because it is not anchored to anything only this candidate, applying to this role, would say.

**Warmth** is a specific, honest statement of why this role is worth the candidate's effort: "the onboarding problem is the part of product work I actually find worth doing", "this is the rare PM role scoped around a problem I already know in my hands". It passes the voice test because it is anchored to the candidate's real motivation and this role's real content.

The rule: if the warm sentence praises the company, it is probably flattery. If it states something true about the candidate's own motivation and ties it to the specific work, it is warmth. Keep warmth. Cut flattery. A letter with zero warmth reads as cold and transactional; a letter with flattery reads as AI. Specific sincerity is the only thing that is neither.

## The em dash rule

No em dashes (—) anywhere in a cover letter. This is a deliberate, slightly arbitrary constraint. The em dash is one of the most reliable tells of AI-generated prose in this era because models overuse it. Removing them entirely costs nothing (commas, periods, and restructured sentences cover every case) and removes one more signal that triggers a reader's "this is AI" pattern match.

The CV does not have this rule — only the cover letter, because the cover letter is the prose document a human actually reads closely.
