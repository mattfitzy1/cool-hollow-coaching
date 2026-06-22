---
name: inbox-triage
description: >
  Clear the inbox in one pass. Reads recent mail, separates real people awaiting a reply from automated noise, and pre-drafts the replies it can so you approve-and-send instead of starting from a blank screen. Draft-only; nothing sends, no drafts are created in your email, replies go to the clipboard for you to send yourself. Use when you say "triage my inbox", "what needs a reply", "clear my email", "what's in my inbox", "draft my replies", "go through my email". Triggers: triage inbox, inbox triage, clear my email, what needs a reply, go through my inbox, draft my replies, email triage.
requires:
  - tool: gmail-mcp
    type: mcp
    bundle: business
    plan: "Phase-2 capability - needs an email connection set up with your builder"
    optional: true
---

# Inbox Triage

> One pass over the inbox: what is noise, what needs you, and a ready draft for each reply you owe. You approve and send. Nothing is sent, no draft is created in your email, no label or archive is touched.

## This skill is a Phase-2 capability (email is not connected yet)

**Before doing anything, check whether email is connected.** At launch, your AIOS has no email connection: reading your inbox needs an email (MCP) connection that is set up separately, with your builder, because it cannot be done by pasting a key into `.env`. This is a deliberate Phase-2 step, not a `/setup` env step.

If there is no email connection available, do not attempt to read mail and do not error out. Say plainly:

> "Reading your inbox needs your email connected first. That's a quick one to do with your builder when you're ready - it needs a connection that I can't set up from a key on my own. Once it's connected, this skill drafts replies for you to approve and send. Want me to note it on your list for next time you two are on a call?"

Only run the steps below once email is actually connected.

## The rules this skill never breaks

- **Draft, never send. No drafts in your email.** Replies are written here in the chat and copied to the clipboard. You read each one and send it yourself, from your own email. Nothing is sent automatically and nothing is saved as a draft in your mailbox.
- **Reply-status the right way.** To decide if a thread is awaiting you, fetch the whole thread and take the **last message by position** (email threads come back in time order). If the last sender is you, it is already handled. Never eyeball mixed-timezone `Date:` headers - that produces false flags.
- **Your voice, US English, no buzzwords.** Draft in the owner's own voice (`context/voice-and-tone.md`). No em dashes unless the voice profile uses them.
- **Read-only by default.** Do not archive, label, mark read, or delete anything unless you explicitly ask in this run.

## Step 1 — Pull recent inbox mail

Search the inbox for recent mail (e.g. anything newer than 2 days, up to ~40 results). Widen the window if it has been a while since the last triage, or use whatever window you name.

## Step 2 — Sort into three buckets

Go through every result and classify:

- **NOISE (ignore)** — newsletters and marketing blasts, social notifications (Instagram, LinkedIn, etc.), receipts and billing system mail, calendar accept/decline auto-mails, app digests. List these as a single collapsed count, do not detail them.
- **FYI (no reply needed)** — real mail that is informational only (a forwarded notice, a receipt that matters, a "thanks, got it"). One line each, no draft.
- **NEEDS REPLY** — real mail from a real person where the last message in the thread is not from you. These are the ones that get drafted.

For anything ambiguous, cross-reference the sender against the people in `context/people/` so someone you know is recognized even if the name alone is not obvious. When unsure, treat it as NEEDS REPLY rather than burying it.

## Step 3 — Confirm reply-status on the NEEDS REPLY candidates

For each candidate, fetch the full thread and check the last message by position (per the rule above). Drop any where you already replied last. This stops false "needs reply" flags.

## Step 4 — Pre-draft the replies you can

For each genuine NEEDS REPLY:

- If you have enough context to write a sensible reply (the ask is clear, the relationship and history are known), draft it in the owner's voice. Warm, clear, and to the point.
- If a reply needs a decision or information only the owner has (a price, a yes/no, a commitment), do NOT guess. Write one line stating what is being asked and what you need to draft it.
- Never state an unverified figure from a thread as fact in a reply.

## Step 5 — Present the triage

Show, in order:

1. **Needs your reply** — for each: `From | subject | one-line why it matters`, then the draft (or the "needs your input" note). Put genuinely time-sensitive ones at the top.
2. **FYI** — one line each.
3. **Noise** — just the count ("28 automated, ignored").

State clearly: nothing has been sent, nothing saved as a draft in your email.

## Step 6 — On approval

For each reply you approve (you may edit first - honor exactly what you approve):

- Copy it to the clipboard with `pbcopy` so you can paste it into your email and send. If there are several, handle them one at a time so each lands on the clipboard cleanly, or ask which order you want.
- Do not create drafts in your email, do not send, do not archive.

## Notes

- The skill is judgement-heavy (what is noise, what matters, what to say). It does not need a script.
- This is meant to be a fast pass. If it gets slow or noisy in real use, tighten this file.
