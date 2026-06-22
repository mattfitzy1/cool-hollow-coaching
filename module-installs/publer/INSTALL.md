---
# This frontmatter is read by scripts/build_registry.py so Publer appears in
# /setup and /doctor alongside the skill-declared tools. Keep these fields in
# step with the matching block in .claude/skills/schedule/SKILL.md.
requires:
  - tool: publer
    type: key
    requires_bin: []
    requires_runtime: []
    account: "Publer"
    bundle: content
    plan: "Free if your plan's API and Instagram publishing are free; otherwise paid"
    signup: "https://publer.com → connect your Instagram → Settings → Access → API key"
    where: "Settings → Access → API key, pasted into PUBLER_API_KEY in .env"
    env: PUBLER_API_KEY
    verify: "Publer API: list workspaces/accounts"
    optional: true
---

# Publer - module installer

> Connects your Instagram so Claude can draft posts straight into Publer for you to review and publish.

<!-- MODULE METADATA
module: publer
version: v1
status: RELEASED
requires: []
phase: 2
category: Content & Social
complexity: low
api_keys: 1
setup_time: 10-15 minutes
-->

---

## FOR CLAUDE

You are connecting **Publer** so the owner can plan Instagram posts and have Claude push them into Publer as **drafts they review and publish themselves**.

**Your role:** A calm, plain-English guide. The owner is non-technical. This is the first paid-or-free social tool they touch, so make it feel small and safe.

**Behaviour:**
- One step at a time. Never paste a wall of instructions.
- The owner owns the key. You guide the click path; they paste the key into `.env`. Never ask them to paste the key into the chat, and never echo a key back.
- The load-bearing promise: `publer_post.py` defaults to `--draft`. Nothing ever posts to Instagram on its own. Say this out loud so the owner trusts it.
- If Publer's free tier on their plan cannot issue an API key or cannot publish to Instagram, that is fine - fall back to "saved to your posts folder, open the Instagram app and post it." Do not dead-end.
- No em-dashes in anything the owner reads. US English. Encourage them ("That's the social side connected - now Claude can do the heavy lifting and you just press publish.").

**Self-detect:** Any Publer-using skill (`schedule`, `publer_post.py`) calls `ensure_ready("publer")` before it runs. If Publer is not connected it routes into this walkthrough rather than erroring. You do not need to run that yourself here - this module IS the walkthrough.

**Escalation line to end on if the owner gets stuck:** "Stuck? Send your builder the output of `/doctor` and they'll point you to the exact step."

---

## OVERVIEW

Read this to the owner before starting:

We're connecting **Publer** - the tool that lets Claude prepare your Instagram posts for you. You write or develop a post, Claude formats it (caption, hashtags, the carousel idea) and drops it into Publer as a **draft**. You open Publer, have a look, and publish it yourself. Nothing ever goes out without you.

Here's what we'll do:

1. **Make a Publer account** (free to start) and connect your Instagram inside it
2. **Copy one API key** from Publer's settings into your `.env` file
3. **Verify** it works - Claude will check the key talks to your account
4. **Confirm** your Instagram shows up so drafts know where to land

**Setup time:** 10-15 minutes
**Running cost:** Free on Publer's starter plan if that plan lets you use the API and publish to Instagram. Some plans gate the API or Instagram behind a paid tier (around 12 US dollars a month). We'll find out during setup - and if your free plan can't do it, we'll just save posts to your folder so you can publish them by hand instead. Either way, you're never blocked.

---

## PREREQUISITES

Publer needs no software on your Mac - it's a website plus one key. The only check is that your workspace has the place for the key.

```bash
ls .env.example
grep -q "PUBLER_API_KEY" .env.example && echo "PUBLER slot present"
```

You should see `PUBLER slot present`. If `.env` doesn't exist yet, create it from the template:

```bash
test -f .env || cp .env.example .env
```

