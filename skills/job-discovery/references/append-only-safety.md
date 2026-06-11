# Append-only safety — the job log is irreplaceable

`data/job-log/Job Listings.xlsx` is a permanent record built up across many sessions. Losing it means losing the candidate's entire application history. This file defines the rules that protect it. They are hard stops. Read them before touching the job log in any way.

## Rule 1 — Back up before every access

Before touching `Job Listings.xlsx` in any session — **including read-only access** — copy it to:

```
data/job-log/Backup/Job Listings — [DD.MM.YY HH.MM].xlsx
```

where the timestamp is the current date and time. Create the `Backup/` folder if it does not exist. Only proceed after the backup copy is confirmed written.

If the backup cannot be created:
- **Interactive session:** hard stop. Notify the user, wait.
- **Unattended session:** skip-and-log. Write to `data/Session Notes.txt`, continue without touching the original file.

## Rule 2 — All writes are additive

Never overwrite the file with a rebuilt version. Never delete rows. Never move rows between sheets. Never rename a sheet. The only permitted write is appending new rows and creating new sheets.

## Rule 3 — Never substitute a copy

If the file cannot be opened, do **not** substitute a copy, a backup, or a rebuilt equivalent and continue as if nothing happened. The presence of `Job Listings - Copy.xlsx` or any similarly named file is **not** permission to use it as a working base. The original is the only authoritative file.

## Rule 4 — Locked file is never "corrupted"

If `openpyxl` (or any library) fails to open `Job Listings.xlsx`, the overwhelmingly likely cause is that **the file is open in Excel**, which holds a lock. This is never an indication that the file is corrupted.

- **Interactive session:** stop immediately. Tell the user the exact error and ask them to close the file in Excel. Wait. Do not proceed, do not work around it, do not rebuild.
- **Unattended session:** see Rule 5.

## Rule 5 — Unattended fallback

If the file cannot be opened in a scheduled or unattended session, proceed with the full workflow — job search, CV tailoring, cover letters — but:

1. Skip the deduplication check (it needs to read the sheet).
2. Skip the normal append.
3. Save the session's results to a **new** file: `data/job-log/Job Listings — [session-date].xlsx`, using the standard sheet and column format.
4. Write one log entry to `data/Session Notes.txt`:

   ```
   [session-date] — WARNING: Job Listings.xlsx could not be opened. Results saved
   separately to Job Listings — [session-date].xlsx. Deduplication skipped. All
   other outputs completed normally.
   ```

5. Never attempt to write to or overwrite the original file.

## Rule 6 — Verify before every append

Before each append: confirm the file opens successfully and the target sheet exists. If either check fails, apply the rules above.

## Column format

The standard column order for every sheet:

```
Source | Selected | Timestamp | # | Job Title | Company | Location |
Job Type | Match Score | Match Justification | Skill Gap |
Salary Range | Apply Link
```

- **Source** — connector/platform name. If a branch was specified for the session, append it in parentheses: `LinkedIn (Product Management)`.
- **Selected** — `✓` for rows chosen for CV tailoring; blank otherwise.
- **Timestamp** — date and time the row was appended, format `H:MM AM/PM DD.MM.YY`. Only populate for rows appended in the current session; leave pre-existing untimestamped rows blank.
- **Apply Link** — a clickable hyperlink, not plain text.

Row fill: Selected rows get a green fill `E2EFDA` on all cells. Other data rows have no fill.

## Why these rules exist

The job log accumulates the candidate's entire application history — every role considered, every CV sent, every Match Score. There is no way to reconstruct it. A single overwrite or a single "the file looked broken so I rebuilt it" destroys months of record. Every rule above is the consequence of treating that file as irreplaceable. The rules are not negotiable and have no exceptions.
