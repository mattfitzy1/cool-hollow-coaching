#!/usr/bin/env python3
"""
Send email via the Gmail API (OAuth2). One scope: gmail.send — a SENSITIVE scope,
so it never triggers restricted/CASA verification. Published to Production, the
token does not expire.

Sender: GMAIL_SENDER env var, else the --from flag.

  python send_email.py --auth                                  # one-time browser consent
  python send_email.py --to a@b.com --subject "Hi" --body "..." # send
  python send_email.py --to a@b.com --subject "..." --body "..." --attach /path/file.pdf --cc c@d.com
"""
import argparse, base64, os, sys
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
from pathlib import Path

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
HERE = Path(__file__).resolve().parent
TOKEN_PATH = HERE / "token.json"
CREDENTIALS_PATH = HERE / "credentials.json"


def get_sender(arg_from):
    s = os.environ.get("GMAIL_SENDER") or arg_from
    if not s:
        print("No sender. Set GMAIL_SENDER or pass --from you@example.com")
        sys.exit(1)
    return s


def authenticate():
    from google_auth_oauthlib.flow import InstalledAppFlow
    if not CREDENTIALS_PATH.exists():
        print(f"Missing {CREDENTIALS_PATH}. Download the OAuth Client (Desktop) JSON and save it here as credentials.json")
        sys.exit(1)
    flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_PATH), SCOPES)
    creds = flow.run_local_server(port=0)
    TOKEN_PATH.write_text(creds.to_json())
    print(f"Token saved to {TOKEN_PATH}")
    print("If the app is still in 'Testing', this token expires in 7 days. Publish to Production to stop that.")


def get_credentials():
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    if not TOKEN_PATH.exists():
        print("No token.json. Run with --auth first.")
        sys.exit(1)
    creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        TOKEN_PATH.write_text(creds.to_json())
    return creds


def send(sender, to, subject, body, attach=None, cc=None):
    from googleapiclient.discovery import build
    service = build("gmail", "v1", credentials=get_credentials())
    msg = MIMEMultipart()
    msg["From"], msg["To"], msg["Subject"] = sender, to, subject
    if cc:
        msg["Cc"] = cc
    msg.attach(MIMEText(body, "plain"))
    if attach:
        fp = Path(attach)
        if not fp.exists():
            print(f"Attachment not found: {attach}")
            sys.exit(1)
        part = MIMEBase("application", "octet-stream")
        part.set_payload(fp.read_bytes())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", "attachment", filename=fp.name)
        msg.attach(part)
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    result = service.users().messages().send(userId="me", body={"raw": raw}).execute()
    print(f"Sent. Message ID: {result['id']}")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Send email via Gmail API (OAuth2)")
    p.add_argument("--auth", action="store_true")
    p.add_argument("--from", dest="sender")
    p.add_argument("--to"); p.add_argument("--subject"); p.add_argument("--body")
    p.add_argument("--attach"); p.add_argument("--cc")
    a = p.parse_args()
    if a.auth:
        authenticate()
    elif a.to and a.subject and a.body:
        send(get_sender(a.sender), a.to, a.subject, a.body, a.attach, a.cc)
    else:
        p.print_help()
