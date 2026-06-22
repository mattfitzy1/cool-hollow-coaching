---
name: x-search
description: >
  X/Twitter search and content intelligence — two-layer architecture.
  Layer 1: Grok x_search (xAI Responses API) — semantic search, synthesized insights, X post citations.
  Layer 2: X API v2 — raw tweet lookup with engagement metrics (likes, retweets, replies, impressions).
  Use for: what are people saying on X, X sentiment, find relevant X posts, X research,
  Twitter discussions, pull tweets, engagement metrics, X content discovery.
user-invocable: false
---

# X Search — Two-Layer Intelligence

Grok discovers and synthesizes. X API enriches with engagement data.

## Setup

```python
import importlib.util, os
spec = importlib.util.spec_from_file_location("x_search_client",
    os.path.join(os.path.dirname(os.path.abspath(".")), "scripts/x_search/client.py"))
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
client = mod.XSearchClient()
```

Or from the workspace root directory:
```bash
python3 -c "from scripts.x_search.client import XSearchClient; c = XSearchClient(); print('Connected')"
```

**Env vars required:**
- `XAI_API_KEY` — xAI API key (https://console.x.ai)
- `X_BEARER_TOKEN` — X API v2 bearer token (https://developer.x.com) — optional, for engagement data

**Models:** x_search only works with `grok-4` family. `grok-3-*` returns 400.

---

## Layer 1: Grok x_search (Discovery)

Semantic search across X via xAI Responses API. Returns synthesized answer + citation URLs.

### `client.search(query, ...)`

```python
# Basic search — last 7 days
result = client.search("AI automation agencies", days_back=7)
print(result["answer"])      # Grok's synthesized response
print(result["citations"])   # List of x.com/i/status/... URLs

# Filter to specific accounts only
result = client.search(
    "thoughts on Claude Code",
    days_back=30,
    allowed_handles=["AnthropicAI", "karpathy"],  # max 10
)

# Date range
result = client.search(
    "AI agent frameworks comparison",
    from_date="2025-03-01",
    to_date="2025-03-22",
)

# With image/video analysis
result = client.search(
    "AI demo videos this week",
    days_back=7,
    enable_images=True,
    enable_video=True,
)
```

### Search Parameters

| Parameter | Type | Notes |
|-----------|------|-------|
| `query` | str | Natural language — Grok handles semantics |
| `days_back` | int | Shortcut for from_date (overrides it) |
| `from_date` | str | `YYYY-MM-DD` |
| `to_date` | str | `YYYY-MM-DD` |
| `allowed_handles` | list[str] | Whitelist — max 10. Mutually exclusive with excluded |
| `excluded_handles` | list[str] | Blocklist — max 10. Mutually exclusive with allowed |
| `enable_images` | bool | Analyze images in posts |
| `enable_video` | bool | Analyze video content |
| `model` | str | Default: `grok-4`. Must be grok-4 family |

### Response Shape

```python
{
    "answer": "Grok's synthesized text response...",
    "citations": [
        "https://x.com/i/status/2033872474019086730",
        "https://x.com/i/status/2034131015845966013",
    ],
    "model": "grok-4-0709",
    "usage": {
        "input_tokens": 7249,
        "output_tokens": 1718,
        "x_search_calls": 1,
        "cost_in_usd_ticks": 449255000,  # divide by 1e10 for USD (~$0.05/search typical)
    }
}
```

**Cost:** ~$0.05 per search call on grok-4 (verified against live billing 24 April 2026). Budget ~$1-1.50 per 20-30 query research session.

---

## Layer 2: X API v2 (Engagement Data)

Raw tweet data with exact engagement metrics. Requires `X_BEARER_TOKEN`.

### `client.lookup_tweets(tweet_ids)`

```python
# Look up specific tweets by ID (from Grok citations)
tweets = client.lookup_tweets(["2033872474019086730", "2034131015845966013"])

for t in tweets:
    m = t.get("public_metrics", {})
    a = t.get("author", {})
    print(f"@{a.get('username')}: {t['text'][:100]}")
    print(f"  {m['like_count']} likes | {m['retweet_count']} RTs | {m['reply_count']} replies")
```

### `client.search_recent(query)`

```python
# X API v2 direct search — raw tweet results
result = client.search_recent(
    "AI automation -is:retweet lang:en",
    max_results=20,
    sort_order="relevancy",  # or "recency"
    start_time="2025-03-15T00:00:00Z",
)

for t in result["tweets"]:
    print(t["text"], t.get("public_metrics"))

# Paginate
next_page = client.search_recent("AI agency", next_token=result["meta"].get("next_token"))
```

### `client.lookup_users(usernames)`

```python
users = client.lookup_users(usernames=["AnthropicAI", "OpenAI", "karpathy"])
for u in users:
    m = u.get("public_metrics", {})
    print(f"@{u['username']}: {m['followers_count']:,} followers")
```

### public_metrics Fields

| Field | What It Is |
|-------|-----------|
| `like_count` | Likes/hearts |
| `retweet_count` | Retweets (not quote tweets) |
| `reply_count` | Direct replies |
| `quote_count` | Quote retweets |
| `bookmark_count` | Private bookmarks |
| `impression_count` | Times shown in feeds |

---

## Combined: Discover + Enrich

```python
# Full pipeline — Grok finds, X API enriches with metrics
result = client.discover_and_enrich(
    "Best AI tools launching this week",
    days_back=7,
    max_enrich=10,  # max tweets to pull from X API
)

print(result["answer"])          # Grok synthesis
print(result["citations"])       # Source URLs
for t in result["enriched_tweets"]:
    m = t.get("public_metrics", {})
    print(f"{m.get('like_count', 0)} likes — {t['text'][:80]}")
```

---

## X API v2 Search Operators

```
# By account
from:elonmusk              # tweets from user
to:AnthropicAI             # replies to user
retweets_of:karpathy       # retweets of user

# Content filters
#hashtag                   # hashtag
-is:retweet                # exclude retweets
-is:reply                  # exclude replies
is:verified                # verified accounts only
has:media                  # has image/video
has:links                  # contains URL
lang:en                    # English only

# Boolean
(AI agents) OR (LLM automation)
"exact phrase"             # exact match

# Combine
from:AnthropicAI -is:retweet lang:en
```

Max query length: 512 characters on pay-per-use.

---

## Rate Limits

| Layer | Limit | Reset |
|-------|-------|-------|
| xAI Responses API | Not published — generous for on-demand | Per request billing |
| X API v2 tweet lookup | 3,500 req / 15 min (app-only) | Every 15 min |
| X API v2 search/recent | 450 req / 15 min (app-only) | Every 15 min |
| X API v2 user lookup | 300 req / 15 min (app-only) | Every 15 min |

Rate limit headers: `x-rate-limit-remaining`, `x-rate-limit-reset` (Unix timestamp).

---

## Known Gotchas

1. `x_search` tool ONLY works with `/v1/responses` endpoint, NOT `/v1/chat/completions`. Using chat/completions returns 422.
2. x_search requires `grok-4` family models. `grok-3-fast` returns 400 with "not supported when using server-side tools".
3. Citations come embedded in Grok's response text as markdown links. Extract with regex `https?://(?:x\.com|twitter\.com)/\S+`.
4. `allowed_x_handles` and `excluded_x_handles` are mutually exclusive. Use one or neither.
5. Cost is charged in `cost_in_usd_ticks`. Divide by 10,000,000,000 (1e10) to get USD. Typical call is ~$0.05 on grok-4. Original module docs said 1e8 — that was wrong, verified against live billing 24 April 2026.
6. Tweet ID extraction from x.com URLs: match `/status/(\d+)` to get the numeric ID.
