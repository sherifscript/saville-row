# Post-render audit — the checks every shipped CV must pass

Before any CV is shipped (saved to the session folder for the user to send), it passes the audit below. The programmatic checks (2, 4, 5, 6, 7, 8, 9, 10, 11) are implemented in [`../scripts/audit.py`](../scripts/audit.py) and run automatically by `run_full_audit()`. The editorial checks (1, 3, and the honesty companion to 9) are graded by the model — and since v1.8.0 they are **required**: `run_full_audit()` seeds them as failed, and `all_passed` stays False until the model records a one-line verdict for each via `result.record_editorial(name, ok, note)`. A CV can no longer pass by omission (the 2026-06-27 Berlin batch shipped with the editorial checks silently skipped). Recording the verdicts is authoring work, not a pause — it never stops a batch run.

There is also a batch-level sweep (12, warn-only) that runs once per session folder, not per CV.

If any check fails, the CV is **not shipped**. The framework either re-renders (for programmatic failures) or regenerates the failing section from the diagnosis (for editorial failures).

## The five questions

### 1. Does each lead slot serve "what is this team actually hiring to fix?" with a named proof point, not a generic noun?

**Editorial check.** Read the diagnosis's section 1 (the problem statement) and the bullets of the lead experience slots. Two things must hold:

1. The lead bullet is a specific outcome that addresses the diagnosed problem, not a generic strength claim. Fail: "led cross-functional teams to drive impact". Pass: "shipped the onboarding redesign that lifted 7-day activation from 32% to 38%, the exact funnel cliff Northwind's JD describes".

2. Each lead slot **names the concrete proof point** the diagnosis assigned it (the institution, client, platform, or number), rather than hiding behind a generic noun. Fail: "tracked positioning for enterprise decision-makers". Pass: "synthesized findings into reports cited by Deloitte and the Harvard Law Review". This is the gap that shipped the 2026-06-25 Cairo batch: the named credentials sat unused in the career file while the bullets used generic audiences. Check 10 catches the named filler phrases programmatically; this editorial check is the broader judgment that a real proof point is actually surfaced.

**On failure:** regenerate the failing slot from its diagnosis proof point. The diagnosis is usually fine; the bullet writer drifted into generic phrasing or left the proof point on the table.

**Recording the verdict (required):** after the programmatic audit returns, call `result.record_editorial('check_1_lead_slots', ok, note)` with a one-line verdict. `all_passed` stays False until it is recorded.

### 2. Do at least two experience bullets contain JD keywords verbatim?

**Programmatic check.** Count diagnosed keywords in the **experience bullets** (the authored bullet strings — Check 5 guarantees they match the rendered document). At least two distinct keywords must appear there specifically; keywords that live only in the tagline, summary, or core skills do not count. (The pre-v1.8.0 implementation searched the whole document and contradicted this spec.)

**On failure:** rewrite one or two bullets to incorporate the missing keywords. This is usually a 60-second fix — the bullet writer used a synonym ("A/B testing infrastructure") where the JD used a specific term ("experimentation platform").

### 3. Could a recruiter read this CV alongside the JD and see the fit immediately, or does it feel like a generic version of my career?

**Editorial check.** This is the gut-check. Read the CV cold. Then read the JD cold. Do they obviously belong together?

The check fails when the CV could plausibly have been submitted for a different role at a different company. Often the diagnosis was weak — too generic, no real point of view on the role — and the CV inherited the genericness.

Three things to judge explicitly, because a CV can pass every programmatic check and still be weak here:

1. **Richness / substance.** Does each experience bullet keep the *concrete specifics* from the career file (named clients, exact numbers, specific nouns), or has it been compressed into category-nouns? The failure pattern: a real, specific fact ("monitored COVID-19 incidence and vaccine-trial data across US and Canadian regions, used by governments and media") rewritten thin ("engineered workflows across high-frequency publication cycles"). If a bullet is markedly shorter and vaguer than its career-file source, it was over-compressed — send it back to the substance bar in `../SKILL.md` "Write strong bullets".
2. **Domain translation.** Are the capability labels, core-skill labels, and summary written in the JD's own vocabulary (the diagnosis's verbatim keywords), or are they literal restatements of the work? Labels like "Methodology under deadline" / "Structured under pressure" are the weak pattern; the JD's concepts framing a real fact ("Time-to-Value", "Competitive Landscape Mapping") are the bar. See `../SKILL.md` "Domain translation".
3. **Could a recruiter without the title still see the fit?** The strongest tailoring makes adjacent experience read as the thing this team hires for, while every fact still traces to the career file (Check 9 guards the line). If the translation is missing, strengthen the diagnosis's "Section angles" framing and re-render.

