#!/usr/bin/env python3
"""
backup.py — silent, local-only backup for your AIOS.

What it does: stages everything, makes a quiet commit if there is anything to
commit, and pushes to your private GitHub repo (origin). That is all.

What it does NOT do: it never posts to social, never sends an email, never
touches any chat tool, never calls an external API beyond `git push`, and
never messages a person. It is safe to run unattended on a schedule. Its only
job is to make sure a day's work is never lost because you forgot to /commit.

How it runs:
  - By hand:        python3 scripts/backup.py
  - On a schedule:  via a launchd job under reference/launchd/
                    (your builder installs this during onboarding; ~16:00 daily).

Requirements: git, and a GitHub auth set up once during onboarding (gh auth /
credential helper) so the push needs no password. GIT_TERMINAL_PROMPT=0 is set
so a push can never hang waiting for credentials — if auth is missing it fails
fast and quietly rather than blocking forever.

Exit codes: 0 = backed up, or nothing to back up, or push skipped cleanly.
            1 = something went wrong (logged to stderr; never raises a dialog).
"""

import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# The repo root is one level up from scripts/.
REPO_ROOT = Path(__file__).resolve().parent.parent


def _git(args, check=True):
    """Run a git command inside the repo. No network prompts can hang it."""
    env = dict(os.environ)
    env["GIT_TERMINAL_PROMPT"] = "0"  # never block waiting for credentials
    return subprocess.run(
        ["git", *args],
        cwd=str(REPO_ROOT),
        env=env,
        capture_output=True,
        text=True,
        check=check,
    )


def _log(msg):
    """Quiet, timestamped line to stderr. No dialogs, no chat, no person."""
    print(f"[backup {datetime.now():%Y-%m-%d %H:%M:%S}] {msg}", file=sys.stderr)


def main():
    # Sanity: are we actually in a git repo?
    inside = _git(["rev-parse", "--is-inside-work-tree"], check=False)
    if inside.returncode != 0 or inside.stdout.strip() != "true":
        _log("not a git repository, nothing to back up.")
        return 0

    # Anything to commit?
    status = _git(["status", "--porcelain"], check=False)
    has_changes = bool(status.stdout.strip())

    if has_changes:
        # Stage everything (.gitignore keeps .env and secrets out).
        _git(["add", "-A"], check=False)

        # Re-check after staging in case everything was ignored.
        staged = _git(["diff", "--cached", "--quiet"], check=False)
        if staged.returncode != 0:
            stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            message = f"chore: auto-backup {stamp}"
            commit = _git(["commit", "-m", message], check=False)
            if commit.returncode != 0:
                _log("commit failed:\n" + (commit.stderr or commit.stdout).strip())
                return 1
            _log(f"committed: {message}")
        else:
            _log("nothing staged after add, skipping commit.")
            has_changes = False
    else:
        _log("working tree clean, nothing new to commit.")

    # Push to her private repo (origin). This is the only network call. If there
    # is no origin or no auth, it fails fast and quietly (prompt is disabled).
    has_origin = _git(["remote", "get-url", "origin"], check=False)
    if has_origin.returncode != 0:
        _log("no 'origin' remote set, local commit saved but not pushed.")
        return 0

    push = _git(["push", "origin", "HEAD"], check=False)
    if push.returncode != 0:
        _log("push skipped or failed (auth/network):\n" + (push.stderr or push.stdout).strip())
        # Local commit is still safe; treat a push miss as non-fatal so the
        # scheduled job stays quiet rather than alarming.
        return 0

    _log("backed up and pushed to origin.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # never raise a dialog at her; just log and exit
        _log(f"unexpected error: {exc}")
        sys.exit(1)
