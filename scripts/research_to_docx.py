#!/usr/bin/env python3
"""Convert a deep-research session's markdown reports into Word documents.

Reads every .md file in `outputs/deep-research/{slug}/` and produces a matching
.docx in two places:
  1. `~/Desktop/Deep Research - {slug}/` (local, for fast read)
  2. My Drive > Research > Deep Research - {slug}/ (cloud mirror, phone-readable)

Markdown sources stay where they are. Word output is for reading, not editing.

Run automatically by the deep-research skill at the end of every session, or
manually with:
    python scripts/research_to_docx.py outputs/deep-research/{slug}/

Skip Drive upload with --no-drive (local-only).
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

ROOT = Path(__file__).resolve().parent.parent

# My Drive > Research (parent folder for every deep-research session).
# Set DRIVE_RESEARCH_FOLDER_ID in your environment to the ID of the Drive folder
# you want research docs uploaded to. Leave unset to upload to My Drive root.
DRIVE_RESEARCH_FOLDER_ID = os.environ.get("DRIVE_RESEARCH_FOLDER_ID", "")
CLIENT_SECRETS = ROOT / "credentials.json"
TOKEN_FILE = ROOT / "token-drive.json"
SCOPES = ["https://www.googleapis.com/auth/drive.file"]
DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
FOLDER_MIME = "application/vnd.google-apps.folder"


def find_session_folder(arg: str) -> Path:
    p = Path(arg).expanduser()
    if not p.is_absolute():
        p = (ROOT / p).resolve()
    if not p.exists():
        raise FileNotFoundError(f"Session folder not found: {p}")
    if not p.is_dir():
        raise NotADirectoryError(f"Not a directory: {p}")
    return p


def desktop_folder_for(session: Path) -> Path:
    desktop = Path.home() / "Desktop"
    label = session.name
    target = desktop / f"Deep Research - {label}"
    target.mkdir(parents=True, exist_ok=True)
    return target


def convert_one(md_path: Path, out_path: Path) -> None:
    cmd = [
        "pandoc",
        str(md_path),
        "-f", "gfm+pipe_tables+task_lists",
        "-t", "docx",
        "--toc",
        "--toc-depth=2",
        "-o", str(out_path),
    ]
    subprocess.run(cmd, check=True, capture_output=True)


def convert_session(session: Path) -> tuple[list[Path], Path]:
    md_files = sorted(p for p in session.glob("*.md") if not p.name.startswith("."))
    if not md_files:
        raise FileNotFoundError(f"No markdown files in {session}")
    target = desktop_folder_for(session)
    written: list[Path] = []
    for md in md_files:
        out = target / (md.stem + ".docx")
        convert_one(md, out)
        written.append(out)
    return written, target


def build_drive_service():
    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRETS), SCOPES)
            creds = flow.run_local_server(port=0)
        TOKEN_FILE.write_text(creds.to_json())
    return build("drive", "v3", credentials=creds)


def find_or_create_drive_folder(service, name: str, parent_id: str) -> str:
    safe_name = name.replace("'", "\\'")
    q = (
        f"name = '{safe_name}' and "
        f"mimeType = '{FOLDER_MIME}' and "
        f"trashed = false"
    )
    if parent_id:
        q += f" and '{parent_id}' in parents"
    resp = service.files().list(
        q=q,
        fields="files(id, name)",
        supportsAllDrives=True,
        includeItemsFromAllDrives=True,
    ).execute()
    if resp.get("files"):
        return resp["files"][0]["id"]
    metadata = {"name": name, "mimeType": FOLDER_MIME}
    if parent_id:
        metadata["parents"] = [parent_id]
    folder = service.files().create(
        body=metadata,
        fields="id",
        supportsAllDrives=True,
    ).execute()
    return folder["id"]


def upload_to_drive(local_paths: list[Path], session_label: str) -> tuple[str, list[str]]:
    service = build_drive_service()
    session_folder_id = find_or_create_drive_folder(
        service, f"Deep Research - {session_label}", DRIVE_RESEARCH_FOLDER_ID
    )
    links: list[str] = []
    for p in local_paths:
        media = MediaFileUpload(str(p), mimetype=DOCX_MIME, resumable=False)
        result = service.files().create(
            body={"name": p.name, "parents": [session_folder_id]},
            media_body=media,
            fields="id, name, webViewLink",
            supportsAllDrives=True,
        ).execute()
        links.append(result.get("webViewLink", ""))
    folder_link = f"https://drive.google.com/drive/folders/{session_folder_id}"
    return folder_link, links


def main() -> int:
    args = sys.argv[1:]
    skip_drive = False
    if "--no-drive" in args:
        skip_drive = True
        args = [a for a in args if a != "--no-drive"]
    if len(args) != 1:
        print(__doc__, file=sys.stderr)
        return 1
    session = find_session_folder(args[0])
    written, target = convert_session(session)
    print(f"Wrote {len(written)} .docx file(s) locally:")
    print(f"  {target}")
    for p in written:
        print(f"  - {p.name}")

    if skip_drive:
        print("Drive upload skipped (--no-drive).")
        return 0

    try:
        folder_link, _file_links = upload_to_drive(written, session.name)
        print(f"\nUploaded to Drive: {folder_link}")
    except Exception as exc:
        print(f"\nDrive upload failed: {exc}", file=sys.stderr)
        print("Local files are still available on Desktop. Re-run later or use --no-drive.")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