**Bolding discipline is part of this check (plain mode).** Scan every bolded phrase in the rendered CV at once. There should be roughly 4–8 bold items total, and every one should be a quantified outcome or a credential proper noun — never a JD keyword. If a phrase is bolded twice, or if most bullets carry a bold phrase, or if a plain skill word like "user research" is bolded, the CV reads as unedited. Fix the `**` markers in the content map (see docxtpl-recipe.md "what to bold") and re-render. In `bullet_style: labeled` this part is suspended: every bullet is supposed to open with a bold capability label, so the 4–8 ceiling does not apply; instead confirm each label is a 2–5 word capability phrase in the role's vocabulary, not a dumped JD keyword.

**On failure:** strengthen the diagnosis first (specifically section 4, "which credential speaks loudest to that bar?"), then re-render. Do not patch the CV directly.

**Recording the verdict (required):** call `result.record_editorial('check_3_recruiter_fit', ok, note)` with a one-line verdict covering richness, domain translation, and the honesty companion (no semantic inflation). `all_passed` stays False until it is recorded.

### 4. Is every `&` from the content_map present in the rendered docx?

**Programmatic check.** Open `word/document.xml` from the rendered file. Count the `&` characters across all `content_map` values; count `&amp;` in the rendered XML. The check fails only if the rendered count is lower than expected — that means `autoescape=False` stripped ampersands.

Double spaces are **not** a fail criterion. Many templates (OPUS included) legitimately use spaced separators like `  |  ` and `  ·  `. A double space is only meaningful as a *locating aid*: once the count check has already failed, scanning for double spaces inside title rows, skill labels, and bullets points at where the `&` went missing (the 2026-04-28 `Artist & Label` → `Artist  Label` failure mode).

**On failure:** the render was done with `autoescape=False`. Re-render with `autoescape=True`. This should never fail if `render_cv.py` is used as written — the helper enforces autoescape.

**Incident:** 2026-04-28, Believe CV batch. Every `&` silently dropped because `autoescape=False` was the default at the time. The fix was to make `autoescape=True` mandatory in the helper.

### 5. Is every authored bullet actually READABLE in the rendered file?

**Programmatic check — rendered-text integrity** (`check_5_rendered_integrity`).
Open the rendered .docx with **python-docx** — the same parse Word and ATS
systems perform — and assert:

1. every authored experience bullet appears as a whole, non-empty paragraph,
   in order; per-slot readable counts match the content map;
2. the same for `msc_bullets` / `ba_bullets`;
3. no paragraph text contains raw markup (`<w:`) or leftover `**` markers;
4. when bold was planned (`bullet_style: labeled` or `inline_bold: true`),
   each planned span's text is covered by a run with `run.bold` True — real
   run inspection, not a regex;
5. the contact hyperlinks survived the postprocess round-trip (>= 2 hyperlink
   relationships in `word/_rels/document.xml.rels`).

**This supersedes the old bold-run regex count**, which could never fail on
the OPUS template (its section headers are themselves bold, so the count was
always non-zero) and therefore passed the corruption it was written to catch.

**The failure mode it exists for:** docxtpl `RichText` passed through the
template's plain `{{ bullet }}` placeholder embeds run-XML inside `<w:t>` —
invalid OOXML that Word/python-docx/ATS read as an **empty paragraph**, while
the text stays visible to a raw-XML regex. An empty bullet paragraph in a
rendered CV is a hard render failure. Full mechanism and the pinned trigger:
`docxtpl-recipe.md` "RichText is banned from the render path".

