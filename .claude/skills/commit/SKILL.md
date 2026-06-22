---
name: commit
description: "Save your work properly and back it up. Saves your changes into git, writes a short note of what changed, updates the changelog, and pushes to your private backup. Run it at the end of a real session."
---

# Commit

> Save your work and back it up to your private repo - all in one go.

## Variables

message: $ARGUMENTS (optional - you can pass a short description, or leave it blank and I'll write one for you)

---

## When to use /commit vs /save

`/commit` is the proper end-of-session save: it locks your work into git, writes a short note of what changed, and pushes it to your private backup so it's safe in the cloud. Run it at the end of a real chunk of work, or at the end of the day.

`/save` is the quick mid-session snapshot - just a memory note, no git, about 10 seconds. Use that between work blocks.

**Rule of thumb:** most days have one or two `/commit` runs and as many `/save` runs as you like.

---

## What this does

1. Saves your changed files into git with a short, clear message.
2. Adds a line to your changelog (`HISTORY.md`) so there's a running record.
3. Writes a session note so the next `/prime` knows where you left off.
4. Pushes everything to your private backup repo.

Follow this in order. Explain each step to the owner in one plain line as you go - never dump raw git output at them.

### Step 1: See what changed

Run `git status` and `git diff HEAD` to see what's changed. Understand it well enough to describe it in plain English - you'll need that for the message and the changelog.

### Step 2: Stage the changes

Stage the changed files. Prefer naming the files rather than `git add -A`, so nothing sensitive sneaks in.

**Never stage:**
- `.env` or any file with keys or passwords in it
- `.mcp.json` (it can hold an API key)
- `data/*.db` database files
- `__pycache__/` or anything that should be gitignored

If anything looks sensitive, pause and check with the owner first in plain language.

### Step 3: Write the message

If a message was passed in `$ARGUMENTS`, use it.

Otherwise write a short one in this shape:

```
<type>: <description>
```

**Types:** `feat` (new thing), `update` (improvement or content change), `fix` (correction), `content` (posts/captions/strategy), `docs` (notes), `chore` (tidying).

**Rules:** present tense (add, fix, update), 50 characters or fewer on the first line, no full stop at the end, be specific.

**Examples:**
- `content: draft this week's posts`
- `update: new hero line on the app`
- `feat: add the new flow to the app`

If the work spans a few areas, pick the most important type and add a couple of bullet points underneath.

### Step 4: Save it (commit)

Run the commit:

```bash
git commit -m "$(cat <<'EOF'
<message here>
EOF
)"
```

Run `git status` afterwards to confirm it worked.

### Step 5: Update the changelog (only when it's worth it)

**Skip this unless the work was a real new thing or improvement** (`feat` or `update`, or a notable deliverable). For small fixes and tidying, skip it.

If it's worth a line:
1. Add an entry to `HISTORY.md` under today's date (create the date heading at the top if it's not there).
2. Format: `## YYYY-MM-DD` heading, then a short title and 2-4 bullets on WHAT changed and WHY.
3. Stage `HISTORY.md` and commit it once with the message `chore: update changelog`.

If it doesn't trigger, say nothing and move on.

### Step 6: Write the session note

Write or overwrite `memory/session_last.md` so the next `/prime` picks up cleanly.

```markdown
---
name: last-session-summary
description: What was worked on, decisions made, and next steps from the most recent session
---

**Date:** [today's date]

**What was worked on:**
- [what got done this session]

**Key decisions:**
- [anything decided, or a change of direction]

**Open / unfinished:**
- [anything left in progress]

**Next steps:**
- [what to pick up next session]
```

Be honest about what was actually done vs just discussed. If a section is empty, write "None this session." This file is overwritten each `/commit` - it's always just the latest session.

### Step 7: Back it up (push)

Push to the private backup repo:

```bash
git push
```

This sends everything to the private GitHub repo (`origin`), so it's safe in the cloud. Tell the owner in one line that it's backed up. If the push fails (e.g. `gh auth` isn't set up yet), explain it plainly and point them to running `/doctor` - never dump the raw error.

### Step 8: Confirm

Report in plain English:
- The commit message used
- That it's saved and backed up
- One line on anything still to do, if relevant

Keep it warm and short. The point is the owner feels their work is safe.

---

## Rules

- **Never save secrets.** No `.env`, `.mcp.json`, keys, or passwords. Warn if any are about to be staged.
- **Never force-push.** No `--force`, `--no-verify`, or anything destructive.
- **Never amend** an existing commit unless the owner explicitly asks. Make a new one.
- **Explain in plain English.** No raw git output, no jargon. The owner should always understand what just happened.
