---
name: clear-to-kill
description: "A quick 'am I safe to close?' check. Looks at whether your work is saved and backed up, and gives one clear answer. Read-only - it never changes anything. Trigger phrases: 'clear to kill', 'safe to close', 'safe to kill', 'am I clear to close', 'can I quit', 'can I close this window'."
---

# /clear-to-kill - "Am I safe to close?" check

> Run this before you close the window or shut the laptop. One quick look, one clear answer.

## What this does

In a few seconds it tells the owner whether their work is saved and backed up, so closing the window is safe. There are three answers only:

- 🟢 **All saved** - everything is committed and backed up. Close away.
- 🟡 **Worth a glance** - nothing is unsaved, but there's a small thing worth knowing first.
- 🔴 **Not yet** - there's work that isn't saved or backed up. It tells the owner exactly what to do (usually just run `/commit`).

This looks at the files on disk, so it's the same answer in any window open in this workspace. It does NOT check unsaved notes inside another app (like a text editor) - if something's been typed elsewhere, save that first.

## Rules

1. **Read-only.** Never run `git add`, `git commit`, `git push`, `git stash`, `git reset`, or any command that changes anything. This skill only looks; the owner decides.
2. **One of the three answers.** Never vague, never "maybe".
3. **Quick.** A few seconds. The only network call allowed is `git fetch --dry-run`.
4. **Plain English.** Never dump raw git output at the owner.

## The checks (in order)

Run these in the workspace. Confirm `CLAUDE.md` exists at the workspace root first; if it doesn't, say so plainly and stop.

### 1. Is anything unsaved? (working tree)
```bash
git status --short
```
- Modified or staged files → there's work not yet committed.
- Untracked files (ignore `.DS_Store` and macOS junk) → new files not yet saved.

### 2. Is everything backed up? (unpushed commits)
```bash
git log --oneline @{u}..HEAD 2>&1
```
If there are commits listed, they're saved locally but not yet pushed to the private backup. If it errors with "no upstream", just note backup tracking isn't set up yet and move on - that's informational, not a blocker.

### 3. Anything coming in from the backup? (divergence)
```bash
git fetch --dry-run 2>&1
```
If the output is empty, you're in sync. If it mentions branches, there are changes on the backup not yet pulled - informational, doesn't stop closing.

## How to decide the answer

First matching rule wins:

1. **Any modified file, staged file, or unpushed commit** → 🔴 **Not yet**.
2. **Any untracked file (other than `.DS_Store`), or incoming changes from the backup, or no backup tracking set up** → 🟡 **Worth a glance**.
3. **Everything else** → 🟢 **All saved**.

## What to show the owner

### 🟢 All saved
```
🟢 All saved - safe to close.

Everything is committed and backed up. Nothing will be lost.
Last save: <short-hash> <subject>
```

### 🔴 Not yet
```
🔴 Not saved yet - hold on a moment.

There's work here that isn't backed up:
  Changed files: <files>
  Not backed up: <count> save(s) waiting to push

To be safe before you close:
  Run /commit - that saves and backs everything up.
```

### 🟡 Worth a glance
```
🟡 Almost - one thing worth knowing.

  <e.g. "A couple of new files aren't saved yet" or
   "There are changes on your backup you don't have locally">

Nothing is lost, but you may want to run /commit first.
```

## How to run it

1. Confirm the workspace exists (`CLAUDE.md` at the root). If not, say so plainly and stop.
2. Run the three checks (chain them in one Bash call to stay quick).
3. Work out the answer and show the matching block. Nothing else - no preamble, no follow-up questions.

## What it does NOT do

- Does not save, back up, or change anything - it only looks.
- Does not stop the owner closing the window - it just tells them.
- Does not see unsaved notes inside other apps (a text editor, a browser tab). Save those yourself first.
- Only runs when asked ("am I clear to close?").