**On failure:** do not re-render and hope. The render path passed a non-string
bullet (RichText) or the postprocess pass did not run. Fix the driver to use
`build_bold_plan()` + `postprocess_cv()` (or simply `render_cv.render()`),
then re-render.

**Incidents:** 2026-05-11 ("Run CV only: General" — every `**markdown**`
bullet empty; trigger unpinned at the time); 2026-06-25 Cairo and 2026-06-27
Berlin (every labeled-mode CV in both batches shipped blank experience
sections with a passing audit). The trigger is now pinned and the render path
redesigned so the corruption cannot recur silently.

### 6. Does the rendered CV contain any em dashes?

**Programmatic check.** Scan visible text for the em dash character (—). Em dashes are banned from all employer-facing output — CV, cover letter, LinkedIn nudge, interview prep. See `shared/conventions.md`.

**On failure:** locate each em dash in the rendered text and replace it with a comma, period, or restructured sentence. Re-render. Do not ship the CV until the check passes.

### 7. Is the experience section in strict reverse-chronological order, with the primary employer's contiguous block in slots 1 + 2?

**Programmatic check.** Two sub-checks, both must pass:

1. **Reverse-chronological order.** The experience list, when ordered by end date (most recent first, ongoing roles = 9999), must match the order in which the roles appear in the CV. Slot 1 is the most recent role. Slot 2 is the next. And so on.

2. **Contiguous employer block in slots 1 + 2.** If the candidate has two adjacent roles at the same primary employer (e.g., Statista Research Expert + Statista Research Assistant), those two roles must occupy Slots 1 and 2 — and no other role may appear between them. This is the hard rule that prevents visible employment gaps. A CV that puts Atheneum (an ongoing role) in Slot 2 below Statista Expert (ended Oct 2025) violates chronology. A CV that skips the Statista Assistant entirely leaves a gap (2020–2023) that a recruiter will notice immediately.

**`end_year` is mandatory (v1.8.0).** Every experience entry must carry an integer `end_year` (9999 = Present); a missing one now FAILS the check instead of skipping it — the old skip-on-absence let the 2026-06-27 Berlin driver bypass chronology entirely by passing no end years. An ongoing SIDE engagement that legitimately sits below the primary block (e.g. concurrent freelance work) sets `concurrent: true` and is exempted from the reverse-chronology sort — but not from the contiguous-block rule.

**On failure:** rebuild the `experiences` list in the content map. Slot 1 = most recent full-time role. Slot 2 = the adjacent role at the same employer (if `continuous_employer_block: true`). Slot 3 = branch-driven choice from `branches.yaml`; mark it `concurrent: true` if it is an ongoing side engagement. Re-render. The check runs against the `content_map.experiences` list before docxtpl rendering; no XML inspection required.

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

**Programmatic check.** Extract metrics from the rendered text — percentages
(`30%`), count claims (`40+`), currency amounts (`$30K`, `$2M`, `$1,500`),
K/M/B magnitudes (`11M`, `2.5B`), and written magnitudes (`11 million`). Each
must have its digit sequence present somewhere in the career file (checked
against both the raw text and a digits-only squash, so `$30,000` grounds
`30000`). Deliberately excluded: bare integers, years, and letter-digit
tokens (`B2`, `Phase III`) — flagging those would fail legitimate dates and
language levels. Conservative by design: only a total absence of the digits
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

### 10. Does any *ungrounded* bullet hide behind a generic abstraction instead of a named proof point?

