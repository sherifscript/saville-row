# Deduplication and blacklist rules

Two filters run before any result is appended or processed: the blacklist filter and the deduplication check.

## Blacklist filter

`data/Blacklist.txt` — one company name per line. Loaded into memory at session start.

Before scoring or presenting any result, remove every listing where the Company Name matches a blacklist entry. Blacklisted companies appear in **nothing** — not the results table, not the job log, not the CV-tailoring shortlist, not the LinkedIn nudges.

Matching is case-insensitive and tolerant of common suffixes ("Acme", "Acme Inc", "Acme Corp" all match a blacklist entry of "Acme"). When in doubt, flag a near-match to the user rather than silently including or excluding.

`Run Blacklist: add [Company], [Company]` and `Run Blacklist: remove [Company], [Company]` edit the file and confirm the change. No other workflow steps run for these commands.

## Deduplication check

Before appending results, open the target country sheet (if it exists) and check each incoming result against existing rows.

**A duplicate** is any row where **both** the Company Name and the Job Title match an incoming result. Exclude duplicates entirely — do not append them, and do not include them in the top-N shortlist for CV tailoring or cover letters.

**A possible duplicate** is a same-company role with a slightly different title ("Senior Marketing Manager" vs. "Marketing Manager, Senior"). Do not silently drop these. Flag them in a note to the user, and exclude them from processing unless the user says otherwise.

## Why deduplication is strict

The job log is a permanent record built up over many sessions. Without deduplication, the same role reappears every time its market is searched, the log bloats, and the candidate wastes effort re-tailoring a CV for a role they already applied to. The dedup check is what keeps the log a clean record of distinct opportunities.

## Order of operations

1. Search connectors.
2. Apply the **blacklist filter** — remove blacklisted companies.
3. Score the survivors (Match Score).
4. Back up the job log (see `append-only-safety.md`).
5. Apply the **deduplication check** against the target sheet.
6. Append non-duplicate, non-blacklisted results.

The blacklist filter runs before scoring (no point scoring a company the candidate will never join). The dedup check runs after the backup and before the append (it needs to read the current sheet).
