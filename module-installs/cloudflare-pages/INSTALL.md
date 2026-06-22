---
# Read by scripts/build_registry.py so Cloudflare shows up in /setup and
# /doctor. Keep in step with .claude/skills/cloudflare-pages/SKILL.md.
requires:
  - tool: cloudflare
    type: key
    requires_bin: [wrangler]
    requires_runtime: [node]
    account: "Cloudflare"
    bundle: app
    plan: "Free"
    signup: "https://dash.cloudflare.com/sign-up → then My Profile → API Tokens → Create Custom Token (Account / Cloudflare Pages: Edit)"
    where: "API token into CLOUDFLARE_API_TOKEN; Account ID (right sidebar on any domain or Pages page) into CLOUDFLARE_ACCOUNT_ID, in .env"
    spend: "Free tier covers everything here (500 builds/month, 100 custom domains per project)"
    verify: "python scripts/cloudflare_pages.py verify"
    optional: false
---

# Cloudflare Pages - Cool Hollow Coaching module installer

> Puts your Cool Hollow Coaching app live on the web at a shareable link, for free.

<!-- MODULE METADATA
module: cloudflare-pages
version: v1
status: RELEASED
requires: []
phase: 2
category: App & Web
complexity: medium
api_keys: 1
setup_time: 15-20 minutes
-->

---

## FOR CLAUDE

You are connecting **Cloudflare Pages** so Matt can deploy the Cool Hollow Coaching app to a live `*.pages.dev` link.

**Your role:** A steady guide through a slightly longer setup (this one needs a small amount of software first, then a token). Matt is non-technical, so do the software install for him where you can and narrate it plainly.

**Behaviour:**
- This is a **key tool**, not a login tool. Cloudflare never runs `wrangler login` or `wrangler whoami`. The token in `.env` is the only credential, and the verify is a token-scoped REST call.
- **Software before key.** Node and wrangler must exist before the token is useful. Install them via Homebrew (Node) and npm (wrangler) first. Do not collect the token until the software check passes.
- He owns the token. You guide the click path; he pastes it into `.env`. Never echo a key back, never ask his to paste it into chat.
- There is no hardcoded fallback account. A missing `CLOUDFLARE_ACCOUNT_ID` must fail loudly into this walkthrough, never silently target someone else's account.
- No em-dashes. US English. Celebrate the deploy ("Your app is live on the internet - that link is yours to send to anyone.").

**Self-detect:** `cloudflare-pages` calls `ensure_ready("cloudflare")` before any deploy. Layer 0 of that check installs Node and wrangler if missing, then checks the token and runs the verify. This module is the human-readable version of that same flow.

**Escalation line:** "Stuck? Send Matthew the output of `/doctor` and he'll point you to the exact step."

---

## OVERVIEW

Read this to Matt before starting:

We're connecting **Cloudflare Pages** - this is how the Cool Hollow Coaching app goes from a file on your Mac to a real, live website anyone can open. When it's done, your app sits at a link like `https://cool-hollow.pages.dev`, and any time you change the app, Claude redeploys it in seconds.

Here's what we'll do:

1. **Install two small bits of software** Cloudflare needs (Node and wrangler) - Claude does this for you
2. **Make a free Cloudflare account**
3. **Create one API token** and copy your account ID
4. **Verify** the token works
5. **Deploy** the Cool Hollow Coaching app and get your live link

**Setup time:** 15-20 minutes (most of it is the one-time software install)
**Running cost:** Free. Cloudflare's free Pages tier covers everything you need (500 builds a month, custom domains, SSL). You will not be charged for this.

---

## PREREQUISITES

Cloudflare deploys through a tool called `wrangler`, which runs on `node`. Both must be on your Mac first. Claude installs them through **Homebrew** (the standard Mac software installer). We install software **before** collecting the token, because a token with nothing to run it is useless.

### Check what's already there

```bash
command -v brew  && echo "brew ok"  || echo "brew MISSING"
command -v node  && echo "node ok"  || echo "node MISSING"
command -v wrangler && echo "wrangler ok" || echo "wrangler MISSING"
```

### Install anything missing, in this order

1. **Homebrew** (only if missing) - paste the one official command:
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
2. **Node** via Homebrew:
   ```bash
   brew install node
   ```
3. **wrangler** via npm:
   ```bash
   npm i -g wrangler
   ```

