# Shortcut commands — the DSL

The pipeline owns a small command grammar. Each command is a one-line invocation that runs a defined slice of the pipeline.

## `Run [Country/City]`

Full pipeline for a geography. `Run Denmark`, `Run Cairo`, `Run Berlin`.

- Geography is the **search scope**. Sheet routing is still per-row by country (see `job-discovery/references/regional-sheet-mapping.md`).
- If no branch is given and `branches.yaml` has multiple branches, present a numbered branch menu (including "General") and wait for a pick. Skip the menu in unattended runs — search broadly.
- Runs: discovery → diagnosis (top-N) → cv-tailor → cover-letter → nudges → session notes.

## `Run [Country] | [Branch]`

Same as above, scoped to a branch. `Run Denmark | Product Management`. The branch sets the third CV experience slot and biases the search keywords.

## `Run Remote` and `Run Remote | [Branch]`

Full pipeline for location-independent roles. `Run Remote`, `Run Remote | Product Management`.

- **Search scope is remote-first.** It searches the dedicated remote boards configured in `connectors.yaml` (HiringCafe, We Work Remotely, Remote OK, Working Nomads by default) **and** applies the remote filter on the primary connectors (Indeed, LinkedIn). See `job-discovery/references/connector-routing.md`.
- **Sheet routing:** a globally-remote role with no country restriction routes to the **Remote** sheet — the one deliberate exception to country-named sheets. A remote role that *is* country-restricted ("Remote, US only", "Remote within Germany") routes to that country's sheet instead. See `job-discovery/references/regional-sheet-mapping.md`.
- **Session folder:** `paths.session_output_dir`/[session-date]/Remote/.
- Branch menu and the rest of the pipeline (diagnosis → cv-tailor → cover-letter → nudges → session notes) are identical to `Run [Country]`.

Natural-language variants map to this command: "run the workflow remote", "run remote jobs", "search remote", "find me remote roles" all resolve to `Run Remote`. If a branch is named in the same breath ("run remote product management"), treat it as `Run Remote | Product Management`.

## `Run CV only: [Branch or General]`

Skip discovery and diagnosis. Produce one untailored CV using the branch context (or broad judgment if `General`).

- Present the region menu, wait for a pick, then use that region's header.
- No JD, so the diagnosis step (role-diagnosis) is skipped — generate the content map from broad branch judgment.
- Save to `paths.session_output_dir`/[session-date]/[Branch] CV.docx (or `General CV.docx`). No country subfolder.

## `Run Request: [URL], [URL], [URL]`

Process specific job postings. Skip the discovery search and the branch menu. For each URL:

- Scrape the posting (Indeed/Apify, not a browser).
- Check the company against the blacklist; skip blacklisted, notify the user.
- Resolve the target country from the posting location.
- Score against the career file.
- Dedup-check against the country sheet; append non-duplicates. Create the sheet if needed.
- Set `Source` to `Request` (append the inferred branch in parentheses if one is clear: `Request (Product Management)`).
- Run full diagnosis → cv-tailor → cover-letter.
- Save to `paths.session_output_dir`/[session-date]/Requests/.

## `Run Blacklist: add [Company], [Company]`
## `Run Blacklist: remove [Company], [Company]`

Edit `paths.assets_dir`/Blacklist.txt. Confirm the change. No other pipeline steps run.

## `Run Interview Prep: [Company], [Job Title]`

Invoke the `interview-prep` skill. Pull the JD from the job log's Apply Link if the role is logged, else search. Produce the prep document in `paths.interview_prep_dir`/.

## `Run Story Bank Refresh`

Invoke the `story-bank` skill's refresh protocol. Extract new STAR+R stories from the career file into `paths.assets_dir`/Interview Story Bank.txt. No duplicates, no invention.

## Extending the DSL

New commands follow the same shape: a `Run [Verb]: [args]` line that maps to a defined pipeline slice. Document any new command here, and update the skill router table in `job-search-pipeline/SKILL.md`.
