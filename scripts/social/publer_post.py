#!/usr/bin/env python3
"""
Social Poster: Publer (drafts) with a manual-post fallback.

Reads a post folder from outputs/social/ and lands it in Publer
as a DRAFT to your Instagram account, for you to review and publish yourself.
Nothing is ever published autonomously.

Two safe outcomes, always:
  1. Publer connected      -> the post is saved as a DRAFT in Publer (you open
                              Publer, check it, and hit publish).
  2. Publer not available   -> the caption + images are written to a small
     (or free tier can't     handoff file in the post folder and you open the
      publish to Instagram)   Instagram app and post it yourself.

Usage:
    python3 scripts/social/publer_post.py <post_folder> [--schedule "2026-06-18T08:00:00"] [--publish] [--dry-run]

Examples:
    # Save Thursday's post to Publer as a draft (the default, recommended)
    python3 scripts/social/publer_post.py "2026-06-18 Launch announcement"

    # Just see what would happen, touch nothing
    python3 scripts/social/publer_post.py "2026-06-18 Launch announcement" --dry-run

Notes:
- --draft is the DEFAULT. The post is never scheduled-live unless you pass
  --publish AND a --schedule time, and even then it goes to Publer where you
  still confirm. There is no path in this script that posts to Instagram on
  its own.
- Your Publer workspace and Instagram account are discovered automatically the
  first time you connect, and saved to data/publer_accounts.json. You never
  copy an ID by hand.
"""

import os
import sys
import json
import time
import glob
import argparse
import requests
from datetime import datetime, timezone, timedelta
from pathlib import Path
from dotenv import load_dotenv

# Make scripts/ importable so the shared no-dead-skills helper resolves.
SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from require_key import ensure_ready  # noqa: E402

# Load environment
ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

BASE_URL = "https://app.publer.com/api/v1"
# Local timezone for scheduling. Set this to your own offset.
LOCAL_TZ = timezone(timedelta(hours=1))

# Where post folders live.
POST_PLANS_BASE = ROOT / "outputs" / "social"

# Discovered Publer IDs live here, written by ensure_ready('publer') during
# setup, never hand-typed. {"workspace_id": "...", "instagram_id": "..."}
ACCOUNTS_FILE = ROOT / "data" / "publer_accounts.json"


def _api_key():
    return os.getenv("PUBLER_API_KEY")


def load_accounts():
    """Read the auto-discovered Publer workspace + Instagram IDs."""
    if ACCOUNTS_FILE.exists():
        try:
            return json.loads(ACCOUNTS_FILE.read_text())
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def headers(workspace_id):
    h = {"Authorization": f"Bearer-API {_api_key()}"}
    if workspace_id:
        h["Publer-Workspace-Id"] = workspace_id
    return h


def upload_image(filepath, workspace_id):
    """Upload an image to Publer and return the media object."""
    print(f"  Uploading: {Path(filepath).name}...")
    with open(filepath, "rb") as f:
        resp = requests.post(
            f"{BASE_URL}/media",
            headers=headers(workspace_id),
            files={"file": (Path(filepath).name, f, "image/jpeg")},
        )
    if resp.status_code not in (200, 201):
        print(f"  Could not upload {Path(filepath).name}: {resp.status_code}")
        return None
    data = resp.json()
    return data


def wait_for_job(job_id, workspace_id, timeout=300):
    """Poll job status until completed."""
    print(f"  Waiting for Publer to finish...")
    start = time.time()
    while time.time() - start < timeout:
        resp = requests.get(f"{BASE_URL}/job_status/{job_id}", headers=headers(workspace_id))
        if resp.status_code == 200:
            data = resp.json()
            status = data.get("status")
            if status in ("completed", "complete"):
                print("  Done.")
                return data.get("payload", data)
            elif status == "failed":
                print(f"  Publer reported a problem: {data}")
                return None
        time.sleep(2)
    print("  Timed out waiting for Publer.")
    return None


def read_post_copy(folder):
    """Read POST-COPY.md and extract the caption text."""
    copy_file = folder / "POST-COPY.md"
    if not copy_file.exists():
        print(f"There is no POST-COPY.md in {folder.name}. Add your caption there first.")
        sys.exit(1)

    content = copy_file.read_text()

    post_text = None
    lines = content.split("\n")
    capture = False
    captured = []

    for line in lines:
        if "## Post Copy" in line or "## Caption" in line:
            capture = True
            continue
        if capture:
            if line.startswith("## ") and captured:
                break
            captured.append(line)

    if captured:
        post_text = "\n".join(captured).strip()

    return post_text


