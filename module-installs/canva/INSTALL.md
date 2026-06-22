---
# Read by scripts/build_registry.py so Canva shows up in /setup and /doctor.
# Canva is OAuth (per-user browser login) with NO key - type: auth, no env
# slot. "Connected" = the Canva MCP responds when Claude calls it. There is no
# CLI status binary, so the verify is descriptive and the skill confirms at
# call time.
requires:
  - tool: canva
    type: auth
    requires_bin: []
    requires_runtime: []
    account: "Canva"
    bundle: creative
    plan: "Free (Canva free account; Pro optional, not required here)"
    signup: "https://www.canva.com → sign up / log in, then connect Canva inside Claude when prompted"
    where: "Browser login (OAuth). No key to paste, nothing goes in .env."
    spend: "Free. A Canva account is all you need."
    verify: "Canva MCP responds (Claude calls a Canva tool and it returns)"
    optional: true
---

# Canva - Cool Hollow Coaching module installer

> Connects your Canva so Claude can create and edit branded designs for you. A login, not a key.

<!-- MODULE METADATA
module: canva
version: v1
status: RELEASED
requires: []
phase: 2
category: Creative Studio
complexity: low
api_keys: 0
setup_time: 5-10 minutes
-->

---

## FOR CLAUDE

You are connecting **Canva** so Matt can have Claude create and edit branded Cool Hollow Coaching designs. Canva is a **login (OAuth) tool** - there is **no API key** and nothing goes in `.env`. He logs into his own Canva in the browser, once, and approves the connection.

**Your role:** A light-touch guide. This is the easiest setup of the bunch - no software, no key. Keep it short and reassuring.

**Behaviour:**
- **No key.** Do not ask for or expect a key. Do not write anything to `.env`. If you catch yourself looking for `CANVA_API_KEY`, stop - there isn't one.
- "Connected" means: he's logged into Canva, the connection is approved, and the Canva MCP responds when Claude calls it. There is no CLI status check; you confirm by actually doing a small Canva action.
- It's his own Canva account, so every design lives in his library, hers to keep.
- No em-dashes. US English. Keep it breezy ("This one's the easy one - just a login, no key to fuss with.").

**Self-detect:** Creative skills that use Canva call `ensure_ready("canva")`. Because Canva is a login tool with no runnable status binary, the readiness check defers to the skill's own Canva call - if Canva isn't connected, the MCP call fails and routes here. This module is the human-readable version.

**Escalation line:** "Stuck? Send Matthew the output of `/doctor` and he'll point you to the exact step."

---

## OVERVIEW

Read this to Matt before starting:

We're connecting **Canva** - so Claude can build and tweak branded designs for you (post layouts, simple graphics, tidy-ups) and they all land in your own Canva library. This is the simplest setup you'll do: there's no key to copy, you just log into your Canva once and say yes to the connection.

Here's what we'll do:

1. **Make sure you have a Canva account** (free is fine)
2. **Connect Canva** when Claude prompts you - a browser login, one approval
3. **Test it** by having Claude make a small design

**Setup time:** 5-10 minutes
**Running cost:** Free. A free Canva account covers what we need here. Canva Pro is optional and not required.

---

## PREREQUISITES

There is no software and no key for Canva. The only prerequisite is a Canva account.

```bash
echo "Canva needs no software and no .env key - just your Canva login."
```

[VERIFY] Matt confirms he has (or is happy to make) a free Canva account. Nothing to install, nothing to paste.

---

## CONNECT (login, not a key)

### Step 1: Make sure you're logged into Canva

Open **https://www.canva.com** in your browser and sign in (or sign up free). Use the account you want your Cool Hollow Coaching designs to live in.

"Tell me when you're logged into Canva in your browser."

[VERIFY] He's logged into his Canva account.

---

### Step 2: Connect Canva to Claude

When Claude first needs Canva, it will prompt you to **connect Canva**. This opens a Canva page in your browser asking you to **allow** the connection. Click **Allow** (or **Authorise**).

"This is the only approval step. It links your Canva to Claude so designs can be made for you and saved to your library. Click allow, then tell me 'done'."

[VERIFY] The browser shows the connection approved and returns you to Claude. There is no key to paste - the approval is the whole step.

If the prompt doesn't appear, ask Claude to do any small Canva action (like "list my Canva folders") - that triggers the connect prompt.

---

## INSTALL

### Step 3: Confirm Canva responds

Have Claude run a tiny read-only Canva action - for example, listing your Canva folders or brand kits. If it returns, the connection is live.

[VERIFY] Claude can read something from your Canva (folders, designs, or brand kit) without error. That's "connected" for a login tool - there's no status command, the proof is that it works.

"Canva's connected - that was the easy one."

---

## TEST

### Make a small branded design

"Let's prove it. Ask me to create a simple Cool Hollow Coaching design - a plain post background in your cream colour with a short line of text."

Claude uses Canva to generate the design.

[VERIFY] A design is created and appears in your Canva library. Open Canva in the browser and confirm it's there, yours to edit.

"Anything Claude makes lands in your own Canva, so you can always open it up and adjust it yourself."

---

## WHAT'S NEXT

Canva is connected. From here:

1. **Set up a Canva brand kit** - once Cool Hollow Coaching's colours and fonts are locked (see `context/brand.md`), add them to your Canva brand kit so every design starts on-brand.
2. **Ask for designs in plain English** - "make me a quote graphic", "a simple program one-pager" - and they land in your library to refine.
3. **Pair it with nano-banana** - use the free image tool for photo-style visuals, Canva for laid-out graphics with text.

**Stuck?** Run `/doctor` for a one-line status of every tool, and send your builder the output if a step won't budge.
