# Session notes — the running log of what went wrong

`data/Session Notes.txt` is the framework's institutional memory. It records anything unexpected so future sessions in the same market have the context.

## When to write an entry

After any session where something deviated from the expected workflow:

- Low job yield in a market
- Language barriers (e.g., a market where most postings are not in English)
- Connector failures (Apify timeout, Indeed returned nothing)
- The job log was locked and the unattended fallback was used
- Any market-specific limitation worth knowing next time

A clean, uneventful session does not need an entry.

## The format

```
[session-date] — [Country or City] ([Branch if applicable])
What happened: [brief description]
Impact: [effect on the session outcome]
Action taken: [how you proceeded]
Recommendation: [guidance for future runs in this market or situation]
---
```

## Example entry

```
20.05.26 — Copenhagen (Product Management)
What happened: LinkedIn via Apify returned only 4 results for senior PM
roles; Indeed returned 9. Retry with broader keywords added 2 more.
Impact: Table 2 had 6 results instead of the target 10. Top-5 selection
applied to the 6.
Action taken: Proceeded with 6. All 6 diagnosed and tailored normally.
Recommendation: The Copenhagen senior-PM market is thin on LinkedIn.
Future Denmark runs should lean on Indeed and consider widening to all
of Zealand rather than Copenhagen city.
---
```

## How session notes are used

At the start of every session, the pipeline reads `Session Notes.txt`. Prior entries become context: if a past entry says "the Copenhagen senior-PM market is thin on LinkedIn," the next Denmark run starts with that expectation and adjusts its search strategy instead of rediscovering the problem.

This is what makes the framework get better over time in a way a stateless tool cannot. The notes are the accumulated knowledge of every prior run.

## After writing an entry

Tell the user one line: *"Logged a session note: Copenhagen senior-PM yield was low on LinkedIn; recommended leaning on Indeed for future Denmark runs."* The user should know the institutional memory was updated.
