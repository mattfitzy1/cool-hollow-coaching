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
