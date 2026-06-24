# Post-render audit — the five questions every shipped CV must pass

Before any CV is shipped (saved to the session folder for the user to send), it passes the audit below. The numbered checks are a mix of editorial and programmatic. The programmatic checks (2, 4, 5, 6, 7, 8, 9) are implemented in [`../scripts/audit.py`](../scripts/audit.py) and run automatically; the editorial checks (1, 3, and the honesty companion to 9) are prompted to the user or run as model inference. The "five questions" framing is historical; the list has grown as new failure modes were caught.

If any check fails, the CV is **not shipped**. The framework either re-renders (for programmatic failures) or prompts the user to regenerate the failing section (for editorial failures).

## The five questions

### 1. Does the lead bullet of the lead experience section serve "what is this team actually hiring to fix?"

**Editorial check.** Read the diagnosis's section 1 (the problem statement) and the lead bullet of the lead experience role. Do they obviously connect?

The check fails when the lead bullet is a generic strength claim ("led cross-functional teams to drive impact") instead of a specific outcome that addresses the diagnosed problem ("shipped the onboarding redesign that lifted 7-day activation from 32% to 38%, the exact funnel cliff Northwind's JD describes").

**On failure:** regenerate the lead experience section. The diagnosis is usually fine; the bullet writer drifted into generic phrasing.

### 2. Do at least two experience bullets contain JD keywords verbatim?

**Programmatic check.** Count occurrences of each diagnosed keyword in the rendered docx (search `word/document.xml`). At least two of the keywords must appear in experience bullets specifically (not just tagline, summary, or core skills).

**On failure:** rewrite one or two bullets to incorporate the missing keywords. This is usually a 60-second fix — the bullet writer used a synonym ("A/B testing infrastructure") where the JD used a specific term ("experimentation platform").

### 3. Could a recruiter read this CV alongside the JD and see the fit immediately, or does it feel like a generic version of my career?

**Editorial check.** This is the gut-check. Read the CV cold. Then read the JD cold. Do they obviously belong together?

The check fails when the CV could plausibly have been submitted for a different role at a different company. Often the diagnosis was weak — too generic, no real point of view on the role — and the CV inherited the genericness.

**Bolding discipline is part of this check.** Scan every bolded phrase in the rendered CV at once. There should be roughly 4–8 bold items total, and every one should be a quantified outcome or a credential proper noun — never a JD keyword. If a phrase is bolded twice, or if most bullets carry a bold phrase, or if a plain skill word like "user research" is bolded, the CV reads as unedited. Fix the `**` markers in the content map (see docxtpl-recipe.md "what to bold") and re-render.

**On failure:** strengthen the diagnosis first (specifically section 4, "which credential speaks loudest to that bar?"), then re-render. Do not patch the CV directly.

### 4. Is every `&` from the content_map present in the rendered docx?

**Programmatic check.** Open `word/document.xml` from the rendered file. Count the `&` characters across all `content_map` values; count `&amp;` in the rendered XML. The check fails only if the rendered count is lower than expected — that means `autoescape=False` stripped ampersands.

Double spaces are **not** a fail criterion. Many templates (OPUS included) legitimately use spaced separators like `  |  ` and `  ·  `. A double space is only meaningful as a *locating aid*: once the count check has already failed, scanning for double spaces inside title rows, skill labels, and bullets points at where the `&` went missing (the 2026-04-28 `Artist & Label` → `Artist  Label` failure mode).

**On failure:** the render was done with `autoescape=False`. Re-render with `autoescape=True`. This should never fail if `render_cv.py` is used as written — the helper enforces autoescape.

**Incident:** 2026-04-28, Believe CV batch. Every `&` silently dropped because `autoescape=False` was the default at the time. The fix was to make `autoescape=True` mandatory in the helper.

### 5. Does the rendered XML actually contain bolded runs inside the experience loop?

**Programmatic check.** Open `word/document.xml`. Count occurrences of `<w:b/>` (paired with `<w:bCs/>`) inside `<w:r>` elements located between the first `experiences` paragraph and the Education section header. If the diagnosis specified bold-worthy phrases for any experience bullet and the count comes back zero, the render failed silently.

The failure mode: the RichText XML gets written inside a `<w:t>` text node instead of as sibling `<w:r>` runs. Word silently ignores it. The user sees empty bullets where the bolded text should be.

**On failure:** re-render. Inspect `convert_content_map()` for the suspect bullet. The trigger has never been definitively pinned, but it typically resolves on a re-render with the same content_map.

**Incident:** 2026-05-11, "Run CV only: General" session. Every bullet containing `**markdown**` rendered as an empty bullet. The BMG CV rendered five days earlier (2026-05-06) used the same template, same loop structure, and same helper, and rendered cleanly. The trigger was never identified — until it is, audit check 5 treats the symptom as the hard gate.

### 6. Does the rendered CV contain any em dashes?

**Programmatic check.** Scan visible text for the em dash character (—). Em dashes are banned from all employer-facing output — CV, cover letter, LinkedIn nudge, interview prep. See `shared/conventions.md`.

