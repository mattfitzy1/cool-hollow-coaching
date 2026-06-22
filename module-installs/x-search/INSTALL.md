# X-Search — AIOS Module Installer

> A plug-and-play module from the AAA Accelerator.
> Grab this and 15+ more at [aaaaccelerator.com](https://aaaaccelerator.com)

---

## FOR CLAUDE

You are helping a user install this AIOS Module. Follow these rules:

**Behavior:**
- Assume the user is non-technical unless they tell you otherwise
- Explain what you are doing at each step in plain English BEFORE doing it
- Celebrate small wins ("X-Search is connected, Claude can now search X and pull engagement data on any post!")
- If something fails, do not dump error logs. Explain the problem simply and suggest the fix
- Never skip verification steps. If a check fails, stop and help the user fix it
- Use encouraging language throughout

**Pacing:**
- Do NOT rush. Pause after major milestones.
- After prerequisites: "Everything looks good. Ready to install?"
- After API key setup: "Key is saved. Now let's install the skill and client."
- After installation: "All done. Let's run a quick test."
- After test: "You're all set. Here's what Claude can do with X-Search."

**Error handling:**
- If `.claude/` folder doesn't exist, they need Claude Code installed first
- If files already exist at the target paths, ask before overwriting
- If the test returns a 401 error, the API key is wrong or not saved correctly
- If the xAI call returns a 400 error, the model might be wrong (must use grok-4 family)
- If X API returns 429, they've hit the rate limit. Wait 15 minutes.
- Never say "check the logs." Find the problem and explain it

---

## OVERVIEW

This module gives Claude two-layer X/Twitter intelligence. Layer 1 uses Grok's x_search through the xAI Responses API for semantic search across X. Ask any question and get a synthesized answer with cited posts. Layer 2 uses the X API v2 for raw tweet data with engagement metrics (likes, retweets, replies, impressions), user profiles, and direct search with boolean operators.

The problem it solves: Claude can't search X by default. When you want to know what people are saying about a topic, track competitor mentions, or gauge sentiment on a product launch, Claude is blind. This module fixes that. Once installed, Claude can search X for any topic, get synthesized answers backed by real posts, and pull exact engagement numbers.

**What Claude can do after this is installed:**
- Search X for any topic and get a synthesized answer with cited source posts
- Filter by date range, specific accounts, or excluded accounts
- Analyze images and video in posts (optional flags)
- Look up engagement metrics on any tweet (likes, retweets, replies, impressions)
- Search recent tweets with X API operators (boolean, account, content type filters)
- Look up user profiles with follower counts and verification status
- Run the full discover-and-enrich pipeline: Grok finds relevant posts, X API adds engagement data

**Where it installs:** Into `.claude/skills/` and `scripts/x-search/` in your current workspace.

**Setup time:** 5-10 minutes (API key + files).

**Running cost:** ~$0.004-0.01 per Grok search call. X API v2 is rate-limited but no per-call cost on pay-per-use.

---

## SCOPING

This module installs as one unit: the skill file, the Python client, and your API keys. The X bearer token (Layer 2) is optional. You can skip it and still get full Grok-powered search.

Ask: "Ready to install? Takes about 5-10 minutes. You'll definitely need an xAI API key. The X bearer token is optional if you want engagement metrics later."

---

## PREREQUISITES

### Python 3

```bash
python3 --version
```

Expected: `Python 3.9` or higher. If not installed:
- macOS: `brew install python3` or download from python.org
- Windows: Download from python.org (check "Add to PATH" during install)

### pip packages

```bash
pip3 install requests python-dotenv
```

[VERIFY] Both checks pass.

Ask: "Python is ready. Let's get your API keys."

---

## API KEY SETUP

### 1. xAI API Key (required)

This powers Layer 1: Grok x_search for semantic search across X.

1. Go to [console.x.ai](https://console.x.ai)
2. Create an account (or sign in)
3. Navigate to **API Keys**
4. Create a new key and copy it

### 2. X Bearer Token (optional, for engagement data)

This powers Layer 2: raw tweet data with likes, retweets, replies, impressions. Skip this for now if you just want search. You can add it later.

1. Go to [developer.x.com](https://developer.x.com/en/portal/projects-and-apps)
2. Create a new app (or use existing)
3. Go to the **Keys and tokens** tab
4. Copy the **Bearer Token**

### Add keys to your workspace

Check if you already have a `.env` file:

**macOS/Linux:**
```bash
ls .env
```

**Windows:**
```powershell
Test-Path .env
```

**If the file exists,** add these lines to it:
```
XAI_API_KEY=your_xai_key_here
X_BEARER_TOKEN=your_x_bearer_token_here
```

**If it doesn't exist,** create it:

macOS/Linux:
```bash
echo "XAI_API_KEY=your_xai_key_here" > .env
echo "X_BEARER_TOKEN=your_x_bearer_token_here" >> .env
```

Windows (PowerShell):
```powershell
"XAI_API_KEY=your_xai_key_here`nX_BEARER_TOKEN=your_x_bearer_token_here" | Out-File -FilePath .env -Encoding utf8
```

Replace the placeholder values with your actual keys. If you skipped the X bearer token, just leave that line out.

[VERIFY]
```bash
grep XAI_API_KEY .env
```
Expected: The line with your key appears.

Ask: "Key is saved. Now let's install the skill and client."

---

## INSTALL

### Step 1: Create the folders

```bash
mkdir -p .claude/skills/x-search
mkdir -p scripts/x_search
```

### Step 2: Install the skill file

Write the following file to `.claude/skills/x-search/SKILL.md`:

````markdown
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
        "cost_in_usd_ticks": 449255000,  # divide by 1e8 for USD
    }
}
```

**Cost:** ~$0.004-0.01 per search call (grok-4 pricing + x_search tool invocation).

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
5. Cost is charged in `cost_in_usd_ticks`. Divide by 100,000,000 to get USD.
6. Tweet ID extraction from x.com URLs: match `/status/(\d+)` to get the numeric ID.
````

[VERIFY]
```bash
cat .claude/skills/x-search/SKILL.md | head -5
```
Expected: File starts with `---` (YAML frontmatter).

### Step 3: Install the Python client

Write the following file to `scripts/x_search/client.py`:

```python
"""
X/Twitter Search Client — Two-layer architecture.

Layer 1: Grok x_search (xAI Responses API) — semantic search, synthesized insights, citations
Layer 2: X API v2 — raw tweet data, engagement metrics, user profiles

Usage:
    from scripts.x_search.client import XSearchClient
    client = XSearchClient()
    result = client.search("AI automation agencies", days_back=7)
"""

import json
import os
import re
from datetime import datetime, timedelta, timezone
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


class XSearchClient:
    """Two-layer X/Twitter search: Grok discovery + X API v2 data."""

    def __init__(self):
        self.xai_key = os.getenv("XAI_API_KEY")
        self.x_bearer = os.getenv("X_BEARER_TOKEN")
        if not self.xai_key:
            raise ValueError("XAI_API_KEY not set in .env")
        self.xai_base = "https://api.x.ai/v1"
        self.x_api_base = "https://api.x.com/2"

    def search(self, query, days_back=None, from_date=None, to_date=None,
               allowed_handles=None, excluded_handles=None,
               enable_images=False, enable_video=False, model="grok-4"):
        x_search_config = {}
        if days_back:
            from_date = (datetime.now(timezone.utc) - timedelta(days=days_back)).strftime("%Y-%m-%d")
        if from_date:
            x_search_config["from_date"] = from_date
        if to_date:
            x_search_config["to_date"] = to_date
        if allowed_handles:
            x_search_config["allowed_x_handles"] = allowed_handles[:10]
        if excluded_handles:
            x_search_config["excluded_x_handles"] = excluded_handles[:10]
        if enable_images:
            x_search_config["enable_image_understanding"] = True
        if enable_video:
            x_search_config["enable_video_understanding"] = True
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
            headers={"Authorization": f"Bearer {self.xai_key}", "Content-Type": "application/json"},
            json=payload, timeout=90,
        )
        resp.raise_for_status()
        data = resp.json()
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
        urls = re.findall(r'https?://(?:x\.com|twitter\.com)/\S+', text)
        urls = [u.rstrip(".,;)\"'") for u in urls]
        return list(set(urls))

    def _x_api_get(self, path, params=None):
        if not self.x_bearer:
            raise ValueError("X_BEARER_TOKEN not set in .env. Get one at https://developer.x.com")
        resp = requests.get(
            f"{self.x_api_base}{path}",
            headers={"Authorization": f"Bearer {self.x_bearer}"},
            params=params or {}, timeout=30,
        )
        if resp.status_code == 429:
            reset = resp.headers.get("x-rate-limit-reset", "unknown")
            raise RuntimeError(f"X API rate limited. Resets at {reset}")
        resp.raise_for_status()
        return resp.json()

    def lookup_tweets(self, tweet_ids, include_metrics=True, include_author=True):
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
            params["user.fields"] = "username,name,verified,public_metrics,profile_image_url"
        if expansions:
            params["expansions"] = ",".join(expansions)
        data = self._x_api_get("/tweets", params)
        tweets = data.get("data", [])
        if include_author and "includes" in data:
            users_map = {u["id"]: u for u in data["includes"].get("users", [])}
            for tweet in tweets:
                author_id = tweet.get("author_id")
                if author_id and author_id in users_map:
                    tweet["author"] = users_map[author_id]
        return tweets

    def search_recent(self, query, max_results=10, sort_order="relevancy",
                      start_time=None, end_time=None, next_token=None):
        params = {
            "query": query[:512], "max_results": min(max_results, 100),
            "sort_order": sort_order,
            "tweet.fields": "created_at,text,author_id,public_metrics,conversation_id,lang",
            "expansions": "author_id",
            "user.fields": "username,name,verified,public_metrics",
        }
        if start_time: params["start_time"] = start_time
        if end_time: params["end_time"] = end_time
        if next_token: params["next_token"] = next_token
        data = self._x_api_get("/tweets/search/recent", params)
        tweets = data.get("data", [])
        if "includes" in data:
            users_map = {u["id"]: u for u in data["includes"].get("users", [])}
            for tweet in tweets:
                author_id = tweet.get("author_id")
                if author_id and author_id in users_map:
                    tweet["author"] = users_map[author_id]
        return {"tweets": tweets, "meta": data.get("meta", {})}

    def lookup_users(self, usernames=None, user_ids=None):
        params = {"user.fields": "created_at,description,public_metrics,verified,verified_type,profile_image_url,url,location"}
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

    def discover_and_enrich(self, query, days_back=7, max_enrich=10, **search_kwargs):
        discovery = self.search(query, days_back=days_back, **search_kwargs)
        tweet_ids = self._extract_tweet_ids(discovery["citations"])
        enriched = []
        if tweet_ids and self.x_bearer:
            enriched = self.lookup_tweets(tweet_ids[:max_enrich])
        return {
            "answer": discovery["answer"], "citations": discovery["citations"],
            "enriched_tweets": enriched, "usage": discovery["usage"],
        }

    def _extract_tweet_ids(self, urls):
        ids = []
        for url in urls:
            match = re.search(r'/status/(\d+)', url)
            if match:
                ids.append(match.group(1))
        return list(set(ids))
```

Also write an empty `__init__.py` in the same folder:

```bash
touch scripts/x_search/__init__.py
```

[VERIFY]
```bash
python3 -c "from scripts.x_search.client import XSearchClient; print('Client module loads OK')"
```
Expected: "Client module loads OK" (will fail if XAI_API_KEY is not set, that's fine at this stage. We just want the import to work structurally.)

---

## TEST

### Quick test

Ask Claude: **"What are people saying on X about AI agents this week?"**

Claude should use the x-search skill, call `client.search()` with `days_back=7`, and return a synthesized answer with cited posts. If it does, the module is working.

### Test with engagement data (if you set up the X bearer token)

Ask Claude: **"Search X for AI agents this week and show me the top posts by engagement."**

Claude should use `discover_and_enrich()` to find posts with Grok and then pull engagement metrics from the X API. You'll see like counts, retweet counts, and reply counts on the cited posts.

---

## WHAT'S NEXT

Claude can now search X for anything. Some things to try:

- **Competitor monitoring:** "What are people saying about [competitor] on X this month?"
- **Thought leader tracking:** "Search X for posts from @karpathy and @AnthropicAI about AI agents in the last 30 days"
- **Product launch sentiment:** "What's the reaction on X to [product name] launching?"
- **Industry pulse:** "What are the biggest AI discussions on X this week? Focus on agent frameworks and automation"
- **Engagement analysis:** "Find the most engaged-with posts about [topic] and break down why they performed well"

---

> A plug-and-play module from Liam Ottley's AAA Accelerator, the #1 AI business launch
> & AIOS program. Grab this and 15+ more at [aaaaccelerator.com](https://aaaaccelerator.com)
