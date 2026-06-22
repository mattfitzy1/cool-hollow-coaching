# Substack Search — AIOS Module Installer

> A plug-and-play module from the AAA Accelerator.
> Grab this and 15+ more at [aaaaccelerator.com](https://aaaaccelerator.com)

---

## FOR CLAUDE

You are helping a user install this AIOS Module. Follow these rules:

**Behavior:**
- Assume the user is non-technical unless they tell you otherwise
- Explain what you are doing at each step in plain English BEFORE doing it
- Celebrate small wins ("Substack search is ready — Claude can now find and read any newsletter on the internet!")
- If something fails, do not dump error logs — explain the problem simply and suggest the fix
- Never skip verification steps
- Use encouraging language throughout

**Pacing:**
- Do NOT rush. Pause after major milestones.
- After prerequisites: "Everything looks good. Ready to install?"
- After installation: "Files are in place. Let's run a quick test."
- After test: "You're all set! Here's what Claude can do with Substack."

**Error handling:**
- If Firecrawl isn't installed: tell them to install the Firecrawl module first
- If test returns connection error: check internet
- If Substack returns 429: normal rate limiting, the client handles it automatically
- Never say "check the logs"

---

## OVERVIEW

This module gives Claude the ability to search Substack newsletters on any topic and extract full article content. It uses a two-layer architecture: Firecrawl searches Google to discover relevant Substack posts, then Substack's undocumented API pulls full article text with metadata (reactions, word count, comments, audience type).

No Substack API key needed. The entire content layer runs on Substack's public endpoints.

**What Claude can do after this is installed:**
- Search for Substack posts on any topic via Google
- Read full newsletter articles as clean plain text
- Browse a publication's archive (newest or top-performing)
- Discover which Substack authors write about a given subject
- Run a full research pipeline: search, discover, and extract in one call

**Where it installs:** `.claude/skills/substack/` for the skill file, `scripts/substack/` for the Python client.

**Setup time:** 3-5 minutes.

**Running cost:** Zero for Substack content. Firecrawl credits for the search/discovery layer (typically 1 credit per search).

---

## SCOPING

This module installs as one unit: a Python client and a Claude Code skill file. Nothing optional to skip.

Ask: "Ready to install? Takes about 3-5 minutes."

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

### Firecrawl module

The search layer depends on Firecrawl to discover Substack posts via Google.

```bash
firecrawl --version
```

Expected: A version number. If you get "command not found", the Firecrawl module needs to be installed first. It's a separate module in the Module Library. Install that one, then come back here.

[VERIFY] All three checks pass.

Ask: "Everything looks good. Ready to install?"

---

## INSTALL

### Step 1: Create the folders

```bash
mkdir -p .claude/skills/substack
mkdir -p scripts/substack
```

### Step 2: Install the Substack skill

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
  For YouTube/TikTok/Instagram, use Supadata. For web articles, use Firecrawl.
  For X/Twitter, use x-search. For Reddit, use reddit.
user-invocable: false
effort: low
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
    "AI product management specs",
    max_posts=5,       # how many posts to extract in full
    search_limit=10,   # how many search results to consider
)

print(f"Found {result['search_results_count']} results")
print(f"Extracted {result['extracted_count']} full posts")

for p in result["extracted_posts"]:
    print(f"\n[{p['publication']}] {p['title']}")
    print(f"  {p['wordcount']} words, {p['reactions']}")
    print(f"  {p['body'][:300]}...")
```

### Response Shape

```python
{
    "query": "AI product management specs",
    "search_results_count": 10,
    "search_results": [
        {"title": "...", "url": "...", "publication": "addyo", "slug": "how-to-write-specs"}
    ],
    "extracted_count": 5,
    "extracted_posts": [
        {
            "title": "How to write a good spec for AI agents",
            "slug": "how-to-write-specs",
            "date": "2026-02-14T...",
            "body": "full plain text content...",
            "body_length": 43683,
            "wordcount": 7093,
            "reactions": {"❤": 245},
            "comment_count": 18,
            "publication": "addyo",
            "url": "https://addyo.substack.com/p/how-to-write-specs",
        }
    ]
}
```

## Individual Methods

### Search for Posts

```python
# Find Substack posts on any topic
results = client.search("AI coding agents", limit=10)
for r in results:
    print(f"[{r['publication']}] {r['title']}")
    print(f"  {r['url']}")
