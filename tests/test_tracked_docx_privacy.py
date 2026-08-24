"""No tracked .docx may carry a real person's contact destination.

This is the recurrence guard for the 2026-08 leak, where the committed OPUS
template and showcase CV held the template author's site and LinkedIn as
hyperlink relationship targets while displaying someone else's text.

It deliberately contains NO personal identifiers. A denylist of the values
being removed would write them permanently into a public repository in order
to remove them from it, and would only ever catch the leak we already know
about. The invariant here — a distributable artifact points only at reserved
example domains — is identifier-free and catches the next one too.

Reserved domains are RFC 2606 / RFC 6761: example.com, .net, .org and any
subdomain of them can never be registered by a third party, so a demo CV can
never send a recruiter to a real stranger.
"""
import os
import re
import subprocess
import zipfile

import pytest

from conftest import REPO_ROOT

RELS_PART = "word/_rels/document.xml.rels"
HYPERLINK = "/relationships/hyperlink"
RESERVED = ("example.com", "example.net", "example.org")

# Private workspace directories. Tracking any of these means personal data has
# been committed, whatever its contents.
NEVER_TRACKED = ("config/", "assets/", "job-log/", "applications/",
                 ".scratch/", "interview-prep/", "plans/")


def _tracked(pattern):
    """Repo-relative paths of tracked files matching a pathspec."""
    out = subprocess.run(["git", "ls-files", "-z", pattern],
                         cwd=REPO_ROOT, capture_output=True, text=True)
    if out.returncode != 0:
        pytest.skip("git unavailable")
    return [p for p in out.stdout.split("\0") if p]


def _external_targets(path):
    """Targets of every hyperlink relationship in the document part."""
    with zipfile.ZipFile(path) as z:
        if RELS_PART not in z.namelist():
            return []
        xml = z.read(RELS_PART).decode("utf-8", "replace")
    targets = []
    for tag in re.findall(r"<Relationship [^>]*>", xml):
        if HYPERLINK not in tag:
            continue
        m = re.search(r'Target="([^"]*)"', tag)
        if m:
            targets.append(m.group(1))
    return targets


def _host(target):
    stripped = re.sub(r"^[a-z][a-z0-9+.-]*://", "", target.strip(), flags=re.I)
    return stripped.split("/")[0].split("?")[0].split("#")[0].lower()


def test_tracked_docx_files_are_discovered():
    """Guard the guard: a rename must not silently empty this suite."""
    assert _tracked("*.docx"), "no tracked .docx found — check the pathspec"


def test_target_extraction_actually_reads_targets():
    """Guard the guard, part two.

    A parser bug that returns [] makes every assertion below vacuously true.
    The OPUS template is known to carry exactly two contact hyperlinks, so
    extraction returning nothing for it means the extractor is broken, not
    that the file is clean.
    """
    tpl = os.path.join(REPO_ROOT, "templates", "OPUS", "full_template.docx")
    targets = _external_targets(tpl)
    assert len(targets) == 2, (
        "expected 2 hyperlink targets in the OPUS template, got %r — the "
        "extractor is broken and every check below is vacuous" % (targets,))


@pytest.mark.parametrize("rel_path", _tracked("*.docx"))
def test_tracked_docx_points_only_at_reserved_domains(rel_path):
    path = os.path.join(REPO_ROOT, rel_path)
    for target in _external_targets(path):
        host = _host(target)
        assert host and any(host == d or host.endswith("." + d)
                            for d in RESERVED), (
            "%s links to %r. Distributable .docx may only point at RFC 2606 "
            "reserved domains — a real target here ships one person's contact "
            "destination inside everyone else's CV." % (rel_path, target))


def test_private_workspace_directories_are_not_tracked():
    for prefix in NEVER_TRACKED:
        hits = _tracked(prefix)
        assert not hits, "%s is tracked: %s" % (prefix, hits[:5])
