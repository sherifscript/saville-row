# Connector setup — wiring job boards, and adding your own

`job-discovery` searches job boards through **connectors**. This guide covers
getting the two primary connectors working, and the plug-and-play pattern for
adding any new board later without touching code.

## What a connector is

A connector is one entry in `connectors.yaml` that tells `job-discovery` how
to reach a job board. There are two kinds:

- **Direct** — the platform is reachable through a connector Claude already
  has (e.g. an Indeed integration). No account or actor ID needed.
- **Apify-backed** — the platform is scraped through an [Apify](https://apify.com)
  actor. Needs an Apify account and an actor ID. LinkedIn, Wuzzuf, StepStone,
  Seek, and most regional boards work this way.

The framework does not care which kind a connector is. It reads
`connectors.yaml`, runs whatever is `enabled: true`, and merges the results.

## One-time setup

### Step 1 — Indeed (direct)

Indeed works through a direct connector. If your Claude environment has an
Indeed integration available, set `indeed.enabled: true` in `connectors.yaml`
and you are done. If it does not, leave it `false` and rely on Apify-backed
connectors instead — nothing else changes.

### Step 2 — Apify account (for LinkedIn and regional boards)

LinkedIn is login-gated and cannot be scraped reliably with a browser. It,
and most regional boards, go through Apify.

1. Create a free account at https://apify.com. The free tier includes a
   monthly usage allowance that covers light job searching; heavier use is
   pay-as-you-go. Check current pricing on their site.
2. Get your Apify API token from the Apify console (Settings → Integrations).
3. Make the Apify connector available to Claude. In Cowork or Claude Code,
   this is done by connecting the Apify MCP — search the connector registry
   for "Apify" and follow the prompts. Claude will ask for your API token.
4. Confirm it works: ask Claude to run a trivial Apify actor. If it returns,
   the connector is live.

### Step 3 — Pick actors and fill in `connectors.yaml`

Each Apify-backed board needs an **actor** — a specific scraper published on
the Apify store. To choose one:

1. Search the Apify store for the platform (e.g. "LinkedIn jobs").
2. Prefer an actor with a high star rating, recent runs, an active maintainer,
   and a clear input schema.
3. Copy its ID — the `username/actor-name` string from its store URL.
4. Put the ID in `connectors.yaml` and set `enabled: true`.

```yaml
connectors:
  indeed:
    enabled: true
  apify-linkedin:
    enabled: true
    actor_id: "curious_coder/linkedin-jobs-scraper"   # verify still active
```

That is the entire setup. Re-run any `Run [Country]` command and the new
connector is in the rotation.

## Adding a new connector — the plug-and-play pattern

You do not need to edit any Python to add a board. A connector is pure
configuration. To add, say, a French board or a niche tech board:

### 1. Add an entry to `connectors.yaml`

```yaml
connectors:
  apify-welcometothejungle:
    enabled: true
    actor_id: "some-author/wttj-jobs-scraper"
    # Optional fields the framework understands:
    regions: ["FR", "EU"]      # only used when the search targets these regions
    platform_label: "Welcome to the Jungle"   # shown in the job log Source column
```

### 2. That is it

`job-discovery` discovers connectors by reading `connectors.yaml` at run time.
Any entry with `enabled: true` and a valid `actor_id` is picked up. There is
no registration step, no code change, no list to update elsewhere.

### Connector entry schema

| Field | Required | Meaning |
| --- | --- | --- |
| `enabled` | yes | Whether to use this connector |
| `actor_id` | for Apify-backed | The Apify actor `username/actor-name` |
| `regions` | no | Restrict this connector to searches targeting these regions. Omit to use it everywhere. |
| `remote_board` | no | `true` marks a dedicated remote-jobs board. Used only for `Run Remote` searches; silent for geo searches. Mutually exclusive with `regions`. |
| `platform_label` | no | Human-readable name written to the job log's Source column. Defaults to the connector key. |

### How regional routing uses `regions`

If a connector lists `regions`, `job-discovery` only invokes it when the
search geography matches. A French board with `regions: ["FR"]` is silent for
a "Run Denmark" search and active for "Run Paris". A connector with no
`regions` field runs for every search. This is how the framework stays fast
as the connector list grows — you can register twenty boards and only the
relevant ones fire per search.

### Remote boards

A connector with `remote_board: true` is the remote-search counterpart of a
regional adapter. It fires **only** for a `Run Remote` search and is silent
for every `Run [Country/City]` search. The framework ships four enabled by
default — HiringCafe, We Work Remotely, Remote OK, Working Nomads — so
`Run Remote` works out of the box once you supply Apify actor IDs for them.
Add another remote board exactly like any connector: a new `connectors.yaml`
entry with `remote_board: true` and an `actor_id`. No code change.

## Failure behavior

A connector that errors, times out, or returns zero after one retry is
skipped for that session and logged. Partial results are not a failure. See
[`connector-routing.md`](./connector-routing.md) for the full rules.

## When an actor breaks

Apify actors are third-party code; they occasionally break or get
deprecated. If a connector that worked last week returns errors:

1. Open the actor's Apify store page — check for a "deprecated" notice or
   recent failure reports.
2. If it is dead, find a replacement actor for the same platform and swap the
   `actor_id` in `connectors.yaml`.
3. No other change is needed — the connector key and everything downstream
   stay the same.

This is why connectors are config, not code: when the scraping landscape
shifts, you edit one line of YAML, not the framework.
