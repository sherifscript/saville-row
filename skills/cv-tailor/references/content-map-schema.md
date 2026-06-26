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
| `tagline` | string | diagnosis | Format: `[Role Title]  \|  [Pillar 1] · [Pillar 2] · [Pillar 3]`. One pipe between role and pillars; middle dots between pillars. |
| `contact_line_1` | string | regional-headers.yaml | "City, Country \| +phone \| email" |
| `personal_site` | string | regional-headers.yaml | Personal site shown on contact line 2 (e.g. `jordanpark.me`). |
| `linkedin_url` | string | regional-headers.yaml | LinkedIn shown on contact line 2 (e.g. `linkedin.com/in/jordanpark`). |
| `contact_line_2_suffix` | string | regional-headers.yaml | Trailing text after the personal-site / LinkedIn entries; varies by region |
| `summary` | string | diagnosis | 3 sentences, framed in the JD's vocabulary (see SKILL.md "Domain translation"). Sentence 1: scope. Sentence 2: strongest proof point. Sentence 3: differentiator. No employer names. |
| `core_skills` | list of `{label, description}` | diagnosis | 4 skill rows + 1 tools row. Each row: `{"label": "Bold Header", "description": "plain description"}`. Labels are the role's domain vocabulary — the JD's own concepts — not literal restatements of the work (see SKILL.md "Domain translation"). |
| `experiences` | list of experience dicts | diagnosis + career file + branches.yaml | Ordered list. Count = `cv.max_experience_slots` |
| `experiences[i].title` | string | career file + diagnosis | Job title, possibly tailored to the JD's vocabulary |
| `experiences[i].dates` | string | career file | Date range as written in the career file |
| `experiences[i].company` | string | career file | Company name |
| `experiences[i].location` | string | career file | City, Country |
| `experiences[i].bullets` | list[string] | diagnosis | Must clear the substance bar in `SKILL.md` "Write strong bullets": **light-edit** the career-file bullet (don't rewrite it thin), **preserve its concrete specifics** (named clients, numbers, specific nouns), surface the named proof point, lead with ownership + scope, frame in the JD's vocabulary, ~25–40 words. The diagnosis's per-slot proof points say which credential each slot names. Bold: `plain` mode marks `**bold**` only on quantified outcomes and credential proper nouns, never JD keywords (see docxtpl-recipe.md "what to bold"); `labeled` mode opens each bullet with a `**Label:**` lead-in that translates the fact into the JD's vocabulary, followed by a full-substance clause. Check 10 rejects generic fillers that lack a concrete proof point. |
| `msc_degree` | string | career file | Higher/most-recent degree name. |
| `msc_date` | string | career file | Higher degree completion date. |
| `msc_institution` | string | career file | Higher degree institution. |
| `msc_location` | string | career file | Higher degree location (City, Country). |
| `msc_bullets` | list[string] | diagnosis | 1–2 descriptive bullets under the higher degree. 25–40 words each. Markdown bold allowed. |
| `ba_degree` | string | career file | Lower/earlier degree name. |
| `ba_date` | string | career file | Lower degree completion date. |
| `ba_institution` | string | career file | Lower degree institution. |
| `ba_location` | string | career file | Lower degree location (City, Country). |
| `ba_bullets` | list[string] | diagnosis | 1–2 descriptive bullets under the lower degree. Same rules. |
| `additional` | list of `{label, description}` | diagnosis + region | Diagnosis-driven items. Work Authorization included for Western/EU/EEA targets, omitted for Egypt/Gulf. Languages typically last. |

> The `msc_*` / `ba_*` keys are named for the two-degree default. They are
> just "higher degree" and "lower degree" slots — a candidate with one
> degree leaves the `ba_*` keys empty and disables the BA region in the
> template; a candidate with a PhD puts it in the `msc_*` slot.
| `publications` | list of `{title, venue, year, link}` | career file | Only present if `cv.sections` includes `publications` |
| `certifications` | list of `{name, issuer, year}` | career file | Only present if `cv.sections` includes `certifications` |
| `volunteering` | list of `{role, organization, dates, description}` | career file | Only present if `cv.sections` includes `volunteering` |

## Section presence

A key is present in `content_map` only if its section is enabled in `cv.sections`. Templates use `{% if publications %}...{% endif %}` guards on optional sections to avoid rendering empty headers.

## Validation

Before `tpl.render()`, `render_cv.py` runs validate:

- Required keys exist (`tagline`, `contact_line_1`, `summary`, `core_skills`, `experiences`, `msc_bullets`, `ba_bullets`)
- No required key is empty or None
- `experiences` length matches `cv.max_experience_slots`
- No employer name appears in `summary`
- No company name appears in any bullet
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
    "msc_bullets": [
        "MSc in Quantitative Psychology with coursework in panel data econometrics, mixed-effects modeling, and **user research** methodology — directly applied to **activation funnel** analysis at Beta Inc.",
    ],
    "ba_bullets": [
        "BA in Cognitive Science with concentrations in human-computer interaction and decision theory; thesis on attention and engagement in consumer mobile apps.",
    ],
    "additional": [
        {"label": "Work Authorization", "description": "US Citizen, available immediately."},
        {"label": "Languages", "description": "English (native), Korean (conversational)."},
    ],
}
```

This is the content_map that, passed to `tpl.render()` with `autoescape=True`, produces the showcase CV.
