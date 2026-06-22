---
name: prime-task
description: "A quick resume for picking work straight back up after a /commit or restart. Loads only where you left off and what plans are open - no full context catch-up. Use this when you're mid-way through something and just want to carry on. For a warm full start, use /prime. Fully offline."
---

# Prime (Task)

> The fast resume. For carrying on with what you were doing, not a full hello.

Use this when you commit and reopen a fresh window in the middle of a task and just want to keep going. The full `/prime` reads all your context files and gives you the warm welcome; this one skips straight to "where were we?"

**Why it's quick:** `CLAUDE.md` already loads at the start of every session, so who you are, what Cool Hollow Coaching is, and your operating rules are already in context. Do NOT re-read them, and do NOT read `context/strategy.md`, `business-info.md`, `voice-and-tone.md`, or `brand.md` - pull any of those on demand only if the task in front of you actually needs them.

## What to do

1. **Date stamp (one line).** Run `date '+%A %d %B %Y'` so dates are correct. Hold it for the session.

2. **Read where we left off.** Read `memory/session_last.md`. This is the carry-over: what was being worked on, any decisions, open threads, and the next step that was flagged. If it does not exist, say so in one line and move on.

3. **List open plans.** Run `ls -t plans/ 2>/dev/null | head -12` so any active plans are visible. Do NOT read them all. If `session_last.md` names one specific plan as the next step, read that ONE plan; otherwise just leave them listed.

That's it. Fully offline - no email, no calendar, no online checks of any kind.

## Output (keep it short)

A tight orientation, not a briefing:

1. **Date** - one line.
2. **Where we left off** - 2-4 lines from `session_last.md`: what was in flight and the flagged next step.
3. **Open plans** - the listing, with the relevant one called out if `session_last` points to it.
4. **Ready** - one line confirming you're ready to carry on, naming the obvious next task if there is one.

If the owner needs the warm full start instead (the proper hello, the toolkits, the brand reflection), tell them in one line to run `/prime`.

## Tone

Minimal and calm. The owner ran this to keep moving, so get them oriented in a few lines and stop. Plain English, US English, no error dumps.
