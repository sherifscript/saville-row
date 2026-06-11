"""
path_utils.py — resolve workspace paths from config.yaml > paths block.

All skills and scripts that need a file path call load_paths() and index
into the returned dict. This keeps path logic in one place and makes the
workspace layout a single config decision rather than a string scattered
across 8 skills.

Default values match the v1.3.0 layout. Users upgrading from v1.2.0
should move their files and update config.yaml with a paths block,
or add a paths block pointing to their old data/ locations.
"""

import os
from datetime import date

import yaml

_DEFAULTS = {
    "config_dir": "config",
    "assets_dir": "assets",
    "job_log_dir": "job-log",
    "session_output_dir": "applications",
    "session_date_format": "dd.mm.yy",
    "interview_prep_dir": "interview-prep",
}

# Keys that are not filesystem paths and must not be joined with repo_root.
_NON_PATH_KEYS = {"session_date_format"}


def load_paths(repo_root=None):
    """Return the resolved paths dict for the current workspace.

    Tries config/config.yaml first (v1.3.0 layout), then config.yaml at
    repo root (v1.2.0 backwards compatibility). Merges user-specified
    paths over the defaults.
    """
    if repo_root is None:
        repo_root = os.getcwd()
    paths = dict(_DEFAULTS)
    for cfg_path in [
        os.path.join(repo_root, "config", "config.yaml"),
        os.path.join(repo_root, "config.yaml"),
    ]:
        if os.path.exists(cfg_path):
            with open(cfg_path, encoding="utf-8") as f:
                cfg = yaml.safe_load(f) or {}
            paths.update(cfg.get("paths", {}))
            break
    return {
        k: (v if k in _NON_PATH_KEYS else os.path.join(repo_root, v))
        for k, v in paths.items()
    }


def session_folder(paths, date_str, geography):
    """Full path to a session output folder: [session_output_dir]/[session-date]/[City]

    `date_str` is the already-formatted session date (see
    `format_session_date()`), e.g. "11.06.26" for `dd.mm.yy` or
    "06.11.26" for `mm.dd.yy`.
    """
    return os.path.join(paths["session_output_dir"], date_str, geography)


def format_session_date(fmt, when=None):
    """Format a date per `paths.session_date_format`.

    Supports exactly two formats, both zero-padded with a two-digit year:
      "dd.mm.yy" -> "11.06.26"  (day.month.year, default)
      "mm.dd.yy" -> "06.11.26"  (month.day.year, US-style)

    `when` defaults to today. Raises ValueError for any other format string.
    """
    if when is None:
        when = date.today()
    day, month, year = f"{when.day:02d}", f"{when.month:02d}", f"{when.year % 100:02d}"
    if fmt == "dd.mm.yy":
        return f"{day}.{month}.{year}"
    if fmt == "mm.dd.yy":
        return f"{month}.{day}.{year}"
    raise ValueError(
        f"Unsupported session_date_format: {fmt!r}. "
        "Supported values are 'dd.mm.yy' and 'mm.dd.yy'."
    )


def job_log_path(paths):
    return os.path.join(paths["job_log_dir"], "Job Listings.xlsx")


def backup_dir(paths):
    return os.path.join(paths["job_log_dir"], "Backup")


def blacklist_path(paths):
    return os.path.join(paths["assets_dir"], "Blacklist.txt")


def session_notes_path(paths):
    return os.path.join(paths["assets_dir"], "Session Notes.txt")


def story_bank_path(paths):
    return os.path.join(paths["assets_dir"], "Interview Story Bank.txt")