[VERIFY] `.env` exists and contains a `PUBLER_API_KEY=` line (it'll be empty for now - that's what we're about to fill).

---

## COLLECT THE KEY

We collect **one** thing here: your Publer API key. We do it last, after the account and Instagram are connected, so the key is actually useful the moment you paste it.

### Step 1: Create your Publer account

Open **https://publer.com** and sign up (the starter plan is free). Use the email you want tied to your brand.

"Tell me when you're signed in and looking at your Publer dashboard."

[VERIFY] The owner is logged into Publer and can see the dashboard.

---

### Step 2: Connect your Instagram inside Publer

In Publer, go to **Accounts** (or "Connect a social account") and connect your **brand Instagram**. Follow Publer's prompts to log into Instagram and approve the connection.

"This is the step that tells Publer which account your drafts belong to. Connect your brand Instagram, then tell me when it shows up in your accounts list."

[VERIFY] The brand Instagram appears in Publer's connected accounts.

If Instagram won't connect on a free plan, note it - we'll use the folder-and-publish-by-hand fallback at the end instead. Don't treat this as a failure.

---

### Step 3: Copy your API key

In Publer go to **Settings → Access → API key**. Copy the key shown there.

"Copy that key - don't paste it to me. We'll put it straight into your secrets file in the next step."

If there's **no API key** option on your plan, that means the API sits behind a paid tier. Tell me and we'll either upgrade (about 12 US dollars a month) or use the by-hand fallback. Your choice.

[VERIFY] The owner has the API key on their clipboard (or has confirmed their plan has no API option).

---

### Step 4: Paste the key into .env

Open `.env` in your workspace, find the line:

```
PUBLER_API_KEY=
```

Paste your key right after the `=` (no spaces, no quotes), so it reads `PUBLER_API_KEY=pblr_...`. Save the file.

"Your key lives only in this file on your Mac, never in our chat and never in anything that gets shared. Save it and tell me 'done'."

[VERIFY] On "done", confirm the slot is now non-empty:

```bash
grep -E "^PUBLER_API_KEY=." .env >/dev/null && echo "key present" || echo "still empty"
```

You should see `key present`.

---

## INSTALL

### Step 5: Verify the key talks to your account

Have Claude run the verify. This calls Publer's API to list your workspaces and accounts - it proves the key works without posting anything.

The Publer-using skills self-detect via `ensure_ready("publer")`, which runs this same check. You can also confirm by listing accounts directly through `publer_post.py`'s account-discovery path.

[VERIFY] The verify returns your workspace and at least one connected account. If it 401s, the key was mistyped - re-copy from Settings → Access and paste again.

"That worked - your key is live."

---

### Step 6: Save your account IDs (no typing)

Once the key verifies, Claude auto-discovers your **workspace ID** and **Instagram account ID** and writes them to `data/publer_accounts.json`. You never copy an ID by hand - that's where mistakes happen, so the setup does it for you.

```bash
ls data/publer_accounts.json && echo "accounts saved"
```

[VERIFY] `data/publer_accounts.json` exists and lists your brand Instagram. This is what tells a draft which account to land in.

---

### Step 7: The draft guarantee

Confirm to the owner, in their own words, the one rule that makes this safe:

> Every post Claude prepares goes into Publer as a **draft**. You review it in Publer and publish it yourself. `publer_post.py` defaults to `--draft`, so nothing posts to Instagram automatically - ever.

[VERIFY] The owner has heard and understood the draft-only behavior. This is the promise the whole content side rests on.

---

## TEST

### Draft a real post

"Let's prove it. Ask me to schedule one of your developed posts for a day this week."

Claude runs the `schedule` flow (or `publer_post.py --draft`), which prepares the caption, hashtags and carousel note and pushes it to Publer **as a draft**.

Then: "Open Publer and look in your drafts - your post should be sitting there, ready. Have a read, tweak anything you like, and publish it when you're happy."

[VERIFY] The post appears as a draft in Publer, tied to the brand Instagram, and nothing has been published.

### Fallback test (only if Publer's API/publish is paid-gated on the owner's plan)

If the owner chose not to pay, prove the fallback instead: "I've saved this post to `outputs/social/`. Open the Instagram app, paste the caption, add the image, and post it from there."

[VERIFY] The post file is in the posts folder with caption and assets ready to copy.

---

## WHAT'S NEXT

Publer is connected. From here:

1. **Build a week of posts** - use `/develop` to turn ideas into finished posts, then `/schedule` to set the days. They all land as Publer drafts for you to publish.
2. **Keep three a week** - that's the rhythm the content strategy is built around. Claude does the drafting; you do the final press of publish.
3. **If you ever change plans** - if you later pay for Publer's API, nothing changes here. Your key already covers it. If you downgrade and the API stops working, Claude falls back to saving posts to your folder automatically.

**Stuck?** Run `/doctor` for a one-line status of every tool, and send your builder the output if a step won't budge.
