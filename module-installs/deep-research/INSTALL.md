# Deep Research -- AIOS Module Installer

> A plug-and-play module from the AAA Accelerator.
> Grab this and 15+ more at [aaaaccelerator.com](https://aaaaccelerator.com)

---

## FOR CLAUDE

You are helping a user install this AIOS Module. This is a large module that installs multiple components. Follow these rules:

**Behavior:**
- Assume the user is non-technical unless they tell you otherwise
- Explain what you are doing at each step in plain English BEFORE doing it
- This module has many files. Walk through each component clearly.
- Celebrate wins: "Reddit client is installed!", "All 5 research platforms are connected!", etc.
- If something fails, do not dump error logs -- explain the problem simply and suggest the fix
- Never skip verification steps

**Pacing:**
- Do NOT rush. This is a bigger install. Pause after each major component.
- After prerequisites: "Ready to install? This will set up 5 research platforms plus the orchestrator."
- After each research client: brief confirmation
- After all clients: "All research platforms are ready. Now let's install the Deep Research orchestrator."
- After orchestrator + prompts: "Everything is installed. Let's test it."
- After test: "You're all set! Here's what you can do with Deep Research."

**Error handling:**
- If Firecrawl isn't installed: "Install the Firecrawl module first"
- If Supadata isn't installed: "Install the Supadata module first"
- If XAI_API_KEY is missing: guide to console.x.ai
- If a client test fails: isolate which one and fix it before moving on
- Never say "check the logs"

---

## OVERVIEW

This is the most powerful research capability you can add to your AIOS. Deep Research launches parallel AI agents that search across 7 platforms simultaneously, score every source for quality, cross-reference findings, and produce a critically reviewed synthesis report.

It works in phases: a fast recon agent scans all platforms to find where the signal lives. You review the recon and confirm the research plan. Then parallel topic agents (each running on Claude Opus) go 3+ levels deep on specific angles. A critic agent reviews all reports for quality issues. A synthesis agent produces the master report with confidence labels.

**What gets installed:**
- 5 research platform clients (Reddit, X-Search, Academic Papers, Podcast Search, Substack)
- 5 matching skill files (so Claude knows how to use each platform)
- The Deep Research orchestrator skill
- 4 prompt templates (recon, topic-agent, critic, synthesis)

**After install, say:** `/deep-research "your topic brain dump"` and Claude runs the whole thing.

---

## PREREQUISITES

### Python 3

```bash
python3 --version
```

Expected: `Python 3.8` or higher. If not installed: download from https://python.org

### pip

```bash
pip3 --version
```

### Install required libraries

```bash
pip3 install requests python-dotenv
```

### Firecrawl module installed

```bash
firecrawl --version
```

If this command fails, install the Firecrawl module first. Several research clients (Academic, Podcast-Search, Substack) depend on Firecrawl for web search and scraping.

### Supadata module installed

```bash
grep SUPADATA_API_KEY .env
```

Expected: your Supadata key appears. If not, install the Supadata module first. The Podcast-Search client depends on Supadata for YouTube search and transcript extraction.

[VERIFY] All four checks pass.

---

## API KEY SETUP

### XAI_API_KEY (required for X-Search)

1. Go to https://console.x.ai
2. Create an account or sign in
3. Generate an API key
4. Add to your `.env` file:

```
XAI_API_KEY=your_key_here
```

### X_BEARER_TOKEN (optional, for engagement metrics on X)

This lets X-Search pull exact like counts, retweet counts, and reply counts for tweets. Without it, you still get Grok's semantic search and synthesis, just not the raw engagement data.

1. Go to https://developer.x.com/en/portal/projects-and-apps
2. Create an app (or use existing)
3. Copy the Bearer Token
4. Add to `.env`:

```
X_BEARER_TOKEN=your_token_here
```

### OPENALEX_EMAIL (optional, recommended)

OpenAlex gives faster responses to "polite" API users who identify themselves. No account needed, just your email.

```
OPENALEX_EMAIL=your@email.com
```

[VERIFY] At minimum, `XAI_API_KEY` is set in `.env`.

Ask: "Ready to install? This will set up 5 research platforms plus the orchestrator."

---

## INSTALL

This is a multi-part install. Do each section in order.

---

### Part 1: Reddit Client

Reddit search and content extraction via public .json endpoints. No API key needed. Auto-detects relevant subreddits, searches posts, extracts full threads with scored comments.

#### Step 1.1: Create the Reddit skill

```bash
mkdir -p .claude/skills/reddit
```

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
    "subreddits_detected": [{"name": "...", "subscribers": 12000}],
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
                {"author": "...", "body": "...", "score": 45, "is_op": false}
            ]
        }
    ]
}
```

## Rate Limits

| Limit | Value |
|-------|-------|
| Unauthenticated requests | 10/min (IP-based) |
| Delay between requests | 6.5s (enforced by client) |
| Typical research() call | 5-8 requests, ~40-50 seconds |
| Max search results per query | 100 |

The client handles rate limiting automatically. If Reddit returns 429, it waits 65 seconds and retries.
````

#### Step 1.2: Create the Reddit client

```bash
mkdir -p scripts/reddit
```

Write an empty `scripts/reddit/__init__.py` file.

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
    MIN_INTERVAL = 6.5  # seconds between requests (10 req/min limit)

    def __init__(self):
        self._last_request = 0.0

    def _get(self, url, params=None):
        """Rate-limited GET returning parsed JSON."""
        elapsed = time.time() - self._last_request
        if elapsed < self.MIN_INTERVAL:
            time.sleep(self.MIN_INTERVAL - elapsed)

        resp = requests.get(url, params=params or {}, headers=self.HEADERS, timeout=30)
        self._last_request = time.time()

        if resp.status_code == 429:
            wait = 65
            print(f"Reddit rate limited. Waiting {wait}s...")
            time.sleep(wait)
            resp = requests.get(url, params=params or {}, headers=self.HEADERS, timeout=30)
            self._last_request = time.time()

        resp.raise_for_status()
        return resp.json()

    # --- Discovery ---

    def search(self, query, sort="relevance", time_filter="year", limit=15,
               subreddit="all"):
        """
        Search Reddit for posts matching a query.

        Args:
            query: Search terms
            sort: relevance, hot, top, new, comments
            time_filter: hour, day, week, month, year, all
            limit: Max results (1-100, Reddit caps at 100)
            subreddit: Subreddit to search in, default "all"

        Returns:
            List of post dicts with: title, subreddit, score, num_comments,
            url, created_utc, selftext, author, upvote_ratio
        """
        params = {
            "q": query,
            "sort": sort,
            "t": time_filter,
            "limit": min(limit, 100),
            "restrict_sr": "on" if subreddit != "all" else "off",
        }

        data = self._get(f"{self.BASE}/r/{subreddit}/search.json", params)
        posts = data.get("data", {}).get("children", [])

        return [self._parse_post(p["data"]) for p in posts]

    def search_subreddit(self, subreddit, query, sort="relevance",
                         time_filter="year", limit=10):
        """Search within a specific subreddit."""
        return self.search(query, sort=sort, time_filter=time_filter,
                           limit=limit, subreddit=subreddit)

    def find_subreddits(self, query, limit=5):
        """
        Find subreddits relevant to a topic.

        Returns:
            List of dicts with: name, subscribers, description, url
        """
        data = self._get(
            f"{self.BASE}/subreddits/search.json",
            params={"q": query, "limit": limit},
        )
        subs = data.get("data", {}).get("children", [])

        return [
            {
                "name": s["data"].get("display_name"),
                "subscribers": s["data"].get("subscribers", 0),
                "description": (s["data"].get("public_description") or "")[:200],
                "url": f"/r/{s['data'].get('display_name')}",
                "active_users": s["data"].get("accounts_active", 0),
            }
            for s in subs
        ]

    def hot(self, subreddit="all", limit=10):
        """Get hot posts from a subreddit."""
        data = self._get(
            f"{self.BASE}/r/{subreddit}/hot.json", params={"limit": limit}
        )
        return [
            self._parse_post(p["data"])
            for p in data.get("data", {}).get("children", [])
        ]

    def top(self, subreddit="all", time_filter="week", limit=10):
        """Get top posts from a subreddit."""
        data = self._get(
            f"{self.BASE}/r/{subreddit}/top.json",
            params={"t": time_filter, "limit": limit},
        )
        return [
            self._parse_post(p["data"])
            for p in data.get("data", {}).get("children", [])
        ]

    # --- Thread Extraction ---

    def extract_thread(self, url, comment_limit=25):
        """
        Extract full thread content: post body + top comments with scores.

        Args:
            url: Reddit thread URL (any format)
            comment_limit: Max comments to extract (sorted by best)

        Returns:
            Dict with full post data + comments list
        """
        clean_url = url.rstrip("/")
        if not clean_url.startswith("http"):
            clean_url = f"{self.BASE}{clean_url}"

        clean_url = re.sub(
            r'https?://(?:old\.|new\.)?reddit\.com', self.BASE, clean_url
        )
        json_url = clean_url + ".json"

        data = self._get(json_url, params={"limit": comment_limit, "sort": "best"})

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

    # --- Full Research Pipeline ---

    def research(self, query, time_filter="year", max_threads=5,
                 max_comments=25, subreddits=None,
                 auto_detect_subreddits=True, max_subreddits=3):
        """
        Full research pipeline: detect subreddits, discover posts, extract threads.

        Args:
            query: Research topic
            time_filter: hour, day, week, month, year, all
            max_threads: How many threads to extract in full (top by score)
            max_comments: Comments per thread
            subreddits: Specific subreddits to search (skips auto-detection)
            auto_detect_subreddits: Auto-find relevant subreddits
            max_subreddits: Max subreddits to auto-detect

        Returns:
            Dict with: query, subreddits_searched, posts_found, threads (with comments)
        """
        detected_subs = []
        all_posts = []

        # Step 1: Auto-detect subreddits
        if subreddits:
            detected_subs = [{"name": s} for s in subreddits]
        elif auto_detect_subreddits:
            detected_subs = self.find_subreddits(query, limit=max_subreddits + 2)
            detected_subs = [
                s for s in detected_subs if s.get("subscribers", 0) > 100
            ][:max_subreddits]

        sub_names = [s["name"] for s in detected_subs]

        # Step 2: Search r/all
        r_all_posts = self.search(
            query, sort="relevance", time_filter=time_filter, limit=15
        )
        all_posts.extend(r_all_posts)

        # Step 3: Search each detected subreddit
        for sub_name in sub_names:
            try:
                sub_posts = self.search_subreddit(
                    sub_name, query, time_filter=time_filter, limit=10
                )
                all_posts.extend(sub_posts)
            except Exception:
                pass

        # Step 4: Deduplicate and rank
        seen_urls = set()
        unique_posts = []
        for p in all_posts:
            if p["url"] not in seen_urls:
                seen_urls.add(p["url"])
                unique_posts.append(p)

        unique_posts.sort(
            key=lambda p: (
                p.get("score", 0) * 0.6 + p.get("num_comments", 0) * 0.4
            ),
            reverse=True,
        )

        # Step 5: Extract top threads
        threads = []
        for post in unique_posts[:max_threads]:
            try:
                thread = self.extract_thread(post["url"], comment_limit=max_comments)
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

    # --- Helpers ---

    def _parse_post(self, data, full_text=False):
        """Parse a Reddit post data dict into a clean structure."""
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
            "link_url": data.get("url") if not data.get("is_self") else None,
        }
````

[VERIFY]
```bash
python3 -c "from scripts.reddit.client import RedditClient; print('Reddit client loaded OK')"
```
Expected: `Reddit client loaded OK`

Reddit client is installed! One down, four to go.

---

### Part 2: X-Search Client

Two-layer X/Twitter search. Layer 1: Grok semantic search via xAI Responses API (discovers and synthesizes). Layer 2: X API v2 for raw tweet data with engagement metrics. Requires `XAI_API_KEY`.

#### Step 2.1: Create the X-Search skill

```bash
mkdir -p .claude/skills/x-search
```

Write the following file to `.claude/skills/x-search/SKILL.md`:

````markdown
---
name: x-search
description: >
  X/Twitter search and content intelligence, two-layer architecture.
  Layer 1: Grok x_search (xAI Responses API), semantic search, synthesized insights, X post citations.
  Layer 2: X API v2, raw tweet lookup with engagement metrics (likes, retweets, replies, impressions).
  Use for: what are people saying on X, X sentiment, find relevant X posts, X research,
  Twitter discussions, pull tweets, engagement metrics, X content discovery.
user-invocable: false
---

# X Search -- Two-Layer Intelligence

Grok discovers and synthesizes. X API enriches with engagement data.

## Setup

```python
from scripts.x_search.client import XSearchClient
client = XSearchClient()
```

**Env vars required:**
- `XAI_API_KEY` -- xAI API key (https://console.x.ai)
- `X_BEARER_TOKEN` -- X API v2 bearer token (optional, for engagement data)

**Models:** x_search only works with `grok-4` family. `grok-3-*` returns 400.

## Layer 1: Grok x_search (Discovery)

Semantic search across X via xAI Responses API. Returns synthesized answer + citation URLs.

```python
# Basic search
result = client.search("AI automation agencies", days_back=7)
print(result["answer"])      # Grok's synthesized response
print(result["citations"])   # List of x.com URLs

