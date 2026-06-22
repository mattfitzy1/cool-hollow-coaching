---
# Read by scripts/build_registry.py so Higgsfield shows up in /setup and
# /doctor. Login tool (no key): configured = `higgsfield account status`
# passes. Ships DORMANT - HIGGSFIELD_ENABLED=false in .env until the owner opts
# in, so they are never pushed into a paid bill at launch. optional: true.
requires:
  - tool: higgsfield
    type: auth
    auth: "higgsfield account status"
    requires_bin: [higgsfield]
    requires_runtime: [ffmpeg]
    account: "Higgsfield"
    bundle: creative
    plan: "Paid, about $59/mo (image and video credits)"
    signup: "https://higgsfield.ai → Sign up → pick a plan → run `higgsfield auth login`"
    where: "Account page after you pick a plan. You log in; there is no key to paste."
    spend: "Paid credits. Cheap-first defaults on. Hard cap: HF_MONTHLY_CAP in .env (default 30)."
    verify: "higgsfield account status"
    optional: true
---

# Higgsfield - module installer (ships dormant until you turn it on)

> The paid AI image and video engine. Free option (nano-banana) already covers everyday work - only set this up when you want AI video or richer visuals.

<!-- MODULE METADATA
module: higgsfield
version: v1
status: RELEASED (DORMANT BY DEFAULT)
requires: []
phase: 2
category: Creative Studio
complexity: high
api_keys: 0
setup_time: 15-25 minutes
cost: PAID ~$59/month
default_state: HIGGSFIELD_ENABLED=false
-->

---

## FOR CLAUDE

You are connecting **Higgsfield** - the paid AI image and video engine. It ships **dormant** (`HIGGSFIELD_ENABLED=false` in `.env`) on purpose, so the owner is **never** pushed into a paid bill at launch. Only run this module when they have explicitly said they want AI video or richer images and are ready to pay.

**Your role:** An honest guide who leads with the cost and the free alternative. The owner is non-technical and cost-anxious, so the first thing they hear is "this one's about $59 a month, and your free tool already covers most things." Make turning it on a clear, deliberate choice - never the default.

**Behaviour:**
- **Lead with cost, every time.** Open with: "This is the paid engine, about $59 a month for credits. Your free option, nano-banana, is already connected and covers most of what you need. Set this up only when you specifically want AI video or richer images. Want to do it now, or skip again?"
- This is a **login tool** (`type: auth`) - there is **no API key**. The owner picks a plan on higgsfield.ai and runs `higgsfield auth login`. Nothing goes in `.env` except the on/off flag and the spend cap.
- **Software before login.** The higgsfield CLI binary (and ffmpeg, for video stitching) must be installed first. Do that, then log in.
- **The dormant flag is load-bearing.** Until the owner finishes this and you flip `HIGGSFIELD_ENABLED=true`, the creative skills will not spend a Higgsfield credit. Flipping it is a deliberate, final step the owner confirms.
- **Credit discipline is automatic and capped.** Stills and `--draft` 480p first; 1080p final only on the owner's explicit "yes, render it"; never auto-regenerate finished media (recover via the job's `result_url`); default `--count` low (1-3); report the credit tally at the end of every run. `HF_MONTHLY_CAP` (default 30) is a **hard cap** - the wrapper refuses a call that would exceed it and tells the owner to raise the cap explicitly.
- If the owner was skipped earlier in `/setup`, open by tying back to that ("You skipped Higgsfield earlier, that's fine; you only need it now because you've asked for a video.").
- No em-dashes. US English.

**Self-detect:** Creative skills (`creative`, `higgsfield-product-photoshoot`, `higgsfield-generate`, `higgsfield-soul-id`, `marketing-video`) call `ensure_ready("higgsfield")`. With the binary missing or `higgsfield account status` failing, they route into this walkthrough rather than erroring. This module is the human-readable version of that flow.

**Escalation line:** "Stuck? Send your builder the output of `/doctor` and they'll point you to the exact step."

---

## OVERVIEW

Read this to the owner before starting - **and lead with the cost**:

Before anything: **this is the paid one.** Higgsfield is the AI engine that makes video and richer images, and it costs **about $59 a month** for credits. Your free tool, **nano-banana**, is already connected and handles most of your everyday images at no cost. So only set this up when you specifically want AI video (like a short brand film) or images nano-banana can't do.

If you're ready, here's what we'll do:

1. **Install the Higgsfield software** on your Mac (Claude does this for you), plus ffmpeg for video
2. **Pick a Higgsfield plan** and log in (a login, not a key)
3. **Set your spend cap** so you can never be surprised by a bill
4. **Turn it on** - flip the dormant switch deliberately, only when you're ready

**Setup time:** 15-25 minutes
**Running cost:** PAID, about **$59 a month** for credits. There is a hard monthly cap in your settings (starts at 30 credits) so spending can't run away. You can change it whenever you like.

"There's no rush on this one. If you're not sure you need video yet, skip it - nano-banana has you covered for free, and we can switch this on any time."

---

## PREREQUISITES

