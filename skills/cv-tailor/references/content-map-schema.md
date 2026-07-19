# Content map schema — every key passed to docxtpl.render()

The `content_map` is a dict built by `render_cv.py` from the diagnosis, the candidate's career file, the regional header config, and the branch config. It is the input to `tpl.render(content_map, autoescape=True)`.

## Facts vs angle — the source rule

Two sources, two jobs. Do not confuse them:

- **The career file is the source of FACTS.** Dates, employers, titles held,
  what actually happened, every number and named credential. Nothing in the
  rendered CV may state a fact the career file does not contain.
- **The diagnosis is the source of ANGLE.** For every content field below —
  not just the lead slot — the diagnosis's "Section angles" block decides
  *which* real fact to surface and *how* to frame it for this role.

The failure this rule fixes: when the diagnosis only angled the lead slot, the
builder filled slots 2..N, education bullets, `additional`, and the optional
sections with the career file's existing phrasing verbatim — so those parts
were byte-for-byte identical across every CV (the Atheneum slot was identical
in all ten CVs of the 2026-06-14 Denmark batch). A field marked
"source: diagnosis" below means *angled by the diagnosis*, not copied from the
career file. A field marked "source: career file" is a verbatim fact (a date,
an institution name) and is correctly not re-angled. The post-render audit's
coverage check (Check 8) flags any experience slot that ships un-angled; the
grounding check (Check 9) flags any number or claim with no career-file source.

## Schema

