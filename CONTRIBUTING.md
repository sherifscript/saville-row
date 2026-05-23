# Contributing to saville-row

Thanks for considering a contribution. This is a small, opinionated
framework — contributions are welcome, but the opinions are load-bearing.

## Before you start

Read the README and `shared/conventions.md`. The framework's design
decisions (diagnosis-first, the post-render audit, append-only data,
anti-rigidity) are deliberate and documented. A change that removes one of
them is a hard sell; a change that strengthens one is welcome.

## Good first contributions

- **A new CV template.** The catalogue has five entries; only OPUS ships as
  a built `.docx`. Building modern-tech, academic, executive, or creative
  is self-contained, valuable work. See `templates/README.md`.
- **A new connector adapter.** Job boards are pure configuration — see
  `job-discovery/references/connector-setup.md`.
- **A new region.** Regional headers are data — see
  `cv-tailor/references/regional-headers.md`.
- **Reference-file improvements.** Clearer explanations, better examples.

## Things to discuss first (open an issue)

- Changing or removing a hard gate (diagnosis-first, the audit, append-only).
- Anything that touches the `docxtpl` render path — `autoescape=True` and the
  `md_to_richtext` helper exist because of specific past failures.
- Expanding scope (multi-candidate, non-modern-CV formats).

## Standards

- **Skills** are markdown. Keep `SKILL.md` lean; put depth in `references/`.
- **Scripts** are Python 3.10+. They must `python3 -m py_compile` cleanly.
- **Never commit personal data.** See `SECURITY.md`. The showcase uses the
  fictional Jordan Park; real data belongs nowhere in the repo.
- **Run the tests** in `tests/` before opening a PR.

## Pull requests

Keep them focused — one template, one connector, one fix per PR. Describe
what changed and why. If you changed render behavior, say how you verified it
(the showcase render plus the audit is the standard check).