def get_images(folder):
    """Get images in the order specified in POST-COPY.md Photos section, falling back to sorted list."""
    copy_file = folder / "POST-COPY.md"
    specified = []

    if copy_file.exists():
        content = copy_file.read_text()
        lines = content.split("\n")
        capture = False
        for line in lines:
            if "## Photos" in line:
                capture = True
                continue
            if capture:
                if line.startswith("## ") and capture:
                    break
                stripped = line.strip()
                if stripped and (stripped[0].isdigit() or stripped.startswith("-")):
                    import re as _re
                    parts = _re.sub(r'^(\d+\.\s*|- )', '', stripped).strip()
                    if parts.endswith(".jpg") or parts.endswith(".png"):
                        specified.append(parts)

    if specified:
        cropped = folder / "cropped-square"
        images = []
        for fname in specified:
            cropped_path = cropped / fname
            original_path = folder / fname
            if cropped_path.exists():
                images.append(str(cropped_path))
            elif original_path.exists():
                images.append(str(original_path))
            else:
                print(f"  Note: could not find image {fname}")
        if images:
            print(f"  Using {len(images)} images from POST-COPY.md order")
            return images

    cropped = folder / "cropped-square"
    if cropped.exists():
        images = sorted(glob.glob(str(cropped / "*.jpg")))
        if images:
            print(f"  Using all cropped images from: {cropped.name}/")
            return images

    images = sorted(glob.glob(str(folder / "[0-9]*.jpg")))
    images += sorted(glob.glob(str(folder / "[0-9]*.png")))
    return images


def write_manual_handoff(folder, post_text, images, reason):
    """Fallback when Publer can't be used: drop a simple file the user opens,
    then posts from the Instagram app themselves. Never dead-ends."""
    handoff = folder / "POST-MANUALLY.md"
    lines = [
        "# Ready to post on Instagram",
        "",
        f"_{reason}_",
        "",
        "Open the Instagram app, create a new post, attach the images below in",
        "this order, and paste the caption. Nothing was posted for you.",
        "",
        "## Caption (copy this)",
        "",
        post_text or "(no caption found)",
        "",
        "## Images (in order)",
        "",
    ]
    for i, img in enumerate(images, 1):
        lines.append(f"{i}. {img}")
    handoff.write_text("\n".join(lines) + "\n")
    print(f"\n  Saved a manual-post handoff to: {handoff}")
    print("  Open Instagram and post it from there when you're ready.")
    return handoff


def schedule_post(instagram_id, workspace_id, post_text, media_ids, scheduled_at, as_draft):
    """Create the post in Publer. as_draft=True (the default) saves a draft for
    review; it does NOT go live. A scheduled-live post still lives in Publer
    until its time, and you can see and cancel it there."""
    account = {"id": instagram_id}
    if scheduled_at:
        account["scheduled_at"] = scheduled_at

    media_list = [{"id": mid, "type": "image"} for mid in media_ids]

    if len(media_ids) == 0:
        img_type = "status"
    elif len(media_ids) == 1:
        img_type = "photo"
    else:
        img_type = "carousel"

    network_payload = {"type": img_type, "text": post_text}
    if media_list:
        network_payload["media"] = media_list

    payload = {
        "bulk": {
            "state": "draft" if as_draft else "scheduled",
            "posts": [
                {
                    "networks": {"instagram": network_payload},
                    "accounts": [account],
                }
            ],
        }
    }

    resp = requests.post(
        f"{BASE_URL}/posts/schedule",
        headers={**headers(workspace_id), "Content-Type": "application/json"},
        json=payload,
    )

    if resp.status_code in (200, 201):
        data = resp.json()
        job_id = data.get("job_id")
        if job_id:
            result = wait_for_job(job_id, workspace_id)
            if result and result.get("failures"):
                for _, failures in result["failures"].items():
                    for f in failures:
                        print(f"  Publer couldn't do one account: {f.get('message')}")
            return result
        return data
    else:
        print(f"  Publer rejected the request: {resp.status_code}")
        return None


