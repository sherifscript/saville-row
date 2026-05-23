# Connectors

## How tool references work

Plugin files use `~~category` as a placeholder for whatever tool the user
connects in that category. The plugin describes workflows by category, not
by specific product.

When you see `~~job board` in a skill description, substitute the job board
you have configured (e.g. Indeed, LinkedIn). When you see `~~web scraper`,
substitute the scraping platform you use (e.g. Apify).

## Connectors for this plugin

| Category      | Placeholder     | Options                                                                     |
| ------------- | --------------- | --------------------------------------------------------------------------- |
| Job board     | `~~job board`   | Indeed, LinkedIn, StepStone, Wuzzuf, Seek, HiringCafe, We Work Remotely, Remote OK, Working Nomads |
| Web scraper   | `~~web scraper` | Apify                                                                       |

## Default configuration

The default setup uses **Indeed** (direct connector — no external account
needed) and **LinkedIn via Apify** (Apify account required; LinkedIn is
login-gated and cannot be scraped directly). All other ~~job boards are
opt-in adapters configured in `connectors.yaml`.

## Configuring connectors

1. Copy `shared/connectors.example.yaml` to `connectors.yaml` at your project root.
2. Set `enabled: true` for each ~~job board you want to use.
3. For ~~web scraper connectors: add the actor ID from your ~~web scraper platform.
4. Run `set up saville-row` (the `job-search-setup` skill) to have the wizard
   guide you through connector setup interactively.

See `skills/job-discovery/references/connector-setup.md` for the full setup guide.