| Key | Type | Source | Notes |
| --- | --- | --- | --- |
| `candidate_name` | string | config.yaml | The candidate's full name. Appears as the CV header name. |
| `tagline` | string | diagnosis | Format: `[Identity]  \|  [Pillar 1] · [Pillar 2] · [Pillar 3]`. One pipe between identity and pillars; middle dots between pillars. The identity follows the diagnosis's Positioning mode — `direct`: the JD's role title; `adjacent`: the real functional identity in the JD's vocabulary (never an unheld seniority/exact title); `transition`: the bridge form `[Real capability identity] \| Transitioning to [Target function]`. See SKILL.md "Positioning drives the frame". |
| `contact_line_1` | string | regional-headers.yaml | "City, Country \| +phone \| email" |
| `personal_site` | string | regional-headers.yaml | Personal site shown on contact line 2 (e.g. `jordanpark.me`). |
| `linkedin_url` | string | regional-headers.yaml | LinkedIn shown on contact line 2 (e.g. `linkedin.com/in/jordanpark`). |
| `contact_line_2_suffix` | string | regional-headers.yaml | Trailing text after the personal-site / LinkedIn entries; varies by region |
| `summary` | string | diagnosis | 3 sentences, framed in the JD's vocabulary (see SKILL.md "Domain translation"). Sentence 1: scope. Sentence 2: strongest proof point. Sentence 3: differentiator. No employer names. |
| `core_skills` | list of `{label, description}` | diagnosis | 4 skill rows + 1 tools row. Each row: `{"label": "Bold Header", "description": "plain description"}`. Labels are the role's domain vocabulary — the JD's own concepts — not literal restatements of the work (see SKILL.md "Domain translation"). |
| `experiences` | list of experience dicts | diagnosis + career file + branches.yaml | Ordered list. Count = `cv.max_experience_slots` (a `transition`-positioned diagnosis may add one slot — see experience-slot-logic.md) |
| `experiences[i].title` | string | career file + diagnosis | Job title, possibly tailored to the JD's vocabulary |
| `experiences[i].dates` | string | career file | Date range as written in the career file |
| `experiences[i].company` | string | career file | Company name |
| `experiences[i].location` | string | career file | City, Country |
| `experiences[i].end_year` | int | career file | **Required.** The role's end year; `9999` for an ongoing (Present) role. Feeds the Check 7 chronology gate — validation rejects a map without it (the old skip-when-absent behavior was exploitable). |
| `experiences[i].concurrent` | bool | career file | Optional, default false. Mark `true` on an ongoing *side* engagement (e.g. freelance) that overlaps the primary block, so chronology checks treat it as concurrent rather than out of order. |
| `experiences[i].bullets` | list[string] | diagnosis | Must clear the substance bar in `SKILL.md` "Write strong bullets": **light-edit** the career-file bullet (don't rewrite it thin), **preserve its concrete specifics** (named clients, numbers, specific nouns), surface the named proof point, lead with ownership + scope, frame in the JD's vocabulary, 25–40 words (a floor on substance — validation rejects any bullet under 12 clause-words and any CV averaging under 20). The diagnosis's per-slot proof points say which credential each slot names. Bold: `plain` mode marks `**bold**` only on quantified outcomes and credential proper nouns, never JD keywords (see docxtpl-recipe.md "what to bold"); `labeled` mode opens each bullet with a `**Label:**` lead-in that translates the fact into the JD's vocabulary, followed by a full-substance clause. Check 10 rejects generic fillers that lack a concrete proof point. |
| `degrees` | list of degree dicts | career file + diagnosis | **Every** degree in the career file, most recent first — including an in-progress degree ("Expected [year]") and the undergraduate degree. Dropping one is the Check 12 failure mode (the 2026-07-14 CV shipped without the BA). |
| `degrees[i].name` | string | career file | Degree name (e.g. "MSc Quantitative Analysis and Social Data Science"). |
| `degrees[i].date` | string | career file | Completion date, or "Expected [year]" for an in-progress degree. |
| `degrees[i].institution` | string | career file | Institution name. |
| `degrees[i].location` | string | career file | City, Country. |
| `degrees[i].bullets` | list[string] | diagnosis | 1–3 descriptive bullets per degree, 25–40 words each, same substance bar as experience bullets. Markdown bold allowed. |
| `additional` | list of `{label, description}` | diagnosis + region | Diagnosis-driven items. Work Authorization included for Western/EU/EEA targets, omitted for Egypt/Gulf. Languages typically last. |
| `publications` | list of `{title, venue, year, link}` | career file | Only present if `cv.sections` includes `publications` |
| `certifications` | list of `{name, issuer, year}` | career file | Only present if `cv.sections` includes `certifications` |
| `volunteering` | list of `{role, organization, dates, description}` | career file | Only present if `cv.sections` includes `volunteering` |

> The pre-v1.9.0 `msc_*` / `ba_*` keys are retired: the fixed two-slot form
> forced a three-degree candidate to drop one, and the drop was silent.
> Validation now rejects those keys outright — put every degree in
> `degrees`, however many there are.

## Bullets are plain strings — always

Every bullet value is a **plain string** carrying optional `**bold**` markers.
The render pipeline strips the markers before `tpl.render()` and applies bold
afterwards via `postprocess_cv()` — a `RichText` object anywhere in the
content_map is a hard error (`build_bold_plan` raises). RichText through the
template's plain placeholders was the 2026-05-11 / test5 corruption that
rendered every bullet invisible; see docxtpl-recipe.md "RichText is banned
from the render path".

## Section presence

A key is present in `content_map` only if its section is enabled for the
render. Section enablement = `cv.sections` (or the default list) minus any
`cv.region_section_overrides[region]` entries set to `false` — resolved by
`render_cv.effective_sections(config, region)`. A region-disabled section
(e.g. `EU: summary: false`) is removed from the rendered document by the
postprocess pass; its content_map key may be omitted entirely.

## Validation

Before `tpl.render()`, `render_cv.py` runs validate:

- Required keys exist (`candidate_name`, `tagline`, `contact_line_1`,
  `core_skills`, `experiences`, `degrees`; `summary` only when the summary
  section is enabled for the target region)
- No required key is empty or None
- The retired `msc_*` / `ba_*` keys are absent (hard error with a migration
  hint when present)
- Every degree has `name`, `date`, `institution`, `location`, and >= 1 bullet
- `experiences` length matches `cv.max_experience_slots` (+1 allowed only in
  `transition` positioning)
- Every experience has an integer `end_year` (9999 = Present)
- Bullet count floors (near-full career-file density): lead slot >= 5
  bullets, slot 2 >= 4, slot 3 and later >= 3. `cv.bullet_floors` overrides
  them only when the career file itself has fewer bullets, never to trim
  rich material
- Bullet length floors (written-thin guard, v2.0.0): every experience
  bullet's substance clause >= 12 words (label lead-in excluded in labeled
  mode) and the section-wide average >= 20 words. Career-file bullets run
  ~25–40; a CV that fails this was compressed, not tailored
