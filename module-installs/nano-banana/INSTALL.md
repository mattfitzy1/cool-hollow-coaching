---
# Read by scripts/build_registry.py so nano-banana shows up in /setup and
# /doctor. MCP tool: configured = .env has the Gemini key AND the MCP reports
# connected via get_configuration_status.
requires:
  - tool: nano-banana
    type: mcp
    requires_bin: [npx]
    requires_runtime: [node]
    account: "Google Gemini (AI Studio)"
    bundle: creative
    plan: "Free tier"
    signup: "https://aistudio.google.com/apikey → Create API key"
    where: "API key into GEMINI_API_KEY in .env (the MCP reads it via .mcp.json)"
    env: GEMINI_API_KEY
    spend: "Free tier covers normal use. Your cheapest creative tool - start here."
    verify: "nano-banana get_configuration_status returns connected"
    optional: false
---

# nano-banana - Cool Hollow Coaching module installer

> Your free, on-brand image generator and editor, powered by Google Gemini.

<!-- MODULE METADATA
module: nano-banana
version: v1
status: RELEASED
requires: []
phase: 2
category: Creative Studio
complexity: medium
api_keys: 1
setup_time: 10-15 minutes
-->

---

## FOR CLAUDE

You are connecting **nano-banana** - an MCP tool that generates and edits images using Matt's own **Google Gemini** key, on the **free tier**. This is his cheapest creative tool and the default for quick on-brand visuals, so it should ship connected early.

**Your role:** A patient guide. Matt is non-technical and this is an MCP tool, which is slightly more abstract than a website. Keep it concrete: "it's a free image tool that uses a Google key."

**Behaviour:**
- This is an **MCP tool** (`type: mcp`). "Connected" means two things are true: the Gemini key is in `.env`, AND the nano-banana MCP reports connected via its own `get_configuration_status`. Check both.
- The key lives in `.env` as `GEMINI_API_KEY` and reaches the MCP through `.mcp.json` (which reads `${GEMINI_API_KEY}`). The key is never written literally into `.mcp.json`, and `.mcp.json` is gitignored. This is deliberate - it keeps his key out of any tracked file.
- He owns the key. You guide the click path; he pastes into `.env`. Never echo a key, never ask for it in chat.
- Cheap-first is his rule: nano-banana (free) is the default for quick edits before any paid engine. Reinforce that.
- No em-dashes. US English. Encourage ("This one's free and it's the one you'll reach for most - nice place to start.").

**Self-detect:** Creative skills call `ensure_ready("nano-banana")`. The Python side checks the `GEMINI_API_KEY` slot; the skill itself confirms the MCP reports connected via `get_configuration_status`. If either is missing it routes here.

**Escalation line:** "Stuck? Send Matthew the output of `/doctor` and he'll point you to the exact step."

---

## OVERVIEW

Read this to Matt before starting:

We're connecting **nano-banana** - your free image tool. It makes and edits pictures in the Cool Hollow Coaching look, and because it runs on Google's free tier, it costs nothing for normal use. This is the one you'll reach for most: quick on-brand visuals, tidy-ups, variations, all without spending a credit.

Here's what we'll do:

1. **Check you have Node** (the small bit of software this runs on) - Claude installs it if needed
2. **Get a free Google Gemini API key** from Google AI Studio
3. **Put the key in your `.env`** so the tool can read it safely
4. **Verify** the image tool reports connected

**Setup time:** 10-15 minutes
**Running cost:** Free. Google's Gemini free tier covers everyday image generation and editing. If you ever push huge volume you might hit a free limit, but for Cool Hollow Coaching content you'll stay free.

---

## PREREQUISITES

nano-banana runs through `npx`, which comes with **Node**. Node must be on your Mac first. Claude installs it through **Homebrew** if it's missing. Software before key - a key with nothing to run it does nothing.

### Check what's there

```bash
command -v brew && echo "brew ok" || echo "brew MISSING"
command -v node && echo "node ok" || echo "node MISSING"
command -v npx  && echo "npx ok"  || echo "npx MISSING"
```

