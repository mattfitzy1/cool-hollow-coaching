---
name: prime
description: "Start a session and get a warm welcome. Reads your context and brand, reminds you what your AIOS can help with, and checks for any unsaved work from last time. Fully offline - no email or calendar."
---

# Prime

> A calm, warm start to your session. Loads who you are and what your business is, reflects your voice back to you, and makes sure nothing from last time got lost.

This is the first thing you run when you sit down. It is offline and fast: it reads your own files, says hello, and gets you ready. It never reaches out to email, calendars, or anything online.

## Step 0: Check today's date

Run `date '+%A %d %B %Y'` to confirm today's day and date. Hold this as the reference for the whole session, and use absolute dates (like "Friday 12 June") rather than "yesterday" or "tomorrow" unless you have checked them.

## Step 1: Read the owner's context

Read these files so you genuinely know Matt and his business before you say a word:

- `context/personal-info.md` - who Matt is, in his own words
- `context/business-info.md` - what the business is
- `context/brand.md` - the brand palette, type, and brand
- `context/voice-and-tone.md` - how Matt writes and sounds (this is HIS voice)
- `context/strategy.md` - what he is focused on right now
- `context/current-data.md` - light current state
- `HISTORY.md` - workspace changelog (what was built, when)
- `docs/_index.md` - documentation routing index (find the right system doc before working on something already built)

If any of these are still empty (a brand-new workspace), that is fine - note it gently and offer to run `/install module-installs/context-os-v1` to fill them in (see Step 4).

Read the last 30 lines of `HISTORY.md` if it exists, to see what was last worked on.

## Step 2: Check last session

Look for `memory/session_last.md`. If it exists, read it so you know where Matt left off - what he was doing, what was unfinished, and any next step he noted. If it does not exist, just say it is a fresh start, nothing to pick up.

## Step 3: Check for unsaved work (the "don't lose anything" check)

Run `git status --porcelain` in the workspace. This is the gentle safety net so a session's work never quietly disappears.

- If it is empty, everything is saved. Say so in one short, reassuring line.
- If there are changes, it means there is work from last time that has not been committed yet. Tell Matt plainly: "There's some work here from last time that hasn't been saved yet. Want me to save it with `/commit`?" Do not save anything automatically; just offer.

Keep this calm. It is a reminder, not a warning.

## Step 4: Detect a fresh workspace

If the context files in Step 1 were mostly empty, this is a brand-new workspace. Warmly offer the next step:

> "It looks like we haven't set up your context yet. Whenever you're ready, run `/install module-installs/context-os-v1` and I'll ask you a few easy questions to learn about you and your business. No rush, and there are no wrong answers."

Use the exact module name `context-os-v1`. If the context files are already filled in, skip this step.

## Step 5: Say hello (the welcome)

Now greet Matt warmly and briefly. This is a welcome, not a briefing. Keep it human and calm. Cover:

1. **Hello, Matt.** Greet him by name and confirm today's date in one friendly line.

2. **What this is.** One or two plain-English sentences: "This is your AIOS - your own AI workspace for your business. You talk to me in normal English and I help you get things done. Nothing goes out into the world without you seeing it first."

3. **What I can help with - your four toolkits**, one line each, in plain language:
   - **Content & social** - writing your posts in your voice, capturing ideas, and planning your week.
   - **Creative studio** - making on-brand images, carousel slides, and video.
   - **App & web** - editing your site or app in plain English and putting it live.
   - **Business backbone** - keeping track of what you're working on, remembering things across sessions, and the day-to-day admin.

4. **I know your brand.** Reflect the brand back to him in one short, warm sentence drawn from `brand.md` and `voice-and-tone.md` - the palette, type, and voice. This is how he knows the context loaded properly. Keep it in his register, not salesy.

5. **Where things stand.** If there was a last session (Step 2), one line on what he was doing and any next step. If there is unsaved work (Step 3), the gentle save offer. If it is a fresh workspace (Step 4), the `/setup` and context-os offer.

6. **Ready.** End with a short, encouraging "What would you like to work on?" Keep it open and easy.

## Tone

Warm, calm, and encouraging. Matt is non-technical and this is the first thing he sees each session, so it should feel like a friendly hello from someone who has his back, never like a software dashboard. Plain English only. Never list technical steps, never dump anything that looks like an error, and never make him feel out of his depth. US English.

## A note on what this does NOT do

This skill is fully offline. It does not check email, calendars, or any online service - those are not connected, and that is by design for now. If you ever want your email or calendar connected, that is a separate setup you would do with your builder. Until then, `/prime` is purely your own files saying hello.
