# Voice references — the framework's most-skipped, highest-leverage feature

A **voice reference** is a sample of the candidate's own writing that generative skills read before drafting. It is the single largest difference between output that sounds like the candidate and output that sounds like an LLM.

## Why it matters

Without a voice reference, Claude defaults to "professional writing in a general business register." That register is the AI-template smell every recruiter has been trained to spot in 2025–2026. With a voice reference, Claude anchors on the candidate's actual rhythm, sentence length, opening patterns, what they would and would not say.

The cover letter skill **refuses to draft** without a voice reference configured. This is intentional. If you cannot produce one sample of how you actually write, the framework cannot tell whether its output sounds like you.

## What counts as a voice reference

For each document type:

| Document type | Acceptable references |
| --- | --- |
| **CV summary** | Existing CVs, About / Bio sections, LinkedIn bios you wrote yourself, the first paragraph of any personal essay |
| **Cover letter** | Any cover letter you wrote yourself; application essays; letters of motivation; if you have nothing, a 200-word "why this matters to me" written for the framework counts |
| **Interview prep stories** | Past STAR-format answers you have written down; reflective journal entries about past roles |
| **LinkedIn nudge** | Sent DMs you have a record of; LinkedIn posts in your voice; the first paragraph of a cold email you sent |

**What does not count:** ghostwritten content, generic templates downloaded from the internet, AI-generated material from a previous session, performance reviews written by managers.

## How the skill uses them

When invoked, the cover-letter skill (or any voice-aware skill) does:

```
1. Read voice reference file(s) for this document type.
2. Identify 3–5 voice markers — sentence length distribution, opener patterns,
   words the candidate uses repeatedly, words the candidate never uses,
   rhetorical moves they favor (concession, direct claim, qualified hedge, etc.).
3. Draft against those markers, not against generic "professional cover letter"
   conventions.
4. Apply the operational test: "could this sentence appear in any cover letter
   for any role?" If yes, cut or rewrite.
```

## Configuring voice references

In `config.yaml`:

```yaml
voice_references:
  cv_summary:
    - data/voice/cv-summary-old.md
  cover_letter:
    - data/voice/cover-letter-bmg.txt
    - data/voice/letter-of-motivation-msc.txt
  interview_prep: []   # empty list disables voice anchoring for this skill
  linkedin_nudge:
    - data/voice/linkedin-dms.txt
```

Multiple files per document type are allowed. The skill reads all of them and builds a composite voice profile.

## The one-shot exception

If the candidate genuinely has no past writing, the setup skill offers to capture one in real-time: *"Tell me, in 200 words, why you're job-searching right now. Write it as you'd write to a friend. I'll save that as your voice reference for cover letters."* The output is saved to `data/voice/voice-reference-onshot.md`. This is a fallback, not the preferred path — older, longer-form writing is always better.

## When to refresh

Voice references age with the candidate. A 5-year-old cover letter still encodes some of your voice, but probably not your current voice. Refresh when:
- Career goals shift significantly (e.g., IC → manager, or industry pivot)
- The cover letters being shipped read like they're from a previous version of you
- You write something good and want to add it to the reference set

Re-running `job-search-setup` skips most steps but always prompts on voice references.