def main():
    parser = argparse.ArgumentParser(description="Social poster (drafts by default)")
    parser.add_argument("post_folder", help="Post folder name under outputs/social/")
    parser.add_argument("--schedule", help="Local time to schedule (e.g. '2026-06-18T08:00:00'). Only used with --publish.")
    parser.add_argument("--publish", action="store_true",
                        help="Opt out of draft mode and let Publer schedule it live (it still sits in Publer for you to see). Off by default.")
    parser.add_argument("--draft", action="store_true",
                        help="Save as a Publer draft for your review (this is already the default).")
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen, change nothing")
    args = parser.parse_args()

    # --draft is the DEFAULT. The only way out of draft mode is the explicit
    # --publish flag, and even then it lands in Publer, never on Instagram
    # directly.
    as_draft = not args.publish

    folder = POST_PLANS_BASE / args.post_folder
    if not folder.exists():
        print(f"Couldn't find that post folder: {folder}")
        print(f"Look inside {POST_PLANS_BASE} for the right name.")
        sys.exit(1)

    print(f"\nCool Hollow Social Poster")
    print(f"{'=' * 44}")
    print(f"Post folder: {folder.name}")
    print(f"Mode: {'DRAFT (you review and publish)' if as_draft else 'scheduled-live in Publer'}")

    post_text = read_post_copy(folder)
    if not post_text:
        print("Couldn't find a caption in POST-COPY.md (looking under '## Caption' or '## Post Copy').")
        sys.exit(1)
    print(f"Caption: {len(post_text)} characters")

    images = get_images(folder)
    if not images:
        print("No images found in this folder.")
        sys.exit(1)
    print(f"Images: {len(images)} files")

    if args.dry_run:
        print("\nDRY RUN. Nothing was sent.")
        print(f"  Would land as: {'a Publer draft' if as_draft else 'a scheduled-live Publer post'}")
        print(f"  Caption preview: {post_text[:120]}...")
        return

    # --- No-dead-skills gate: make sure Publer is set up before we touch it. ---
    # ensure_ready installs/verifies and runs the guided walkthrough if needed.
    # If Publer cannot be made ready (e.g. free tier won't issue a key or can't
    # publish to Instagram), we never error out; we fall back to a manual-post
    # handoff so the work is never lost.
    ready = ensure_ready("publer")
    if not ready:
        write_manual_handoff(
            folder, post_text, images,
            "Publer isn't connected yet (or its free tier can't publish to Instagram).",
        )
        return

    accounts = load_accounts()
    workspace_id = accounts.get("workspace_id")
    instagram_id = accounts.get("instagram_id")

    if not workspace_id or not instagram_id:
        # ensure_ready should have written these; if not, don't dead-end.
        write_manual_handoff(
            folder, post_text, images,
            "Publer is connected but your Instagram account wasn't found in it. "
            "Open Publer and make sure Instagram is connected, then try again.",
        )
        return

    scheduled_at = None
    if args.publish and args.schedule:
        local_time = datetime.fromisoformat(args.schedule).replace(tzinfo=LOCAL_TZ)
        scheduled_at = local_time.astimezone(timezone.utc).isoformat()
        print(f"Scheduled for: {args.schedule} local ({scheduled_at} UTC)")

    print(f"\nUploading {len(images)} images to Publer...")
    media_ids = []
    for img in images:
        result = upload_image(img, workspace_id)
        if result and "id" in result:
            media_ids.append(result["id"])
        else:
            print(f"  Skipping {Path(img).name} (upload failed)")

    if not media_ids:
        # Upload failed; fall back rather than dead-end.
        write_manual_handoff(
            folder, post_text, images,
            "Publer wouldn't accept the images this time.",
        )
        return
    print(f"Uploaded {len(media_ids)} images")

    print(f"\nSaving to Publer...")
    result = schedule_post(instagram_id, workspace_id, post_text, media_ids, scheduled_at, as_draft)

    if result:
        if as_draft:
            print("\nDone. It's saved as a DRAFT in Publer.")
            print("Open Publer, give it a final look, and publish it yourself.")
        else:
            print("\nDone. It's scheduled in Publer.")
            print("You can see it (and cancel it) in Publer any time before it goes out.")
    else:
        # Publer call failed; still don't dead-end.
        write_manual_handoff(
            folder, post_text, images,
            "Publer couldn't save the post this time.",
        )


if __name__ == "__main__":
    main()
