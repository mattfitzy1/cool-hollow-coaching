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
