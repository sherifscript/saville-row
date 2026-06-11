# saville-row

A **Claude Code plugin** implementing a diagnosis-first job search system. Install with one command; eight skills cover the full pipeline — discover → diagnose → tailor → cover → interview prep → story bank — with opinionated defaults and named failure-mode guards drawn from a real job search.

---

## Why this exists

Most AI resume tools take a job description and a CV, ask the model to "tailor," and ship whatever comes out. The output reads tailored. It rarely is. The headline shifts, a keyword or two gets sprinkled in, and the same generic bullets appear under every application.

`saville-row` does the opposite. Every CV starts with a one-page **diagnosis** — what is this team actually hiring to fix, what would a great hire deliver in 90 days, what is the real bar, which of the candidate's credentials speaks loudest to that bar, and which JD keywords must appear verbatim. No diagnosis, no CV. The diagnosis drives every bullet on the page.

The render is built on `docxtpl` with a small set of hard-won rules (`autoescape=True` is mandatory; a `RichText` helper handles inline bold; a seven-check post-render audit catches the specific failure modes that have shipped broken CVs in the past). The cover letter skill takes a voice reference file in the candidate's own writing and refuses to draft without it.

It is opinionated. It will tell you when you're about to skip something the framework was built to prevent.

---

## Features

- **role-diagnosis** — the editorial gate. Five-section template that drives every downstream choice.
- **cv-tailor** — `docxtpl` render with modular section composition, regional headers, a seven-check post-render audit, and an opt-in inline-bold toggle (`cv.inline_bold`).
- **cover-letter** — voice-anchored, sub-300-word, no-em-dash, with the operational test *"could this sentence appear in any cover letter?"*
- **interview-prep** — role snapshot + STAR+R story map + hard questions + your ask.
- **story-bank** — STAR+R story library, refreshed from your career file.
- **job-discovery** — ~~job board (Indeed) + ~~job board via ~~web scraper (Apify-LinkedIn) primary, adapter slots for more ~~job boards.
- **job-search-pipeline** — the orchestrator. Chains everything. Owns the 11-command shortcut DSL (`Run [Country]`, `Run [Country] | [Branch]`, `Run Remote`, `Run CV only`, `Run Request`, `Run Blacklist`, `Run Interview Prep`, `Run Story Bank Refresh`, and more). See [CHEATSHEET.md](./CHEATSHEET.md) for the full reference.
- **job-search-setup** — first-run wizard. Reads your career file, proposes branches, prompts for voice references, picks output formats. Writes config files to `config/`.

---

## What makes this different

| Most AI resume tools | saville-row |
| --- | --- |
| Prompt-and-pray rendering | `docxtpl` with `autoescape=True` enforced; ampersand-strip and empty-bold-bullet regressions guarded by audit checks |
| One CV style | Modular sections — toggle summary / additional / publications / certifications per user and per application |
| Generic cover letters | Voice anchor required; opener must be load-bearing on the role's specifics |
| No memory of failure modes | Seven-check post-render audit names actual incidents (the `&` strip, the empty-bold regression, the em-dash, the employment gap from a dropped contiguous block) and fails the build if they recur |
| Tailoring = keyword sprinkling | Diagnosis-first hard gate; every bullet defensible against *"what is this team actually hiring to fix?"* |

---

## Installation

### Method 1 — Plugin install (recommended)

```bash
claude plugin marketplace add sherifscript/saville-row
claude plugin install saville-row@sherifscript
```

All eight skills install in one command. Say *"set up saville-row"* to run
the first-time wizard.

### Method 2 — Local plugin (development or offline)

```bash
git clone https://github.com/sherifscript/saville-row.git
claude --plugin-dir ./saville-row
```

Or add it permanently to your Claude config with `claude plugin install --scope user ./saville-row`.

### Method 3 — Claude Cowork (desktop)

1. Clone the repo: `git clone https://github.com/sherifscript/saville-row.git ~/saville-row`
2. Open Claude desktop → Cowork tab → select the cloned folder as your working directory.
3. Cowork auto-detects the `skills/` directory. Say *"set up saville-row"* to trigger the setup wizard.

### Method 4 — claude.ai upload

Upload the eight `skills/*/SKILL.md` files to a claude.ai Project's Knowledge. Optionally upload the `references/` files for richer behavior. Claude.ai cannot run the Python rendering scripts, so this method is best for diagnosis, cover-letter, interview-prep, and story-bank — the editorial skills. CV rendering requires local Python.

