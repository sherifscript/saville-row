"""Contact hyperlink targets belong to the rendered candidate — nobody else.

The 2026-08 leak: templates/OPUS/full_template.docx was built from a finished
personal CV, so its two <w:hyperlink> RELATIONSHIP targets stayed pinned to
that person's site and LinkedIn. docxtpl rewrites the visible <w:t> and never
word/_rels/document.xml.rels, so every CV rendered from the template showed the
new candidate's URLs and clicked through to the template author's. Invisible on
screen; harvested by any ATS that reads relationships instead of display text.

The predecessor test asserted `>= 2 hyperlink rels`, which the leak satisfied
perfectly. These tests assert the pairing instead, and assert it POSITIVELY:
"candidate A's values are absent from candidate B's file" passes trivially when
a renderer leaves both candidates pointing at neutral template placeholders.
"""
import zipfile

import pytest
from docxtpl import DocxTemplate

from conftest import TEMPLATE, contact_links, minimal_content_map
from md_to_richtext import build_bold_plan
from postprocess import ContactLinkError, postprocess_cv
from audit import _read_hyperlinks, _norm_target

ALICE = {"candidate_name": "Alice Alpha",
         "personal_site": "alice.example.com",
         "linkedin_url": "linkedin.example.com/in/alicealpha"}
BOB = {"candidate_name": "Bob Beta",
       "personal_site": "bob.example.org",
       "linkedin_url": "linkedin.example.net/in/bobbeta"}


def _render(tmp_path, name, **overrides):
    cm = minimal_content_map(**overrides)
    cm, plan = build_bold_plan(cm, mode="plain")
    path = str(tmp_path / name)
    tpl = DocxTemplate(TEMPLATE)
    tpl.render(cm, autoescape=True)
    tpl.save(path)
    postprocess_cv(path, plan, contact_links=contact_links(cm))
    return path, cm


def _all_bytes(path):
    with zipfile.ZipFile(path) as z:
        return "".join(z.read(n).decode("utf-8", "ignore")
                       for n in z.namelist()).lower()


@pytest.mark.parametrize("who", [ALICE, BOB], ids=["alice", "bob"])
def test_targets_equal_their_own_labels(tmp_path, who):
    path, cm = _render(tmp_path, "cv.docx", **who)
    links = {label: target for label, _rid, target in _read_hyperlinks(path)}
    for key in ("personal_site", "linkedin_url"):
        label = cm[key]
        assert label in links, "no hyperlink labelled %r" % label
        assert _norm_target(links[label]) == _norm_target(label)
        assert links[label].startswith("https://"), (
            "Word needs an explicit scheme or the rel is not an external link")


def test_second_render_carries_nothing_from_the_first(tmp_path):
    a, _ = _render(tmp_path, "a.docx", **ALICE)
    b, _ = _render(tmp_path, "b.docx", **BOB)
    blob = _all_bytes(b)
    for value in ("alice", "alpha", ALICE["personal_site"],
                  ALICE["linkedin_url"]):
        assert value.lower() not in blob, "%r leaked into B" % value
    # And the same in reverse, so a swap cannot pass either.
    assert "bob" not in _all_bytes(a)


def test_template_targets_never_survive_a_render(tmp_path):
    """The specific regression: the committed template's own targets."""
    with zipfile.ZipFile(TEMPLATE) as z:
        rels = z.read("word/_rels/document.xml.rels").decode()
    path, cm = _render(tmp_path, "cv.docx", **ALICE)
    rendered = {t for _l, _r, t in _read_hyperlinks(path)}
    for stale in ("https://example.com",
                  "https://linkedin.example.com/in/example"):
        assert stale in rels, "template placeholder changed; update this test"
        assert stale not in rendered


def test_unsupported_scheme_is_rejected(tmp_path):
    for bad in ("javascript:alert(1)", "file:///etc/passwd", "data:text/html,x"):
        with pytest.raises(ContactLinkError):
            _render(tmp_path, "evil.docx", personal_site=bad)


def test_unmatched_link_fails_loudly(tmp_path):
    """A value with no hyperlink to bind it must not pass silently."""
    cm = minimal_content_map()
    cm, plan = build_bold_plan(cm, mode="plain")
    path = str(tmp_path / "cv.docx")
    tpl = DocxTemplate(TEMPLATE)
    tpl.render(cm, autoescape=True)
    tpl.save(path)
    with pytest.raises(ContactLinkError):
        postprocess_cv(path, plan,
                       contact_links={"personal_site": "absent.example.com"})


def test_contact_keys_are_required_by_validation():
    from render_cv import BASE_REQUIRED_KEYS, validate_content_map
    assert "personal_site" in BASE_REQUIRED_KEYS
    assert "linkedin_url" in BASE_REQUIRED_KEYS
    cm = minimal_content_map()
    del cm["personal_site"]
    with pytest.raises(ValueError) as exc:
        validate_content_map(cm, {"cv": {}})
    assert "personal_site" in str(exc.value)
