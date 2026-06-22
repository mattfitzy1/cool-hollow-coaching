---
name: setup
description: "Guided, one-at-a-time wizard that connects your tools to your AIOS. Walks through them cheapest-and-most-useful first (Content, then Creative, then App), installs any software you're missing, explains what each tool is and what it costs, gives you the exact sign-up steps, watches you paste the key into your secrets file (never the chat), checks it's working, and lets you skip anything for later. Trigger phrases: 'setup', 'set up my tools', 'connect my tools', 'run setup', 'finish setting up', 'set up content', 'set up creative', 'set up app'."
---

# /setup - connect your tools, one calm step at a time

> Nothing here is hard, and nothing here can break. We go one tool at a time,
> cheapest and most useful first, and you can stop or skip whenever you like.

## What this is

`/setup` connects the outside tools your AIOS uses (for posting, images, and
putting your app live) to your own accounts. It is the friendly front door so
you never hit a confusing "not set up" message on your own. For each tool it:

1. installs any software it needs (you just paste one command if asked),
2. explains in plain English what the tool is and what it costs,
3. gives you the exact link and clicks to sign up,
4. watches you paste your key into your secrets file (never into the chat),
5. checks it's actually working, celebrates, and moves on.

You can run the whole thing, or just one toolkit: `/setup content`,
`/setup creative`, `/setup app`.

## The order (cheapest and most useful first)

Always walk the toolkits in this order, so the free, high-value stuff lands
first and the owner never faces a wall of bills:

1. **Content** - posting your Instagram (Publer). Free on most plans. Highest
   day-one value.
2. **Creative** - making images and video. Start with **nano-banana** (free,
   Google Gemini). **Higgsfield** is the paid video engine (about $59/mo);
   flag it as "set up later, only when you want video", and let the owner skip it.
3. **App** - putting your app live (Cloudflare Pages). Free.
   Needs a couple of small bits of software installed first.

There is deliberately **no email or calendar step here.** Those are a later
capability set up with your builder, because they need a connection that can't
be done self-serve. Never ask the owner to paste an email or calendar key.

## How to run it (Claude's procedure)

Read the tool list from `data/skill_registry.json` (built by
`build_registry.py`, never hand-edited). Group the tools by `bundle` and walk
them in the order above. For **each** tool, follow this loop:

### Step A - say where we are
One warm line: "Next up is Publer - this is what posts your Instagram for you."
If it's a paid tool, say the cost up front and that you can skip it:
"Higgsfield is the AI video engine. It's about $59 a month, so only set it up
when you actually want video. Your free image tool, nano-banana, is already
sorted. Want to do this now, or skip it for later?"

### Step B - install any software first (Layer 0)
Some tools need a small piece of software on the owner's Mac before the key matters.
Read `requires_bin` and `requires_runtime` for the tool from the registry and
check each with `command -v <name>`. If anything is missing, install it for
them, explaining as you go:

- If `brew` (Homebrew) is missing and is needed, give them the **one official
  paste-command** from https://brew.sh and wait for it to finish.
- Node: `brew install node` (do NOT use nvm - it's fiddly for a non-technical
  user). Needed by nano-banana, wrangler, and new-app.
- ffmpeg: `brew install ffmpeg` (needed by the video tools).
- wrangler (Cloudflare deploy): `npm install -g wrangler`.
- The Higgsfield CLI: its documented install, plus seeding the global
  `~/.claude/higgsfield-skills/` folder if the setup needs it.

After each install, confirm it's there (`command -v <name>`) before moving on.
Never collect a key for a tool whose software isn't installed yet - that's a
dead tool, which is exactly what we're avoiding.

### Step C - explain + sign up + paste the key
Use the registry's own fields so the wording is always accurate:
- `plan` - the cost (e.g. "Free tier", "Paid ~$59/mo").
- `signup` - the exact link and click path. Read it to the owner step by step.
- `where` - where the key goes.

Then, for the credential, by tool `type`:

- **Key tools** (Publer, nano-banana/Gemini, Cloudflare): walk the owner to the key,
  then ask them to **open `.env` and paste it into the named slot** (e.g.
  `PUBLER_API_KEY=`, `GEMINI_API_KEY=`, `CLOUDFLARE_API_TOKEN=` plus
  `CLOUDFLARE_ACCOUNT_ID=`). Tell them to save the file and say "done". **You
  never type, read aloud, or echo the key.** Their hands, their file, their account.
  If `.env` doesn't exist yet, have them copy `.env.example` to `.env` first.
- **Login tools** (Higgsfield): there's no key. Run the interactive login it
  needs (`higgsfield auth login`) and let them complete it.
- **MCP tools** (nano-banana): the key goes in `.env` as `GEMINI_API_KEY`; the
  connection is read from there.

### Step D - verify live, then celebrate
Run `python3 scripts/doctor.py` (or the tool's own verify) and check that the
tool now shows green. If it does, celebrate warmly and specifically:
"Publer's connected - that's your posting sorted." If it doesn't, reassure
the owner, show the one thing that's off (usually a mistyped key), and let them try
again. Never dump a raw error.

### Step E - skip is always allowed
The owner can skip any tool or any whole toolkit. Skipping is fine and fully
recoverable: tell them "no problem, you can connect this any time with
`/setup <toolkit>`, or it'll offer itself the moment you first need it."
Record nothing scary; just move on.

## Rules for Claude (important)

1. **One tool at a time. Never a wall of steps.** Finish one, celebrate, then
   the next.
2. **The key is always theirs.** You guide the clicks; the owner pastes into `.env`.
   Never put a key in the chat, never read one back, never write it for them.
   This keeps the secrets-in-.env / no-keys-in-chat rule intact even when
   your builder is helping over the owner's shoulder.
3. **Software before keys.** A valid key with no software installed is still a
   dead tool. Always do Layer 0 (Step B) first.
4. **Cost up front for paid tools.** Higgsfield's ~$59/mo is said before the owner
   touches it, and skipping it is the easy, encouraged default at launch. It
   ships dormant (`HIGGSFIELD_ENABLED=false`); leave that as-is unless the owner
   explicitly chooses to pay and turn it on.
5. **Tie back to skips.** If the owner skipped a tool earlier and now needs it, open
   by acknowledging that: "You skipped Higgsfield earlier - that's fine. You
   only need it now because you asked for a video. Connect it (about $59/mo)
   or skip again?"
6. **No email/calendar here.** If the owner asks, explain it's a later step with
   your builder, not a missing key.
7. **Plain English, calm, encouraging.** US English. Explain before doing.
   Never make the owner feel out of their depth. If something's not connected, it's
   "not connected yet", never a mistake.
8. **End with `/doctor`.** When you've gone through a toolkit (or all of
   them), run `python3 scripts/doctor.py` and show the owner the table so they can
   see what's now green.

## Escalation line (end every tool's walkthrough with this)

"Stuck on this one? Run `/doctor` and send your builder the output - they'll point
you to the exact step."

## What it reads / touches

- Reads: `data/skill_registry.json`, `.env.example` (for slot names and
  instructions), `.env` (to see what's filled - values never echoed).
- Touches: helps the owner install software (with their paste/confirm), helps them
  populate `.env` (their hands), runs read-only verifies. It never commits and
  never posts anything.
