#!/usr/bin/env python3
"""Sync the plugin version across all the places it lives, in one command.

Usage:
    python scripts/bump_version.py 1.6.0
    python scripts/bump_version.py 1.6.0 --check   # verify sync, change nothing

The version lives in three places that must agree (see CLAUDE.md "release"):
  - .claude-plugin/plugin.json            -> "version": "X.Y.Z"
  - .claude-plugin/marketplace.json       -> "version": "X.Y.Z" (plugin entry)
  - skills/*/SKILL.md frontmatter         -> version: X.Y.Z

This does NOT touch CHANGELOG.md or the CLAUDE.md prose line — those carry
human-written context, so they stay manual on purpose.
"""
import re
import sys
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")

# (path, regex, replacement-template). {v} is the new version.
JSON_FILES = [".claude-plugin/plugin.json", ".claude-plugin/marketplace.json"]
JSON_RE = re.compile(r'("version":\s*")\d+\.\d+\.\d+(")')
SKILL_RE = re.compile(r'^(\s*version:\s*)\d+\.\d+\.\d+\s*$', re.MULTILINE)


def skill_files():
    skills_dir = os.path.join(REPO, "skills")
    return [os.path.join(skills_dir, d, "SKILL.md")
            for d in sorted(os.listdir(skills_dir))
            if os.path.isfile(os.path.join(skills_dir, d, "SKILL.md"))]


def apply(path, pattern, repl, check):
    full = os.path.join(REPO, path) if not os.path.isabs(path) else path
    text = open(full, encoding="utf-8").read()
    new, n = pattern.subn(repl, text)
    if n == 0:
        print(f"  WARN no version match in {os.path.relpath(full, REPO)}")
        return False
    changed = new != text
    if changed and not check:
        open(full, "w", encoding="utf-8", newline="\n").write(new)
    status = "would change" if (changed and check) else ("changed" if changed else "ok")
    print(f"  [{status}] {os.path.relpath(full, REPO)} ({n} site(s))")
    return not changed if check else True


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    check = "--check" in sys.argv
    if len(args) != 1 or not SEMVER.match(args[0]):
        print("usage: bump_version.py X.Y.Z [--check]", file=sys.stderr)
        sys.exit(2)
    v = args[0]
    print(("Checking" if check else "Bumping") + f" version -> {v}")
    in_sync = True
    for p in JSON_FILES:
        in_sync &= apply(p, JSON_RE, r'\g<1>' + v + r'\g<2>', check)
    for p in skill_files():
        in_sync &= apply(p, SKILL_RE, r'\g<1>' + v, check)
    if check and not in_sync:
        print("OUT OF SYNC — run without --check to fix.", file=sys.stderr)
        sys.exit(1)
    print("Done." + ("" if check else " Update CHANGELOG.md + the CLAUDE.md version line by hand, then tag."))


if __name__ == "__main__":
    main()