**Programmatic check.** Scan every experience bullet for a short blocklist of generic
filler phrases ("enterprise decision-makers", "global process owners", "analytical
workstreams", "client-ready", "evidence-based reports", "actionable insights /
recommendations"). A phrase fails the CV **only when the bullet carrying it has no
concrete proof of its own** — no number and no named entity. A grounded bullet may keep
one of these phrases ("managed analytical workstreams for 40+ multinationals across
Technology and Telecom" is strong; the phrase is incidental). This is deliberate: the
earlier unconditional substring ban was the v1.6.0 over-correction that pushed bullets
toward thin paraphrase, failing the exact phrasing the rich benchmark CVs use legitimately.

This is the programmatic floor under the editorial bar in checks 1 and 3 and in `SKILL.md`
"Write strong bullets". It does not, on its own, prove the proof point was surfaced (that
judgment is checks 1/3 plus the diagnosis's per-slot proof points); it catches the
specific way the 2026-06-25 Cairo batch failed — *thin* bullets defaulting to a generic
audience with no number or named credential anywhere in them.

**Proof-density floor (v1.8.0, career file supplied).** Beyond the phrase
blocklist, each slot must clear a density floor: slots with 3+ bullets need
**at least 2 proofed** bullets; 2-bullet slots need at least 1. "Proofed"
means the bullet carries a digit or a capitalized token that actually appears
in the career file — minus a stoplist of sector/language nouns (Technology,
Telecom, Media, English, ...) that the old heuristic wrongly counted as
grounding. One interpretive/ungrounded bullet per 3-bullet slot is allowed
**by design**: that is the domain-translation pattern, not a defect. Without
a career file the floor is skipped and detection falls back to the old
heuristic.

**On failure:** either ground the flagged bullet with the named credential or metric the
diagnosis assigned that slot, or drop the abstraction — then re-render. Implemented as
`check_10_bullet_strength` (with `_is_proofed` / `_career_whitelist`) in
[`../scripts/audit.py`](../scripts/audit.py).

### 11. Does each slot surface the proof point the diagnosis assigned it?

**Programmatic check.** Parse the `- Slot N ... | proof point: ...` lines
from the Diagnosis.md (the file is the source of truth — a model-copied field
would be a dodge surface), extract each proof point's distinctive tokens
(numbers/metrics and career-grade capitalized phrases), and require at least
one to appear (word-bounded, case-insensitive) in that slot's rendered
bullets.

Check 8 proves a slot carries *a* keyword; this proves the slot carries *its
assigned credential*. It catches the observed drift where the lead slot's
"+30% publication speed" proof point silently fell out of the rendered
bullets while everything else still passed (2026-06-27 Berlin batch).

A proof point written as `none` — or one with no distinctive token (e.g.
"data used by institutions, governments, media") — is **skipped loudly**
(named in the note), never false-failed. Skipped entirely when no diagnosis
file is supplied (`Run CV only`).

**On failure:** put the named credential/metric back into one of the slot's
bullets, or fix the diagnosis if the assignment genuinely changed — then
re-render. Implemented as `check_11_proof_points` in
[`../scripts/audit.py`](../scripts/audit.py).

### 12. Batch sameyness sweep (per session folder, WARN only)

**Batch-level, not part of `run_full_audit`.** After the last CV of a batch,
`python audit.py --sameyness <session folder>` scans every `CV - *.docx` for
exact-duplicate experience bullets across different CVs — both whole bullets
and identical clauses hiding behind different capability labels.

Warn-only by design: reusing a true fact across two similar JDs is sometimes
legitimate. The sweep exists so cross-CV duplication is a **visible choice in
the closing summary**, not silent drift (2026-06-14 Denmark: one slot
byte-identical across all ten CVs, discovered only by a later investigation).
Implemented as `scan_batch_sameyness` in [`../scripts/audit.py`](../scripts/audit.py);
wired into the pipeline's closing summary.

## Running the audit

```python
from audit import run_full_audit

audit_result = run_full_audit(
    rendered_docx_path="CV - Northwind - Senior PM.docx",
    diagnosis_md_path="Diagnosis - Northwind - Senior PM.md",  # Check 11 reads it
    content_map=content_map,          # post-build_bold_plan (plain strings)
    expected_keywords=["workflow automation", "B2B SaaS", "..."],
    career_file_path="career.txt",    # enables Checks 9 + 10 grounding
    bold_plan=bold_plan,              # from build_bold_plan(); Check 5 bold
)

# REQUIRED: record the editorial verdicts — all_passed stays False otherwise.
audit_result.record_editorial(
    "check_1_lead_slots", True,
    "lead bullets serve the diagnosed dashboard-consolidation problem; "
    "the 30% pipeline proof point leads slot 1")
audit_result.record_editorial(
    "check_3_recruiter_fit", True,
    "bullets keep the career-file specifics; labels frame in JD vocabulary; "
    "no semantic inflation")

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
