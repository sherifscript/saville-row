# LinkedIn recruiter nudge — the short DM

When the scraped job data identifies a recruiter or job poster (a name, a title, and a LinkedIn profile link), the framework drafts a short direct message to that person. A well-aimed DM is one of the highest-yield, lowest-effort moves in a job search.

## When to draft a nudge

- The job data includes a named contact with a LinkedIn profile.
- The company is **not** in the blacklist.
- The candidate has opted into nudges (`config.yaml > cover_letter.linkedin_nudges: true`).

## The format

The message must:

- Be **under 80 words**
- **Open with the specific role name** — no generic "I came across your profile" opener
- **Lead with the strongest 1–2 credentials** relevant to that role, with no employer named
- **Mention current location and immediate availability**, consistent with the regional context
- **Close with a low-friction ask** — offer to send the CV, not request a meeting
- Contain **no em dashes**

## Why these constraints

- **Under 80 words:** recruiters read DMs on their phone between meetings. Long messages get archived.
- **Role name first:** the recruiter is hiring for several roles. Tell them which one immediately.
- **No employer named:** the same reason the CV summary names no employer — it keeps the focus on the credential, and it avoids the awkwardness of name-dropping in a cold message.
- **Availability:** removes a question the recruiter would otherwise have to ask.
- **Low-friction ask:** "happy to send my CV" is a yes/no the recruiter can answer in one tap. "Could we find 30 minutes to chat?" is a calendar negotiation they will defer.

## Worked example

Recruiter: Dana Liu, Talent Partner at Northwind Operations. Role: Senior Product Manager, Workflow Automation.

> Hi Dana, I saw Northwind is hiring a Senior PM for Workflow Automation. I most recently shipped an onboarding redesign that lifted 7-day activation 18% in a quarter, and built the experimentation platform behind it. I'm Brooklyn-based and available immediately. Happy to send my CV if it's useful. Thanks for considering.

61 words. Role named first. Credentials lead, no employer named. Location and availability stated. Low-friction close. No em dashes.

## Saving nudges

Append each nudge to a single plain-text file in the session folder:

```
paths.session_output_dir/[session-date]/[Country or City]/LinkedIn Messages.txt
```

(or `paths.session_output_dir/[session-date]/Requests/LinkedIn Messages.txt` for the `Run Request` shortcut)

Create the file if it does not exist. Format each entry:

```
=====================================
Recruiter: [Name] — [Title]
Job: [Company] | [Job Title]
LinkedIn: [Profile URL]
-------------------------------------
[Message text]
=====================================
```

The file accumulates every nudge for the session, so the candidate can work through them in one pass.

## What the nudge does not do

- It does not get sent automatically. The framework drafts; the candidate sends. Sending is a relationship action the candidate should own.
- It does not follow up. If the candidate wants a follow-up cadence, that is a manual decision.
- It does not connect-request with a note — it assumes the candidate will send the message after connecting or via InMail. The draft is the message body only.
