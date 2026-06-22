# Podcast Search — AIOS Module Installer

> A plug-and-play module from the AAA Accelerator.
> Grab this and 15+ more at [aaaaccelerator.com](https://aaaaccelerator.com)

---

## FOR CLAUDE

You are helping a user install this AIOS Module. Follow these rules:

**Behavior:**
- Assume the user is non-technical unless they tell you otherwise
- Explain what you are doing at each step in plain English BEFORE doing it
- Celebrate small wins ("Podcast Search is installed — Claude can now find podcast episodes on any topic and pull full transcripts!")
- If something fails, do not dump error logs — explain the problem simply and suggest the fix
- Never skip verification steps — if a check fails, stop and help the user fix it
- Use encouraging language throughout

**Pacing:**
- Do NOT rush. Pause after major milestones.
- After prerequisites: "Everything looks good. Ready to install?"
- After file creation: "Files are in place. Let's run a quick test."
- After test: "You're all set. Here's what Claude can do with Podcast Search."

**Error handling:**
- If Firecrawl CLI is missing: they need the Firecrawl module installed first — point them to it
- If SUPADATA_API_KEY is missing from .env: they need the Supadata module installed first — point them to it
- If `.claude/` folder doesn't exist: they need Claude Code installed first
- If files already exist at the target paths: ask before overwriting
- Never say "check the logs" — find the problem and explain it

---

## OVERVIEW

This module gives Claude the ability to find podcast episodes on any topic, rank them by quality, and extract full transcripts. It combines two discovery layers: Firecrawl searches Google for episodes across Apple Podcasts, Spotify, YouTube, and podcast sites. Supadata searches YouTube directly and extracts transcripts. Quality scoring ranks every discovered episode from 0-100 based on view count, duration, and source authority.

**What Claude can do after this is installed:**
- Search for podcast episodes on any topic across all major platforms
- Rank discovered episodes by a quality score (views, duration, known authority hosts)
- Pull full transcripts from YouTube episodes via Supadata
- Run the full pipeline in one call: discover, rank, extract top transcripts

**Where it installs:** Into `.claude/skills/` and `scripts/podcast-search/` in your current workspace.

**Setup time:** 5 minutes (files only, no new API keys needed).

**Running cost:** Uses credits from your existing Firecrawl and Supadata accounts. A typical research query costs roughly 5 Firecrawl credits and 14 Supadata credits.

---

## PREREQUISITES

### Firecrawl module

```bash
firecrawl --version
```

Expected: A version number. If you get "command not found", install the Firecrawl module first (it's a separate module in the Module Library).

### Supadata module

```bash
grep SUPADATA_API_KEY .env
```

Expected: A line showing your Supadata API key. If nothing appears, install the Supadata module first (it's a separate module in the Module Library).

### Python and pip

```bash
python3 --version && pip3 --version
```

If Python isn't installed: download from https://python.org.

### Python dependencies

```bash
pip3 install requests python-dotenv
```

[VERIFY] All checks pass without errors.

Ask: "Everything looks good. Ready to install?"

---

## INSTALL

### Step 1: Create the folders

```bash
mkdir -p .claude/skills/podcast-search
mkdir -p scripts/podcast_search
```

### Step 2: Install the Podcast Search skill

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
effort: low
---

# Podcast Episode Search & Transcripts

Find podcast episodes on any topic across all platforms, rank by quality, and extract full transcripts from YouTube. Two discovery layers (Google + YouTube), quality scoring, and Supadata transcript extraction.

## Setup

```python
import importlib.util, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(".")), "scripts"))
spec = importlib.util.spec_from_file_location("podcast_search_client",
    os.path.join(os.path.dirname(os.path.abspath(".")), "scripts/podcast_search/client.py"))
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
client = mod.PodcastSearchClient()
```

**Env vars:** Uses `FIRECRAWL_API_KEY` and `SUPADATA_API_KEY` (both from `.env`).

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
    max_transcripts=3,    # how many transcripts to pull
    search_limit=10,      # Firecrawl results
    youtube_limit=10,     # YouTube results
    min_quality_score=55, # minimum score for transcript extraction
    upload_date="year",   # YouTube recency filter
)

print(f"Discovered {result['total_discovered']} episodes")
print(f"Extracted {result['transcripts_extracted']} transcripts")

for ep in result["episodes"][:5]:
    has_t = "transcript" in ep
    print(f"[score:{ep['quality_score']:.0f}] {ep['title'][:60]}")
    if has_t:
        print(f"  Transcript: {ep['transcript_length']:,} chars")
        print(f"  Preview: {ep['transcript'][:200]}...")
```

### How the Pipeline Works

```
1. Firecrawl search: "{topic} podcast episode interview" — finds Apple Podcasts, Spotify, YouTube, podcast sites
2. YouTube search: "{topic} podcast interview" (long duration, sorted by views) — finds high-view interviews
3. Merge + deduplicate (by YouTube ID and URL)
4. Quality score all episodes (0-100)
5. Sort by score descending
6. Extract transcripts from top N YouTube episodes (Supadata)
```

## Quality Scoring (0-100)

Every discovered episode gets a quality score. Use this to pick which episodes are worth pulling transcripts from.

| Signal | Score Impact |
|--------|-------------|
| Views > 1M | +25 |
| Views > 500K | +20 |
| Views > 100K | +15 |
| Views > 50K | +10 |
| Duration 20-120 min (interview sweet spot) | +10 |
| Known authority source (Lex Fridman, YC, a16z, No Priors, Hormozi, etc.) | +10 |
| YouTube source (transcript extractable) | +5 |
| Noise signal (#shorts, "60 seconds", clip) | -20 |

## Search Strategies

### For a specific topic
```python
# Broad search across all platforms
episodes = client.search("autonomous AI coding teams", limit=10)

# YouTube-focused (better for known podcast interviews)
episodes = client.youtube_search("AI coding agents", limit=10, upload_date="year")
```

### For recent content
```python
episodes = client.youtube_search("Claude Code", upload_date="month", limit=10)
```

### For a specific person's podcast appearances
```python
episodes = client.search("Peter Steinberger interview podcast", limit=10)
episodes += client.youtube_search("Peter Steinberger", limit=5)
```

### Getting transcripts from known URLs
```python
transcript = client.get_transcript("https://youtube.com/watch?v=VIDEO_ID")
# Returns plain text string or None
```

## YouTube Search Parameters

| Parameter | Type | Default | Values |
|-----------|------|---------|--------|
| `upload_date` | str | `"year"` | `hour`, `today`, `week`, `month`, `year` |
| `duration` | str | `"long"` | `short` (<4min), `medium` (4-20min), `long` (>20min) |
| `limit` | int | 10 | Max results |

For podcast interviews, always use `duration="long"` to filter out clips and shorts.

## Known Authority Sources

The quality scorer gives bonus points to these podcast networks/hosts:

Lex Fridman, Dwarkesh Patel, Y Combinator, a16z, No Priors, All-In, Acquired, My First Million, Lenny's Podcast, Software Engineering Daily, Changelog, Practical AI, ML Street Talk, Replit, Hormozi, Huberman, Tim Ferriss, Joe Rogan

Add more by editing the `authority_signals` list in `scripts/podcast_search/client.py`.
````

[VERIFY]
```bash
cat .claude/skills/podcast-search/SKILL.md | head -5
```
Expected: File starts with `---` (YAML frontmatter).

### Step 3: Install the Python client

Write the following file to `scripts/podcast_search/__init__.py`:

```python
"""Podcast Search module."""
```

Write the following file to `scripts/podcast_search/client.py`:

````python
"""
Podcast Search & Transcript Client

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


def _score_episode(episode):
    score = 50.0
    views = episode.get("views", 0)
    if isinstance(views, str):
        views = int(views) if views.isdigit() else 0
    if views > 1_000_000: score += 25
    elif views > 500_000: score += 20
    elif views > 100_000: score += 15
    elif views > 50_000: score += 10
    elif views > 10_000: score += 5
    elif views > 0: score += 2

    duration_min = episode.get("duration_min", 0)
    if 20 <= duration_min <= 120: score += 10
    elif 10 <= duration_min < 20: score += 3
    elif duration_min > 120: score += 5

    source = episode.get("source", "")
    if source == "youtube": score += 5
    elif source == "apple_podcasts": score += 3

    title_lower = (episode.get("title", "") + " " + episode.get("show", "") + " " + episode.get("channel", "")).lower()
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

    noise_signals = ["shorts", "tiktok", "#shorts", "60 seconds", "in 1 minute", "clip"]
    for noise in noise_signals:
        if noise in title_lower:
            score -= 20
            break

    return min(max(score, 0), 100)


class PodcastSearchClient:
    def __init__(self):
        self._supadata = None

    @property
    def supadata(self):
        if self._supadata is None:
            self._supadata = _get_supadata()
        return self._supadata

    def search(self, query, limit=10):
        try:
            result = subprocess.run(
                ["firecrawl", "search", f"{query} podcast episode interview",
                 "--limit", str(limit), "--json"],
                capture_output=True, text=True, timeout=60,
                cwd=str(_ROOT_DIR),
            )
            if result.returncode != 0:
                return []
            data = json.loads(result.stdout)
            items = []
            if isinstance(data, dict):
                web = data.get("data", {}).get("web", data.get("results", []))
                if isinstance(web, list): items = web
            elif isinstance(data, list):
                items = data
            episodes = []
            for item in items[:limit]:
                url = item.get("url", item.get("metadata", {}).get("sourceURL", ""))
                title = item.get("title", item.get("metadata", {}).get("title", ""))
                desc = item.get("description", item.get("metadata", {}).get("description", ""))
                source = "web"
                if "youtube.com" in url or "youtu.be" in url: source = "youtube"
                elif "podcasts.apple.com" in url: source = "apple_podcasts"
                elif "spotify.com" in url: source = "spotify"
                elif "podcast" in url.lower(): source = "podcast_site"
                yt_id = ""
                if source == "youtube":
                    match = re.search(r'(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})', url)
                    if match: yt_id = match.group(1)
                ep = {"title": title, "url": url, "description": desc[:300] if desc else "",
                      "source": source, "youtube_id": yt_id, "show": "", "channel": "",
                      "views": 0, "duration_min": 0}
                ep["quality_score"] = _score_episode(ep)
                episodes.append(ep)
            episodes.sort(key=lambda x: x["quality_score"], reverse=True)
            return episodes
        except Exception as e:
            print(f"Firecrawl search failed: {e}")
            return []

    def youtube_search(self, query, limit=10, upload_date="year", duration="long"):
        try:
            results = self.supadata.youtube_search(
                f"{query} podcast interview",
                upload_date=upload_date, sort_by="views", duration=duration, limit=limit,
            )
            items = results.get("results", []) if isinstance(results, dict) else []
            episodes = []
            for item in items:
                vid_id = item.get("id", item.get("videoId", ""))
                channel = item.get("channelTitle", "")
                if isinstance(channel, dict): channel = channel.get("name", "")
                views = item.get("viewCount", item.get("views", 0))
                if isinstance(views, str): views = int(views) if views.isdigit() else 0
                duration_val = item.get("duration", "")
                duration_min = 0
                if isinstance(duration_val, str) and ":" in duration_val:
                    parts = duration_val.split(":")
                    if len(parts) == 3: duration_min = int(parts[0]) * 60 + int(parts[1])
                    elif len(parts) == 2: duration_min = int(parts[0])
                elif isinstance(duration_val, (int, float)):
                    duration_min = int(duration_val / 60) if duration_val > 1000 else int(duration_val)
                ep = {"title": item.get("title", ""), "url": f"https://youtube.com/watch?v={vid_id}",
                      "youtube_id": vid_id, "channel": channel, "views": views,
                      "duration_min": duration_min, "published": item.get("publishedAt", ""),
                      "source": "youtube", "show": channel, "description": item.get("description", "")[:300]}
                ep["quality_score"] = _score_episode(ep)
                episodes.append(ep)
            episodes.sort(key=lambda x: x["quality_score"], reverse=True)
            return episodes
        except Exception as e:
            print(f"YouTube search failed: {e}")
            return []

    def get_transcript(self, url):
        try:
            return self.supadata.transcript_text(url)
        except Exception as e:
            print(f"Transcript extraction failed for {url}: {e}")
            return None

    def research(self, query, max_transcripts=3, search_limit=10, youtube_limit=10,
                 min_quality_score=55, upload_date="year"):
        firecrawl_results = self.search(query, limit=search_limit)
        youtube_results = self.youtube_search(query, limit=youtube_limit, upload_date=upload_date)
        all_episodes = []
        seen_ids, seen_urls = set(), set()
        for ep in youtube_results + firecrawl_results:
            yt_id = ep.get("youtube_id", "")
            url = ep.get("url", "")
            if yt_id and yt_id in seen_ids: continue
            if url and url in seen_urls: continue
            if yt_id: seen_ids.add(yt_id)
            if url: seen_urls.add(url)
            all_episodes.append(ep)
        all_episodes.sort(key=lambda x: x.get("quality_score", 0), reverse=True)
        transcripts_extracted = 0
        for ep in all_episodes:
            if transcripts_extracted >= max_transcripts: break
            if ep.get("quality_score", 0) < min_quality_score: break
            if ep.get("source") != "youtube" or not ep.get("youtube_id"): continue
            transcript = self.get_transcript(ep["url"])
            if transcript:
                ep["transcript"] = transcript
                ep["transcript_length"] = len(transcript)
                transcripts_extracted += 1
        return {"query": query, "total_discovered": len(all_episodes),
                "transcripts_extracted": transcripts_extracted, "episodes": all_episodes}
````

[VERIFY]
```bash
ls scripts/podcast_search/client.py scripts/podcast_search/__init__.py
```
Expected: Both files listed.

---

## TEST

Ask Claude: "Find podcast episodes about AI coding agents and get the transcript of the best one"

Claude should use the Podcast Search skill, discover episodes across Google and YouTube, rank them by quality score, pull the transcript from the highest-scoring YouTube episode, and present a summary. If it does, the module is fully installed.

If the test fails:
- "Firecrawl search failed" — check that `firecrawl --version` works and `firecrawl init` has been run with your API key
- "SupadataClient not found" — make sure `supadata.py` exists in your workspace root or at `scripts/utils/supadata.py`
- "SUPADATA_API_KEY not set" — check your `.env` file has the key

---

## WHAT'S NEXT

Claude can now research any topic through podcast conversations. Some things to try:

- **Expert interview research:** "Find the best podcast interviews about building AI agents and summarise the key insights from the top 3"
- **Competitor podcast analysis:** "Search for podcast episodes where [competitor name] has been interviewed and pull the transcripts"
- **Topic landscape mapping:** "Find 15 podcast episodes about AI in healthcare, rank them, and give me a summary of the main themes across the top 5"
- **Person research:** "Find all podcast appearances by [person name] in the last year and pull transcripts from the best ones"
- **Content research:** "What are the most-viewed podcast interviews about [topic] this year? Get transcripts from the top 3"

---

> A plug-and-play module from Liam Ottley's AAA Accelerator — the #1 AI business launch
> & AIOS program. Grab this and 15+ more at [aaaaccelerator.com](https://aaaaccelerator.com)
