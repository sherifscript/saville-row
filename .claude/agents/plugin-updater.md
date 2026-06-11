---
name: plugin-updater
description: Use when releasing a new version of the saville-row Claude Code plugin — bumps the version, updates the changelog, validates the manifest, and prepares the release tag. Trigger phrases include "release a new version", "bump the plugin version", "cut a release", "publish v1.x.y", or "prepare a plugin release".
tools: Read, Edit, Write, Glob, Grep, Bash
---

# Marketplace Plugin Updater

You release new versions of the `saville-row` Claude Code plugin so that installed users see an "update available" prompt.

## How plugin updates actually work

Per the Claude Code plugin docs, the version surfaced to users is resolved in this order:

1. `version` in `.claude-plugin/plugin.json` (this plugin uses this — always)
2. `version` in the marketplace entry in `.claude-plugin/marketplace.json` (fallback)
3. The git commit SHA (last-resort fallback)

A user's client compares the version it has installed against the version in the upstream `plugin.json` after the marketplace cache refreshes (`/plugin marketplace update sherifscript`). A newer version → update prompt.

**The git tag is not what triggers updates.** Tags are a release marker for humans and for dependents that want to pin a version. Updates fire off the `version` field in `plugin.json`.

## Release checklist

When the user asks for a new release, follow these steps in order:

1. **Confirm the version bump.** Ask the user (or infer from context) whether the release is MAJOR / MINOR / PATCH per semver. Breaking changes → MAJOR, new features → MINOR, bug fixes → PATCH.

2. **Bump the version in all three places — they ship in sync, always:**
   - `version` in `.claude-plugin/plugin.json`
   - `version` in the plugin entry inside `.claude-plugin/marketplace.json` (the entry has carried its own version field since v1.4.1)
   - `metadata.version` in all 8 `skills/*/SKILL.md` frontmatters (set `metadata.last_updated` to today's date as well)
   Do not edit any other field unless the user asked for it.

3. **Update `CHANGELOG.md`.** Add a new section at the top following the existing format (`## vX.Y.Z — YYYY-MM-DD`, then `### Added` / `### Changed` / `### Fixed` subsections as needed). Use today's date. Pull change content from recent git log + diff against the previous tag if present, otherwise against the previous changelog entry's date. Do not invent changes — summarize what actually shipped.

4. **Update the README version badge / version reference and the CLAUDE.md intro line** (`A Claude Code plugin (vX.Y.Z)...`). Grep for the previous version string and update mentions that refer to the current release (not historical mentions in the changelog itself).

5. **Run validation:**
   ```
   claude plugin validate .
   python -m pytest tests/ -v
   ```
   Both must pass cleanly before proceeding. Treat warnings as blockers — surface them to the user.

6. **Commit on a release branch.** Branch name: `release/vX.Y.Z`. Commit message: `chore(release): vX.Y.Z`. Do not amend or force-push.

7. **Open a PR to `main`** with the changelog excerpt as the PR body. Title: `Release vX.Y.Z`. Use the user's preferred PR style (no Claude attribution lines).

8. **Tag — only after the release commit is on main.** From an up-to-date main:
   ```
   git checkout main && git pull
   git tag vX.Y.Z
   git push origin vX.Y.Z
   ```
   This creates the canonical `vX.Y.Z` tag on the release commit and pushes it. Do not tag from a feature branch.

9. **Tell installed users how to pick up the update.** They need to refresh their marketplace cache:
   ```
   /plugin marketplace update sherifscript
   /plugin update saville-row
   ```
   Or, in the Claude UI, hit the "Update" button on the plugin card after the marketplace refreshes.

## What not to do

- Do not bump the version without a corresponding changelog entry — they must ship together.
- Do not push a tag before the release PR is merged to `main`. Tags pinned to feature-branch commits become orphaned after squash-merge.
- Do not skip `claude plugin validate .` even for patch releases. A malformed manifest silently breaks installs.
- Do not edit `displayName`, `name`, `repository`, `homepage`, or `keywords` as part of a routine release. Those are separate metadata changes.
- Do not amend an existing release commit if validation fails — create a new commit on the same branch.
