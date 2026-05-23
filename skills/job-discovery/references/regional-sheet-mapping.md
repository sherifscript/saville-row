# Regional sheet mapping — routing rows to country sheets

The job log (`Job Listings.xlsx`) has one sheet per country. Never a city sheet. This file defines how an incoming job row is routed to a sheet.

## The rule

**Sheets are named after the country, always.** The search geography and the sheet target are two different things:

- The **search scope** is whatever the prompt specified — a city, a country, a region.
- The **sheet target** is resolved per row, from the job posting's location.

A "Run Cairo" prompt searches Cairo but routes results to the **Egypt** sheet. A "Run Denmark" prompt searches countrywide and routes to the **Denmark** sheet. A single search can route rows to multiple country sheets if it returned cross-border results.

## Resolving the country from a location string

| Posting location | Sheet |
| --- | --- |
| "Cairo, Egypt" / "Cairo" / "Alexandria" | Egypt |
| "Riyadh" / "Jeddah" / "Saudi Arabia" | Saudi Arabia |
| "Copenhagen" / "Aarhus" / "Denmark" | Denmark |
| "Berlin, Germany" / "Munich" | Germany |
| "London" / "Manchester, UK" | United Kingdom |
| "New York" / "Austin, TX" | United States |
| "Remote, US only" / "Remote within Germany" / any remote role with a country restriction | that country's sheet (US, Germany, ...) |
| "Remote" / "Remote, Worldwide" / "Fully remote" with no country restriction | **Remote** |

For locations not in this table, resolve the country by general knowledge (the city's country) and create the sheet if it does not exist.

## The Remote sheet — the one non-country exception

The **Remote** sheet is the single deliberate exception to the country-naming rule. It exists because a globally-remote role has no meaningful country, and forcing it onto the employer's HQ country would scatter remote roles across sheets and make them impossible to review together.

The test is the *role's* location requirement, not the employer's address:

- A role that can be done from anywhere → **Remote** sheet.
- A role advertised as remote but fenced to a country or region ("Remote, US only", "Remote, EU time zones") → that **country's** sheet, because the work authorization constraint is country-level. For a region fence with no single country (e.g. "Remote, EU"), route to the country the candidate is targeting from `config.yaml`, or to the candidate's own country if unclear.

A `Run Remote` search routes the bulk of its rows to the Remote sheet but may still route country-fenced rows to country sheets. A `Run [Country]` search never routes to the Remote sheet — it routes country-fenced remote roles to that country's sheet like any other row.

The Remote sheet uses the same column order as every country sheet, and is created on first use exactly like a country sheet.

## Folder vs. sheet

The two naming conventions are independent:

- **Sheet** is always country-named (Egypt, Denmark, ...).
- **Session folder** uses whatever the prompt specified. A "Run Cairo" session keeps its CVs and cover letters in `data/sessions/[dd.mm]/Cairo/` even though the rows land on the Egypt sheet.

This is deliberate: the folder reflects the work session; the sheet reflects the permanent country-level record.

## Creating a sheet

If a row resolves to a country with no existing sheet, create the sheet with the standard column order (see `append-only-safety.md`) and append the row. Creating a new sheet is an additive operation and is always allowed.

## Never

- Never create a city-named sheet. (The **Remote** sheet is the only allowed non-country sheet.)
- Never rename an existing sheet.
- Never move rows between sheets.
