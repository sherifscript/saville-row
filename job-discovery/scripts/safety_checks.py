"""
safety_checks.py — pre-flight checks for the append-only job log.

Enforces the rules in job-discovery/references/append-only-safety.md.
Every job-log access must call backup_job_log() first, then verify_openable().
"""

import os
import shutil
import datetime


class JobLogLocked(Exception):
    """Raised when the job log cannot be opened — almost always because it
    is open in Excel. Never interpret this as file corruption."""


class BackupFailed(Exception):
    """Raised when the pre-access backup could not be written."""


def backup_job_log(job_log_path):
    """Copy the job log to the Backup/ folder with a timestamp.

    Returns the backup path. Raises BackupFailed if the copy cannot be made.
    Must be called before ANY access to the job log, including read-only.
    """
    if not os.path.exists(job_log_path):
        # Nothing to back up yet — the log will be created fresh. Allowed.
        return None

    backup_dir = os.path.join(os.path.dirname(job_log_path), "Backup")
    try:
        os.makedirs(backup_dir, exist_ok=True)
        stamp = datetime.datetime.now().strftime("%d.%m.%y %H.%M")
        backup_path = os.path.join(backup_dir, f"Job Listings — {stamp}.xlsx")
        shutil.copy2(job_log_path, backup_path)
    except OSError as exc:
        raise BackupFailed(
            f"Could not back up the job log to {backup_dir}: {exc}. "
            f"Interactive session: stop and notify the user. "
            f"Unattended session: skip-and-log, do not touch the original."
        ) from exc

    if not os.path.exists(backup_path):
        raise BackupFailed("Backup copy was not written; aborting access.")
    return backup_path


def verify_openable(job_log_path):
    """Confirm the job log opens. Raises JobLogLocked if it does not.

    A failure here means the file is open in Excel — NOT that it is
    corrupted. See append-only-safety.md Rule 4.
    """
    if not os.path.exists(job_log_path):
        return True  # will be created fresh

    try:
        from openpyxl import load_workbook
    except ImportError as exc:
        raise ImportError("safety_checks needs openpyxl: pip install openpyxl") from exc

    try:
        wb = load_workbook(job_log_path, read_only=True)
        wb.close()
    except (OSError, PermissionError, KeyError) as exc:
        raise JobLogLocked(
            f"Could not open {job_log_path}: {exc}. "
            f"This almost certainly means the file is open in Excel. "
            f"It is NOT corrupted. Interactive session: ask the user to "
            f"close it and wait. Unattended session: use the separate-file "
            f"fallback (append-only-safety.md Rule 5)."
        ) from exc
    return True


def preflight(job_log_path, interactive=True):
    """Run the full pre-access sequence: back up, then verify openable.

    Returns the backup path on success. On failure, raises — the caller
    decides interactive (stop and wait) vs. unattended (skip-and-log)
    behavior based on the `interactive` flag and the exception type.
    """
    backup_path = backup_job_log(job_log_path)
    verify_openable(job_log_path)
    return backup_path


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python safety_checks.py <Job Listings.xlsx>")
        sys.exit(1)
    try:
        bp = preflight(sys.argv[1])
        print(f"Preflight passed. Backup: {bp}")
    except (BackupFailed, JobLogLocked) as e:
        print(f"Preflight FAILED: {e}")
        sys.exit(2)