# Filter to specific accounts
result = client.search(
    "thoughts on Claude Code",
    days_back=30,
    allowed_handles=["AnthropicAI", "karpathy"],
)

# Date range
result = client.search(
    "AI agent frameworks",
    from_date="2026-03-01",
    to_date="2026-03-22",
)
```

### Search Parameters

| Parameter | Type | Notes |
|-----------|------|-------|
| `query` | str | Natural language, Grok handles semantics |
| `days_back` | int | Shortcut for from_date (overrides it) |
| `from_date` | str | `YYYY-MM-DD` |
| `to_date` | str | `YYYY-MM-DD` |
| `allowed_handles` | list | Whitelist, max 10. Mutually exclusive with excluded |
| `excluded_handles` | list | Blocklist, max 10 |
| `enable_images` | bool | Analyze images in posts |
| `enable_video` | bool | Analyze video content |

### Response Shape

```python
{
    "answer": "Grok's synthesized text response...",
    "citations": ["https://x.com/i/status/123...", "https://x.com/i/status/456..."],
    "model": "grok-4-0709",
    "usage": {"input_tokens": 7249, "output_tokens": 1718}
}
```

## Layer 2: X API v2 (Engagement Data)

Raw tweet data with exact engagement metrics. Requires `X_BEARER_TOKEN`.

```python
# Look up tweets by ID (from Grok citations)
tweets = client.lookup_tweets(["123456789", "987654321"])
for t in tweets:
    m = t.get("public_metrics", {})
    print(f"{m['like_count']} likes | {m['retweet_count']} RTs | {m['reply_count']} replies")

# Search recent tweets
result = client.search_recent("AI automation -is:retweet lang:en", max_results=20)

# User profiles
users = client.lookup_users(usernames=["AnthropicAI", "OpenAI"])
```

## Combined: Discover + Enrich

```python
result = client.discover_and_enrich("AI tools launching this week", days_back=7)
print(result["answer"])
for t in result["enriched_tweets"]:
    m = t.get("public_metrics", {})
    print(f"{m.get('like_count', 0)} likes -- {t['text'][:80]}")
```

## Rate Limits

| Layer | Limit |
|-------|-------|
| xAI Responses API | Per request billing (~$0.004-0.01/call) |
| X API v2 tweet lookup | 3,500 req / 15 min |
| X API v2 search/recent | 450 req / 15 min |
| X API v2 user lookup | 300 req / 15 min |
````

#### Step 2.2: Create the X-Search client

```bash
mkdir -p scripts/x_search
```

Write an empty `scripts/x_search/__init__.py` file.

Write the following file to `scripts/x_search/client.py`:

````python
"""
X/Twitter Search Client -- Two-layer architecture for X content discovery and data enrichment.

Layer 1: Grok x_search (xAI Responses API) -- semantic search, synthesized insights, citations
Layer 2: X API v2 -- raw tweet data, engagement metrics, user profiles

Usage:
    from scripts.x_search.client import XSearchClient

    client = XSearchClient()
    result = client.search("AI automation agencies", days_back=7)
    print(result["answer"])
"""

import json
import os
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv


# Load .env -- walk up from this file until we find it
def _find_and_load_env():
    current = Path(__file__).resolve().parent
    for _ in range(5):
        candidate = current / ".env"
        if candidate.exists():
            load_dotenv(candidate)
            return
        current = current.parent

_find_and_load_env()


class XSearchClient:
    """Two-layer X/Twitter search: Grok discovery + X API v2 data."""

    def __init__(self):
        self.xai_key = os.getenv("XAI_API_KEY")
        self.x_bearer = os.getenv("X_BEARER_TOKEN")

        if not self.xai_key:
            raise ValueError("XAI_API_KEY not set in .env")

        self.xai_base = "https://api.x.ai/v1"
        self.x_api_base = "https://api.x.com/2"

    # --- Layer 1: Grok x_search (Discovery) ---

    def search(self, query, days_back=None, from_date=None, to_date=None,
               allowed_handles=None, excluded_handles=None,
               enable_images=False, enable_video=False, model="grok-4"):
        """
        Semantic search via Grok x_search. Returns synthesized answer + citations.

        Args:
            query: Natural language search query
            days_back: Shortcut, search last N days (overrides from_date)
            from_date: ISO8601 date string (YYYY-MM-DD)
            to_date: ISO8601 date string (YYYY-MM-DD)
            allowed_handles: Only search these accounts (max 10)
            excluded_handles: Exclude these accounts (max 10)
            enable_images: Analyze images in posts
            enable_video: Analyze videos in posts
            model: Grok model to use

        Returns:
            dict with keys: answer, citations, model, usage
        """
        x_search_config = {}

        # Date handling
        if days_back:
            from_date = (
                datetime.now(timezone.utc) - timedelta(days=days_back)
            ).strftime("%Y-%m-%d")
        if from_date:
            x_search_config["from_date"] = from_date
        if to_date:
            x_search_config["to_date"] = to_date

        # Handle filters
        if allowed_handles:
            x_search_config["allowed_x_handles"] = allowed_handles[:10]
        if excluded_handles:
            x_search_config["excluded_x_handles"] = excluded_handles[:10]

        # Media understanding
        if enable_images:
            x_search_config["enable_image_understanding"] = True
        if enable_video:
            x_search_config["enable_video_understanding"] = True

        # Build tool config
        tool = {"type": "x_search"}
        if x_search_config:
            tool.update(x_search_config)

        payload = {
            "model": model,
            "input": [{"role": "user", "content": query}],
            "tools": [tool],
        }

        resp = requests.post(
            f"{self.xai_base}/responses",
            headers={
                "Authorization": f"Bearer {self.xai_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=90,
        )
        resp.raise_for_status()
        data = resp.json()

        # Extract text from Responses API output format
        answer = ""
        for item in data.get("output", []):
            if item.get("type") == "message":
                for c in item.get("content", []):
                    if c.get("type") == "output_text":
                        answer += c.get("text", "")

        return {
            "answer": answer,
            "citations": self._extract_citations_from_text(answer),
            "model": data.get("model", model),
            "usage": data.get("usage", {}),
        }

    def _extract_citations_from_text(self, text):
        """Extract X post URLs from Grok's response text."""
        urls = re.findall(r'https?://(?:x\.com|twitter\.com)/\S+', text)
        urls = [u.rstrip(".,;)\"'") for u in urls]
        return list(set(urls))

    # --- Layer 2: X API v2 (Data Enrichment) ---

    def _x_api_get(self, path, params=None):
        """Make authenticated GET request to X API v2."""
        if not self.x_bearer:
            raise ValueError(
                "X_BEARER_TOKEN not set in .env. "
                "Get one at https://developer.x.com/en/portal/projects-and-apps"
            )
        resp = requests.get(
            f"{self.x_api_base}{path}",
            headers={"Authorization": f"Bearer {self.x_bearer}"},
            params=params or {},
            timeout=30,
        )
        if resp.status_code == 429:
            reset = resp.headers.get("x-rate-limit-reset", "unknown")
            raise RuntimeError(
                f"X API rate limited. Resets at Unix timestamp {reset}. "
                f"Remaining: {resp.headers.get('x-rate-limit-remaining', '0')}"
            )
        resp.raise_for_status()
        return resp.json()

    def lookup_tweets(self, tweet_ids, include_metrics=True, include_author=True):
        """
        Look up tweets by ID with engagement metrics.

        Args:
            tweet_ids: List of tweet ID strings (max 100 per call)
            include_metrics: Include like_count, retweet_count, etc.
            include_author: Expand author user data

        Returns:
            List of tweet dicts with engagement data
        """
        if not tweet_ids:
            return []

        params = {"ids": ",".join(tweet_ids[:100])}

        tweet_fields = ["created_at", "text", "author_id", "conversation_id", "lang"]
        if include_metrics:
            tweet_fields.append("public_metrics")

        params["tweet.fields"] = ",".join(tweet_fields)

        expansions = []
        if include_author:
            expansions.append("author_id")
            params["user.fields"] = (
                "username,name,verified,public_metrics,profile_image_url"
            )

        if expansions:
            params["expansions"] = ",".join(expansions)

        data = self._x_api_get("/tweets", params)

        tweets = data.get("data", [])

        # Merge author data into tweets if expanded
        if include_author and "includes" in data:
            users_map = {u["id"]: u for u in data["includes"].get("users", [])}
            for tweet in tweets:
                author_id = tweet.get("author_id")
                if author_id and author_id in users_map:
                    tweet["author"] = users_map[author_id]

        return tweets

    def search_recent(self, query, max_results=10, sort_order="relevancy",
                      start_time=None, end_time=None, next_token=None):
        """
        Search recent tweets via X API v2 with raw engagement data.

        Args:
            query: Search query with operators (max 512 chars)
            max_results: 10-100 per request
            sort_order: 'recency' or 'relevancy'
            start_time: ISO8601 (e.g. '2026-03-14T00:00:00Z')
            end_time: ISO8601
            next_token: Pagination token from previous response

        Returns:
            dict with keys: tweets (list), meta (pagination info)
        """
        params = {
            "query": query[:512],
            "max_results": min(max_results, 100),
            "sort_order": sort_order,
            "tweet.fields": "created_at,text,author_id,public_metrics,conversation_id,lang",
            "expansions": "author_id",
            "user.fields": "username,name,verified,public_metrics",
        }
        if start_time:
            params["start_time"] = start_time
        if end_time:
            params["end_time"] = end_time
        if next_token:
            params["next_token"] = next_token

        data = self._x_api_get("/tweets/search/recent", params)

        tweets = data.get("data", [])

        # Merge author data
        if "includes" in data:
            users_map = {u["id"]: u for u in data["includes"].get("users", [])}
            for tweet in tweets:
                author_id = tweet.get("author_id")
                if author_id and author_id in users_map:
                    tweet["author"] = users_map[author_id]

        return {
            "tweets": tweets,
            "meta": data.get("meta", {}),
        }

    def lookup_users(self, usernames=None, user_ids=None):
        """
        Look up X user profiles with follower counts.

        Args:
            usernames: List of usernames (without @, max 100)
            user_ids: List of user ID strings (max 100)

        Returns:
            List of user dicts with public_metrics
        """
        params = {
            "user.fields": (
                "created_at,description,public_metrics,verified,"
                "verified_type,profile_image_url,url,location"
            ),
        }

        if usernames:
            params["usernames"] = ",".join(usernames[:100])
            path = "/users/by"
        elif user_ids:
            params["ids"] = ",".join(user_ids[:100])
            path = "/users"
        else:
            return []

        data = self._x_api_get(path, params)
        return data.get("data", [])

    # --- Combined Workflows ---

    def discover_and_enrich(self, query, days_back=7, max_enrich=10,
                            **search_kwargs):
        """
        Full pipeline: Grok discovers relevant posts, X API enriches with engagement data.

        Args:
            query: Research query
            days_back: How far back to search
            max_enrich: Max tweets to enrich via X API (saves credits)

        Returns:
            dict with: answer, citations, enriched_tweets (with metrics)
        """
        # Step 1: Grok discovers
        discovery = self.search(query, days_back=days_back, **search_kwargs)

        # Step 2: Extract tweet IDs from citation URLs
        tweet_ids = self._extract_tweet_ids(discovery["citations"])

        # Step 3: Enrich with X API (if bearer token available)
        enriched = []
        if tweet_ids and self.x_bearer:
            enriched = self.lookup_tweets(tweet_ids[:max_enrich])

        return {
            "answer": discovery["answer"],
            "citations": discovery["citations"],
            "enriched_tweets": enriched,
            "usage": discovery["usage"],
        }

    def _extract_tweet_ids(self, urls):
        """Extract tweet IDs from X/Twitter URLs."""
        ids = []
        for url in urls:
            match = re.search(r'/status/(\d+)', url)
            if match:
                ids.append(match.group(1))
        return list(set(ids))
````

[VERIFY]
```bash
python3 -c "from scripts.x_search.client import XSearchClient; print('X-Search client loaded OK')"
```
Expected: `X-Search client loaded OK` (will fail if XAI_API_KEY is not set, which is expected before env setup)

X-Search client is installed! Two down, three to go.

---

### Part 3: Academic Client

Academic paper search across 250M+ papers via OpenAlex. Finds free PDFs of paywalled papers via Unpaywall. Scrapes full article text via Firecrawl. Zero auth required.

#### Step 3.1: Create the Academic skill

```bash
mkdir -p .claude/skills/academic
```

Write the following file to `.claude/skills/academic/SKILL.md`:

````markdown
---
name: academic
description: >
  Academic paper search and content extraction via OpenAlex (250M+ papers).
  Search scholarly articles, find research papers, get abstracts, citation graphs,
  find free PDFs of paywalled papers. Academic research, scientific papers,
  peer-reviewed articles, literature review, citations, scholarly search.
user-invocable: false
---

# Academic Paper Search

OpenAlex-powered search across 250M+ scholarly works. Zero auth required. Includes Unpaywall for finding free PDFs and citation graph traversal.

## Setup

```python
from scripts.academic.client import AcademicClient
client = AcademicClient()
```

**No env vars needed.** OpenAlex and Unpaywall are free, no auth. Set `OPENALEX_EMAIL` in `.env` for faster responses (polite access pool).

## Method Reference

| Method | What | Source |
|--------|------|--------|
| `search(query, limit, year_from, ...)` | Search 250M+ papers by topic | OpenAlex |
| `get_paper(doi=)` | Get paper by DOI | OpenAlex |
| `get_citations(openalex_id, limit)` | Papers that cite a given paper | OpenAlex |
| `find_free_pdf(doi)` | Find free legal PDF of paywalled paper | Unpaywall |
| `get_full_text(url)` | Scrape article page for full text | Firecrawl |
| `research(query, max_papers, ...)` | Full pipeline: search, enrich, extract | All |

## Full Research Pipeline

```python
result = client.research(
    "AI code generation testing",
    max_papers=5,
    year_from=2024,
    find_free_pdfs=True,
    extract_full_text=False,
)