---

## First run

After install, in any Claude session inside the project folder:

```
You: set up saville-row
```

The setup wizard will:

1. Ask for your career history file (free-form text or markdown is fine — no template to fill).
2. Read it once and propose 2–4 candidate **branches** (distinct career arcs you might emphasize for different roles). You accept, edit, or reject.
3. Ask which **regions** you target (US / UK / EU / Gulf / etc.) and offer to draft headers for each.
4. Ask whether you have **voice reference files** — old cover letters or application essays in your own writing — and where to find them.
5. Pick your **output formats**: `docx` only (default) or `docx + pdf` (warns about LibreOffice dependency and extra render cost).
6. Write `config.yaml`, `branches.yaml`, and `regional-headers.yaml` into `config/`. Career file and voice references are expected under `assets/`.

Then you can run any of the shortcut commands:

```
You: Run Denmark
You: Run Denmark | Product Management
You: Run Remote
You: Run CV only: General
You: Run Request: https://linkedin.com/jobs/view/...
You: Run Interview Prep: Stripe, Senior Product Manager
You: Run Blacklist: add Acme Corp
You: Run Story Bank Refresh
```

See [CHEATSHEET.md](./CHEATSHEET.md) for the full 11-command reference.

---

## Troubleshooting

**The plugin shows up as "SavilleRow" (raw, title-cased name) or its skills appear empty.**

If skills appear empty or the name looks stale, the marketplace cache predates the current release — run `claude plugin marketplace update sherifscript`, then reinstall. Some app surfaces (e.g. the Claude Desktop plugin directory) title-case the raw `name` field instead of honoring `displayName: "SavilleRow"`, which is why the plugin is named `saville-row`.

**Claude Desktop users:** update or re-add the marketplace rather than sideloading a zip — a sideloaded zip won't pick up manifest or marketplace updates on its own.

---

## Showcase

The `examples/showcase/` folder contains a complete end-to-end run for a fictional candidate — a senior product manager moving from B2C consumer apps to B2B SaaS. It includes the candidate profile, config files, diagnosis, rendered CV, cover letter, interview prep doc, and LinkedIn messages for a single target role (Northwind Operations, Senior PM).

---

## Scope and non-goals

`saville-row` targets the **modern CV** format used across the US, UK, EU, MENA, and most of Asia outside Japan. Explicit non-goals:

- **German Lebenslauf** (photo, DOB, marital status, signature) — not supported. The German job market does accept modern CVs, especially for tech and international roles.
- **Japanese Rirekisho / Shokumukeirekisho** — not supported.
- **Multi-candidate management** for career coaches — out of scope. Each candidate runs in a separate project folder.
- **Direct ATS submission** — saville-row produces the documents; you submit them.

---

## Opinionation policy

The framework has hard gates (e.g., no diagnosis → no CV; no voice reference → no cover letter; max 3 experience slots by default). When you ask Claude to skip a gate, the first time per session it will explain the gate and the failure mode it prevents. After that, it complies silently. Power users can tighten or loosen any gate in `config.yaml`.

This is **less strict than the original private workflow** the framework was extracted from, which refuses outright. If you want that behavior, set `opinionation: strict` in `config.yaml`.

---

## Requirements

- Claude Code, Claude desktop with Cowork, or claude.ai Projects.
- Python 3.10+ for the CV render scripts.
- `docxtpl`, `python-docx`, `openpyxl`, `PyYAML` (install via `pip install -r requirements.txt`).
- Optional: LibreOffice for PDF output; a ~~web scraper (e.g. Apify) account for ~~job board discovery (LinkedIn, Wuzzuf, etc.).

---

## License

[CC BY-NC 4.0](./LICENSE). Free to share and adapt for non-commercial use with attribution.

---

## Changelog

See [CHANGELOG.md](./CHANGELOG.md) for the full version history. Current release: **v1.4.1**.

---

## Credits

Extracted from a real personal workflow built over many months of job searching. The named failure modes guarded by the audit (the `Artist & Label → Artist  Label` ampersand strip; the empty-bold-bullet regression; the "every CV looked tailored, none were" diagnosis-skip incident) all happened. Those are the scars this framework was built around.
