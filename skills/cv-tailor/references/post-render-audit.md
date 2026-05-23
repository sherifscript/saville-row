# Post-render audit — the five questions every shipped CV must pass

Before any CV is shipped (saved to the session folder for the user to send), it passes a five-question audit. Three of the checks are editorial; two are programmatic. The programmatic checks are implemented in [`../scripts/audit.py`](../scripts/audit.py) and run automatically. The editorial checks are prompted to the user (or run as model inference).

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

## Running the audit

```python
from audit import run_full_audit

audit_result = run_full_audit(
    rendered_docx_path="CV - Northwind - Senior PM.docx",
    diagnosis_md_path="Diagnosis - Northwind - Senior PM.md",
    content_map=content_map,
    expected_keywords=["workflow automation", "B2B SaaS", "..."],
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