for p in result["papers"]:
    print(f"[{p['cited_by']} cites] {p['title']}")
    print(f"  {', '.join(a['name'] for a in p['authors'][:2])}")
```

## Search Parameters

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `query` | str | required | Search topic |
| `limit` | int | 10 | Max 200 per page |
| `year_from` | int | None | Minimum publication year |
| `year_to` | int | None | Maximum publication year |
| `open_access_only` | bool | False | Only OA papers |
| `cited_by_min` | int | None | Minimum citation count |
| `sort` | str | `relevance_score:desc` | Also: `cited_by_count:desc`, `publication_date:desc` |

## Paper Fields

| Field | Type | What |
|-------|------|------|
| `title` | str | Paper title |
| `abstract` | str | Reconstructed from inverted index |
| `year` | int | Publication year |
| `cited_by` | int | Citation count |
| `doi` | str | DOI (without https://doi.org/ prefix) |
| `open_access` | bool | Is it freely accessible? |
| `oa_url` | str | Open access URL (if available) |
| `authors` | list | `[{"name": "...", "institution": "..."}]` |
| `venue` | str | Journal/conference name |

## Rate Limits

| API | Limit |
|-----|-------|
| OpenAlex | 100 req/s (shared pool) |
| Unpaywall | 100K req/day |
| Client delay | 200ms between requests |
````

#### Step 3.2: Create the Academic client

```bash
mkdir -p scripts/academic
```

Write an empty `scripts/academic/__init__.py` file.

Write the following file to `scripts/academic/client.py`:

````python
"""
Academic Paper Search Client -- OpenAlex-powered research engine.

Primary: OpenAlex API (250M+ papers, excellent search quality, zero auth)
Supplement: Unpaywall (find free PDFs of paywalled papers via DOI)
Content: Firecrawl (scrape full article text from publisher pages)

Usage:
    from scripts.academic.client import AcademicClient
    client = AcademicClient()
    papers = client.search("autonomous AI coding agents", limit=10, year_from=2024)
"""

import json
import os
import re
import subprocess
import time
from pathlib import Path

import requests
from dotenv import load_dotenv


def _find_and_load_env():
    current = Path(__file__).resolve().parent
    for _ in range(5):
        candidate = current / ".env"
        if candidate.exists():
            load_dotenv(candidate)
            return
        current = current.parent

_find_and_load_env()

# Rate limiter
_last_request = 0.0


def _rate_limit(delay=0.2):
    """Polite delay between requests."""
    global _last_request
    elapsed = time.time() - _last_request
    if elapsed < delay:
        time.sleep(delay - elapsed)
    _last_request = time.time()


def _reconstruct_abstract(inverted_index):
    """Reconstruct abstract from OpenAlex's inverted index format."""
    if not inverted_index:
        return ""
    word_positions = []
    for word, positions in inverted_index.items():
        for pos in positions:
            word_positions.append((pos, word))
    word_positions.sort()
    return " ".join(w for _, w in word_positions)


class AcademicClient:
    """Academic paper search via OpenAlex + Unpaywall + Firecrawl."""

    OPENALEX_BASE = "https://api.openalex.org"
    UNPAYWALL_BASE = "https://api.unpaywall.org/v2"

    def __init__(self):
        self.email = os.getenv("OPENALEX_EMAIL", "user@example.com")
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": f"AIOS-Research/1.0 (mailto:{self.email})",
            "Accept": "application/json",
        })

    # --- OpenAlex: Search & Discovery ---

    def search(self, query, limit=10, year_from=None, year_to=None,
               open_access_only=False, sort="relevance_score:desc",
               cited_by_min=None):
        """
        Search for academic papers via OpenAlex.

        Args:
            query: Search topic
            limit: Max results (up to 200 per page)
            year_from: Filter papers published from this year
            year_to: Filter papers published up to this year
            open_access_only: Only return open access papers
            sort: Sort order (relevance_score:desc, cited_by_count:desc, publication_date:desc)
            cited_by_min: Minimum citation count filter

        Returns:
            List of paper dicts with title, abstract, authors, year, citations, DOI, OA status
        """
        _rate_limit()

        filters = []
        if year_from:
            filters.append(f"from_publication_date:{year_from}-01-01")
        if year_to:
            filters.append(f"to_publication_date:{year_to}-12-31")
        if open_access_only:
            filters.append("open_access.is_oa:true")
        if cited_by_min:
            filters.append(f"cited_by_count:>{cited_by_min}")

        params = {
            "search": query,
            "per_page": min(limit, 200),
            "sort": sort,
        }
        if filters:
            params["filter"] = ",".join(filters)

        try:
            resp = self.session.get(
                f"{self.OPENALEX_BASE}/works", params=params, timeout=15
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"OpenAlex search failed: {e}")
            return []

        results = data.get("results", [])

        papers = []
        for r in results:
            abstract = _reconstruct_abstract(r.get("abstract_inverted_index", {}))

            # Extract authors
            authors = []
            for a in r.get("authorships", [])[:5]:
                name = a.get("author", {}).get("display_name", "")
                institution = ""
                insts = a.get("institutions", [])
                if insts:
                    institution = insts[0].get("display_name", "")
                if name:
                    authors.append({"name": name, "institution": institution})

            # Open access info
            oa = r.get("open_access", {})
            oa_url = oa.get("oa_url", "")

            # Primary location (journal/venue)
            location = r.get("primary_location", {}) or {}
            source = location.get("source", {}) or {}
            venue = source.get("display_name", "")

            doi = r.get("doi", "")
            if doi and doi.startswith("https://doi.org/"):
                doi_short = doi.replace("https://doi.org/", "")
            else:
                doi_short = doi

            papers.append({
                "title": r.get("title", ""),
                "abstract": abstract,
                "year": r.get("publication_year"),
                "cited_by": r.get("cited_by_count", 0),
                "doi": doi_short,
                "doi_url": doi,
                "open_access": oa.get("is_oa", False),
                "oa_url": oa_url,
                "authors": authors,
                "venue": venue,
                "type": r.get("type", ""),
                "openalex_id": r.get("id", ""),
            })

        return papers

    def get_paper(self, doi=None, openalex_id=None):
        """Get a specific paper by DOI or OpenAlex ID."""
        _rate_limit()

        if doi:
            url = f"{self.OPENALEX_BASE}/works/doi:{doi}"
        elif openalex_id:
            url = f"{self.OPENALEX_BASE}/works/{openalex_id}"
        else:
            return None

        try:
            resp = self.session.get(url, timeout=15)
            if resp.status_code != 200:
                return None
            r = resp.json()
        except Exception:
            return None

        abstract = _reconstruct_abstract(r.get("abstract_inverted_index", {}))
        authors = [
            {"name": a.get("author", {}).get("display_name", "")}
            for a in r.get("authorships", [])[:10]
        ]

        oa = r.get("open_access", {})
        location = r.get("primary_location", {}) or {}
        source = location.get("source", {}) or {}

        doi_val = r.get("doi", "")
        if doi_val and doi_val.startswith("https://doi.org/"):
            doi_val = doi_val.replace("https://doi.org/", "")

        return {
            "title": r.get("title", ""),
            "abstract": abstract,
            "year": r.get("publication_year"),
            "cited_by": r.get("cited_by_count", 0),
            "doi": doi_val,
            "open_access": oa.get("is_oa", False),
            "oa_url": oa.get("oa_url", ""),
            "authors": authors,
            "venue": source.get("display_name", ""),
            "type": r.get("type", ""),
            "referenced_works_count": len(r.get("referenced_works", [])),
            "related_works": r.get("related_works", [])[:5],
        }

    def get_citations(self, openalex_id, limit=10):
        """Get papers that cite a given paper."""
        _rate_limit()

        try:
            resp = self.session.get(
                f"{self.OPENALEX_BASE}/works",
                params={
                    "filter": f"cites:{openalex_id}",
                    "per_page": limit,
                    "sort": "cited_by_count:desc",
                },
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception:
            return []

        return [
            {
                "title": r.get("title", ""),
                "year": r.get("publication_year"),
                "cited_by": r.get("cited_by_count", 0),
                "doi": (r.get("doi", "") or "").replace("https://doi.org/", ""),
                "openalex_id": r.get("id", ""),
            }
            for r in data.get("results", [])
        ]

    # --- Unpaywall: Free PDF Finder ---

    def find_free_pdf(self, doi):
        """Find a free legal PDF for a paywalled paper via Unpaywall."""
        _rate_limit()

        clean_doi = doi.replace("https://doi.org/", "")
        try:
            resp = self.session.get(
                f"{self.UNPAYWALL_BASE}/{clean_doi}",
                params={"email": self.email},
                timeout=10,
            )
            if resp.status_code != 200:
                return None
            data = resp.json()
            best = data.get("best_oa_location", {}) or {}
            return best.get("url_for_pdf") or best.get("url")
        except Exception:
            return None

    # --- Full Text Extraction ---

    def get_full_text(self, url):
        """Scrape full article text from a URL via Firecrawl."""
        try:
            result = subprocess.run(
                ["firecrawl", "scrape", url, "--json"],
                capture_output=True, text=True, timeout=30,
                cwd=str(Path(__file__).resolve().parent.parent.parent),
            )
            if result.returncode != 0:
                return None
            data = json.loads(result.stdout)
            if isinstance(data, dict):
                return data.get("markdown", data.get("content", ""))
            elif isinstance(data, list) and data:
                return data[0].get("markdown", "")
            return None
        except Exception:
            return None

    # --- Combined Research Pipeline ---

    def research(self, query, max_papers=5, search_limit=15, year_from=2024,
                 extract_full_text=False, find_free_pdfs=True):
        """
        Full research pipeline: search, enrich with free PDFs, optionally extract full text.

        Args:
            query: Research topic
            max_papers: How many papers to fully process
            search_limit: How many search results to consider
            year_from: Minimum publication year
            extract_full_text: Scrape full article text (slower, uses Firecrawl credits)
            find_free_pdfs: Look up free PDFs via Unpaywall for paywalled papers

        Returns:
            dict with: query, papers (list with abstracts, PDFs, optionally full text)
        """
        # Step 1: Search
        papers = self.search(query, limit=search_limit, year_from=year_from)

        # Step 2: Take top N
        top_papers = papers[:max_papers]

        # Step 3: Enrich with free PDFs
        if find_free_pdfs:
            for paper in top_papers:
                if not paper.get("open_access") and paper.get("doi"):
                    pdf_url = self.find_free_pdf(paper["doi"])
                    if pdf_url:
                        paper["free_pdf_url"] = pdf_url
                        paper["open_access"] = True

        # Step 4: Optionally extract full text
        if extract_full_text:
            for paper in top_papers:
                url = paper.get("oa_url") or paper.get("free_pdf_url")
                if url:
                    text = self.get_full_text(url)
                    if text:
                        paper["full_text"] = text[:50000]
                        paper["full_text_length"] = len(text)

        return {
            "query": query,
            "total_found": len(papers),
            "papers_processed": len(top_papers),
            "papers": top_papers,
        }
````

[VERIFY]
```bash
python3 -c "from scripts.academic.client import AcademicClient; print('Academic client loaded OK')"
```
Expected: `Academic client loaded OK`

Academic client is installed! Three down, two to go.

---

### Part 4: Podcast-Search Client

Podcast episode discovery, quality ranking, and transcript extraction. Two-layer: Firecrawl discovers episodes across all platforms, Supadata searches YouTube and pulls transcripts. Quality scoring ranks episodes 0-100 based on views, duration, authority, and freshness.

#### Step 4.1: Create the Podcast-Search skill

```bash
mkdir -p .claude/skills/podcast-search
```

Write the following file to `.claude/skills/podcast-search/SKILL.md`:

````markdown
---
name: podcast-search
description: >
  Podcast episode search, quality ranking, and transcript extraction.
  Find podcast episodes on any topic, rank by quality (views, duration, authority),
  pull full transcripts from YouTube. Two-layer: Firecrawl discovers across all platforms,
  Supadata searches YouTube and extracts transcripts.
  Podcast research, find podcast episodes, podcast interviews, podcast transcripts,
  podcast discovery, what podcasts discuss, podcast about, episode search.
user-invocable: false
---

# Podcast Episode Search & Transcripts

Find podcast episodes on any topic across all platforms, rank by quality, and extract full transcripts from YouTube.

## Setup

```python
from scripts.podcast_search.client import PodcastSearchClient
client = PodcastSearchClient()
```

**Env vars:** Uses `FIRECRAWL_API_KEY` and `SUPADATA_API_KEY` (both already configured).

## Method Reference

| Method | What | Layer |
|--------|------|-------|
| `search(query, limit)` | Find episodes across all platforms via Google | Firecrawl |
| `youtube_search(query, limit, upload_date, duration)` | Find podcast interviews on YouTube | Supadata |
| `get_transcript(url)` | Pull full transcript from YouTube URL | Supadata |
| `research(query, max_transcripts, ...)` | Full pipeline: discover, rank, extract | Both |

## Full Research Pipeline

```python
result = client.research(
    "AI coding agents software engineering",
    max_transcripts=3,
    search_limit=10,
    youtube_limit=10,
    min_quality_score=55,
    upload_date="year",
)

