---
name: cover-letter
description: Write voice-anchored cover letters under 300 words, no em dashes, with an opener load-bearing on the role's specifics. Refuses to draft without a voice reference. Also drafts LinkedIn recruiter nudges.
metadata:
  version: 1.6.1
  last_updated: 2026-06-11
---

# cover-letter

## When to activate

- User says "write a cover letter for [company]"
- Pipeline orchestrator invokes after cv-tailor for Western-market roles
- `Run Request` shortcut for non-blacklisted roles in cover-letter markets

## Hard gate — voice reference required

Before drafting the first sentence, read the candidate's voice reference file(s) for cover letters, configured in `config.yaml > voice_references.cover_letter`. If none is configured:

- **warn-once-then-comply (default):** explain that without a voice reference the letter will read like generic AI output, offer to set one up, then comply if the user insists.
- **strict:** refuse. Run `job-search-setup` to add a voice reference.

See [`../job-search-setup/references/voice-references.md`](../job-search-setup/references/voice-references.md).

The objective is not to imitate the structure of the reference letters — it is to write in the same voice: direct, plainly told, no consultant framing, no sentences performed for impressiveness.

## When to write a cover letter at all

- **Western markets (US, UK, EU, Canada, etc.):** write one for every selected role.
- **Egypt / Gulf:** write one **only** for multinational employers (e.g. Spotify MENA, the Big Four, McKinsey, Ipsos). For local companies, CV only. See `config.yaml > cover_letter.markets`.

## Quality standard

A recruiter reads a cover letter in 20 to 40 seconds, and while they read it they are doing one thing: risk assessment. The letter's job is to make the candidate the obvious low-risk choice. Every rule below serves that.

Every cover letter must:

1. **Open with one tight sentence** explaining why the candidate is applying to this role at this company specifically — load-bearing on the specifics, and short (aim for 25 words or fewer). A load-bearing opener that is also a run-on loses the skim reader. See [`references/opening-rules.md`](./references/opening-rules.md).
2. **Show the strongest relevant proof as plain description** of what the candidate has done — not a problem/solution pitch, not labelled credentials ("First, my data background. Second..."). Describe the work; let the reader draw the conclusion.
3. **Address the obvious objection, if there is one.** If the candidacy has a visible risk — a career change, an industry switch, a seniority jump, an employment gap, a run of short tenures — name it in one honest sentence and resolve it. The recruiter is looking for that risk anyway; a candidate who names it first reads as confident, not weak. See [`references/objections-and-close.md`](./references/objections-and-close.md).
4. **Include one genuine line of motivation** — a real, specific reason this company or role is worth the candidate's effort. Not flattery, not "I admire your mission." Something concrete and honest. A letter with zero motivation reads as cold and transactional; this is the one place sincerity belongs.
5. **Close warmly, with a concrete next step.** See [`references/objections-and-close.md`](./references/objections-and-close.md).
6. Stay **between 200 and 300 words**, in three or four short paragraphs.
7. Contain **no em dashes** anywhere. Use commas, periods, or restructure.
8. Pass the operational voice test on every sentence. See [`references/voice-anchor.md`](./references/voice-anchor.md).

**Structure that satisfies this:** opener; one paragraph of strongest proof; one paragraph that is either a second proof arc or the objection-handling; a two-sentence close. Never more than four paragraphs.

## The operational voice test

Apply to every sentence before finalizing:

> *Could this exact sentence appear in a cover letter for a different role at a different company?*

If yes, cut or rewrite it. This single test catches the AI-template smell that vague advice about "sounding human" never does. See [`references/voice-anchor.md`](./references/voice-anchor.md).

## Format

Plain text, no styling, no bold anywhere — including the signature:

```
Dear Hiring Manager,

[body]

Best regards,
Jordan Park
```

The candidate's name comes from `config.yaml`. No bold on any part of the name. No em dashes anywhere in the letter.

## Render to .docx (mandatory)

Drafting the letter as plain text is not the deliverable. Once the text passes every check above:

1. Write the draft as plain text (a `.scratch/` working file, not the session folder — see `${CLAUDE_PLUGIN_ROOT}/shared/conventions.md`).
2. Render it via `python ${CLAUDE_PLUGIN_ROOT}/shared/scripts/text_to_docx.py <draft> <output.docx>`, saving to the path in "Save location" below.
3. The `.docx` is the **only** deliverable. Never leave a `.md` or `.txt` cover letter in the session folder.

If the render fails, that is a failed stage — apply the failure-recovery rules in `job-search-pipeline/references/failure-recovery.md`. A failed render is not a license to ship the markdown draft instead.

## Save location

```
paths.session_output_dir/[session-date]/[Country or City]/Cover Letter - [Company] - [Job Title].docx
```

`[session-date]` is today's date formatted per `paths.session_date_format` (default `dd.mm.yy`, e.g. `11.06.26`).

## LinkedIn recruiter nudge

If the scraped job data identifies a recruiter or job poster (name + title + LinkedIn profile), draft a short DM. Skip any company in the blacklist. The nudge must:

- Be under 80 words
- Open with the specific role name (no generic opener)
- Lead with the strongest 1–2 credentials relevant to that role, no employer named
- Mention current location and immediate availability
- Close with a low-friction ask (offer to send the CV, not a meeting request)
- Contain no em dashes

See [`references/linkedin-nudge.md`](./references/linkedin-nudge.md) for the format and the append-to-file convention.

## Files referenced

- [`references/voice-anchor.md`](./references/voice-anchor.md) — the operational voice test, plus warmth vs. flattery
- [`references/opening-rules.md`](./references/opening-rules.md) — the load-bearing, tight opener
- [`references/objections-and-close.md`](./references/objections-and-close.md) — naming the obvious objection, and the warm close
- [`references/linkedin-nudge.md`](./references/linkedin-nudge.md) — the recruiter DM format
- [`templates/cover-letter.txt.tmpl`](./templates/cover-letter.txt.tmpl)
- [`${CLAUDE_PLUGIN_ROOT}/shared/scripts/text_to_docx.py`](${CLAUDE_PLUGIN_ROOT}/shared/scripts/text_to_docx.py) — markdown → .docx render
