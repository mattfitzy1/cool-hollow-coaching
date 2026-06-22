#!/usr/bin/env python3
"""Create Google Forms from a YAML spec via Google Forms API.

Uses USER OAuth (your own Google account) because the Forms API
does not accept service account ownership for standard accounts.

Usage:
    # First time — triggers browser auth:
    python3 .claude/skills/create-form/create_form.py --auth

    # Create a form:
    python3 .claude/skills/create-form/create_form.py --spec <path-to-spec.yaml>

Requires:
    - credentials.json in workspace root (OAuth Desktop Client)
    - Forms API + Drive API enabled on the GCP project
    - python3 -m pip install google-api-python-client google-auth google-auth-oauthlib pyyaml
"""

import argparse
import json
import sys
from pathlib import Path

import yaml
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


WORKSPACE = Path(__file__).resolve().parent.parent.parent.parent
OAUTH_CLIENT = WORKSPACE / "credentials.json"
TOKEN_PATH = WORKSPACE / ".token-forms.json"
SCOPES = [
    "https://www.googleapis.com/auth/forms.body",
    "https://www.googleapis.com/auth/drive",
]


def get_credentials(force_auth: bool = False) -> Credentials:
    """Load or create OAuth credentials with Forms + Drive scopes."""
    creds = None
    if TOKEN_PATH.exists() and not force_auth:
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token and not force_auth:
            creds.refresh(Request())
        else:
            if not OAUTH_CLIENT.exists():
                sys.exit(
                    f"OAuth client file not found at {OAUTH_CLIENT}\n"
                    "   This should be the Desktop Client secret from GCP console."
                )
            flow = InstalledAppFlow.from_client_secrets_file(str(OAUTH_CLIENT), SCOPES)
            creds = flow.run_local_server(
                port=0,
                prompt="consent",
                access_type="offline",
                open_browser=True,
            )
        TOKEN_PATH.write_text(creds.to_json())
        print(f"  Token saved to {TOKEN_PATH}")
    return creds


def get_services(force_auth: bool = False):
    creds = get_credentials(force_auth=force_auth)
    forms = build("forms", "v1", credentials=creds, cache_discovery=False)
    drive = build("drive", "v3", credentials=creds, cache_discovery=False)
    return forms, drive


def build_item_request(item, index):
    """Convert a YAML item to a Forms API createItem request."""
    itype = item["type"]

    if itype == "grid":
        # Grid uses questionGroupItem, not questionItem — different envelope
        questions_for_grid = [
            {
                "rowQuestion": {"title": row},
                "required": item.get("required", False),
            }
            for row in item["rows"]
        ]
        return {
            "createItem": {
                "item": {
                    "title": item["title"],
                    "description": item.get("help", ""),
                    "questionGroupItem": {
                        "questions": questions_for_grid,
                        "grid": {
                            "columns": {
                                "type": "RADIO",
                                "options": [{"value": c} for c in item["columns"]],
                            }
                        },
                    },
                },
                "location": {"index": index},
            }
        }

    question_base = {"required": item.get("required", False)}

    if itype == "paragraph_text":
        question = {**question_base, "textQuestion": {"paragraph": True}}
    elif itype == "short_answer":
        question = {**question_base, "textQuestion": {"paragraph": False}}
    elif itype == "multiple_choice":
        options = [{"value": c} for c in item["choices"]]
        if item.get("other"):
            options.append({"isOther": True})
        question = {
            **question_base,
            "choiceQuestion": {"type": "RADIO", "options": options, "shuffle": False},
        }
    elif itype == "checkbox":
        options = [{"value": c} for c in item["choices"]]
        if item.get("other"):
            options.append({"isOther": True})
        question = {
            **question_base,
            "choiceQuestion": {"type": "CHECKBOX", "options": options, "shuffle": False},
        }
    elif itype == "scale":
        question = {
            **question_base,
            "scaleQuestion": {
                "low": item.get("min", 1),
                "high": item.get("max", 5),
                "lowLabel": item.get("min_label", ""),
                "highLabel": item.get("max_label", ""),
            },
        }
    else:
        raise ValueError(f"Unknown item type: {itype}")

    return {
        "createItem": {
            "item": {
                "title": item["title"],
                "description": item.get("help", ""),
                "questionItem": {"question": question},
            },
            "location": {"index": index},
        }
    }


def build_section_break(title, description, index):
    return {
        "createItem": {
            "item": {
                "title": title,
                "description": description or "",
                "pageBreakItem": {},
            },
            "location": {"index": index},
        }
    }


def make_public(drive_svc, form_id):
    """Set 'anyone with the link' to reader so external recipients can open and
    respond. ALWAYS applied on creation — an org-locked form is useless to a
    prospect. supportsAllDrives covers forms that live in a Shared Drive."""
    drive_svc.permissions().create(
        fileId=form_id,
        body={"type": "anyone", "role": "reader"},
        sendNotificationEmail=False,
        supportsAllDrives=True,
        fields="id",
    ).execute()