print(f"Discovered {result['total_discovered']} episodes")
print(f"Extracted {result['transcripts_extracted']} transcripts")

for ep in result["episodes"][:5]:
    has_t = "transcript" in ep
    print(f"[score:{ep['quality_score']:.0f}] {ep['title'][:60]}")
    if has_t:
        print(f"  Transcript: {ep['transcript_length']:,} chars")
```

## Quality Scoring (0-100)

| Signal | Score Impact |
|--------|-------------|
| Views > 1M | +25 |
| Views > 500K | +20 |
| Views > 100K | +15 |
| Views > 50K | +10 |
| Duration 20-120 min | +10 |
| Known authority source | +10 |
| YouTube source | +5 |
| Noise signal (#shorts, clip) | -20 |

**Authority sources:** Lex Fridman, Dwarkesh, Y Combinator, a16z, No Priors, All-In, Acquired, My First Million, Lenny, Hormozi, Huberman, Tim Ferriss, Joe Rogan

## YouTube Search Parameters

| Parameter | Type | Default | Values |
|-----------|------|---------|--------|
| `upload_date` | str | `"year"` | `hour`, `today`, `week`, `month`, `year` |
| `duration` | str | `"long"` | `short` (<4min), `medium` (4-20min), `long` (>20min) |
| `limit` | int | 10 | Max results |
````

#### Step 4.2: Create the Podcast-Search client

```bash
mkdir -p scripts/podcast_search
```

Write an empty `scripts/podcast_search/__init__.py` file.

Write the following file to `scripts/podcast_search/client.py`:

Note: This client uses a hyphenated directory name (`podcast-search`) but Python imports use underscores. The deep research agents import it as `from scripts.podcast_search.client import PodcastSearchClient`. Create a symlink or use the import helper shown in the code.

````python
"""
Podcast Search & Transcript Client -- discovery + quality filtering + extraction.

Two-layer architecture:
  Layer 1 (Discovery): Firecrawl Google search + Supadata YouTube search
  Layer 2 (Extraction): Supadata transcript_text() for YouTube episodes

Usage:
    from scripts.podcast_search.client import PodcastSearchClient
    client = PodcastSearchClient()
    result = client.research("AI coding agents", max_transcripts=3)
"""

import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv


def _find_and_load_env():
    current = Path(__file__).resolve().parent
    for _ in range(5):
        candidate = current / ".env"
        if candidate.exists():
            load_dotenv(candidate)
            return
        current = current.parent

_find_and_load_env()

_SCRIPTS_DIR = Path(__file__).resolve().parent.parent
_ROOT_DIR = _SCRIPTS_DIR.parent


def _get_supadata():
    """Load SupadataClient from the workspace."""
    # Try workspace scripts/utils path first
    sys.path.insert(0, str(_SCRIPTS_DIR))
    try:
        from utils.supadata import SupadataClient
        return SupadataClient()
    except ImportError:
        pass
    # Try root-level supadata.py
    sys.path.insert(0, str(_ROOT_DIR))
    try:
        from supadata import SupadataClient
        return SupadataClient()
    except ImportError:
        raise ImportError(
            "SupadataClient not found. Install the Supadata module first. "
            "It should be at scripts/utils/supadata.py or supadata.py in your workspace root."
        )


# --- Quality Scoring ---

def _score_episode(episode):
    """
    Score a podcast episode 0-100 for research quality.

    Signals:
    - View count (YouTube): Higher views = more reach, likely higher quality guest
    - Duration: 20-120 min is the sweet spot for interviews
    - Source authority: Known podcast networks score higher
    - Freshness: Recent episodes score higher for fast-moving topics
    """
    score = 50.0  # baseline

    # View count signal
    views = episode.get("views", 0)
    if isinstance(views, str):
        views = int(views) if views.isdigit() else 0
    if views > 1_000_000:
        score += 25
    elif views > 500_000:
        score += 20
    elif views > 100_000:
        score += 15
    elif views > 50_000:
        score += 10
    elif views > 10_000:
        score += 5
    elif views > 0:
        score += 2

    # Duration sweet spot (20-120 min = interview territory)
    duration_min = episode.get("duration_min", 0)
    if 20 <= duration_min <= 120:
        score += 10
    elif 10 <= duration_min < 20:
        score += 3
    elif duration_min > 120:
        score += 5

    # Source type bonus
    source = episode.get("source", "")
    if source == "youtube":
        score += 5
    elif source == "apple_podcasts":
        score += 3

    # Channel/show authority
    title_lower = (
        episode.get("title", "") + " "
        + episode.get("show", "") + " "
        + episode.get("channel", "")
    ).lower()
    authority_signals = [
        "lex fridman", "dwarkesh", "y combinator", "a16z", "no priors",
        "all-in", "acquired", "starter story", "my first million",
        "lenny", "pragmatic engineer", "software engineering daily",
        "changelog", "syntax", "shop talk", "js party", "real python",
        "talk python", "corecursive", "scale", "gradient dissent",
        "practical ai", "machine learning street talk", "replit",
        "hormozi", "huberman", "tim ferriss", "joe rogan",
    ]
    for signal in authority_signals:
        if signal in title_lower:
            score += 10
            break

    # Penalize noise
    noise_signals = ["shorts", "tiktok", "#shorts", "60 seconds", "in 1 minute", "clip"]
    for noise in noise_signals:
        if noise in title_lower:
            score -= 20
            break

    return min(max(score, 0), 100)


# --- Client ---

class PodcastSearchClient:
    """Podcast episode discovery + quality ranking + transcript extraction."""

    def __init__(self):
        self._supadata = None

    @property
    def supadata(self):
        if self._supadata is None:
            self._supadata = _get_supadata()
        return self._supadata

    # --- Discovery Layer 1: Firecrawl Google Search ---

    def search(self, query, limit=10):
        """
        Search Google for podcast episodes on a topic via Firecrawl.
        Finds episodes across Apple Podcasts, Spotify, YouTube, and podcast sites.

        Returns ranked list of episodes with quality scores.
        """
        try:
            result = subprocess.run(
                [
                    "firecrawl", "search",
                    f"{query} podcast episode interview",
                    "--limit", str(limit), "--json",
                ],
                capture_output=True, text=True, timeout=60,
                cwd=str(_ROOT_DIR),
            )
            if result.returncode != 0:
                return []

            data = json.loads(result.stdout)
            items = []
            if isinstance(data, dict):
                web = data.get("data", {}).get("web", data.get("results", []))
                if isinstance(web, list):
                    items = web
            elif isinstance(data, list):
                items = data

            episodes = []
            for item in items[:limit]:
                url = item.get("url", item.get("metadata", {}).get("sourceURL", ""))
                title = item.get("title", item.get("metadata", {}).get("title", ""))
                desc = item.get(
                    "description",
                    item.get("metadata", {}).get("description", ""),
                )

                # Classify source
                source = "web"
                if "youtube.com" in url or "youtu.be" in url:
                    source = "youtube"
                elif "podcasts.apple.com" in url:
                    source = "apple_podcasts"
                elif "spotify.com" in url:
                    source = "spotify"
                elif "podcast" in url.lower():
                    source = "podcast_site"

                # Extract YouTube video ID if applicable
                yt_id = ""
                if source == "youtube":
                    match = re.search(
                        r'(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})', url
                    )
                    if match:
                        yt_id = match.group(1)

                ep = {
                    "title": title,
                    "url": url,
                    "description": desc[:300] if desc else "",
                    "source": source,
                    "youtube_id": yt_id,
                    "show": "",
                    "channel": "",
                    "views": 0,
                    "duration_min": 0,
                }
                ep["quality_score"] = _score_episode(ep)
                episodes.append(ep)

            episodes.sort(key=lambda x: x["quality_score"], reverse=True)
            return episodes

        except Exception as e:
            print(f"Firecrawl search failed: {e}")
            return []

    # --- Discovery Layer 2: YouTube via Supadata ---

    def youtube_search(self, query, limit=10, upload_date="year", duration="long"):
        """
        Search YouTube for podcast interviews on a topic.

        Args:
            query: Topic to search
            limit: Max results
            upload_date: hour, today, week, month, year
            duration: short (<4min), medium (4-20min), long (>20min)

        Returns ranked list with quality scores, view counts, and YouTube IDs.
        """
        try:
            results = self.supadata.youtube_search(
                f"{query} podcast interview",
                upload_date=upload_date,
                sort_by="views",
                duration=duration,
                limit=limit,
            )
            items = results.get("results", []) if isinstance(results, dict) else []

            episodes = []
            for item in items:
                vid_id = item.get("id", item.get("videoId", ""))
                channel = item.get("channelTitle", "")
                if isinstance(channel, dict):
                    channel = channel.get("name", "")

                views = item.get("viewCount", item.get("views", 0))
                if isinstance(views, str):
                    views = int(views) if views.isdigit() else 0

                # Parse duration
                duration_val = item.get("duration", "")
                duration_min = 0
                if isinstance(duration_val, str) and ":" in duration_val:
                    parts = duration_val.split(":")
                    if len(parts) == 3:
                        duration_min = int(parts[0]) * 60 + int(parts[1])
                    elif len(parts) == 2:
                        duration_min = int(parts[0])
                elif isinstance(duration_val, (int, float)):
                    duration_min = (
                        int(duration_val / 60) if duration_val > 1000
                        else int(duration_val)
                    )

                ep = {
                    "title": item.get("title", ""),
                    "url": f"https://youtube.com/watch?v={vid_id}",
                    "youtube_id": vid_id,
                    "channel": channel,
                    "views": views,
                    "duration_min": duration_min,
                    "published": item.get("publishedAt", item.get("published", "")),
                    "source": "youtube",
                    "show": channel,
                    "description": item.get("description", "")[:300],
                }
                ep["quality_score"] = _score_episode(ep)
                episodes.append(ep)

            episodes.sort(key=lambda x: x["quality_score"], reverse=True)
            return episodes

        except Exception as e:
            print(f"YouTube search failed: {e}")
            return []

    # --- Transcript Extraction ---

    def get_transcript(self, url):
        """
        Get transcript from a YouTube video URL via Supadata.
        Returns plain text transcript or None.
        """
        try:
            text = self.supadata.transcript_text(url)
            return text
        except Exception as e:
            print(f"Transcript extraction failed for {url}: {e}")
            return None

    # --- Combined Research Pipeline ---

    def research(self, query, max_transcripts=3, search_limit=10,
                 youtube_limit=10, min_quality_score=55, upload_date="year"):
        """
        Full pipeline: discover episodes, rank by quality, extract transcripts.

        1. Firecrawl finds episodes across all platforms
        2. YouTube search finds high-view podcast interviews
        3. Merge + deduplicate + rank by quality score
        4. Extract transcripts from top YouTube results

        Args:
            query: Research topic
            max_transcripts: How many transcripts to pull
            search_limit: Firecrawl search results
            youtube_limit: YouTube search results
            min_quality_score: Minimum score to consider for transcripts
            upload_date: YouTube recency filter

        Returns dict with all discovered episodes + extracted transcripts.
        """
        # Step 1: Dual discovery
        firecrawl_results = self.search(query, limit=search_limit)
        youtube_results = self.youtube_search(
            query, limit=youtube_limit, upload_date=upload_date
        )

        # Step 2: Merge and deduplicate
        all_episodes = []
        seen_ids = set()
        seen_urls = set()

        for ep in youtube_results + firecrawl_results:
            yt_id = ep.get("youtube_id", "")
            url = ep.get("url", "")

            if yt_id and yt_id in seen_ids:
                continue
            if url and url in seen_urls:
                continue

            if yt_id:
                seen_ids.add(yt_id)
            if url:
                seen_urls.add(url)

            all_episodes.append(ep)

        # Step 3: Sort by quality score
        all_episodes.sort(key=lambda x: x.get("quality_score", 0), reverse=True)

        # Step 4: Extract transcripts from top YouTube episodes
        transcripts_extracted = 0
        for ep in all_episodes:
            if transcripts_extracted >= max_transcripts:
                break
            if ep.get("quality_score", 0) < min_quality_score:
                break
            if ep.get("source") != "youtube" or not ep.get("youtube_id"):
                continue

            transcript = self.get_transcript(ep["url"])
            if transcript:
                ep["transcript"] = transcript
                ep["transcript_length"] = len(transcript)
                transcripts_extracted += 1

        return {
            "query": query,
            "total_discovered": len(all_episodes),
            "transcripts_extracted": transcripts_extracted,
            "episodes": all_episodes,
        }
````

Note about the import path: The directory is `scripts/podcast-search/` (hyphen) but Python imports use underscores. Create a symlink so both work:

```bash
cd scripts && ln -sf podcast-search podcast_search && cd ..
```

[VERIFY]
```bash
python3 -c "
import sys; sys.path.insert(0, '.')
from scripts.podcast_search.client import PodcastSearchClient
print('Podcast-Search client loaded OK')
" 2>/dev/null || python3 -c "
import sys; sys.path.insert(0, '.')
import importlib.util
spec = importlib.util.spec_from_file_location('client', 'scripts/podcast_search/client.py')
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
print('Podcast-Search client loaded OK')
"
```

Podcast-Search client is installed! Four down, one to go.

---

### Part 5: Substack Client

Substack search and content extraction. Two-layer: Firecrawl discovers posts via Google search, Substack's undocumented API extracts full article content with metadata. Zero auth required.

#### Step 5.1: Create the Substack skill

```bash
mkdir -p .claude/skills/substack
```

Write the following file to `.claude/skills/substack/SKILL.md`:

````markdown
---
name: substack
description: >
  Substack search and content extraction. Two-layer: Firecrawl discovers posts via Google,
  Substack undocumented API extracts full article content and metadata.
  Search Substack, find newsletters, read Substack articles, newsletter research,
  Substack publications, thought leadership, newsletter content, expert analysis.
  No API key needed. Zero auth.
user-invocable: false
---

# Substack Search & Content Extraction

Two-layer architecture: Firecrawl discovers Substack posts via Google search, Substack's undocumented API extracts full article content with metadata. Zero auth required.

## Setup

```python
from scripts.substack.client import SubstackClient
client = SubstackClient()
```

**No env vars needed.** Uses Firecrawl (already configured) for search, Substack's public endpoints for content.

## Method Reference

| Method | What | Layer |
|--------|------|-------|
| `search(query, limit)` | Find Substack posts on a topic via Google | Firecrawl |
| `list_posts(publication, limit, sort)` | List posts from a known publication | Substack API |
| `get_post(publication, slug, as_text)` | Get full post content + metadata | Substack API |
| `discover_publications(query, limit)` | Find publications writing about a topic | Firecrawl |
| `research(query, max_posts, search_limit)` | Full pipeline: search, discover, extract | Both |

## Full Research Pipeline

```python
result = client.research(
    "AI product management",
    max_posts=5,
    search_limit=10,
)

