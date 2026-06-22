---
name: skill-finder
description: "Scan the public Claude Code skill landscape and surface high-signal candidates worth borrowing into the workspace. Run weekly or on demand to operationalise the 'Borrow Before You Build' principle. Trigger words: skill-finder, find skills, scan skills, what skills exist, new skills, claude code skills, community skills, borrow before you build, awesome claude code, public skills, skill landscape, find new commands, find claude plugins."
---

# Skill Finder

> Scans the public Claude Code skill landscape via GitHub topic search, scores hits against the workspace, and writes a digest of "borrow this" candidates to `outputs/skill-finder/{date}.md`. Operationalises the AIOS principle: borrow before you build.

## When to run

- **Weekly check-in** — pull up Monday morning, scan the digest, queue anything worth a closer look.
- **Before starting a new build** — if a custom skill is about to take more than 2 hours, run this first. The `czlonkowski/n8n-skills` find on 2026-05-13 saved ~3 hours of build work via one `/plugin install`.
- **After hearing a community signal** — when someone in the AAA group, AfricAI, or Command Centre mentions a tool, run this to find adjacent ones at the same time.
- **Before /create-plan on anything skill-shaped** — the planning step should know what already exists.

## What it does

1. Queries GitHub via the `gh` CLI across three high-signal topics:
   - `topic:claude-code-skills`
   - `topic:claude-skills`
   - `topic:claude-code-plugins`
2. Filters out junk: archived repos, <50 stars, last push older than 180 days, non-permissive licences.
3. Fetches the README for the top candidates.
4. Scores each candidate on:
   - stars (capped buckets)
   - recency of last push
   - permissive licence
   - keyword match against the workspace's current priority terms (AIOS, Outlook, LinkedIn, Cloudflare, n8n, etc. — edit the `PRIORITY_TERMS` list in the script as priorities shift)
   - penalty for overlap with installed skills or anything already in `docs/_index.md`
5. Writes a markdown digest to `outputs/skill-finder/{YYYY-MM-DD}.md` with top 5 detailed + full ranked table.

## How to run

Phase 2 is live: the launchd agent `com.aios.skill-finder` runs `find_skills.py --notify` every Monday at 05:30 SAST. You only need to run it by hand for an ad-hoc scan.

```
python3 scripts/find_skills.py
```

Useful flags:

```
python3 scripts/find_skills.py --limit 10           # detail top 10 instead of 5
python3 scripts/find_skills.py --since 90           # only repos pushed in last 90 days
python3 scripts/find_skills.py --min-stars 100      # raise the star floor
python3 scripts/find_skills.py --no-readme          # faster, skips README context
python3 scripts/find_skills.py --print              # also print digest to stdout
python3 scripts/find_skills.py --notify             # send a Telegram ping after the run (cron uses this)
python3 scripts/find_skills.py --no-task-match      # skip the task-audit + next-actions cross-reference
```

When the user invokes the skill in conversation:

1. Run `python3 scripts/find_skills.py` from the repo root.
2. Read the resulting digest at `outputs/skill-finder/{today}.md`.
3. In chat: summarise the top 3 in one sentence each, with their fit score and a short "borrow it?" judgement.
4. Flag anything that looks like a duplicate of an installed skill — push the user away from those.
5. If nothing scores above ~6, say so plainly. A quiet week is fine.

## Hard rules

- **Advisory only.** Never auto-install. Skills run arbitrary code; bad ones can do real damage.
- **License filter is real.** GPL or proprietary licences are excluded by the script. Don't override silently.
- **Don't get attached to stars.** A 50k-star repo is often a mega-framework with little reusable signal. A 200-star repo doing one thing well is usually the better borrow.
- **Match against current priorities.** A skill that scores high on stars but doesn't match any priority term is probably noise this week.

## Output

`outputs/skill-finder/{YYYY-MM-DD}.md` — markdown digest with:

