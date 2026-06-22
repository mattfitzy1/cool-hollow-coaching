---
name: catchup
description: "Deferred / Phase-2. A full period recap (what happened over a stretch of days) that pulls from email and calendar as well as your own memory. Not active at launch because it needs your email and calendar connected, which is a Phase-2 step set up with your builder. For now, use /recall instead."
---

# /catchup — Full Period Recap (deferred / Phase-2)

This skill is **not active at launch.** It is the bigger sibling of `/recall`: it reconstructs a whole period (a week, a month, a date range) by pulling from your email, your calendar, and your workspace memory together.

The two outside sources it needs — your email and your calendar — are not connected at launch. Connecting them is a deliberate **Phase-2 step you do with your builder**, because it needs a connection that cannot be set up by pasting a key into `.env`. Until then, this skill stays parked so it never half-works or throws an error.

## What to do when it is called now

Do not attempt to read email or calendar. Say plainly:

> "A full catch-up like this pulls from your email and calendar, which aren't connected yet — that.s a Phase-2 thing to set up with your builder when you.re ready. In the meantime, `/recall` searches everything already in your workspace (your memory, notes, projects and content) and covers most of what you'd want. Want me to run `/recall` for that period instead?"

Then, if you say yes, run `/recall` for the period you named.

## When this gets switched on (later, with your builder)

Once email and calendar are connected, this skill becomes a real period recap: read the dated files in `memory/deep-memory/`, read `HISTORY.md`, pull sent and received mail for the range, pull calendar events for the range, and compile a day-by-day narrative plus a period summary (themes, what moved, what's still open). At that point this file gets fleshed out into the full workflow. Until then, it stays a friendly pointer to `/recall`.