for p in result["extracted_posts"]:
    print(f"[{p['publication']}] {p['title']}")
    print(f"  {p['wordcount']} words")
    print(f"  {p['body'][:300]}...")
```

### Response Shape

```python
{
    "query": "AI product management",
    "search_results_count": 10,
    "extracted_count": 5,
    "extracted_posts": [
        {
            "title": "How to write specs for AI agents",
            "slug": "how-to-write-specs",
            "date": "2026-02-14T...",
            "body": "full plain text content...",
            "wordcount": 7093,
            "reactions": {"heart": 245},
            "comment_count": 18,
            "publication": "addyo",
            "url": "https://addyo.substack.com/p/how-to-write-specs",
        }
    ]
}
```

## Rate Limits

| Layer | Limit |
|-------|-------|
| Firecrawl search | Per Firecrawl plan credits |
| Substack API | ~10-20 req/min before 429 |
| Client delay | 2s between Substack API calls |
````

#### Step 5.2: Create the Substack client

```bash
mkdir -p scripts/substack
```

Write an empty `scripts/substack/__init__.py` file.

Write the following file to `scripts/substack/client.py`:

````python
"""
Substack Search & Content Client -- Two-layer architecture.

Layer 1: Firecrawl (discovery) -- search Google for Substack content via site:substack.com
Layer 2: Substack undocumented API (extraction) -- pull full post content, archives, metadata

Usage:
    from scripts.substack.client import SubstackClient
    client = SubstackClient()
    results = client.search("AI coding agents")
"""

import json
import os
import re
import subprocess
import time
from datetime import datetime, timezone
from html import unescape
from pathlib import Path

import requests
from dotenv import load_dotenv


# Load .env
def _find_and_load_env():
    current = Path(__file__).resolve().parent
    for _ in range(5):
        candidate = current / ".env"
        if candidate.exists():
            load_dotenv(candidate)
            return
        current = current.parent

_find_and_load_env()

# Rate limiter for Substack API
_last_substack_request = 0.0


def _rate_limit(min_delay=2.0):
    """Enforce minimum delay between Substack API requests."""
    global _last_substack_request
    elapsed = time.time() - _last_substack_request
    if elapsed < min_delay:
        time.sleep(min_delay - elapsed)
    _last_substack_request = time.time()


def _strip_html(html):
    """Convert HTML to clean plain text."""
    if not html:
        return ""
    text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
    text = re.sub(r'<br\s*/?>', '\n', text)
    text = re.sub(r'</p>', '\n\n', text)
    text = re.sub(r'</h[1-6]>', '\n\n', text)
    text = re.sub(r'</li>', '\n', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = unescape(text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


class SubstackClient:
    """Two-layer Substack search: Firecrawl discovery + Substack API extraction."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36"
            ),
            "Accept": "application/json",
        })

    # --- Layer 1: Firecrawl Discovery ---

    def search(self, query, limit=10):
        """
        Search for Substack posts on a topic via Firecrawl + Google.

        Args:
            query: Search topic
            limit: Max results (default 10)

        Returns:
            List of dicts with: title, url, description, publication, slug
        """
        try:
            result = subprocess.run(
                [
                    "firecrawl", "search",
                    f"{query} site:substack.com",
                    "--limit", str(limit), "--json",
                ],
                capture_output=True, text=True, timeout=60,
                cwd=str(Path(__file__).resolve().parent.parent.parent),
            )

            if result.returncode != 0:
                return []

            data = json.loads(result.stdout)

            # Handle different Firecrawl output formats
            items = []
            if isinstance(data, dict):
                web = data.get("data", {}).get("web", data.get("results", []))
                if isinstance(web, list):
                    items = web
            elif isinstance(data, list):
                items = data

            results = []
            for item in items[:limit]:
                url = item.get(
                    "url", item.get("metadata", {}).get("sourceURL", "")
                )
                title = item.get(
                    "title", item.get("metadata", {}).get("title", "")
                )
                desc = item.get(
                    "description",
                    item.get("metadata", {}).get("description", ""),
                )

                pub, slug = self._parse_substack_url(url)

                results.append({
                    "title": title,
                    "url": url,
                    "description": desc,
                    "publication": pub,
                    "slug": slug,
                })

            return results

        except Exception as e:
            print(f"Firecrawl search failed: {e}")
            return []

    def _parse_substack_url(self, url):
        """Extract publication name and post slug from a Substack URL."""
        # Pattern: {pub}.substack.com/p/{slug}
        match = re.search(
            r'(?:https?://)?([^./]+)\.substack\.com/p/([^/?#]+)', url
        )
        if match:
            return match.group(1), match.group(2)

        # Pattern: open.substack.com/pub/{pub}/p/{slug}
        match = re.search(
            r'open\.substack\.com/pub/([^/]+)/p/([^/?#]+)', url
        )
        if match:
            return match.group(1), match.group(2)

        # Custom domain: try to extract slug from /p/ path
        slug = ""
        pub = ""
        match = re.search(r'/p/([^/?#]+)', url)
        if match:
            slug = match.group(1)
            domain_match = re.search(r'https?://(?:www\.)?([^./]+)', url)
            if domain_match:
                pub = domain_match.group(1)

        return pub, slug

    # --- Layer 2: Substack API (Extraction) ---

    def _api_get(self, base_url, path, params=None):
        """Make rate-limited GET to Substack's undocumented API."""
        _rate_limit()
        url = f"https://{base_url}/api/v1{path}"
        try:
            resp = self.session.get(url, params=params or {}, timeout=15)
            if resp.status_code == 429:
                time.sleep(10)
                resp = self.session.get(url, params=params or {}, timeout=15)
            if resp.status_code != 200:
                return None
            return resp.json()
        except Exception:
            return None

    def list_posts(self, publication, limit=12, offset=0, sort="new"):
        """
        List posts from a Substack publication.

        Args:
            publication: Publication subdomain (e.g., 'oneusefulthing')
            limit: Posts per page (max ~50)
            offset: Pagination offset
            sort: 'new' or 'top'

        Returns:
            List of post dicts with title, slug, date, wordcount, reactions
        """
        for base in [
            f"{publication}.substack.com",
            f"www.{publication}.com",
            publication,
        ]:
            data = self._api_get(
                base, "/archive",
                {"sort": sort, "limit": limit, "offset": offset},
            )
            if data and isinstance(data, list):
                return [
                    {
                        "title": p.get("title", ""),
                        "slug": p.get("slug", ""),
                        "date": p.get("post_date", ""),
                        "wordcount": p.get("wordcount", 0),
                        "reactions": p.get("reactions", {}),
                        "subtitle": p.get("subtitle", ""),
                        "audience": p.get("audience", ""),
                        "comment_count": p.get("comment_count", 0),
                        "publication": publication,
                        "url": f"https://{base}/p/{p.get('slug', '')}",
                    }
                    for p in data
                ]

        return []

    def get_post(self, publication, slug, as_text=True):
        """
        Get full post content from a Substack publication.

        Args:
            publication: Publication subdomain
            slug: Post slug (from URL or list_posts)
            as_text: Convert HTML body to plain text (default True)

        Returns:
            Dict with title, date, body, wordcount, reactions, comments, etc.
        """
        for base in [
            f"{publication}.substack.com",
            f"www.{publication}.com",
            publication,
        ]:
            data = self._api_get(base, f"/posts/{slug}")
            if data and isinstance(data, dict) and data.get("title"):
                body_html = data.get("body_html", "") or ""
                body = _strip_html(body_html) if as_text else body_html

                return {
                    "title": data.get("title", ""),
                    "slug": slug,
                    "date": data.get("post_date", ""),
                    "body": body,
                    "body_length": len(body),
                    "wordcount": data.get("wordcount", 0),
                    "reactions": data.get("reactions", {}),
                    "comment_count": data.get("comment_count", 0),
                    "subtitle": data.get("subtitle", ""),
                    "audience": data.get("audience", ""),
                    "publication": publication,
                    "url": f"https://{base}/p/{slug}",
                    "canonical_url": data.get("canonical_url", ""),
                }

        return None

    # --- Combined Workflows ---

    def research(self, query, max_posts=5, search_limit=10):
        """
        Full research pipeline: Firecrawl discovers, Substack API extracts content.

        Args:
            query: Research topic
            max_posts: Max posts to extract full content for
            search_limit: How many search results to consider

        Returns:
            dict with: query, search_results, extracted_posts
        """
        # Step 1: Discover via Firecrawl
        search_results = self.search(query, limit=search_limit)

        # Step 2: Extract full content from top results
        extracted = []
        for result in search_results[:max_posts]:
            pub = result.get("publication", "")
            slug = result.get("slug", "")

            if not pub or not slug:
                continue

            post = self.get_post(pub, slug)
            if post and post.get("body"):
                extracted.append(post)

        return {
            "query": query,
            "search_results_count": len(search_results),
            "search_results": search_results,
            "extracted_count": len(extracted),
            "extracted_posts": extracted,
        }

    def discover_publications(self, query, limit=10):
        """
        Find Substack publications on a topic via Google search.

        Returns unique publications found in search results.
        """
        results = self.search(query, limit=limit)
        pubs = {}
        for r in results:
            pub = r.get("publication", "")
            if pub and pub not in pubs and pub != "open":
                pubs[pub] = {
                    "publication": pub,
                    "url": f"https://{pub}.substack.com",
                    "found_via": r.get("title", ""),
                }
        return list(pubs.values())
````

[VERIFY]
```bash
python3 -c "from scripts.substack.client import SubstackClient; print('Substack client loaded OK')"
```
Expected: `Substack client loaded OK`

All 5 research platforms are connected! Now let's install the Deep Research orchestrator.

---

### Part 6: Deep Research Orchestrator

This is the brain. The orchestrator skill tells Claude how to run the full deep research pipeline: scope interview, recon, parallel topic agents, critic review, and synthesis. It includes 4 prompt templates that get populated with session variables and fed to subagents.

#### Step 6.1: Create the orchestrator skill

```bash
mkdir -p .claude/skills/deep-research/prompts
```

Write the following file to `.claude/skills/deep-research/SKILL.md`:

````markdown
---
name: deep-research
description: >
  Multi-platform deep research system using parallel topic-scoped AI agents. Orchestrates
  research across Firecrawl (web), Supadata (YouTube/video), Reddit (community), X-Search
  (real-time discourse), Academic (papers), Podcast-Search (audio), and Substack (newsletters).
  Two-phase: recon scan to find where signal lives, then parallel Opus agents go 3+ levels
  deep on topic angles with signal scoring, triangulation, source profiling, and critic review.
  Use when: deep research, research this topic, investigate, find signal, who are the thought
  leaders on, what's happening in, multi-platform research, intelligence gathering, dive deep,
  research agents. Returns per-agent synthesized reports + master synthesis in
  outputs/deep-research/{date}-{slug}/. Prompt templates live in prompts/.
user-invocable: true
---

# Deep Research Skill

Multi-agent research orchestration across 7 platforms. Topic-scoped parallel agents go
3+ levels deep, score sources rigorously, triangulate claims, and produce critically cited
synthesis reports.

**Output location:** `outputs/deep-research/{date}-{topic-slug}/`
**Prompt templates:** `.claude/skills/deep-research/prompts/`

---

## The Flow

```
/deep-research "brain dump"
  -> Scope Interview (3-4 questions)
  -> Recon Agent (Sonnet, 2-3 min) -> recon.md
  -> HUMAN CHECKPOINT -- review recon, confirm agent roster
  -> Parallel Topic Agents (Opus max, 10-20 min each) -> 01-angle.md, 02-angle.md, ...
  -> Critic Agent (Opus max, review-only) -> critic-notes.md
  -> Synthesis Agent (Opus max) -> synthesis.md
