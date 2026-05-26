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
import yaml

_DEFAULTS = {
    "config_dir": "config",
    "assets_dir": "assets",
    "job_log_dir": "job-log",
    "session_output_dir": ".",
    "interview_prep_dir": "interview-prep",
}


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
    return {k: os.path.join(repo_root, v) for k, v in paths.items()}


def session_folder(paths, date_str, geography):
    """Full path to a session output folder: [session_output_dir]/[dd.mm]/[City]"""
    return os.path.join(paths["session_output_dir"], date_str, geography)


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
