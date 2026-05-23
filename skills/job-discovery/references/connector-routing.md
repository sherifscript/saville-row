# Connector routing — which platform, scraped how

## Primary connectors

Indeed and LinkedIn are the two largest job platforms worldwide; they are the framework's primary connectors. Everything else is an adapter.

- **Indeed** — direct connector. Search by location and keyword set derived from the career file.
- **LinkedIn** — login-gated. **Never scrape LinkedIn with a browser** — login walls and rate limits make it unreliable. Always go through an Apify LinkedIn jobs scraper. Configure the scraper ID in `connectors.yaml`.

## connectors.yaml

```yaml
connectors:
  indeed:
    enabled: true
  apify-linkedin:
    enabled: true
    actor_id: "curious_coder/linkedin-jobs-scraper"   # example; pick a rated, active actor
  apify-wuzzuf:
    enabled: false
    actor_id: "shahidirfan/wuzzuf-jobs-scraper"
  apify-stepstone:
    enabled: false
    actor_id: ""
  apify-seek:
    enabled: false
    actor_id: ""
  apify-hiringcafe:
    enabled: true
    remote_board: true
    actor_id: ""
  apify-weworkremotely:
    enabled: true
    remote_board: true
    actor_id: ""
  apify-remoteok:
    enabled: true
    remote_board: true
    actor_id: ""
  apify-workingnomads:
    enabled: false
    remote_board: true
    actor_id: ""

discovery:
  min_match_score: 5          # roles below this are filtered before CV tailoring
  results_target_per_table: 10
```

The first time job-discovery runs without a `connectors.yaml`, it writes this default and asks the user which connectors to enable and to supply Apify actor IDs.

## Remote-focused connectors

Dedicated remote-job boards aggregate location-independent roles that the geo-keyed primaries surface poorly. The framework ships four as defaults: **HiringCafe**, **We Work Remotely**, **Remote OK**, and **Working Nomads**.

A connector marked `remote_board: true` is invoked **only** for a `Run Remote` search. It is silent for any `Run [Country/City]` search — a remote board has nothing useful to add to a Cairo search. This mirrors how the `regions` field gates regional adapters.

Conversely, a `Run Remote` search invokes: every `remote_board: true` connector that is enabled, **plus** the primary connectors (Indeed, LinkedIn) with their remote filter applied. The primaries still carry remote roles the niche boards miss, so a `Run Remote` search uses both.

`remote_board` and `regions` are mutually exclusive on a connector — a board is either remote-scoped or region-scoped, not both. A connector with neither field runs for every geo search and is skipped for `Run Remote` unless it is a primary.

## Region-specific platform routing

Some regions have dominant local boards worth scraping in addition to the primaries:

- **Egypt** → LinkedIn + Wuzzuf
- **DACH (Germany, Austria, Switzerland)** → LinkedIn + StepStone
- **Australia / NZ** → LinkedIn + Seek
- **`Run Remote`** → LinkedIn + Indeed (remote filter) + every enabled `remote_board` connector (HiringCafe, We Work Remotely, Remote OK, Working Nomads)
- **Everywhere else** → LinkedIn (plus Indeed where Indeed has coverage)

The skill picks the regional adapters automatically based on the target geography, but only uses adapters that are `enabled: true` in `connectors.yaml`.

## Picking an Apify actor

When a platform has no pre-configured actor, choose a highly-rated, actively-maintained Apify actor for that platform. Prefer actors with recent runs, a high success rate, and a clear input schema. Record the chosen actor ID back into `connectors.yaml` so future runs are deterministic.

## Two-table output

Results are presented as two tables:

- **Table 1 — direct connectors** (Indeed)
- **Table 2 — Apify connectors** (LinkedIn, plus any regional adapters; for a `Run Remote` search this table also carries the remote-board connectors)

This separation makes it easy to see which platform produced which leads and to spot when one connector underperformed.

## Partial results vs. failure

A connector **fails** only on a technical error: an error response, a timeout, or zero results after at least one retry. On failure, skip that connector's table for the session and log it.

**Partial results are not a failure.** If a connector returns 2–3 results instead of 10, those results flow through to CV tailoring and cover letters normally. Never skip a table just because the count is lower than expected. Apply the top-N selection rule to whatever was returned.

## Retry rule

If a first search returns fewer than the target (`results_target_per_table`, default 10) relevant results, retry once with an alternative keyword set or search URL. A low yield after one retry is acceptable — proceed with whatever relevant results were found. Note a persistently low yield in the session notes (see `job-search-pipeline/references/session-notes.md`) so future runs in that market have the context.