```

---

## Phase 1 MVP (Start Here)

For the first research run, skip recon and critic. Run topic agents directly.

1. Ask the user the scope interview questions
2. Determine 3-6 topic angles based on the brain dump
3. Create session folder: `outputs/deep-research/{date}-{topic-slug}/`
4. Launch all topic agents simultaneously (batch in one message)
5. Run synthesis agent on all outputs

---

## Phase 2: Full Flow

Add recon and critic once the core loop is validated.

1. Scope interview
2. Launch recon agent using `prompts/recon.md` template, populate all variables
3. Show recon.md to user, ask for confirmation/adjustments to agent roster
4. Generate topic angle list from recon + user input
5. Launch all topic agents simultaneously, each populated from `prompts/topic-agent.md`
6. Launch critic agent from `prompts/critic.md` once all topic agents complete
7. Launch synthesis agent from `prompts/synthesis.md`

---

## Scope Interview Questions

Ask these at the start of every session:

1. **Core question:** What's the main thing you're trying to find out or understand?
2. **Time period:** How recent does the information need to be? (last 30 days / 90 days / 1 year / any)
3. **Starting points:** Any known people, publications, repos, or platforms to prioritize?
4. **Depth vs breadth:** Focused on one specific angle, or broad survey of the space?

---

## Populating the Agent Templates

### Session variables (set at scope interview):
- `{TOPIC_BRAIN_DUMP}` -- user's full brain dump, verbatim
- `{TIME_PERIOD}` -- recency requirement from scope interview
- `{STARTING_POINTS}` -- known people/publications/repos (or "none")
- `{SESSION_SLUG}` -- `{YYYY-MM-DD}-{kebab-case-topic}`, e.g. `2026-03-27-ai-engineering-tooling`

### Recon variables:
- All session variables

### Topic agent variables:
- All session variables
- `{TOPIC_ANGLE}` -- the specific angle this agent is researching
- `{N}` -- agent number (01, 02, 03...)
- `{ANGLE_SLUG}` -- kebab-case version of the angle, e.g. `practitioner-shipping-reality`
- `{RECON_HOT_PLATFORMS}` -- from recon.md (or "unknown, check all" if skipping recon)
- `{RECON_KEY_PEOPLE}` -- from recon.md (or "none identified yet")
- `{RECON_QUERIES}` -- from recon.md (or "generate your own")

### Critic variables:
- `{TOPIC_BRAIN_DUMP}` -- session context
- `{SESSION_SLUG}` -- session folder name
- `{LIST_OF_AGENT_REPORT_FILES}` -- comma-separated list of report filenames

### Synthesis variables:
- All session variables
- `{LIST_OF_AGENT_REPORT_FILES}` -- comma-separated list of report filenames

---

## Launching Agents in Parallel

CRITICAL: To get true parallel execution, all topic agent calls must be in a single message.
Do not launch them sequentially. Use multiple Agent tool calls in one response.

Each topic agent should:
- Use the `general-purpose` subagent type
- Have the full populated prompt from `prompts/topic-agent.md`
- Write output to its specific file path

---

## Typical Agent Roster Examples

**"AI engineering tooling trends"** (4 agents):
- Agent 1: What practitioners are actually shipping and what's breaking in production
- Agent 2: Key thought leaders and their frameworks, who's setting the direction
- Agent 3: Academic and research frontier vs production reality gap
- Agent 4: Tool ecosystem, what's emerging, what's consolidating, what's dying

**"Understanding [person]'s work and influence"** (3 agents):
- Agent 1: Their published work, talks, and primary sources
- Agent 2: How their ideas are being applied by others, reception and criticism
- Agent 3: The people and ideas that influenced them, intellectual lineage

**"Market landscape for [category]"** (5 agents):
- Agent 1: Incumbent players and their positioning
- Agent 2: Emerging challengers and new entrants
- Agent 3: Practitioner sentiment, what's working, what's not
- Agent 4: Academic research direction
- Agent 5: Business model and pricing landscape

---

## Signal Quality Quick Reference

```
RECENCY:     Primary work (any date): 2 | <30d: 3 | <90d: 2 | <1yr: 1 | old current-tech: 0
SOURCE:      Primary/academic: 3 | Named practitioner: 2 | Tech journalism: 1 | Aggregator: 0
SPECIFICITY: Numbers/code/failures: 2 | Some specifics: 1 | Generic: 0
INDEPENDENT: Not citing existing: 1 | Cites existing: 0.5 | Same org: 0
Score >=5: pursue | 3-4: include with caveat | <3: drop
```

High-value domains: arxiv.org, github.com/issues, github.com/discussions, official docs
Low-value domains: SEO farms, /blog/ai-guide-YYYY patterns, AI-pivot domains post-2023
````

#### Step 6.2: Create the Recon prompt template

Write the following file to `.claude/skills/deep-research/prompts/recon.md`:

````markdown
# Recon Agent Prompt Template

**Model:** Sonnet | **Runtime:** ~2-3 minutes | **Output:** `recon.md`

---

You are a research recon agent. Your job is to do a fast, shallow sweep across multiple
platforms to determine where the signal lives for a given topic. You are NOT doing deep
research -- you are doing a reconnaissance pass to inform a deeper research operation.

## Research Topic
{TOPIC_BRAIN_DUMP}

## Time Period
Focus on content from: {TIME_PERIOD}
Known starting points (if any): {STARTING_POINTS}

## Your Tools

### Firecrawl (web search + scraping)
```bash
firecrawl search "{query}" --scrape
firecrawl scrape "{url}"
```

### Supadata (YouTube + social transcripts)
```python
from scripts.utils.supadata import SupadataClient
client = SupadataClient()
client.youtube_search("{query}", upload_date="month", limit=5)
client.transcript_text("{youtube_url}")
```

### Reddit (community discussions)
```python
from scripts.reddit.client import RedditClient
reddit = RedditClient()
reddit.search("{query}", time_filter="month", limit=10)
reddit.find_subreddits("{topic}", limit=5)
```

### X-Search (real-time practitioner discourse)
```python
from scripts.x_search.client import XSearchClient
xclient = XSearchClient()
xclient.search("{query}", days_back=30)
```

### Substack (newsletter / long-form)
```python
from scripts.substack.client import SubstackClient
sub = SubstackClient()
sub.search("{query}", limit=5)
```

### Academic (papers)
```python
from scripts.academic.client import AcademicClient
academic = AcademicClient()
academic.search("{query}", limit=5, year_from=2024)
```

### Podcast-Search (audio / video intelligence)
```python
from scripts.podcast_search.client import PodcastSearchClient
pods = PodcastSearchClient()
pods.youtube_search("{query}", limit=5, upload_date="month")
```

## Your Method

For each platform, run 1-2 searches on the topic. Note what comes back. You are
scanning, not diving deep.

Rate each platform for this specific topic:
- HOT: meaningful signal, active discussion, multiple credible sources
- WARM: some signal, worth a deeper look
- COLD: little or nothing relevant

## What to Return

Write your findings to: outputs/deep-research/{SESSION_SLUG}/recon.md

Structure:
1. **Platform Signal Map** -- HOT / WARM / COLD rating per platform with brief reason
2. **Key People** -- 3-8 practitioners surfacing, with platform and why they look credible
3. **Key Threads/Sources** -- most promising URLs or discussions, 1-line description each
4. **Emerging Angles** -- 4-8 distinct research angles worth a dedicated agent
5. **Query Intelligence** -- search terms that produced the best results
6. **Time Period Assessment** -- hot or cold topic right now? Where is the freshest primary work?

Be specific and concrete. This briefing is what the human uses to plan the deep agent roster.
````

#### Step 6.3: Create the Topic Agent prompt template

Write the following file to `.claude/skills/deep-research/prompts/topic-agent.md`:

````markdown
# Topic Research Agent Prompt Template

**Model:** Opus, max effort | **Runtime:** 10-20 minutes | **Output:** `{N}-{angle-slug}.md`

---

You are a deep recursive research agent. Your job is to exhaustively investigate
{TOPIC_ANGLE} as it relates to the broader research goal below. You have full access
to all research platforms and should use them as needed, following signal wherever it leads.

## Big Picture Context
{TOPIC_BRAIN_DUMP}

## Your Specific Angle
{TOPIC_ANGLE}

## Time Period
Prioritize content from: {TIME_PERIOD}
Note: recent does not equal high quality. A primary source from 2022 beats AI commentary on it
from last week. Optimize for primary sources, not just recent ones.

## Recon Intelligence
Richest platforms for this topic: {RECON_HOT_PLATFORMS}
Key people already identified: {RECON_KEY_PEOPLE}
Promising queries: {RECON_QUERIES}

---

## Your Tools -- EXPLICIT SYNTAX

Use all tools as needed. Start wide across all platforms, then chase signal deep.

### Firecrawl -- Web search, scraping, crawling
```bash
firecrawl search "{query}" --scrape
firecrawl scrape "{url}"
firecrawl map "{domain}"
firecrawl crawl "{url}" --limit 10
firecrawl browser "{url}"
```

### Supadata -- YouTube transcripts, social video, metadata
```python
from scripts.utils.supadata import SupadataClient
client = SupadataClient()
results = client.youtube_search("{query}", upload_date="year", sort_by="relevance", limit=10)
transcript = client.transcript_text("{youtube_url}")
meta = client.youtube_video("{url_or_id}")
channel = client.youtube_channel("{handle}")
page = client.web_scrape("{url}")
```

### Reddit -- Community discussions, practitioner sentiment
```python
from scripts.reddit.client import RedditClient
reddit = RedditClient()
posts = reddit.search("{query}", sort="relevance", time_filter="year", limit=15)
posts = reddit.search_subreddit("{subreddit}", "{query}", time_filter="month")
subs = reddit.find_subreddits("{topic}", limit=8)
thread = reddit.extract_thread("{url}", comment_limit=50)
results = reddit.research("{query}", time_filter="year", max_threads=10, max_comments=30)
```

### X-Search -- Real-time practitioner discourse
```python
from scripts.x_search.client import XSearchClient
xclient = XSearchClient()
# Layer 1: Grok semantic search + synthesis
result = xclient.search("{query}", days_back=90)
# result.content = synthesized answer | result.citations = tweet URLs
# Layer 2: X API engagement data
tweets = xclient.lookup_tweets(["{tweet_id1}", "{tweet_id2}"])
# tweets[i].public_metrics = {like_count, retweet_count, reply_count, impression_count}
users = xclient.lookup_users(["{username}"])
# Combined
enriched = xclient.discover_and_enrich("{query}", days_back=60, max_enrich=20)
```

### Academic -- Papers, citations, free PDFs
```python
from scripts.academic.client import AcademicClient
academic = AcademicClient()
papers = academic.search("{query}", limit=10, year_from=2023, cited_by_min=10, sort="cited_by_count")
paper = academic.get_paper(doi="10.xxxx/xxx")
citations = academic.get_citations("{openalex_id}", limit=20)
pdf_url = academic.find_free_pdf("{doi}")
results = academic.research("{query}", max_papers=8, year_from=2023, find_free_pdfs=True)
```

### Substack -- Newsletter analysis, long-form thought leadership
```python
from scripts.substack.client import SubstackClient
sub = SubstackClient()
posts = sub.search("{query}", limit=10)
pubs = sub.discover_publications("{topic}", limit=8)
archive = sub.list_posts("{publication_name}", limit=10, sort="new")
content = sub.get_post("{publication}", "{slug}", as_text=True)
results = sub.research("{query}", max_posts=6, search_limit=15)
```

### Podcast-Search -- Audio intelligence, expert interviews
```python
from scripts.podcast_search.client import PodcastSearchClient
pods = PodcastSearchClient()
episodes = pods.search("{query}", limit=15)
yt_episodes = pods.youtube_search("{query}", limit=10, upload_date="year", duration="long")
transcript = pods.get_transcript("{youtube_url}")
results = pods.research("{query}", max_transcripts=4, min_quality_score=50, upload_date="year")
```

---

## Research Method: BREADTH-FIRST DISCOVERY then DEPTH-FIRST EXPLOITATION

### Round 1 -- Platform Dip

Generate 3-5 query variants for your topic angle. Target different angles:
technical implementation, failure modes, practitioner experience, academic foundation,
recent developments. Run 1-2 searches per platform with your best variants.
Log what each returns. Which platforms have signal? Which are dead for this topic?

### Round 2 -- Signal Chase

For highest-signal findings from Round 1:
- Person: pull everything they've written on this topic across all platforms
- Thread: extract full comments, follow cited sources, look at who's replying
- YouTube video: pull full transcript, note every tool/person/repo mentioned
- Paper: get full text, check citation list, find papers that cite it
- GitHub repo: read README, issues, discussions, who's building with it and what breaks

Cross-reference: take something found on X and search for it on Reddit, Substack, academic.

### Round 3+ -- Contradiction Search

Actively search for evidence AGAINST your strongest findings:
"{finding} is wrong", "problems with {tool}", "{person} criticism", "alternative to {approach}"

Repeat until 3+ levels deep or clear diminishing returns.

---

## Source Scoring -- SCORE EVERY SOURCE BEFORE GOING DEEP

```
RECENCY:       Primary work (any date): 2 | <30 days: 3 | <90 days: 2 | <1 year: 1 | older current-tech: 0
SOURCE_TYPE:   Primary/academic: 3 | Named practitioner: 2 | Tech journalism: 1 | Aggregator: 0
SPECIFICITY:   Numbers/code/failure modes: 2 | Some specifics: 1 | Generic: 0
INDEPENDENCE:  Not citing existing sources: 1 | Cites existing: 0.5 | Same org: 0

