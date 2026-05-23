# Regional headers — what changes by region and why

A regional header is the top of the CV: location, phone, email, citizenship, work authorization. Different regions screen for different signals. Wrong header = automatic rejection in some markets.

## The pattern

Every CV header has two lines:

- **Line 1:** Location | Phone | Email
- **Line 2:** Personal site / LinkedIn | [optional citizenship / work-auth suffix]

The suffix on line 2 is what varies most by region.

## Region-specific rules

### Denmark and EU/EEA

```
Copenhagen, Denmark | +45 XX XX XX XX | candidate@example.com
candidate.me | linkedin.com/in/candidate | EU Citizen
```

The "EU Citizen" suffix matters. Danish employers (and many EU employers, especially in tech) routinely screen out non-EU candidates because sponsorship is expensive and slow. If you are EU-eligible, **say so on line 2**. If you are not, leave it off — saying "requires sponsorship" guarantees a rejection in this market.

### United States / Canada (North America)

```
City, State | +1 XXX XXX XXXX | candidate@example.com
candidate.me | linkedin.com/in/candidate
```

No citizenship or work-auth line by convention. US employers do not expect it on the CV; if asked, candidates disclose during the application. Putting "US Citizen" on the header reads as defensive in this market.

### United Kingdom

```
London, UK | +44 XXX XXX XXXX | candidate@example.com
candidate.me | linkedin.com/in/candidate
```

Same as North America by default. If you have right-to-work, you can add "Right to work in the UK" as a suffix on line 2. If you require visa sponsorship, mention it in the cover letter or application form, not the CV.

### Gulf region (UAE, Saudi Arabia, Qatar, etc.)

```
City, Country | +XXX XXX XXX XXXX | candidate@example.com
candidate.me | linkedin.com/in/candidate | Nationality: [your nationality]
```

Nationality is openly displayed and often required by ATS systems in the Gulf. Different nationalities are treated differently by different employers (this is the reality of the market, however uncomfortable). Be honest.

### Egypt

```
City, Egypt | +20 XXX XXX XXXX | candidate@example.com
candidate.me | linkedin.com/in/candidate | [Nationality] | Military: [status]
```

For male candidates, **military service status is expected**: Exempted, Completed, Postponed, or Not Required. This is a hard filter for many Egyptian employers. Female candidates omit this line.

### Japan, Korea, China — out of scope at v1

These markets use entirely different CV formats (Rirekisho, Shokumukeirekisho, etc.) with photos, age, marital status, family details. The framework does not generate these formats at v1. Candidates targeting these markets should use country-specific tools.

### Anywhere else

If the target region is not in the shipped defaults, the setup wizard prompts the user for the convention. Once defined, it lives in `regional-headers.yaml` and the user can reuse it.

## How the framework picks a region

Three sources, in priority order:

1. **Explicit prompt.** "Tailor a CV for [company] targeting Berlin." → region: EU.
2. **Job posting location.** Pulled from the discovery data. "Stripe — Dublin, Ireland" → region: EU.
3. **User default.** `config.yaml > default_region`. Used when the prompt and posting are silent.

The diagnosis can override by specifying a `target_region:` field, though this is rarely needed.

## Work Authorization in the `additional` section

Separately from the header, the `additional` section can include a Work Authorization item:

```yaml
additional:
  - label: Work Authorization
    description: "EU Citizen, eligible to work in the EU/EEA without sponsorship; available immediately."
```

This is **included** for Western/EU/EEA targets and **omitted** for Egypt/Gulf targets. The setup wizard configures this default; the diagnosis can override per role.

## Regional-headers.yaml schema

```yaml
regions:
  denmark:
    location: "Copenhagen, Denmark"
    phone: "+45 XX XX XX XX"
    email: "candidate@example.com"
    line_2_links:
      - "candidate.me"
      - "linkedin.com/in/candidate"
    line_2_suffix: "EU Citizen"
    additional_work_auth: true     # include Work Authorization in additional section
    additional_work_auth_text: "EU Citizen, eligible to work in the EU/EEA without sponsorship; available immediately."
  egypt:
    location: "Cairo, Egypt"
    phone: "+20 XXX XXX XXXX"
    email: "candidate@example.com"
    line_2_links:
      - "candidate.me"
      - "linkedin.com/in/candidate"
    line_2_suffix: "Egyptian | Military: Exempted"
    additional_work_auth: false
```

## Why this matters

Three rejections seen in the framework's history that the regional header would have prevented:

- Denmark role, no "EU Citizen" → screened out by ATS for "requires sponsorship" assumption
- Egypt role, no military status → manually rejected by HR who could not file the application
- US role, "EU Citizen" suffix → recruiter read it as confusing/foreign, never replied

Regional headers are five seconds of work. They prevent a meaningful share of silent rejections.
