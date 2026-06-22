---
name: schedule
description: "Schedule Instagram content, pick developed ideas, assign dates, manage the content calendar"
requires:
  - tool: publer
    type: key
    optional: true
    account: "Publer"
    bundle: content
    plan: "Free if its API and Instagram publish are free on your plan; otherwise paid"
    signup: "https://publer.com → connect Instagram → Settings → Access → API key"
    where: "Settings → Access → API key"
    env: PUBLER_API_KEY
    verify: "Publer API: list workspaces/accounts"
---

# /schedule: Schedule Content

> Interactive scheduling session for Instagram: pick developed ideas, assign dates, and manage the content calendar. Aim for about three posts a week.

**Publer is optional here.** This skill plans the calendar; it never posts and never auto-schedules. If you connect Publer (a key tool, optional), drafts can be pushed to Publer as drafts for you to review and publish yourself. If you have not connected Publer, that is completely fine: the plan still works and each piece is saved to your posts folder to publish from the Instagram app.

> Before doing anything with Publer, run `ensure_ready("publer")`. If its software or its credential is missing, or its verify fails, **do not attempt the task and do not error out.** Run the setup walkthrough (what to sign up for, the exact link and click path, where the key goes in `.env`, then verify) and only once it passes, continue. Because Publer is optional, if she would rather not connect it, fall back to saving the plan and the posts to her folder and carry on without it. **Never auto-schedule or auto-publish anything.**

## Variables

mode: $ARGUMENTS (optional: "review" to review the existing schedule instead of scheduling new content)

## Instructions

You are running a **Scheduling Session** for Cool Hollow Coaching's social channels. Your job is to help you pick which developed ideas to post next, assign dates, and keep a calm, steady calendar of about three posts a week.

### Setup: Load Current State

1. **Read the strategy:**
   - `content/strategy.md`, platform (Instagram), cadence (~3/week), the loose weekly shape, format types

2. **Query the pipeline:**
   ```bash
   source .venv/bin/activate && python3 -c "
   import sys, sqlite3; sys.path.insert(0, '.')
   from scripts.content_db import get_connection
   conn = get_connection()

   # Developed ideas ready to schedule
   developed = conn.execute(\"\"\"
       SELECT id, title, channel, format_type, priority_score,
              edit_turnaround_days, audience_segment, offer_alignment, created_at
       FROM content_ideas WHERE production_status = 'developed'
       ORDER BY COALESCE(priority_score, 0) DESC, created_at DESC
   \"\"\").fetchall()

   # Currently scheduled
   scheduled = conn.execute(\"\"\"
       SELECT id, title, channel, format_type, film_by_date,
              publish_date, production_status
       FROM content_ideas WHERE production_status IN ('scheduled', 'filmed', 'editing')
       ORDER BY publish_date ASC
   \"\"\").fetchall()

   print('=== DEVELOPED (ready to schedule) ===')
   for r in developed:
       p = f'P{r[\"priority_score\"]}' if r['priority_score'] else '-'
       print(f'  #{r[\"id\"]} [{r[\"format_type\"] or \"?\"}] {r[\"title\"]} ({p})')

   print()
   print('=== CURRENTLY SCHEDULED ===')
   for r in scheduled:
       print(f'  #{r[\"id\"]} [{r[\"format_type\"] or \"?\"}] {r[\"title\"]} - publish: {r[\"publish_date\"] or \"TBD\"} ({r[\"production_status\"]})')

   conn.close()
   "
   ```

3. **Read the offer** (so a post can land alongside something current):
   - `content/offers-and-funnels.md`

### Stage 1: REVIEW THE CURRENT WEEK

Present the current state:
- **Scheduled / in-progress items** with dates
- **Gaps**: where the next slots are, against the target of about three a week
- **Format balance**: how the mix of reel / carousel / still / story is looking against the loose weekly shape (one teaching, one brand/story, one lighter)

Format it as a compact table.

### Stage 2: PRESENT DEVELOPED IDEAS

Show developed ideas ranked by priority:

```
Ready to Schedule:
| # | ID | Title | Format | Pillar | Priority |
|---|-----|-------|--------|--------|----------|
...
```

Suggest which ideas fill the gaps in the week and keep the format mix balanced.

**Ask: "Which would you like to post this week? Give me the IDs and the days."**

**STOP. Wait for her picks.**

### Stage 3: CALCULATE DATES & CONFIRM

For each picked idea:
1. If it needs filming or design lead time, calculate `film_by_date = publish_date - edit_turnaround_days` (reels and carousels need more lead time than a still or a story).
2. Check for clashes (two things on the same prep day, or more than the target cadence in a week).
3. Present the schedule:

```
This Week:
| Prep By | Publish | Title | Format | Pillar |
|---------|---------|-------|--------|--------|
...
```

**Ask: "Does this week work? Any date changes?"**

**STOP. Wait for confirmation.**

### Stage 4: UPDATE THE CALENDAR (and optionally draft into Publer)

After confirmation:

1. **Update content_ideas:**
   ```bash
   source .venv/bin/activate && python3 -c "
   import sys; sys.path.insert(0, '.')
   from scripts.content_db import get_connection
   from scripts.content_writer import update_status

   conn = get_connection()
   # Repeat for each scheduled idea:
   update_status(conn, IDEA_ID, 'scheduled',
       film_by_date='YYYY-MM-DD', publish_date='YYYY-MM-DD')
   conn.close()
   print('Schedule updated.')
   "
   ```

2. **Regenerate the pipeline:**
   ```bash
   source .venv/bin/activate && python3 scripts/generate_pipeline.py
   ```

3. **Optional Publer draft (only if she wants it and Publer is connected):**
   - Run `ensure_ready("publer")` first. If Publer is not connected and she does not want to set it up now, skip this step entirely and just save the post to her folder.
   - When used, `publer_post.py` always pushes as a **draft** for her to review and publish herself. Never publish directly.

4. **Report:**
   - Summary: X posts scheduled this week
   - The next prep day and what to make
   - Where each draft lives (Publer draft or her posts folder)

### Review Mode

If `$ARGUMENTS` = "review":
- Show all scheduled / in-progress items
- Flag anything overdue (film_by_date < today, still "scheduled")
- Allow status updates (mark as filmed, move to editing, mark published)

### Critical Rules

- **Interactive**: always confirm before updating dates.
- **Never auto-schedule and never auto-publish**: she picks what to post and when, and she publishes. The system only plans and drafts.
- **Steady cadence**: aim for about three a week. Calm and consistent beats heavy and burnt out. Flag if a week is getting overloaded.
- **Format-aware**: reels and carousels need more lead time than a still or a story.
- **Balanced mix**: nudge toward the loose weekly shape (one teaching, one brand/story, one lighter) rather than three of the same.
- **Publer is optional**: if it is not connected, fall back to the posts folder + manual Instagram post, never dead-end.