- In `labeled` mode, every experience bullet opens with a `**Label:**` lead-in
- No employer name appears in `summary`
- No company name appears in any bullet
- No em dash in any content_map value (banned in employer-facing output)
- `contact_line_1` and `contact_line_2_suffix` match the target region

If validation fails, render aborts with the specific failure.

## Example

```python
content_map = {
    "tagline": "Senior Product Manager  |  Activation · Workflow Automation · B2B SaaS",
    "contact_line_1": "Brooklyn, NY | +1 718 555 0142 | jordan.park@example.com",
    "contact_line_2_suffix": "",
    "summary": "Senior product manager with 8 years shipping consumer and enterprise products across mobile and web. Most recent work redesigned the onboarding funnel at a 15M-user consumer app, lifting 7-day activation 18% in a single quarter and earning a TechCrunch writeup. Strong at translating quantitative funnel insights into roadmap priorities cross-functional teams will defend.",
    "core_skills": [
        {"label": "Product-led growth", "description": "experimentation platform design, activation funnels, retention loops"},
        {"label": "Roadmap ownership", "description": "stakeholder management across engineering, design, and GTM"},
        {"label": "User research", "description": "qualitative interviewing, usability testing, JTBD frameworks"},
        {"label": "Cross-functional delivery", "description": "shipping in 2-week iterations, async-first remote teams"},
        {"label": "Tools", "description": "Amplitude, Mixpanel, Looker, Linear, Figma, dbt"},
    ],
    "experiences": [
        {
            "title": "Senior Product Manager — Activation",
            "dates": "March 2024 – Present",
            "company": "Beta Inc",
            "location": "Brooklyn, NY",
            "bullets": [
                "Shipped onboarding redesign that lifted **7-day activation from 32% to 38%** in one quarter; covered in **TechCrunch** as a case study on **product-led growth** at scale.",
                "Built and ran the **experimentation platform** that now powers 40+ concurrent tests across 7 product surfaces; reduced average time-from-hypothesis-to-readout from 3 weeks to 6 days.",
                "Owned the **roadmap** for the onboarding and activation surfaces, including quarterly OKRs, **stakeholder management** across engineering, design, marketing, and analytics.",
            ],
        },
        # ... two more experience entries
    ],
    "degrees": [
        {
            "name": "MSc in Quantitative Psychology",
            "date": "2019",
            "institution": "NYU",
            "location": "New York, NY",
            "bullets": [
                "Coursework in panel data econometrics, mixed-effects modeling, and **user research** methodology, directly applied to **activation funnel** analysis at Beta Inc.",
            ],
        },
        {
            "name": "BA in Cognitive Science",
            "date": "2016",
            "institution": "Reed College",
            "location": "Portland, OR",
            "bullets": [
                "Concentrations in human-computer interaction and decision theory; thesis on attention and engagement in consumer mobile apps.",
            ],
        },
    ],
    "additional": [
        {"label": "Work Authorization", "description": "US Citizen, available immediately."},
        {"label": "Languages", "description": "English (native), Korean (conversational)."},
    ],
}
```

This is the content_map that, passed to `tpl.render()` with `autoescape=True`, produces the showcase CV.