Higgsfield runs as a command-line tool on your Mac, and it uses **ffmpeg** to stitch video. Both must be installed before you log in. Claude installs them through **Homebrew**. Software before login - logging in to an engine that isn't installed does nothing.

### Check what's there

```bash
command -v brew       && echo "brew ok"       || echo "brew MISSING"
command -v ffmpeg     && echo "ffmpeg ok"     || echo "ffmpeg MISSING"
command -v higgsfield && echo "higgsfield ok" || echo "higgsfield MISSING"
```

### Install anything missing, in this order

1. **Homebrew** (only if missing):
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
2. **ffmpeg** via Homebrew:
   ```bash
   brew install ffmpeg
   ```
3. **The Higgsfield CLI** - install per its official docs, then fetch its global skills folder into `~/.claude/higgsfield-skills/`. The `/setup` wizard does this fetch for you when you choose to turn Higgsfield on.

[VERIFY] All three checks now say `ok`:

```bash
command -v brew && command -v ffmpeg && command -v higgsfield && echo "all software ready"
ls ~/.claude/higgsfield-skills/ >/dev/null 2>&1 && echo "skills folder present" || echo "skills folder MISSING (run /setup creative to fetch it)"
```

---

## CONNECT (login, paid - no key)

### Step 1: Pick a plan and sign up

Open **https://higgsfield.ai**, sign up, and **pick a plan** (this is the ~$59/month paid step). Credits come with the plan.

"Just to say it again: this is the paid step, about $59 a month. Happy to go ahead?"

[VERIFY] The owner has chosen a plan and confirms they're ready to proceed with the paid setup.

---

### Step 2: Log in from your Mac

Run the interactive login. This is a **login, not a key** - nothing to copy or paste into `.env`.

```bash
higgsfield auth login
```

Follow the prompts. When it finishes, you're logged in.

[VERIFY] Confirm the login took:

```bash
higgsfield account status
```

It should report your account as logged in. If it doesn't, run `higgsfield auth login` again.

"You're logged in. Two safety steps left before it can spend anything."

---

### Step 3: Set your spend cap

Open `.env` and check the cap:

```
HF_MONTHLY_CAP=30
```

This is a **hard monthly cap** on Higgsfield credits - Claude refuses any generation that would push you over it, and tells you if you want more. 30 is a sensible starting point. Raise or lower it whenever you like.

"This is your safety net. Even if something asks for a big render, it can't go past this number without you saying so."

[VERIFY] `HF_MONTHLY_CAP` is set to a number the owner is comfortable with.

---

## INSTALL

### Step 4: Turn Higgsfield on (the deliberate switch)

Higgsfield ships **off**. In `.env` you'll see:

```
HIGGSFIELD_ENABLED=false
```

Only when you're fully ready, change it to:

```
HIGGSFIELD_ENABLED=true
```

Save. This is the deliberate "I'm ready to use the paid engine" switch. Until it's `true`, the creative tools will not spend a single Higgsfield credit.

"This is the on switch. Flip it only when you actually want to start making video or richer images. You can flip it back to `false` any time to pause."

[VERIFY] Confirm the flag:

```bash
grep -E "^HIGGSFIELD_ENABLED=true" .env >/dev/null && echo "Higgsfield ON" || echo "still dormant (false)"
```

If the owner is still deciding, leave it `false` - the module is done either way, and `/doctor` will simply show Higgsfield amber "needs setup / off" with no error.

---

## TEST

> Only run this once `HIGGSFIELD_ENABLED=true`. If it's still `false`, stop here - Higgsfield is correctly installed-but-dormant and that's a valid finished state.

### A cheap still first (credit discipline in action)

"Let's prove it with the cheapest possible call - a single still, draft quality. We always explore cheap before spending real credits."

Have Claude generate **one** still (`--count 1`, draft) in the brand look (see `context/brand.md`).

[VERIFY] One still is produced. Claude reports the credit tally at the end of the run, and the spend is recorded against `HF_MONTHLY_CAP`.

### Confirm the cap bites

Ask Claude what would happen if a render exceeded the cap.

[VERIFY] Claude confirms it would **refuse** the call and ask you to raise `HF_MONTHLY_CAP` explicitly first - the cap is a hard stop, not a reminder.

"That's the paid engine connected, and capped. Remember: nano-banana stays your free default for everyday images; reach for Higgsfield when you want video or something it can't do."

---

## WHAT'S NEXT

Higgsfield is connected (or correctly left dormant). From here:

1. **Make a short brand film** - `/marketing-video` builds a cinematic brand film. It's gated behind your explicit "yes, render it" and your spend cap, so video credits only burn on purpose.
2. **Richer product and lifestyle stills** - `higgsfield-product-photoshoot` for shots beyond what nano-banana does. Still cheap-first: stills before video, drafts before finals.
3. **Pause it any time** - set `HIGGSFIELD_ENABLED=false` to stop all Higgsfield spend without uninstalling anything. Your free tools keep working.
4. **Watch the tally** - Claude reports credits used at the end of every run, and `HF_MONTHLY_CAP` is the hard ceiling.

**Stuck?** Run `/doctor` for a one-line status of every tool, and send your builder the output if a step won't budge.
