#!/usr/bin/env python3
"""
Send emails via Gmail API (OAuth2).

The sender address is read from the GMAIL_SENDER environment variable. Set it
to your own Gmail address before using.

First run:  GMAIL_SENDER="you@example.com" python scripts/send_email.py --auth
Usage:      GMAIL_SENDER="you@example.com" python scripts/send_email.py --to "recipient@example.com" --subject "Hello" --body "Message here"
Attach:     GMAIL_SENDER="you@example.com" python scripts/send_email.py --to "..." --subject "..." --body "..." --attach "/path/to/file.pdf"
"""

import argparse
import base64
import json
import os
import sys
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
from pathlib import Path

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
WORKSPACE = Path(__file__).resolve().parent.parent
TOKEN_PATH = WORKSPACE / "token.json"
CREDENTIALS_PATH = WORKSPACE / "credentials.json"


def get_sender() -> str:
    sender = os.environ.get("GMAIL_SENDER")
    if not sender:
        print("GMAIL_SENDER environment variable not set. Set it to your Gmail address.")
        print('  e.g. export GMAIL_SENDER="you@example.com"')
        sys.exit(1)
    return sender


def authenticate():
    """One-time OAuth2 flow — opens browser, saves refresh token to token.json."""
    from google_auth_oauthlib.flow import InstalledAppFlow

    if not CREDENTIALS_PATH.exists():
        print(f"Missing {CREDENTIALS_PATH}")
        print("Download OAuth Client ID (Desktop) JSON from Google Cloud Console.")
        sys.exit(1)

    flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_PATH), SCOPES)
    creds = flow.run_local_server(port=0)

    TOKEN_PATH.write_text(creds.to_json())
    print(f"Token saved to {TOKEN_PATH}")


def get_credentials():
    """Load credentials from token.json, refreshing if expired."""
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials

    if not TOKEN_PATH.exists():
        print("No token.json found. Run: python scripts/send_email.py --auth")
        sys.exit(1)

    creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        TOKEN_PATH.write_text(creds.to_json())

    return creds


def send_email(to: str, subject: str, body: str, attachment: str = None):
    """Send an email, optionally with a file attachment."""
    from googleapiclient.discovery import build

    creds = get_credentials()
    service = build("gmail", "v1", credentials=creds)

    msg = MIMEMultipart()
    msg["From"] = get_sender()
    msg["To"] = to
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    if attachment:
        file_path = Path(attachment)
        if not file_path.exists():
            print(f"Attachment not found: {attachment}")
            sys.exit(1)

        mime_types = {
            ".pdf": "application/pdf",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        }
        content_type = mime_types.get(file_path.suffix.lower(), "application/octet-stream")
        maintype, subtype = content_type.split("/", 1)

        with open(file_path, "rb") as f:
            part = MIMEBase(maintype, subtype)
            part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", "attachment", filename=file_path.name)
        msg.attach(part)

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    result = service.users().messages().send(userId="me", body={"raw": raw}).execute()
    print(f"Sent. Message ID: {result['id']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send email via Gmail API")
    parser.add_argument("--auth", action="store_true", help="Run one-time OAuth2 setup")
    parser.add_argument("--to", help="Recipient email")
    parser.add_argument("--subject", help="Email subject")
    parser.add_argument("--body", help="Email body text")
    parser.add_argument("--attach", help="File path to attach (.pdf, .docx)")
    args = parser.parse_args()

    if args.auth:
        authenticate()
    elif args.to and args.subject and args.body:
        send_email(args.to, args.subject, args.body, args.attach)
    else:
        parser.print_help()
