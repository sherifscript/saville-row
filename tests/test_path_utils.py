"""
Tests for shared/scripts/path_utils.py — workspace path resolution and the
configurable session date format introduced in v1.4.0.

Covers: default paths (session_output_dir == "applications",
session_date_format == "dd.mm.yy"), user-override merging from
config/config.yaml, format_session_date() for both supported formats, and
rejection of unsupported format strings.
"""
from datetime import date

import pytest
import yaml

from path_utils import format_session_date, load_paths


def test_defaults_resolve_to_applications_and_dd_mm_yy(tmp_path):
    paths = load_paths(repo_root=str(tmp_path))
    assert paths["session_output_dir"] == str(tmp_path / "applications")
    assert paths["session_date_format"] == "dd.mm.yy"


def test_user_override_merges_over_defaults(tmp_path):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    config = {
        "paths": {
            "session_output_dir": "Requests",
            "session_date_format": "mm.dd.yy",
        }
    }
    (config_dir / "config.yaml").write_text(yaml.safe_dump(config), encoding="utf-8")

    paths = load_paths(repo_root=str(tmp_path))

    # Overridden keys take the user's values.
    assert paths["session_output_dir"] == str(tmp_path / "Requests")
    assert paths["session_date_format"] == "mm.dd.yy"

    # Keys the user didn't set still fall back to defaults.
    assert paths["assets_dir"] == str(tmp_path / "assets")
    assert paths["job_log_dir"] == str(tmp_path / "job-log")


def test_format_session_date_dd_mm_yy():
    when = date(2026, 6, 11)
    assert format_session_date("dd.mm.yy", when=when) == "11.06.26"


def test_format_session_date_mm_dd_yy():
    when = date(2026, 6, 11)
    assert format_session_date("mm.dd.yy", when=when) == "06.11.26"


def test_format_session_date_zero_pads_single_digits():
    when = date(2026, 1, 2)
    assert format_session_date("dd.mm.yy", when=when) == "02.01.26"
    assert format_session_date("mm.dd.yy", when=when) == "01.02.26"


def test_format_session_date_rejects_unsupported_format():
    with pytest.raises(ValueError):
        format_session_date("yyyy-mm-dd")