[VERIFY] Re-run the three checks above; all three should now say `ok`:

```bash
command -v brew && command -v node && command -v wrangler && echo "all software ready"
```

"That's the software side done - the trickiest part. Now we just need your free account."

---

## COLLECT THE KEY

Two things go into `.env`: an **API token** and your **account ID**. Both come from the Cloudflare dashboard. We collect them one at a time.

### Step 1: Create a free Cloudflare account

Open **https://dash.cloudflare.com/sign-up** and sign up. No card needed for the free tier.

"Tell me when you're signed in and looking at the Cloudflare dashboard."

[VERIFY] He's logged into the Cloudflare dashboard.

---

### Step 2: Create the API token

In the dashboard, click your profile (top right) → **My Profile** → **API Tokens** → **Create Token**. Choose **Create Custom Token** and set exactly these permissions:

- **Account** · **Cloudflare Pages** · **Edit**

Then create the token and **copy it** (Cloudflare shows it once).

"Copy the token - don't paste it to me. Keep that browser tab open, we need your account ID next."

[VERIFY] He has the token copied. (If he navigated away before copying, he'll need to make a fresh one - Cloudflare only shows a token once.)

---

### Step 3: Paste the token into .env

```bash
test -f .env || cp .env.example .env
```

Open `.env`, find:

```
CLOUDFLARE_API_TOKEN=
```

Paste the token right after the `=` (no spaces, no quotes). Save.

"Tell me 'done' when it's saved."

[VERIFY] On "done":

```bash
grep -E "^CLOUDFLARE_API_TOKEN=." .env >/dev/null && echo "token present" || echo "still empty"
```

---

### Step 4: Copy and paste your account ID

Back in Cloudflare, go to **Workers & Pages**. On the right-hand sidebar you'll see your **Account ID** - copy it. Paste it into `.env`:

```
CLOUDFLARE_ACCOUNT_ID=
```

Save.

"This tells Claude which account to deploy into - yours, and only yours. Tell me 'done'."

[VERIFY] On "done":

```bash
grep -E "^CLOUDFLARE_ACCOUNT_ID=." .env >/dev/null && echo "account id present" || echo "still empty"
```

---

## INSTALL

### Step 5: Verify the token

Have Claude run the verify. This is a **token-scoped REST call** - it asks Cloudflare to confirm the token can see your account and Pages projects. It never runs `wrangler login` and never touches anyone else's account.

```bash
python3 scripts/cloudflare_pages.py verify
```

[VERIFY] The verify returns your account and reports the token is valid. If it fails:
- 401/403 → the token is mistyped or missing the **Cloudflare Pages: Edit** permission. Re-create it with exactly that permission.
- "account not found" → the `CLOUDFLARE_ACCOUNT_ID` is wrong. Re-copy from Workers & Pages → right sidebar.

"Token's live and pointed at your account. Let's put the app up."

---

### Step 6: Deploy the Cool Hollow Coaching app

Have Claude deploy the live app:

```bash
python3 scripts/cloudflare_pages.py deploy apps/cool-hollow cool-hollow
```

This publishes the Cool Hollow Coaching app to `https://cool-hollow.pages.dev`.

[VERIFY] The deploy reports success and prints the live URL. Open it in a browser - the Cool Hollow Coaching app should load.

---

## TEST

### Open your live link

"Open **https://cool-hollow.pages.dev** in your browser. That's your app, live on the internet, on your own account. Send that link to anyone."

### Prove a redeploy

Make a tiny visible change to the app (Claude can adjust a heading), then redeploy with the same command.

[VERIFY] The change appears at the live link within a few seconds of redeploying. This proves the full edit-and-publish loop works end to end.

"That's the whole point of this - you change the app, Claude redeploys, the live link updates. No fiddly hosting, no monthly bill."

---

## WHAT'S NEXT

Cloudflare Pages is connected and the Cool Hollow Coaching app is live. From here:

1. **Edit the app in plain English** - ask Claude to change copy, colours or sections (`frontend-design` keeps it on-brand), then say "put it live" and it redeploys.
2. **A custom domain later** - when you're ready, Cloudflare can point your own domain (like coolhollow.com) at this app with free SSL. Just ask.
3. **Roll back if something looks wrong** - every deploy is kept, so Claude can roll back to the previous version instantly.

**Stuck?** Run `/doctor` for a one-line status of every tool, and send Matthew the output if a step won't budge.