TOTAL >= 5: pursue | 3-4: include with caveat | <3: drop
```

Domain pre-filter BEFORE fetching:
- High-value: arxiv.org, github.com/issues, github.com/discussions, official docs, known practitioners
- Low-value: Medium (unless known author), /blog/ai-guide-2025 URL patterns, AI-content-pivot domains

Low engagement does not equal low quality: a practitioner post with 0 likes but specific failure modes
and version numbers may be the highest-signal find in the run. Evaluate specificity, not popularity.

---

## Quality Requirements

**Sub-document chunking:** Extract 2-4 most relevant paragraphs per source, not the full page.
A page with no specific citable paragraphs gets dropped.

**Knowledge Filter gate:** Before including any source, check:
- Directly addresses the research question? (0-3)
- Contains concrete claims, data, or examples, not generic assertions? (0-3)
- Total < 4: exclude. Total >= 4: include with score noted.

**Triangulation:** No factual claim enters your report without 2 independent sources.
Independent = not same org, not one citing the other, not published within 7 days of each other.
Label: [SINGLE SOURCE -- NEEDS VERIFICATION] | [UNVERIFIED] | [CONFLICTING SOURCES EXIST]

**Negative rejection:** If you find no reliable source for a claim, say so explicitly.
Do not synthesize from poor sources to fill gaps.

**Source profiles for heavy citations:** If you cite a person 3+ times, include:
- Who they are and what they've shipped
- Platform, audience, publishing frequency
- Known commercial interests or biases
- Why they're credible (or not) on THIS specific topic

**AI content warning signs to flag:**
- Exactly 5-7 parallel bullet points per section
- Headers: "What is X?", "Why does X matter?", "Benefits of X"
- No author, no byline, no track record
- Describes tools without mentioning failure modes or tradeoffs
- "Comprehensive solution", "in today's fast-paced landscape"

---

## Output

Write your full synthesized report to:
outputs/deep-research/{SESSION_SLUG}/{N}-{ANGLE_SLUG}.md

### Report Structure

```
# Deep Research: {TOPIC_ANGLE}
**Session:** {SESSION_SLUG} | **Date:** {DATE}
**Big Picture Context:** {TOPIC_BRAIN_DUMP}