### Install anything missing

1. **Homebrew** (only if missing):
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
2. **Node** (brings `npx` with it):
   ```bash
   brew install node
   ```

[VERIFY] All three checks now say `ok`:

```bash
command -v brew && command -v node && command -v npx && echo "all software ready"
```

---

## COLLECT THE KEY

One thing goes in: a free **Gemini API key**.

### Step 1: Create a free Gemini API key

Open **https://aistudio.google.com/apikey** and sign in with a Google account. Click **Create API key**. Copy the key it shows you.

"Copy the key - don't paste it to me. We'll put it into your secrets file next. This is the free Google key; you won't be asked for a card."

[VERIFY] He has the key copied.

---

### Step 2: Paste the key into .env

```bash
test -f .env || cp .env.example .env
```

Open `.env`, find:

```
GEMINI_API_KEY=
```

Paste the key right after the `=` (no spaces, no quotes). Save.

"Tell me 'done' when it's saved. Your key stays in this one file on your Mac, never in our chat and never in anything shared."

[VERIFY] On "done":

```bash
grep -E "^GEMINI_API_KEY=." .env >/dev/null && echo "key present" || echo "still empty"
```

---

### Step 3: Wire up .mcp.json (key by reference, never literal)

The image tool reads your key through `.mcp.json`. We copy the template, which points at `${GEMINI_API_KEY}` - it references your `.env` key rather than copying it in, so your actual key never lands in a tracked file.

```bash
test -f .mcp.json || cp .mcp.json.example .mcp.json
```

[VERIFY] `.mcp.json` exists and contains `${GEMINI_API_KEY}` (a placeholder), not a literal `AIza...` key:

```bash
grep -q '${GEMINI_API_KEY}' .mcp.json && echo "references the env key (good)"
grep -q 'AIza' .mcp.json && echo "WARNING: literal key in .mcp.json - remove it" || echo "no literal key (good)"
```

`.mcp.json` is gitignored, so even this referenced setup never gets shared.

---

## INSTALL

### Step 4: Restart so Claude loads the MCP

MCP tools load when Claude Code starts. After `.env` and `.mcp.json` are set, **restart Claude Code** (close and reopen) so it picks up nano-banana.

"Close this window and open Claude Code again - that's how it notices the new image tool. Then come back here."

[VERIFY] After restart, nano-banana is available as a tool.

---

### Step 5: Verify it reports connected

Have Claude call nano-banana's **`get_configuration_status`**. This is the MCP's own self-check - it confirms the key reached the tool and it's ready.

[VERIFY] `get_configuration_status` returns **connected**. If it doesn't:
- key not found → re-check the `GEMINI_API_KEY` line in `.env` (no quotes, no trailing space)
- still not connected after a correct key → confirm Claude was fully restarted after the edit

"Connected - and it's free. This is your everyday image tool now."

---

## TEST

### Make a Cool Hollow Coaching image

"Let's try it. Ask me to make an on-brand image in the Cool Hollow Coaching look (see `context/brand.md`) - clean, professional, calm."

Claude calls nano-banana to generate the image.

[VERIFY] An on-brand image is produced and saved. No credits were spent (this is the free tier).

### Edit it

"Now ask me to tweak it - warmer, or a different crop. nano-banana edits images too."

[VERIFY] The edit returns a revised image, proving the generate-and-edit loop works.

"That's your free creative engine sorted. Reach for this first, before any paid tool."

---

## WHAT'S NEXT

nano-banana is connected. From here:

1. **Use it as your default** - for quick on-brand stills and edits, nano-banana is free and fast. Start here before anything paid.
2. **Build a brand pack** - `/brand-pack` sets up the Cool Hollow Coaching creative foundation so every image stays on-brand.
3. **Paid engines come later, only when you want them** - Higgsfield (for AI video and richer images) is a separate, paid setup you can do whenever you're ready. nano-banana covers the everyday for free.

**Stuck?** Run `/doctor` for a one-line status of every tool, and send Matthew the output if a step won't budge.