def create_form_from_spec(spec_path: Path):
    spec = yaml.safe_load(spec_path.read_text())
    forms_svc, drive_svc = get_services()

    print(f"Creating form: {spec['title']}")
    form = forms_svc.forms().create(body={"info": {"title": spec["title"]}}).execute()
    form_id = form["formId"]
    print(f"  ID: {form_id}")

    # Rename the Drive file to match the form title (Drive filename != Forms title by default)
    try:
        drive_svc.files().update(fileId=form_id, body={"name": spec["title"]}).execute()
        print(f"  Drive filename set to: {spec['title']}")
    except HttpError as e:
        print(f"  WARN: could not rename Drive file: {e}")

    updates = []
    if spec.get("description"):
        updates.append({
            "updateFormInfo": {
                "info": {"description": spec["description"]},
                "updateMask": "description",
            }
        })
    if updates:
        forms_svc.forms().batchUpdate(formId=form_id, body={"requests": updates}).execute()
        print("  Description applied")

    requests = []
    index = 0
    for section in spec.get("sections", []):
        requests.append(build_section_break(section["title"], section.get("description"), index))
        index += 1
        for item in section.get("items", []):
            requests.append(build_item_request(item, index))
            index += 1

    for i in range(0, len(requests), 50):
        chunk = requests[i : i + 50]
        forms_svc.forms().batchUpdate(formId=form_id, body={"requests": chunk}).execute()
        print(f"  Added items {i + 1}–{i + len(chunk)}")

    folder_id = spec.get("drive_folder_id")
    if folder_id:
        current = drive_svc.files().get(fileId=form_id, fields="parents").execute()
        prev_parents = ",".join(current.get("parents", []))
        drive_svc.files().update(
            fileId=form_id,
            addParents=folder_id,
            removeParents=prev_parents,
            fields="id, parents",
        ).execute()
        print(f"  Moved to folder {folder_id}")

    for shared in spec.get("share_with", []) or []:
        email = shared["email"]
        role = shared.get("role", "writer")
        try:
            drive_svc.permissions().create(
                fileId=form_id,
                body={"type": "user", "role": role, "emailAddress": email},
                sendNotificationEmail=False,
                fields="id",
            ).execute()
            print(f"  Shared with {email} as {role}")
        except HttpError as e:
            print(f"  WARN: could not share with {email}: {e}")

    # ALWAYS make the form public so external recipients can open and respond.
    make_public(drive_svc, form_id)
    print("  Public access set: anyone with the link can respond")

    # After creation, refetch to get responderUri
    form = forms_svc.forms().get(formId=form_id).execute()
    published = form.get("responderUri") or f"https://docs.google.com/forms/d/{form_id}/viewform"
    edit = f"https://docs.google.com/forms/d/{form_id}/edit"
    print()
    print(f"RESPONDER URL: {published}")
    print(f"EDIT URL:      {edit}")
    return {"formId": form_id, "responder_url": published, "edit_url": edit}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", help="Path to YAML spec")
    ap.add_argument("--auth", action="store_true", help="Force OAuth re-auth")
    ap.add_argument("--make-public", metavar="FORM_ID",
                    help="Repair an existing org-locked form: set anyone-with-link "
                         "reader and verify. Skips spec creation.")
    args = ap.parse_args()

    if args.auth:
        get_credentials(force_auth=True)
        print("Auth complete. Token stored.")
        return

    if args.make_public:
        _, drive_svc = get_services()
        make_public(drive_svc, args.make_public)
        perms = drive_svc.permissions().list(
            fileId=args.make_public, supportsAllDrives=True,
            fields="permissions(type,role,emailAddress)",
        ).execute().get("permissions", [])
        anyone = [p for p in perms if p.get("type") == "anyone"]
        state = "PUBLIC OK" if anyone else "STILL NOT PUBLIC"
        print(f"{args.make_public}: {state} — "
              f"{[(p.get('type'), p.get('role')) for p in perms]}")
        return

    if not args.spec:
        ap.error("--spec is required unless --auth or --make-public is used")

    spec_path = Path(args.spec)
    if not spec_path.exists():
        sys.exit(f"Spec not found: {spec_path}")

    try:
        result = create_form_from_spec(spec_path)
        print()
        print(json.dumps(result, indent=2))
    except HttpError as e:
        err = json.loads(e.content).get("error", {}) if e.content else {}
        if err.get("status") == "PERMISSION_DENIED" and "has not been used" in err.get("message", ""):
            sys.exit(
                "\nGoogle Forms API is not enabled on this GCP project.\n"
                "   Enable it here (one-time, 30 seconds):\n"
                "   https://console.developers.google.com/apis/api/forms.googleapis.com/overview?project=670276229240\n"
                "   Then rerun this command."
            )
        raise


if __name__ == "__main__":
    main()
