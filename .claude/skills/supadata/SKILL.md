---
name: supadata
description: >
  Fetch video transcripts and transcriptions from external URLs — YouTube transcripts, TikTok transcripts,
  Instagram, X, Facebook. Pull a transcript, get a transcription, extract captions from any video URL.
  Also: YouTube search (find videos, keyword research, competitor discovery), web scraping (scrape a page
  to markdown, crawl a website), social media metadata (views, likes, engagement stats), channel and
  playlist data.
user-invocable: false
---

# Supadata API

Content extraction API for YouTube, social media, and web pages. 21 endpoints, credit-based pricing.

## Authentication

- **API key env var:** `SUPADATA_API_KEY` (in `.env`)
- **Header:** `x-api-key: <key>`
- **Base URL:** `https://api.supadata.ai/v1`

## Python Client

A `supadata.py` client is available in the workspace. Import and use it like this:

```python
import os, sys
sys.path.insert(0, '.')
from supadata import SupadataClient

client = SupadataClient()  # reads SUPADATA_API_KEY from .env automatically

# Get a transcript as plain text
text = client.transcript_text("https://youtube.com/watch?v=VIDEO_ID")

# Search YouTube
results = client.youtube_search("AI agency", upload_date="month", sort_by="views")

# Scrape a webpage
page = client.web_scrape("https://example.com")
print(page["content"])  # clean markdown
```

## Key Methods

| Method | What It Does | Credits |
|--------|-------------|---------|
| `transcript_text(url)` | Get transcript as plain string — YouTube, TikTok, IG, X, FB | 1 |
| `transcript(url, text=False)` | Full transcript with timestamps/chunks | 1 |
| `youtube_search(query, upload_date=, sort_by=, duration=, limit=)` | Search YouTube | 1/page |
| `youtube_video(url_or_id)` | Video metadata (title, views, duration, channel) | 1 |
| `youtube_channel(id_or_handle)` | Channel stats (subscribers, videos, total views) | 1 |
| `youtube_channel_videos(id_or_handle, limit=)` | List video IDs from a channel | 1 |
| `youtube_playlist_videos(id_or_url, limit=)` | List video IDs from a playlist | 1 |
| `metadata(url)` | Social post metadata — views, likes, author, etc. | 1 |
| `web_scrape(url)` | Scrape any webpage to clean markdown | 1 |
| `web_map(url)` | Discover all URLs linked from a page | 1 |
| `me()` | Check credits remaining | 1 |

## Search Parameters

`youtube_search` supports these filters:
- `upload_date`: `all`, `hour`, `today`, `week`, `month`, `year`
- `type`: `all`, `video`, `channel`, `playlist`, `movie`
- `duration`: `short` (<4m), `medium` (4-20m), `long` (>20m)
- `sort_by`: `relevance`, `rating`, `date`, `views`

## Async Jobs

Videos longer than 20 minutes and batch/crawl operations return `{"jobId": "..."}` instead of results. Poll with the corresponding `_status()` method until `status == "completed"`.

```python
job = client.transcript("https://youtube.com/watch?v=LONG_VIDEO")
if "jobId" in job:
    import time
    while True:
        status = client.transcript_status(job["jobId"])
        if status["status"] == "completed":
            print(status["content"])
            break
        time.sleep(5)
```

## Supported Platforms

- **Transcripts:** YouTube, TikTok, Instagram, X (Twitter), Facebook
- **Metadata:** YouTube, TikTok, Instagram, X, Facebook
- **Not supported:** Live streams in progress, private/unlisted videos, YouTube Music

## Error Reference

| Code | Meaning |
|------|---------|
| 401 | Invalid API key |
| 402 | Out of credits or plan limit |
| 429 | Rate limit hit — slow down |
| `transcript-unavailable` | No transcript exists (still costs 1 credit) |

## Relationship to Other Tools

- **YouTube transcripts only, no API key needed:** use the existing `/assess-video` skill (youtube-transcript-api). Supadata is the upgrade path when you need non-YouTube transcripts, search, or metadata.
- **Web scraping:** prefer `/firecrawl` (higher credit limit, already set up). Supadata's `web_scrape` is available as a backup.
