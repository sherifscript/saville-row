# Failure recovery — what to do when a stage breaks

The rule across every stage: **never silently fall back.** Stop, log, notify. A degraded output the user does not know is degraded is worse than a clear failure.

## Discovery stage

| Failure | Recovery |
| --- | --- |
| A connector errors / times out / returns zero after one retry | Skip that connector's table for the session. Log it. Proceed with the other connector. |
| A connector returns partial results (2–3 instead of 10) | **Not a failure.** Proceed with what was returned. Apply top-N to it. |
| Both connectors fail | Hard stop in interactive sessions — notify the user. In unattended sessions, log and end the session; there is nothing to tailor. |
| The job log is locked | See `job-discovery/references/append-only-safety.md` Rules 4–5. |

## Diagnosis stage

| Failure | Recovery |
| --- | --- |
| The JD cannot be retrieved for a role | Skip that role, note it, continue with the others. Do not tailor a CV without a JD (except `Run CV only`). |
| The diagnosis comes out generic / weak | Do not proceed to cv-tailor. A weak diagnosis produces a generic CV. Strengthen section 4 (the lead credential) and retry. |

## CV-tailor stage

| Failure | Recovery |
| --- | --- |
| The template file is locked (open in Word) | Hard stop. Notify the user. Do NOT fall back to a copy or an older template version. Wait. |
| Pre-render validation fails | Fix the content_map (the validation error names the problem). Do not render an invalid map. |
| Post-render audit check fails | Do not ship the CV. For programmatic failures (4, 5), re-render. For editorial failures (1, 3), regenerate the failing section or strengthen the diagnosis. |

## Cover-letter stage

| Failure | Recovery |
| --- | --- |
| No voice reference configured | warn-once-then-comply: explain, then draft anyway. strict: refuse, route to setup. |
| The voice reference path is broken | Notify the user the file is missing. Do not draft from memory of "what good looks like." |

## Logging a failure

Every failure that changes the session outcome gets a `Session Notes.txt` entry (see `session-notes.md`) and a one-line notification to the user. The user should always know: what failed, what the framework did about it, and whether the session's output is complete or partial.

## The principle

A job application is a one-shot action. A silently degraded CV or a cover letter drafted without a voice reference can cost a real opportunity. Every failure mode above resolves toward *making the degradation visible* rather than papering over it. When in doubt, stop and ask.
