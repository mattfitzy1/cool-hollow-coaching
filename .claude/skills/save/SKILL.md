---
name: save
description: "Quick context save before closing a window. Captures what this session worked out into a dated memory file and updates session_last.md so the next /prime picks up where you left off. Does NOT commit, push, or touch git history - pure local writes, about 10 seconds. Trigger phrases: '/save', 'save context', 'save this session', 'snapshot this', 'checkpoint', 'save before I close'."
---

# /save - Quick Context Snapshot

> A fast, no-git save. Captures what this session figured out so the next window's `/prime` knows where you left off. Pair it with `/commit` for a proper end-of-day save.

## What this does

Writes a short summary of *this session's* thinking to two places, both inside your own workspace:

1. **A new dated file in `memory/deep-memory/`** - a durable record of this save.
2. **`memory/session_last.md`** - overwritten with the same summary so the next `/prime` reads it first.

No git. No pushing. No syncing anywhere. Pure local writes, done in about 10 seconds.

## When to use this vs `/commit`

| | Use it when | What it does |
|---|---|---|
| `/save` | A quick capture before you close a window. As often as you like. | Writes a memory file + updates `session_last.md`. No git. |
| `/commit` | The end of a real session, when you want it backed up. | Saves your files into git and pushes to your private backup. |

Your files on disk are safe either way - both of these are about preserving the *story* of what was decided, not the files themselves.

## Rules

1. **Never run `git add`, `git commit`, `git push`, or any write-side git command.** This skill never touches git. `git status --short` (read-only) is fine, just for context.
2. **Never touch `HISTORY.md`.** That is `/commit`'s job.
3. **Never sync anywhere.** No Desktop copy, no external folders. Everything stays in her workspace.
4. **Don't ask questions mid-save.** Pick a sensible name, write the files, report. If the session is hard to summarise, just describe what was discussed.
5. **Speed matters.** Aim for under 10 seconds.

## Execution

### Step 1 - Work out the filename

1. Get today's date: run `date '+%Y-%m-%d %A'` - capture both the date and the weekday. Don't assume from earlier in the conversation; it may have crossed midnight.
2. List existing `memory/deep-memory/{date}-save-*.md` files to find the next save number for today. First save of the day is `save-1`, then `save-2`, and so on.
3. Pick a short 2-4 word kebab-case slug for the main thread of the session (e.g. `restore-carousel`, `app-hero-edit`, `week-content-plan`).
4. Final filename: `memory/deep-memory/{date}-save-{N}-{slug}.md`.

**Date discipline:** stamp both the date AND the weekday on the memory file and on `session_last.md`. The next `/prime` uses these to talk about "today" vs an earlier day correctly.

### Step 2 - Read a little git context (read-only)

```bash
git status --short
git log -1 --format="%h %s"
```

Use these to fill in the "Workspace state" section. Read-only, never write.

### Step 3 - Write the memory file

Use this template. Keep it tight - bullets, not essays. About one page.

```markdown
# Save - {date} ({day of week}), Save {N} - {slug-as-title}

Quick save before closing the window. Written by /save, not /commit.

---

## What was worked on

- {specific - files, skills, decisions, what was talked through}

## Key decisions

- {anything decided or any change of direction, with a one-line why}

## Open threads / mid-flight items

- {anything left in progress, and questions to come back to}

## Next steps

1. {next concrete action}
2. {next concrete action}
3. {next concrete action - max 3}

## Workspace state at save time

- Modified files: {from git status, or "none"}
- Untracked files: {from git status, or "none"}
- Last commit: {short-hash + subject from git log -1}
- Not yet saved to git (run /commit later): {yes/no}

## Notes for next /prime

- {anything the next session needs that isn't obvious from the files}
```

### Step 4 - Overwrite session_last.md

Write the same content (compress it a little if the memory file is long) to `memory/session_last.md`, using this format:

```markdown
---
name: last-session-summary
description: "Quick /save snapshot - {date} save-{N} - {one-line summary}"
---

**Date:** {date} ({day of week} - /save snapshot, not a full /commit)

{body - same structure as the memory file above}

**Save type:** /save (quick) - not yet saved to git, no HISTORY entry.
```

The "Save type" line tells the next `/prime` this was a quick save, so if it sees uncommitted changes it knows why.

### Step 5 - Report

One short, reassuring line:

```
Saved → memory/deep-memory/{date}-save-{N}-{slug}.md
session_last.md updated.
Safe to close this window. Your files and your notes are kept. Run /commit later to back it up properly.
```

## Non-goals

- Does not commit, push, or stage anything.
- Does not update `HISTORY.md` - that's `/commit`'s job.
- Does not sync anywhere outside her workspace.
- Does not ask follow-up questions. Pick a slug, write, report.
- Does not replace `/commit`. `/save` captures the story; `/commit` backs up the files.