## Executive Summary
3-5 sentences: what did you find, highest-confidence finding, biggest unknown

## Key Findings

### Finding 1: {title}
{Specific claim with evidence}
**Confidence:** High / Medium / Low
**Based on:** {source 1} + {source 2} (triangulated / single source / conflicting)

## Source Profiles
{For every person cited 3+ times}
### {Name}
- **Who:** {background, what they've shipped, verifiable track record}
- **Platform:** {where they publish, audience size}
- **Bias:** {commercial interests, ideological lean, platform effects}
- **Strength:** {why credible on this specific topic}
- **Weakness:** {what to discount or verify independently}
- **Signal score:** X/9

## Cross-Platform Validation
{Findings confirmed by 2+ independent platforms, highest-confidence claims}

## Tensions & Contradictions
{Where sources disagree. Analyze WHY, don't pick a side silently.}

## Primary Sources vs Commentary
{Distinguish original work from AI-generated commentary on it.}

## Gaps & Negative Rejections
{"No reliable source found for X" is a valid entry. What questions remain open.}

## All Citations
| Source | Platform | Signal Score | URL |
|--------|----------|-------------|-----|
```

Include ALL source URLs. Do not summarize sources you haven't actually read.
````

#### Step 6.4: Create the Critic prompt template

Write the following file to `.claude/skills/deep-research/prompts/critic.md`:

````markdown
# Critic Agent Prompt Template

**Model:** Opus, max effort | **Constraint:** Review only, no searching, no fetching, no new research
**Input:** All topic agent report files | **Output:** `critic-notes.md`

---

You are a research critic. Your job is to read all topic agent research reports and
identify quality problems before synthesis. You do not search, fetch URLs, or produce
new research. You work only from what's already in the reports.

## Research Session
Topic: {TOPIC_BRAIN_DUMP}
Session folder: outputs/deep-research/{SESSION_SLUG}/

## Reports to Review
{LIST_OF_AGENT_REPORT_FILES}

## Your 10 Review Criteria

### 1. Missing Source Profiles
Flag any person cited 3+ times without a source profile.
Format: [MISSING PROFILE] {Name}, cited {N} times in {report}, no profile provided

### 2. Echo Chambers
Identify clusters where multiple "independent" sources all cite the same 2-3 people
or originate from the same organization. These count as ONE data point.
Format: [ECHO CHAMBER] Sources {A}, {B}, {C} in {report} all trace back to {original source}

### 3. Claim Weight Mismatch
Flag big claims supported only by low-credibility sources.
Format: [CLAIM WEIGHT MISMATCH] "{claim}" in {report}, backed only by {source type/credibility}

### 4. Unlabeled Single-Source Claims
Flag factual claims with only one source not labeled [SINGLE SOURCE].
Format: [UNLABELED SINGLE SOURCE] "{claim}" in {report}

### 5. Recency Bias
Flag cases where recent AI-generated summaries are used where older primary work exists.
Format: [RECENCY BIAS] {report} cites {recent source} on {topic}, primary work is {older source}

### 6. Negative Rejection Failures
Flag gaps synthesized over rather than flagged as unknown. Look for vague hedging
without citing absence of sources.
Format: [NEGATIVE REJECTION FAILURE] {report} makes claim about {X} with no source, should be [UNVERIFIED]

### 7. Unsupported Generalizations
Flag broad claims with no specific evidence.
Format: [UNSUPPORTED GENERALIZATION] "{claim}" in {report}, no specific evidence provided

### 8. AI Content Signals
Flag sources showing strong AI-generation warning signs.
Format: [AI CONTENT SIGNAL] {source} in {report}, signals: {list warning signs}

### 9. Cross-Report Contradictions
Identify where two agents reached opposing conclusions on the same factual question.
Format: [CONTRADICTION] {Report A} claims {X}, {Report B} claims {Y}, re: {topic}

### 10. Verification Needs
Note whether flagged items need verification or just a label change.
Format: [NEEDS VERIFICATION] {specific claim or source}, {why}

## Output

Write to: outputs/deep-research/{SESSION_SLUG}/critic-notes.md

Structure:
1. **Summary** -- reports reviewed, overall quality assessment (1 paragraph)
2. **Critical Flags** -- issues that could materially affect synthesis (fix before synthesis)
3. **Minor Flags** -- labeling issues, minor gaps (note but don't block synthesis)
4. **Cross-Report Contradictions** -- all opposing claims across reports
5. **Verification Queue** -- specific claims or sources needing follow-up search

Be specific. Reference the exact report filename and claim.
````

#### Step 6.5: Create the Synthesis prompt template

Write the following file to `.claude/skills/deep-research/prompts/synthesis.md`:

````markdown
# Synthesis Agent Prompt Template

**Model:** Opus, max effort | **Input:** All topic reports + critic-notes.md | **Output:** `synthesis.md`

---

You are a research synthesis agent. You have access to a set of deep research reports
produced by parallel topic agents and a critic's review. Your job is to produce a single,
authoritative master synthesis document.

## Research Session
Topic: {TOPIC_BRAIN_DUMP}
Time period: {TIME_PERIOD}
Session folder: outputs/deep-research/{SESSION_SLUG}/

## Inputs
Topic agent reports: {LIST_OF_AGENT_REPORT_FILES}
Critic notes: outputs/deep-research/{SESSION_SLUG}/critic-notes.md

## Your Method

Step 1: Read everything, all topic reports and critic notes, before writing anything.

Step 2: Map the landscape: themes across multiple reports (high-confidence signal),
contradictions between reports, gaps flagged by the critic, single-source claims needing labels.

Step 3: Apply confidence weighting:
- How many independent agents/sources confirm it
- Source tier of confirming sources (primary/practitioner > aggregator)
- Whether the critic flagged issues with those sources
- Cross-platform confirmation (X + Reddit + academic = stronger than any one platform)

Do NOT flatten everything to the same confidence level. Be explicit about what you know
well vs what you know weakly. A synthesis that treats everything as equal confidence is
worse than no synthesis at all.

Step 4: Write the synthesis.

## Output

Write to: outputs/deep-research/{SESSION_SLUG}/synthesis.md

### Required Structure

```
# Deep Research Synthesis: {TOPIC_SLUG}
**Date:** {DATE}
**Agents run:** {N} topic agents + critic + synthesis
**Platforms covered:** {LIST}
**Time period:** {TIME_PERIOD}

## The Short Version
5-10 bullet points, most important findings with confidence labels:
- [HIGH] {finding}
- [MEDIUM] {finding}
- [LOW / SINGLE SOURCE] {finding}

## High-Confidence Findings
Confirmed by 2+ independent agents/sources, high-quality sources.
For each: what it is, why we're confident, which agents/sources confirm it.

## Medium-Confidence Findings
Some support but not fully triangulated, or source quality concerns.
For each: what it is, what the caveat is.

## Tensions & Contradictions
Where agents or sources reached different conclusions.
For each: the tension, why it might exist, what would resolve it.

## Key People & Sources
Consolidated profiles of most-cited people across all reports.
Ranked by: citations x source credibility x independence.

## Platform Signal Map
Which platforms were richest for this topic.
| Platform | Signal Level | Best use for this topic |
|----------|-------------|------------------------|

## What We Don't Know
Gaps, negative rejections, [UNVERIFIED] claims, [NEEDS VERIFICATION] flags from critic.
"We found no reliable primary source for {X}" is a valuable finding.

## Recommended Next Steps
If this research feeds into a decision, content piece, or further investigation:
what should happen next?

## Source Registry
Master list of all sources cited across all reports.
| Source | Platform | Signal Score | Report(s) | URL |
|--------|----------|-------------|-----------|-----|
```
````

#### Step 6.6: Create the deep-research command

Write the following file to `.claude/commands/deep-research.md`:

```markdown
Run the deep-research skill on: $ARGUMENTS
```

[VERIFY]
```bash
ls .claude/skills/deep-research/SKILL.md .claude/skills/deep-research/prompts/recon.md .claude/skills/deep-research/prompts/topic-agent.md .claude/skills/deep-research/prompts/critic.md .claude/skills/deep-research/prompts/synthesis.md .claude/commands/deep-research.md
```
Expected: All 6 files listed without errors.

Everything is installed. Let's test it.

---

## TEST

### Create the output directory

```bash
mkdir -p outputs/deep-research
```

### Quick test

Ask Claude:

> "Run a quick deep research on AI coding agents. Just use 2 topic agents to keep it fast."

Claude should:
1. Ask you the scope interview questions (core question, time period, starting points, depth vs breadth)
2. Create a session folder like `outputs/deep-research/2026-04-02-ai-coding-agents/`
3. Launch 2 topic agents in parallel (you'll see them searching across platforms)
4. Produce a synthesis report

If you see reports appearing in the session folder, everything is working.

---

## WHAT'S NEXT

You're all set. Here's what you can do with Deep Research:

- **Full research run:** `/deep-research "your topic brain dump"` for the complete pipeline with recon, parallel agents, critic review, and synthesis
- **Quick research:** Ask for 2-3 agents on a focused topic to keep it fast
- **Build on it:** Add more platform clients, tune the prompt templates in `.claude/skills/deep-research/prompts/`, customize the source scoring

The prompt templates are designed to improve over time. After each research run, if Claude discovers a better research pattern, a tool syntax quirk, or a common failure mode, it updates the relevant template automatically.

---

> A plug-and-play module from Liam Ottley's AAA Accelerator, the #1 AI business launch
> & AIOS program. Grab this and 15+ more at [aaaaccelerator.com](https://aaaaccelerator.com)
