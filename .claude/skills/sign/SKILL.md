---
name: sign
description: Full document signing workflow - find, analyse, sign, store, and draft return email
user_invocable: true
---

# /sign - Document Signing Workflow

> Find a document, analyse it, sign it, store it, and draft the return email. All from one command.

## Arguments

The user will provide one of:
- A document name or description: `/sign the vendor SLA`
- A file path: `/sign ~/Downloads/contract.pdf`
- A reference to an email: `/sign the document from Sarah`
- Just `/sign` with no args — ask what they want to sign

## Google Drive Folder IDs (configure per user)

Read these from `context/business-info.md` or a similar config file. If not configured, ask the user to provide them or to create them in Drive and paste the IDs back.

- **Proposals & Signables:** `<paste folder ID>`
- **Signed:** `<paste folder ID>`

## Signature

- **Signature image:** `reference/signature.png` (transparent PNG, cropped — user supplies)
- **Signing script:** `scripts/sign_pdf.py`
- **Signer name:** Pull from `context/personal-info.md`

## Gmail Attachment Download

**The `mcp__gmail__download_attachment` tool is broken** — it uses the attachment ID as the filename which exceeds filesystem limits. Instead, download Gmail attachments using Python directly:

```python
import json, urllib.request, urllib.parse, base64, os

# Refresh OAuth token
with open(os.path.expanduser("~/.gmail-mcp/credentials.json")) as f:
    creds = json.load(f)
with open(os.path.expanduser("~/.gmail-mcp/gcp-oauth.keys.json")) as f:
    oauth = json.load(f)
oauth_config = oauth.get("installed", oauth.get("web", {}))
data = urllib.parse.urlencode({
    "client_id": oauth_config["client_id"],
    "client_secret": oauth_config["client_secret"],
    "refresh_token": creds["refresh_token"],
    "grant_type": "refresh_token"
}).encode()
req = urllib.request.Request("https://oauth2.googleapis.com/token", data=data)
access_token = json.loads(urllib.request.urlopen(req).read().decode())["access_token"]

# Get message and find attachment
message_id = "MESSAGE_ID_HERE"
url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{message_id}?format=full"
req = urllib.request.Request(url, headers={"Authorization": f"Bearer {access_token}"})
msg = json.loads(urllib.request.urlopen(req).read().decode())

# Find attachment, download, decode base64url, save to file
```

## Phase 1: Find the Document

Based on the user's input, find the document:

1. **If a file path is given:** Use that directly.
2. **If a document name is given:** Search in these locations in order:
   - `~/Downloads/` (most likely for recent documents)
   - `~/Desktop/`
   - Gmail attachments (search Gmail, then use the Python download method above — NOT `mcp__gmail__download_attachment`)
   - Google Drive (use `mcp__google-sheets__searchDriveFiles`)
3. **If an email reference is given:** Search Gmail for the email, find the attachment, download using the Python method above.

Once found, confirm with the user: "Found [filename]. Is this the right document?"

## Phase 2: Store and Analyse

1. **Copy to Desktop** if not already there
2. **Upload to Google Drive** > the user's "Proposals & Signables" folder (ID configured above)
3. **Read the document** (Claude can read PDFs directly with the Read tool)
4. **Present a structured analysis:**

### Document Analysis

**Summary**
- What the document is
- Who the parties are
- What it commits the user to

**Key Terms**
- Pricing / fees / payment terms
- Duration / term length
- Termination clauses
- Liability / indemnification
- Exclusivity or non-compete
- Intellectual property
- Confidentiality

**Flags**
- Anything unusual, one-sided, or potentially problematic
- Missing clauses that should be there
- Ambiguous language

**Suggested Questions**
- Things to clarify with the other party before signing

**Suggested Changes**
- Specific edits or additions to negotiate

5. Ask: "Happy to sign, or do you want to discuss anything first?"

## Phase 3: Sign

When the user says "sign it" / "approved" / "go ahead":

1. **Run the signing script:**
   ```bash
   python3 scripts/sign_pdf.py "<path_to_pdf>" --page <last_page_or_specified> --position <detected_or_default>
   ```
   The script:
   - Overlays the user's signature image onto the PDF
   - Adds the date below the signature
   - Adds the signer's name (from `context/personal-info.md`) below the date
   - Saves as `<filename>_signed.pdf`

2. If the script can't auto-detect the signature position, ask:
   - "Which page should I sign? (default: last page)"
   - "Where should the signature go? (bottom-left, bottom-right, or I can try to find the signature line)"

3. **Visually verify the signature yourself before showing to the user.** After signing:
   - Render the signed page as an image using PyMuPDF: `page.get_pixmap(dpi=200)`, save to `/tmp/`, then read it with the Read tool
   - Look at the rendered image yourself. Check:
     - Is the signature the right way up? (should read naturally)
     - Is it horizontal, not vertical or rotated?
     - Is it in the correct position (inside the signature block, not overlapping text)?
     - Is it a reasonable size (not too large, not too small)?
   - If anything looks wrong, fix it and re-render before showing to the user
   - **Do NOT skip this step.** The signature image orientation has caused issues before.
4. **Show the verified signed page** to the user for final confirmation: "Here's the signed document. Does the signature placement look right?"

## Phase 4: Store Signed Version

1. **Copy signed PDF to Desktop**
2. **Upload to Google Drive** > the user's "Signed" folder (ID configured above)
3. **Copy to `outputs/`** in the workspace

## Phase 5: Draft Return Email

1. **Identify the recipient** — from the original email thread, or ask the user
2. **Draft an email** using `mcp__gmail__draft_email`:
   - To: the relevant person
   - Subject: Re: [original subject] or "Signed: [document name]"
   - Body: Brief, in the user's voice (see `context/voice-and-tone.md`). Something like:
     "Hi [Name], Signed document attached. Let me know if you need anything else. Thanks, [signer first name]"
   - Attach the signed PDF
3. **Show the draft** for approval: "Here's the email draft. Want me to send it?"
4. On approval, send via `mcp__gmail__send_email`

## Rules

- **Always show the analysis before signing.** Never sign without the user reviewing.
- **Always show the signed document before storing/sending.** Visual confirmation of placement.
- **Always show the email draft before sending.** No emails go out without approval.
- **Never commit the signature image to git.** It should be in `.gitignore`.
- **Use the user's voice** for all email drafts (see `context/voice-and-tone.md`).
