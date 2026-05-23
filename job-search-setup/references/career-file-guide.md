# Writing your career file

The career file is the one thing the framework cannot write for you. Everything else — diagnoses, CVs, cover letters, interview prep — is generated *from* it. This guide tells you what to put in it.

## The short version

Open a blank document and write down everything you have ever done that might matter to a job. Every role, every project, every number, every thing someone external said about your work. Do not organize it for an audience. Do not trim it. The framework picks what to use per application; your job is to make sure everything it might need is on the page.

A good career file is **longer than any CV will ever be.** That is correct. A CV is a selection; the career file is the source.

## Format

Plain text or markdown. There is no schema, no template, no form to fill. Write in whatever structure is natural to you — headings per employer is the common choice, but prose works too. The framework reads it the way a person would.

Save it wherever you like and point `config.yaml > candidate.career_file` at it. `data/career.md` is the conventional location.

## What to include

For each role:

- **The basics** — title, company, location, exact dates.
- **What you actually did** — not the job description you were given, but the work you did. The decisions, the projects, the things that would not have happened without you.
- **Numbers** — every quantified outcome you can honestly state. Percentages, revenue, user counts, time saved, team size, scale of coverage. Numbers are what the framework reaches for first when it tailors. If a result was real but you never measured it, say so plainly ("activation clearly improved; I did not have a clean baseline").
- **External validation** — anything someone outside your team said about your work. Press coverage, citations, awards, a customer quote, an exec who repeated your framing back to you. These are gold and candidates routinely forget them.
- **What went wrong** — failures, things you would do differently, projects that did not land. These do not go on a CV, but the interview-prep and story-bank skills need them. A career file with no failures in it produces flat interview stories.

Also include: education (degrees, dates, institutions, relevant coursework, thesis topics), languages, tools you genuinely use, work authorization, and any side projects with visible outcomes.

## What not to do

- **Do not write it as a CV.** A CV is trimmed, formatted, and audience-aware. The career file is the opposite — raw, complete, unformatted.
- **Do not embellish.** The framework treats this file as fact. Every number it puts on a CV traces back to here. If it is not true here, it becomes a lie there.
- **Do not pre-decide what is relevant.** The thing you think is minor may be the exact lead for a role you have not seen yet. Write it down anyway.
- **Do not leave gaps unexplained.** If there is a year you were not working, a sentence about why helps the framework handle it well rather than awkwardly.

## A worked example

`examples/showcase/candidate-profile.md` is a complete career file for the fictional candidate Jordan Park. It is the right length and the right level of detail. Read it before writing your own — it shows the texture: free-form, specific, numbers where they exist, a "Notes for the framework" section at the end where the candidate flags things like which roles form a continuous block.

That last move is worth copying. A short "notes for the framework" section at the end of your file — where you point out continuous-employer blocks, possible branches, anything ambiguous — makes the setup wizard's job easier and the output better.

## Keeping it current

The career file is a living document. Add to it when you finish a project, hit a number, get a piece of external recognition, or change roles. Re-running `job-search-setup` after a substantial update lets the framework re-detect your branches. `Run Story Bank Refresh` pulls any new interview stories out of the additions.

The single highest-leverage habit in this whole framework is keeping the career file fed. A rich career file makes every downstream skill better; a thin one limits all of them.
