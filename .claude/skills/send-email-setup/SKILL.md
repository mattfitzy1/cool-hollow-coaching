# /send-email-setup — Stand up Gmail sending for a client (or yourself)

Set up real email *sending* (not drafting) via the Gmail API + OAuth, end to end. Does
everything mechanical — venv, libraries, script, token, test send, optional VPS port —
and pauses at the only two steps a human must do: the Google Cloud Console clicks and
the consent "Allow".

## Why this exists

The Claude Gmail MCP can only *draft*, not send. Real sending needs a Google OAuth app
(`gmail.send`). Published to Production it never needs reauth. This skill is the repeatable
install of that, for each client (or your own account). Proven path — see
`context/deep-memory` for the 8 June (logged as 5 June) walk-through.

## What you provide

- **Sender email** — the Google account email to send *from* (the client's, or yours).
- **Target** — `local` (this machine), `vps` (a box over Tailscale SSH), or both.
- For `vps`: the SSH host alias + the Linux user + the dir on the box (e.g. `aios-vps`,
  user `aios`, `~/sendmail-test`).
- **Work dir** — where the script + secrets live. Default `~/sendmail-test` for a sandbox,
  or `<repo>/` + `scripts/` if installing into a client's AIOS repo.

If anything is missing, ask before starting.

## The two human gates (the skill pauses, never tries to automate these)

- **GATE 1 — Google Cloud Console.** Only the person with the Google account can do this.
- **GATE 2 — the consent "Allow".** Only a human in the browser can click it.

Everything else the skill does itself.

---

## Step 0: Prerequisites

- `python3` available on the target(s). For a VPS target, confirm SSH works:
  `ssh <host> 'whoami'`.
- The skill's template script lives next to this file: `send_email.py`. Use it as the
  canonical sender (copy it into the work dir — do not hand-write one).

## Step 1: GATE 1 — Google Cloud Console (guide, then wait)

Tell the user to do this at https://console.cloud.google.com (signed in as the **sender's**
Google account — this is whose mailbox sends):

1. New project (e.g. `<client>-sendmail`).
2. APIs & Services → Library → enable **Gmail API**.
3. **Google Auth Platform / OAuth consent screen**:
   - User type **External** (personal Gmail) — or **Internal** if the sender is on the
     same Google Workspace org (Internal needs no warning, no 7-day expiry, no verification).
   - App name + support email + developer email.
   - Add the sender as a **Test user** (External only).
4. **Clients → Create client → OAuth client ID → Application type: Desktop app** → Create →
   **Download JSON**.

Then pause: ask the user to confirm the JSON is downloaded, and where. **Do not proceed
until they confirm.**

## Step 2: Place credentials.json (auto)

- Find the downloaded client secret: look in `~/Downloads` for `client_secret*.json`
  (most recent), or wherever the user said.
- Create the work dir if needed, and move/rename the file to `<workdir>/credentials.json`.
- `chmod 600` it. Confirm it parses and the key is `installed` (Desktop client):
  `python3 -c "import json;print(list(json.load(open('<workdir>/credentials.json')))[0])"`.

## Step 3: Environment (auto)

- Copy `send_email.py` (next to this SKILL.md) into `<workdir>/`.
- Create a venv and install the libraries:
  ```bash
  cd <workdir>
  python3 -m venv .venv
  .venv/bin/pip install -q --upgrade pip
  .venv/bin/pip install -q google-auth google-auth-oauthlib google-api-python-client
  .venv/bin/python -c "import googleapiclient; print('libs OK')"
  ```

## Step 4: GATE 2 — consent (launch, then wait)

- Run the auth flow. It opens the **sender's** browser:
  ```bash
  cd <workdir> && .venv/bin/python send_email.py --auth
  ```
  Run it `run_in_background: true` (it blocks until the browser flow completes).
- Tell the user: sign in as the **sender's** account → "Google hasn't verified this app" →
  **Advanced → Go to … (unsafe) → Allow**.
- Wait until `<workdir>/token.json` exists, then `chmod 600` it.

## Step 5: Test send (auto)

```bash
cd <workdir>
GMAIL_SENDER="<sender>" .venv/bin/python send_email.py \
  --to "<sender>" --subject "send-email-setup test" --body "First send via OAuth. Working."
```
Confirm a `Message ID:` line. If it errors with `access_blocked` / `unverified`, the
Workspace admin may be blocking unverified apps — use Internal user type or allowlist it.

## Step 6: Kill the 7-day expiry — GATE 1 again (guide)

Tell the user: **OAuth consent screen → Audience → Publish app → push to Production**
(instant, free, no verification — do NOT click "Prepare for verification"). Then re-run
Step 4 once so the token is minted under Production (the earlier token may still carry the
7-day clock). The new token does not expire.

## Step 7: Port to a VPS (optional — only if target includes `vps`)

The VPS has no browser, so you never auth there. Carry the token up (it is account-bound,
not machine-bound):

1. Make the box dir + venv + libs (mirror Step 3 over SSH, as the box user).
2. Copy `credentials.json` + `token.json` + `send_email.py` up. A clean way:
   ```bash
   tar -C <workdir> -cf - credentials.json token.json send_email.py | base64 | \
     ssh <host> "mkdir -p <boxdir> && base64 -d | tar -C <boxdir> -xf - && \
       chmod 600 <boxdir>/credentials.json <boxdir>/token.json"
   ```
   (chown to the box user if connecting as root.)
3. Send a test **from the box** to prove headless sending:
   ```bash
   ssh <host> "su - <user> -c 'cd <boxdir> && GMAIL_SENDER=\"<sender>\" \
     .venv/bin/python send_email.py --to <sender> --subject \"VPS headless test\" --body \"Sent from the cloud.\"'"
   ```

## Step 8: Report

State: where it's set up (local / VPS), the sender, that it sends (test Message IDs),
whether it's in Production (no 7-day reauth) or still Testing (7-day — finish Step 6).

## Guardrails

- `credentials.json` and `token.json` are **secrets**. Keep them **outside any git repo**
  (a `~/sendmail-test`-style dir), or if inside a repo, confirm `.gitignore` covers
  `credentials.json` + `token.json` before anything commits. Never echo their contents.
- Only `gmail.send` scope by default (sensitive — no CASA). If a client needs more, add
  scopes deliberately and note that restricted scopes (`gmail.readonly`/`compose`) raise the
  verification bar.
- The consent must be done as the **sender's** Google account — that is whose mail goes out.
- For a client VPS, transfer the token carefully (their own tailnet / one-time secret), and
  never SSH into a shared box from a client's machine.