- Top N candidates (configurable, default 5): repo URL, stars, last push, licence, topics, description, score, score reasons, overlap flags, install snippet (manual review required), README preview.
- Full kept table (after filtering) ranked by score.
- The exact queries used.

## Why this skill exists

From the `plans/explore-2026-05-13-skill-finder-automation.md` explore doc:

> Liam's "Borrow Before You Build" is one of the five AIOS principles. The n8n find proved the principle pays — a 20k-star battle-tested MCP replaces ~3 hours of custom build with one `/plugin install` line. There are likely 10–30 more skills like that already published that would either replace work in flight or unlock new capabilities. We don't see them because we're not looking.

This skill closes that gap. It's a five-minute weekly habit, not a heavy process.

## Phase 3 — live (2026-05-13)

- **Task cross-reference:** every run parses open rows from `context/task-audit.md` and open bullets from `gtd/next-actions.md`, then matches them against each candidate via stopword-filtered token overlap (≥2 shared content terms = match).
- **Score boost:** +3 per matched task, capped at +6 total per candidate so cross-reference doesn't drown the existing star/recency/priority signals.
- **Digest surface:** each top candidate gets a "Could unblock" section listing the matched task-audit row IDs or next-action snippets, with the shared terms that triggered the match.
- **Stopword tuning:** the matcher's stopword list explicitly excludes the universal Claude-ecosystem terms (`claude`, `code`, `agent`, `skill`, `mcp`, etc.) because they appear in every candidate and produce noise rather than signal. Edit `STOPWORDS` in `scripts/find_skills.py` if false matches creep in.
- **Disable per-run:** `python3 scripts/find_skills.py --no-task-match` skips the cross-reference (useful when scanning for skills unrelated to your current work).

## Phase 2 — live (2026-05-13)

- **Weekly cron:** `~/Library/LaunchAgents/com.aios.skill-finder.plist`. Fires Mondays at 05:30 SAST. Logs to `data/skill-finder.log`. Sends a Telegram ping to the Automations topic with top 3 candidates + digest path.
- **Morning brief surface:** `scripts/daily_brief.py` appends a one-line skill-finder block on Mondays. Shows top 2 candidates + total kept + digest path. Falls back to a "cron may not be firing" warning if the latest digest is older than 7 days.
- **Source expansion** was scoped out: 3 GitHub topic queries already produce ~75 candidates per run, which is plenty. Anthropic marketplace and `awesome-claude-code` aggregators get added if the manual habit shows the existing source set is too narrow.

### Re-load the cron after editing the plist

```
launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/com.aios.skill-finder.plist
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.aios.skill-finder.plist
launchctl list | grep skill-finder
```

### Trigger the next run immediately (for testing)

```
launchctl kickstart -k gui/$(id -u)/com.aios.skill-finder
```

## Future phases (parked)

- **Auto-fork to skill-mirror.** Was scoped into Phase 3 originally, then dropped on 13 May. Reason: the `your-org` GitHub org doesn't exist yet, the candidates are public 50+-star repos so they're not going to vanish overnight, and forking into `your-github-account` directly would clutter the repo list. Revisit if (a) we lose a useful upstream, or (b) a your own GitHub org gets registered for other reasons.
- **Source expansion.** Anthropic marketplace, GitHub Trending, awesome-aggregators. Still parked. The three topic queries produce ~75 candidates/week; expansion gets justified when the existing source set demonstrably misses a known good skill.

## Maintenance

- Edit `PRIORITY_TERMS` in `scripts/find_skills.py` when strategic priorities shift (e.g. when a new vertical or integration becomes hot, add it; when something is parked, drop it).
- The three GitHub topic queries are stable, but if a new topic becomes the dominant one (e.g. `claude-skills-2` style), add it to the `QUERIES` constant.
- Re-test live every quarter: GitHub search ranking changes, `gh` CLI auth can expire, and new aggregator repos appear that may deserve their own source.