**On failure:** locate each em dash in the rendered text and replace it with a comma, period, or restructured sentence. Re-render. Do not ship the CV until the check passes.

### 7. Is the experience section in strict reverse-chronological order, with the primary employer's contiguous block in slots 1 + 2?

**Programmatic check.** Two sub-checks, both must pass:

1. **Reverse-chronological order.** The experience list, when ordered by end date (most recent first, ongoing roles = 9999), must match the order in which the roles appear in the CV. Slot 1 is the most recent role. Slot 2 is the next. And so on.

2. **Contiguous employer block in slots 1 + 2.** If the candidate has two adjacent roles at the same primary employer (e.g., Statista Research Expert + Statista Research Assistant), those two roles must occupy Slots 1 and 2 — and no other role may appear between them. This is the hard rule that prevents visible employment gaps. A CV that puts Atheneum (an ongoing role) in Slot 2 below Statista Expert (ended Oct 2025) violates chronology. A CV that skips the Statista Assistant entirely leaves a gap (2020–2023) that a recruiter will notice immediately.

**On failure:** rebuild the `experiences` list in the content map. Slot 1 = most recent full-time role. Slot 2 = the adjacent role at the same employer (if `continuous_employer_block: true`). Slot 3 = branch-driven choice from `branches.yaml`. Re-render. The check runs against the `content_map.experiences` list before docxtpl rendering; no XML inspection required.

**Incident root cause (2026-05-24 Cairo trial):** `experience-slot-logic.md` had the hard rule; `cv-tailor/SKILL.md` had only a soft one-liner ("adjacent role at the same employer *if applicable*"). The render script read the soft rule and treated the Statista Assistant as droppable. This check ensures the structural failure is caught before the CV ships even if the render script makes the same mistake.

### 8. Is every experience slot tailored to this role, or did a slot ship as boilerplate?

**Programmatic check.** For each slot in `content_map.experiences`, count diagnosed
keywords in that slot's bullets. A slot with zero is the symptom of un-angled
career-file phrasing pasted across CVs. The diagnosis's "Section angles" block now
mandates that at least one keyword/angle reaches every slot, including the lower and
branch slots, so a zero-keyword slot means the mandate was skipped.

**Incident:** 2026-06-14, Denmark batch. The lead Statista slot was tailored per role,
but the Research Assistant slot was identical boilerplate in 6 of 10 CVs and the
Atheneum slot was byte-for-byte identical in all 10. Tailoring effort decayed down the
page because nothing audited below the lead.

**On failure:** give the un-angled slot a Section-angle in the diagnosis and rebuild its
bullets from that angle (a real career-file fact, framed for this role). Do not paste
career-file phrasing verbatim. Re-render. Skipped to manual review when keywords or
bullets are absent.

### 9. Does every number in the CV trace to the career file?

**Programmatic check.** Extract percentages (`\d+%`) and count claims (`\d+\+`) from the
rendered text. Each must have its digit sequence present somewhere in the career file.
Conservative by design: only metrics are checked, and only a total absence of the digits
fails, so a real figure written slightly differently still passes.

This is the truth gate the framework historically lacked ("What the audit does not catch:
Truthfulness"). Widening tailoring raises the temptation to invent a metric that makes a
bullet land; this check refuses it. A bullet may re-frame a real fact; it may not add a
number the career file does not contain.

**Editorial honesty companion (model-run).** The number check cannot see semantic
inflation. Confirm by reading: a contributor role was not upgraded to owner ("supported"
did not become "led"), a team outcome was not claimed as a solo one, a tool used once was
not described as expertise. Same facts-vs-angle line: re-frame what is true, invent
nothing.

**On failure:** remove or correct the unsupported metric/claim, or add the fact to the
career file if it is genuinely real and was simply missing. Re-render.

## Running the audit

```python
from audit import run_full_audit

audit_result = run_full_audit(
    rendered_docx_path="CV - Northwind - Senior PM.docx",
    diagnosis_md_path="Diagnosis - Northwind - Senior PM.md",
    content_map=content_map,
    expected_keywords=["workflow automation", "B2B SaaS", "..."],
    career_file_path="career.txt",   # enables Check 9 numeric grounding
)

if not audit_result.all_passed:
    print(audit_result.failure_summary)
    print("CV not shipped. Fix and re-render.")
else:
    print("CV passed audit. Ready to ship.")
```

See [`../scripts/audit.py`](../scripts/audit.py).

## What the audit does not catch

- **Truthfulness.** The audit cannot tell whether a quantified outcome is real or invented. The framework trusts the career file. If the career file is wrong, the CV will be wrong.
- **Tone.** The audit does not score whether the writing sounds like the candidate. Voice references handle that for the cover letter; the CV is more mechanical and the audit treats it accordingly.
- **Whether you should apply.** Editorial fit, not strategic fit, is the audit's scope.

## The audit's purpose

The audit exists because every named failure mode in this framework's history could have been caught by a fast check. The audit takes ~30 seconds per CV. It catches the failures that otherwise reach the recruiter.

Do not skip it.