```

### Discover Publications

```python
# Find which Substack authors write about a topic
pubs = client.discover_publications("artificial intelligence", limit=10)
for p in pubs:
    print(f"{p['publication']} — {p['url']}")
```

### Browse a Publication

```python
# List recent posts from a known publication
posts = client.list_posts("oneusefulthing", limit=10, sort="new")
for p in posts:
    hearts = p.get("reactions", {}).get("❤", 0)
    print(f"[{hearts} ❤] {p['title']} ({p['wordcount']} words)")

# Also works with sort="top"
top_posts = client.list_posts("pragmaticengineer", limit=5, sort="top")
```

### Read Full Post

```python
# Get full article content as plain text
post = client.get_post("oneusefulthing", "the-shape-of-the-thing")
print(post["title"])
print(post["body"])       # clean plain text (HTML stripped)
print(post["wordcount"])
print(post["reactions"])

# Get raw HTML instead
post_html = client.get_post("oneusefulthing", "the-shape-of-the-thing", as_text=False)
print(post_html["body"])  # raw HTML
```

## Known Publications (AI/Tech)

| Publication | Subdomain | Known For |
|------------|-----------|-----------|
| One Useful Thing | `oneusefulthing` | Ethan Mollick, AI strategy and research |
| Pragmatic Engineer | `pragmaticengineer` | Gergely Orosz, software engineering |
| Lenny's Newsletter | `lennysnewsletter` | Product management |
| Stratechery | `stratechery` | Ben Thompson, tech strategy |
| The Gradient | `thegradient` | AI/ML research |
| AI Supremacy | `aisupremacy` | AI industry analysis |

## Rate Limits

| Layer | Limit |
|-------|-------|
| Firecrawl search | Per Firecrawl plan credits |
| Substack API | ~10-20 req/min before 429 |
| Client delay | 2s between Substack API calls |
| Typical research() call | 1 Firecrawl + 3-5 API calls, ~15 seconds |

The client handles rate limiting automatically. On 429, waits 10 seconds and retries.

## Paywalled Content

Free posts return full HTML body. Paywalled (subscriber-only) posts return truncated content. The `audience` field tells you: `"everyone"` = free, `"only_paid"` = paywalled.
````

[VERIFY]
```bash
cat .claude/skills/substack/SKILL.md | head -5
```
Expected: File starts with `---` (YAML frontmatter).

### Step 3: Create the Python package files

Write an empty file to `scripts/substack/__init__.py`:

```python
# Substack search and content extraction client
```

### Step 4: Install the Substack client

Write the following file to `scripts/substack/client.py`:

```python
"""
Substack Search & Content Client

Usage:
    from scripts.substack.client import SubstackClient
    client = SubstackClient()
    results = client.search("AI coding agents")
    post = client.get_post("oneusefulthing", "the-shape-of-the-thing")
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


def _find_and_load_env():
    current = Path(__file__).resolve().parent
    for _ in range(5):
        candidate = current / ".env"
        if candidate.exists():
            load_dotenv(candidate)
            return
        current = current.parent

_find_and_load_env()

_last_substack_request = 0.0


def _rate_limit(min_delay=2.0):
    global _last_substack_request
    elapsed = time.time() - _last_substack_request
    if elapsed < min_delay:
        time.sleep(min_delay - elapsed)
    _last_substack_request = time.time()


def _strip_html(html):
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
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept": "application/json",
        })

    def search(self, query, limit=10):
        try:
            result = subprocess.run(
                ["firecrawl", "search", f"{query} site:substack.com",
                 "--limit", str(limit), "--json"],
                capture_output=True, text=True, timeout=60,
                cwd=str(Path(__file__).resolve().parent.parent.parent),
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
            results = []
            for item in items[:limit]:
                url = item.get("url", item.get("metadata", {}).get("sourceURL", ""))
                title = item.get("title", item.get("metadata", {}).get("title", ""))
                desc = item.get("description", item.get("metadata", {}).get("description", ""))
                pub, slug = self._parse_substack_url(url)
                results.append({"title": title, "url": url, "description": desc,
                               "publication": pub, "slug": slug})
            return results
        except Exception as e:
            print(f"Firecrawl search failed: {e}")
            return []

    def _parse_substack_url(self, url):
        match = re.search(r'(?:https?://)?([^./]+)\.substack\.com/p/([^/?#]+)', url)
        if match:
            return match.group(1), match.group(2)
        match = re.search(r'open\.substack\.com/pub/([^/]+)/p/([^/?#]+)', url)
        if match:
            return match.group(1), match.group(2)
        slug = ""
        pub = ""
        match = re.search(r'/p/([^/?#]+)', url)
        if match:
            slug = match.group(1)
            domain_match = re.search(r'https?://(?:www\.)?([^./]+)', url)
            if domain_match:
                pub = domain_match.group(1)
        return pub, slug

    def _api_get(self, base_url, path, params=None):
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
        for base in [f"{publication}.substack.com", f"www.{publication}.com", publication]:
            data = self._api_get(base, "/archive", {"sort": sort, "limit": limit, "offset": offset})
            if data and isinstance(data, list):
                return [{"title": p.get("title", ""), "slug": p.get("slug", ""),
                         "date": p.get("post_date", ""), "wordcount": p.get("wordcount", 0),
                         "reactions": p.get("reactions", {}), "subtitle": p.get("subtitle", ""),
                         "audience": p.get("audience", ""), "comment_count": p.get("comment_count", 0),
                         "publication": publication,
                         "url": f"https://{base}/p/{p.get('slug', '')}"} for p in data]
        return []

    def get_post(self, publication, slug, as_text=True):
        for base in [f"{publication}.substack.com", f"www.{publication}.com", publication]:
            data = self._api_get(base, f"/posts/{slug}")
            if data and isinstance(data, dict) and data.get("title"):
                body_html = data.get("body_html", "") or ""
                body = _strip_html(body_html) if as_text else body_html
                return {"title": data.get("title", ""), "slug": slug,
                        "date": data.get("post_date", ""), "body": body,
                        "body_length": len(body), "wordcount": data.get("wordcount", 0),
                        "reactions": data.get("reactions", {}),
                        "comment_count": data.get("comment_count", 0),
                        "subtitle": data.get("subtitle", ""),
                        "audience": data.get("audience", ""),
                        "publication": publication,
                        "url": f"https://{base}/p/{slug}",
                        "canonical_url": data.get("canonical_url", "")}
        return None

    def research(self, query, max_posts=5, search_limit=10):
        search_results = self.search(query, limit=search_limit)
        extracted = []
        for result in search_results[:max_posts]:
            pub = result.get("publication", "")
            slug = result.get("slug", "")
            if not pub or not slug:
                continue
            post = self.get_post(pub, slug)
            if post and post.get("body"):
                extracted.append(post)
        return {"query": query, "search_results_count": len(search_results),
                "search_results": search_results, "extracted_count": len(extracted),
                "extracted_posts": extracted}

    def discover_publications(self, query, limit=10):
        results = self.search(query, limit=limit)
        pubs = {}
        for r in results:
            pub = r.get("publication", "")
            if pub and pub not in pubs and pub != "open":
                pubs[pub] = {"publication": pub, "url": f"https://{pub}.substack.com",
                            "found_via": r.get("title", "")}
        return list(pubs.values())
```

[VERIFY]
```bash
python3 -c "from scripts.substack.client import SubstackClient; print('Client loaded')"
```
Expected: `Client loaded`. If it fails with an import error, check that `requests` and `python-dotenv` are installed.

---

## TEST

Ask Claude:

> "Search Substack for articles about AI agents and summarize the top 3"

Claude should use the Substack skill to search, extract full articles, and give you a summary with titles, authors, and key points from each post. If it does, everything is working.

---

## WHAT'S NEXT

Claude can now search and read any Substack newsletter. Some things to try:

- **Thought leader research:** "Find what Ethan Mollick has written about AI agents recently"
- **Newsletter analysis:** "List the top 10 posts from pragmaticengineer by engagement and summarize the themes"
- **Competitive intelligence:** "Search Substack for articles about AI automation agencies and pull the key insights"
- **Topic deep-dive:** "Research what Substack writers are saying about Claude Code and summarize the consensus"
- **Publication discovery:** "Find the best Substack newsletters covering AI startups"

---

> A plug-and-play module from Liam Ottley's AAA Accelerator — the #1 AI business launch
> & AIOS program. Grab this and 15+ more at [aaaaccelerator.com](https://aaaaccelerator.com)
