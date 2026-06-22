# Reddit Research -- AIOS Module Installer

> A plug-and-play module from the AAA Accelerator.
> Grab this and 15+ more at [aaaaccelerator.com](https://aaaaccelerator.com)

---

## FOR CLAUDE

You are helping a user install this AIOS Module. Follow these rules:

**Behavior:**
- Assume the user is non-technical unless they tell you otherwise
- Explain what you are doing at each step in plain English BEFORE doing it
- Celebrate small wins ("Reddit research is live -- Claude can now search any topic across Reddit!")
- If something fails, do not dump error logs -- explain the problem simply and suggest the fix
- Never skip verification steps -- if a check fails, stop and help the user fix it
- Use encouraging language throughout

**Pacing:**
- Do NOT rush. Pause after major milestones.
- After prerequisites: "Everything looks good. Ready to install?"
- After installation: "Files are in place. Let's run a quick test."
- After test: "You're all set. Here's what Claude can do with Reddit research."

**Error handling:**
- If `.claude/` folder doesn't exist, they need Claude Code installed first
- If files already exist at the target paths, ask before overwriting
- If `requests` module is missing, guide them to `pip3 install requests`
- If Reddit returns 429 errors during test, that's normal rate limiting. The client handles retries automatically.
- Never say "check the logs" -- find the problem and explain it

---

## OVERVIEW

This module gives Claude the ability to search Reddit, auto-detect relevant communities, and extract full threads with scored comments. All via Reddit's public .json endpoints.

Here's the problem it solves: Claude can't read Reddit by default. When you ask "what are people saying about X on Reddit?", Claude has to guess based on training data. This module fixes that. Once installed, Claude can search Reddit in real time, find the right subreddits automatically, and pull actual posts and comments with engagement scores.

**What Claude can do after this is installed:**
- Search all of Reddit or specific subreddits for any topic
- Auto-detect relevant communities (finds the right subreddits for you)
- Extract full thread content with top comments, scores, and author info
- Browse hot, top, and new posts from any subreddit
- Run a full research pipeline in one call: detect subreddits, search, rank by engagement, extract top threads

**Where it installs:** Into `.claude/skills/` and `scripts/reddit/` in your current workspace.

**Setup time:** 2-3 minutes. No accounts, no API keys, no approvals.

**Running cost:** Free. Reddit's public endpoints have no billing. Rate limited to 10 requests/minute (the client enforces spacing automatically).

---

## SCOPING

This module installs as one unit: the skill file and the Python client together. Nothing optional to skip.

Ask: "Ready to install? Takes about 2-3 minutes. No API key needed for this one."

---

## PREREQUISITES

### Python 3

```bash
python3 --version
```

Expected: `Python 3.8` or higher. If not installed: download from https://python.org (click Downloads, install the latest version).

### pip

```bash
pip3 --version
```

pip comes with Python. If this fails, reinstall Python from python.org.

### Install the requests library

```bash
pip3 install requests
```

No API key needed! Reddit's public endpoints are open.

[VERIFY] All checks pass without errors.

Ask: "Everything looks good. Ready to install the Reddit research skill?"

---

## INSTALL

### Step 1: Create the skill folder

```bash
mkdir -p .claude/skills/reddit
```

### Step 2: Install the Reddit skill

Write the following file to `.claude/skills/reddit/SKILL.md`:

````markdown
---
name: reddit
description: >
  Reddit search and content extraction via public .json endpoints (no API key needed).
  Search posts across all of Reddit or specific subreddits, auto-detect relevant subreddits,
  read full post content, extract comment trees with scores, browse hot/new/top posts.
  Reddit threads, Reddit comments, Reddit search, subreddit posts, Reddit discussion,
  what are people saying, Reddit opinions, community discussion, Reddit sentiment.
user-invocable: false
---

# Reddit Search & Extraction

Zero-auth Reddit research via public .json endpoints. Auto-detects subreddits, searches across Reddit, extracts full threads with scored comments. No API key, no PRAW, no approval wait.

## Setup

```python
from scripts.reddit.client import RedditClient
client = RedditClient()
```

**No env vars needed.** Uses Reddit's public .json endpoints (append `.json` to any Reddit URL).

## Method Reference

| Method | What | Rate Cost |
|--------|------|-----------|
| `search(query, sort, time_filter, limit, subreddit)` | Search r/all or a specific subreddit | 1 request |
| `search_subreddit(subreddit, query, sort, time_filter)` | Search within one subreddit | 1 request |
| `find_subreddits(query, limit)` | Auto-detect relevant subreddits for a topic | 1 request |
| `hot(subreddit, limit)` | Hot posts from a subreddit | 1 request |
| `top(subreddit, time_filter, limit)` | Top posts by time period | 1 request |
| `extract_thread(url, comment_limit)` | Full post body + top N comments with scores | 1 request |
| `research(query, time_filter, max_threads, ...)` | Full pipeline: detect, discover, extract | 5-8 requests |

## Full Research Pipeline

```python
# One call does everything: finds subreddits, searches, extracts top threads
result = client.research(
    "AI automation agency pricing",
    time_filter="year",    # hour, day, week, month, year, all
    max_threads=5,         # how many threads to extract in full
    max_comments=25,       # comments per thread
)

print(f"Searched: {result['subreddits_searched']}")
print(f"Found {result['posts_found']} posts, extracted {result['threads_extracted']} threads")

for t in result["threads"]:
    print(f"\n[{t['score']} pts, {t['comments_extracted']} comments] r/{t['subreddit']}")
    print(f"  {t['title']}")
    print(f"  {t['selftext'][:200]}...")
    for c in t["comments"][:3]:
        print(f"    [{c['score']} pts] u/{c['author']}: {c['body'][:100]}")
```

### research() Parameters

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `query` | str | required | Research topic |
| `time_filter` | str | `"year"` | hour, day, week, month, year, all |
| `max_threads` | int | `5` | Threads to extract in full |
| `max_comments` | int | `25` | Comments per thread (sorted by best) |
| `subreddits` | list | None | Override auto-detection with specific subreddits |
| `auto_detect_subreddits` | bool | True | Auto-find relevant subreddits |
| `max_subreddits` | int | `3` | Max subreddits to auto-detect |

### Response Shape

```python
{
    "query": "AI automation agency pricing",
    "subreddits_searched": ["all", "AINativeAgencies", "Entrepreneur"],
    "subreddits_detected": [{"name": "...", "subscribers": 12000, ...}],
    "posts_found": 22,
    "threads_extracted": 5,
    "threads": [
        {
            "title": "My client fired their $3k/mo SEO agency...",
            "subreddit": "AiAutomations",
            "score": 142,
            "num_comments": 87,
            "author": "username",
            "selftext": "full post body...",
            "url": "https://reddit.com/r/...",
            "created_utc": 1770367752.0,
            "upvote_ratio": 0.95,
            "comments_extracted": 25,
            "comments": [
                {"author": "...", "body": "...", "score": 45, "created_utc": ..., "is_op": false},
            ]
        }
    ]
}
```

## Individual Methods

### Search

```python
# Search all of Reddit
posts = client.search("Claude Code vs Cursor", sort="relevance", time_filter="month")

# Search one subreddit
posts = client.search_subreddit("ClaudeAI", "Claude Code tips", time_filter="week")

# Browse top posts
posts = client.top("SaaS", time_filter="week", limit=10)
posts = client.hot("artificial", limit=10)
```

### Search Parameters

| Parameter | Values | Default |
|-----------|--------|---------|
| `sort` | `relevance`, `hot`, `top`, `new`, `comments` | `relevance` |
| `time_filter` | `hour`, `day`, `week`, `month`, `year`, `all` | `year` |
| `limit` | 1-100 | 15 |

### Subreddit Discovery

```python
subs = client.find_subreddits("property management software", limit=5)
for s in subs:
    print(f"r/{s['name']} -- {s['subscribers']:,} members")
```

### Thread Extraction

```python
thread = client.extract_thread(
    "https://reddit.com/r/ClaudeAI/comments/abc123/post_title/",
    comment_limit=25,
)

print(thread["title"])
print(thread["selftext"])  # full post body
for c in thread["comments"]:
    print(f"  [{c['score']}] u/{c['author']}: {c['body'][:200]}")
```

## Rate Limits

| Limit | Value |
|-------|-------|
| Unauthenticated requests | 10/min (IP-based) |
| Delay between requests | 6.5s (enforced by client) |
| Typical research() call | 5-8 requests, ~40-50 seconds |
| Max search results per query | 100 |

The client handles rate limiting automatically. If Reddit returns 429, it waits 65 seconds and retries.

## Post Fields

| Field | Type | What |
|-------|------|------|
| `title` | str | Post title |
| `selftext` | str | Post body (full in extract_thread, truncated in search) |
| `score` | int | Net upvotes |
| `num_comments` | int | Total comments |
| `subreddit` | str | Subreddit name |
| `author` | str | Username |
| `created_utc` | float | Unix timestamp |
| `upvote_ratio` | float | 0.0-1.0 |
| `url` | str | Reddit permalink |
| `link_url` | str/None | External link (None for text posts) |

## Comment Fields

| Field | Type | What |
|-------|------|------|
| `author` | str | Username |
| `body` | str | Comment text |
| `score` | int | Net upvotes |
| `created_utc` | float | Unix timestamp |
| `is_op` | bool | True if posted by the thread author |
| `controversiality` | int | 0 or 1 |
````

[VERIFY]
```bash
cat .claude/skills/reddit/SKILL.md | head -5
```
Expected: File starts with `---` (YAML frontmatter).

### Step 3: Create the client directory and script

Create the directory:

```bash
mkdir -p scripts/reddit
```

Write the following file to `scripts/reddit/client.py`:

````python
"""
Reddit Search & Content Extraction Client
==========================================
Zero-auth Reddit research via public .json endpoints.

Usage:
    from scripts.reddit.client import RedditClient
    client = RedditClient()
    result = client.research("AI automation agencies", time_filter="year", max_threads=5)
"""

import re
import time
from datetime import datetime, timezone
from urllib.parse import quote_plus

import requests


class RedditClient:
    """Reddit search and extraction via public .json endpoints. No API key needed."""

    BASE = "https://www.reddit.com"
    HEADERS = {"User-Agent": "AIOS-Reddit/1.0 (research agent)"}
    MIN_INTERVAL = 6.5

    def __init__(self):
        self._last_request = 0.0

    def _get(self, url, params=None):
        elapsed = time.time() - self._last_request
        if elapsed < self.MIN_INTERVAL:
            time.sleep(self.MIN_INTERVAL - elapsed)
        resp = requests.get(
            url, params=params or {}, headers=self.HEADERS, timeout=30
        )
        self._last_request = time.time()
        if resp.status_code == 429:
            time.sleep(65)
            resp = requests.get(
                url, params=params or {}, headers=self.HEADERS, timeout=30
            )
            self._last_request = time.time()
        resp.raise_for_status()
        return resp.json()

    def search(self, query, sort="relevance", time_filter="year", limit=15,
               subreddit="all"):
        """Search r/all or a specific subreddit."""
        params = {
            "q": query,
            "sort": sort,
            "t": time_filter,
            "limit": min(limit, 100),
            "restrict_sr": "on" if subreddit != "all" else "off",
        }
        data = self._get(
            f"{self.BASE}/r/{subreddit}/search.json", params
        )
        return [
            self._parse_post(p["data"])
            for p in data.get("data", {}).get("children", [])
        ]

    def search_subreddit(self, subreddit, query, sort="relevance",
                         time_filter="year", limit=10):
        """Search within one subreddit."""
        return self.search(
            query, sort=sort, time_filter=time_filter,
            limit=limit, subreddit=subreddit
        )

    def find_subreddits(self, query, limit=5):
        """Auto-detect relevant subreddits for a topic."""
        data = self._get(
            f"{self.BASE}/subreddits/search.json",
            params={"q": query, "limit": limit},
        )
        return [
            {
                "name": s["data"].get("display_name"),
                "subscribers": s["data"].get("subscribers", 0),
                "description": (
                    s["data"].get("public_description") or ""
                )[:200],
                "url": f"/r/{s['data'].get('display_name')}",
                "active_users": s["data"].get("accounts_active", 0),
            }
            for s in data.get("data", {}).get("children", [])
        ]

    def hot(self, subreddit="all", limit=10):
        """Hot posts from a subreddit."""
        data = self._get(
            f"{self.BASE}/r/{subreddit}/hot.json",
            params={"limit": limit},
        )
        return [
            self._parse_post(p["data"])
            for p in data.get("data", {}).get("children", [])
        ]

    def top(self, subreddit="all", time_filter="week", limit=10):
        """Top posts by time period."""
        data = self._get(
            f"{self.BASE}/r/{subreddit}/top.json",
            params={"t": time_filter, "limit": limit},
        )
        return [
            self._parse_post(p["data"])
            for p in data.get("data", {}).get("children", [])
        ]

    def extract_thread(self, url, comment_limit=25):
        """Full post body + top N comments with scores."""
        clean_url = url.rstrip("/")
        if not clean_url.startswith("http"):
            clean_url = f"{self.BASE}{clean_url}"
        clean_url = re.sub(
            r'https?://(?:old\.|new\.)?reddit\.com',
            self.BASE,
            clean_url,
        )
        json_url = clean_url + ".json"
        data = self._get(
            json_url, params={"limit": comment_limit, "sort": "best"}
        )
        if not isinstance(data, list) or len(data) < 2:
            return {"error": "Unexpected response format", "url": url}
        post_data = data[0]["data"]["children"][0]["data"]
        post = self._parse_post(post_data, full_text=True)
        comments = []
        for c in data[1]["data"]["children"]:
            if c.get("kind") == "t1":
                cd = c["data"]
                comments.append({
                    "author": cd.get("author"),
                    "body": cd.get("body", ""),
                    "score": cd.get("score", 0),
                    "created_utc": cd.get("created_utc"),
                    "is_op": cd.get("author") == post.get("author"),
                    "controversiality": cd.get("controversiality", 0),
                })
        comments.sort(key=lambda x: x.get("score", 0), reverse=True)
        post["comments"] = comments[:comment_limit]
        post["comments_extracted"] = len(comments[:comment_limit])
        return post

    def research(self, query, time_filter="year", max_threads=5,
                 max_comments=25, subreddits=None,
                 auto_detect_subreddits=True, max_subreddits=3):
        """Full pipeline: detect subreddits, search, rank, extract top threads."""
        detected_subs = []
        all_posts = []

        if subreddits:
            detected_subs = [{"name": s} for s in subreddits]
        elif auto_detect_subreddits:
            detected_subs = self.find_subreddits(
                query, limit=max_subreddits + 2
            )
            detected_subs = [
                s for s in detected_subs
                if s.get("subscribers", 0) > 100
            ][:max_subreddits]

        sub_names = [s["name"] for s in detected_subs]

        # Search r/all first
        r_all_posts = self.search(
            query, sort="relevance", time_filter=time_filter, limit=15
        )
        all_posts.extend(r_all_posts)

        # Then search each detected subreddit
        for sub_name in sub_names:
            try:
                sub_posts = self.search_subreddit(
                    sub_name, query, time_filter=time_filter, limit=10
                )
                all_posts.extend(sub_posts)
            except Exception:
                pass

        # Deduplicate by URL
        seen_urls = set()
        unique_posts = []
        for p in all_posts:
            if p["url"] not in seen_urls:
                seen_urls.add(p["url"])
                unique_posts.append(p)

        # Rank by weighted engagement
        unique_posts.sort(
            key=lambda p: (
                p.get("score", 0) * 0.6
                + p.get("num_comments", 0) * 0.4
            ),
            reverse=True,
        )

        # Extract top threads
        threads = []
        for post in unique_posts[:max_threads]:
            try:
                thread = self.extract_thread(
                    post["url"], comment_limit=max_comments
                )
                threads.append(thread)
            except Exception as e:
                post["comments"] = []
                post["comments_extracted"] = 0
                post["extraction_error"] = str(e)
                threads.append(post)

        return {
            "query": query,
            "time_filter": time_filter,
            "subreddits_searched": ["all"] + sub_names,
            "subreddits_detected": detected_subs,
            "posts_found": len(unique_posts),
            "threads_extracted": len(threads),
            "threads": threads,
        }

    def _parse_post(self, data, full_text=False):
        """Parse a Reddit post data dict into a clean format."""
        text_limit = 10000 if full_text else 300
        return {
            "title": data.get("title"),
            "subreddit": data.get("subreddit"),
            "score": data.get("score", 0),
            "num_comments": data.get("num_comments", 0),
            "url": f"https://reddit.com{data.get('permalink', '')}",
            "created_utc": data.get("created_utc"),
            "selftext": (data.get("selftext") or "")[:text_limit],
            "author": data.get("author"),
            "upvote_ratio": data.get("upvote_ratio"),
            "link_url": (
                data.get("url") if not data.get("is_self") else None
            ),
        }
````

[VERIFY]
```bash
python3 -c "from scripts.reddit.client import RedditClient; print('Client loaded OK')"
```
Expected: `Client loaded OK`

---

## TEST

### Quick test

Ask Claude: "What are people saying on Reddit about Claude Code?"

Claude should use the Reddit skill, call the research pipeline, and return a summary of real Reddit threads with scores and comment highlights. If it does, the module is fully installed.

If the test takes 40-50 seconds, that's normal. The client spaces requests 6.5 seconds apart to stay within Reddit's rate limits.

---

## WHAT'S NEXT

Claude can now research anything on Reddit in real time. Some things to try:

- **Market research:** "What are people on Reddit saying about AI automation agencies?"
- **Sentiment check:** "Search Reddit for opinions on [your product/competitor] and summarise the sentiment"
- **Community discovery:** "Find the best subreddits for [your niche] and show me the top posts this month"
- **Feature research:** "What are the most common complaints about [tool/service] on Reddit?"
- **Trend spotting:** "What's trending on r/SaaS this week?"

---

> A plug-and-play module from Liam Ottley's AAA Accelerator -- the #1 AI business launch
> & AIOS program. Grab this and 15+ more at [aaaaccelerator.com](https://aaaaccelerator.com)
