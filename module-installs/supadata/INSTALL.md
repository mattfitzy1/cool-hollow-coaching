# Supadata — AIOS Module Installer

> A plug-and-play module from the AAA Accelerator.
> Grab this and 15+ more at [aaaaccelerator.com](https://aaaaccelerator.com)

---

## FOR CLAUDE

You are helping a user install this AIOS Module. Follow these rules:

**Behavior:**
- Assume the user is non-technical unless they tell you otherwise
- Explain what you are doing at each step in plain English BEFORE doing it
- Celebrate small wins ("Supadata is connected — Claude can now pull transcripts from any YouTube video!")
- If something fails, do not dump error logs — explain the problem simply and suggest the fix
- Never skip verification steps — if a check fails, stop and help the user fix it
- Use encouraging language throughout — they are building something real

**Pacing:**
- Do NOT rush. Pause after major milestones.
- After prerequisites: "Everything looks good. Ready to install?"
- After API key setup: "Key is in place. Now let's install the skill and client."
- After installation: "Files are in place. Let's run a quick test."
- After test: "You're all set! Here's what Claude can do with Supadata."

**Error handling:**
- If `.claude/` folder doesn't exist → they need Claude Code installed first
- If files already exist at the target paths → ask before overwriting
- If the test returns a 401 error → API key is wrong or not saved correctly
- If the test returns a 402 error → account needs credits or a paid plan
- Never say "check the logs" — find the problem and explain it

---

## OVERVIEW

This module gives Claude the ability to pull content from anywhere on the internet — YouTube transcripts, TikTok captions, social media metadata, and web pages — using the Supadata API.

Here's the problem it solves: Claude can't access the internet by default. If you want Claude to read a YouTube video, scrape a competitor's site, or pull transcript data for analysis, it can't. This module fixes that. Once installed, Claude knows how to call Supadata's API and can do it any time you ask.

**What Claude can do after this is installed:**
- Pull the full transcript of any YouTube video (or TikTok, Instagram, X, Facebook)
- Search YouTube and return results with view counts, durations, upload dates
- Get metadata from any social post — views, likes, comments, author
- Scrape any webpage to clean markdown
- Get channel stats, playlist video lists, video metadata
- Extract structured data from video content (free during beta)

**Where it installs:** Into `.claude/skills/` in your current workspace, plus a reusable `supadata.py` client script your own code can import.

**Setup time:** 5-10 minutes (API key + files).

**Running cost:** Credit-based. Most operations cost 1 credit. Free plan available at supadata.ai. 1 credit = one transcript, one search page, one scrape, etc.

---

## SCOPING

**RECOMMENDED** (full install — skill + Python client)
- The Supadata skill (Claude knows all 21 API endpoints and when to use them)
- A standalone `supadata.py` client script (reusable in your own Python projects)
- API key wired into your `.env` file

**CUSTOM** (skill only)
- Option: Skip the Python client if you're not writing Python scripts and just want Claude to call the API conversationally

Ask: "Want to go with RECOMMENDED, or just install the skill without the Python client?"

---

## PREREQUISITES

### Claude Code CLI
```bash
claude --version
```
If not installed:
```bash
npm install -g @anthropic-ai/claude-code
```

### Workspace .claude/ folder
```bash
ls .claude/
```
If it doesn't exist:
```bash
mkdir -p .claude/skills
```

### Python and pip (for the client script)
```bash
python3 --version && pip3 --version
```
If Python isn't installed: download from https://python.org (click Downloads, install the latest version).

### Install Python dependencies
```bash
pip3 install requests python-dotenv
```

[VERIFY] All checks pass without errors.

Ask: "Everything looks good. Ready to set up your Supadata API key?"

---

## API KEY SETUP

### Get your Supadata API key

1. Go to https://supadata.ai
2. Click **Sign Up** (or Sign In if you already have an account)
3. Once logged in, go to your **Dashboard**
4. Click **API Keys** in the left sidebar
5. Click **Create API Key**, give it a name (e.g. "claude-workspace")
6. Copy the key — it starts with `supa_`

### Add it to your workspace

Check if you already have a `.env` file:
```bash
ls .env
```

**If the file exists** — add this line to it:
```
SUPADATA_API_KEY=supa_your_key_here
```

**If it doesn't exist** — create it:
```bash
echo "SUPADATA_API_KEY=supa_your_key_here" > .env
```

Replace `supa_your_key_here` with your actual key.

[VERIFY]
```bash
grep SUPADATA_API_KEY .env
```
Expected: The line with your key appears.

Ask: "Key is saved. Ready to install the skill and client files?"

---

## INSTALL

### Step 1: Create the skill folder

```bash
mkdir -p .claude/skills/supadata
```

### Step 2: Install the Supadata skill

Write the following file to `.claude/skills/supadata/SKILL.md`:

````markdown
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
````

[VERIFY]
```bash
cat .claude/skills/supadata/SKILL.md | head -5
```
Expected: File starts with `---` (YAML frontmatter).

### Step 3: Install the Python client (RECOMMENDED only)

Write the following file to `supadata.py` in your workspace root:

````python
"""
Supadata API client — standalone version.

Drop this file anywhere in your project and import it.

Usage:
    from supadata import SupadataClient

    client = SupadataClient()  # reads SUPADATA_API_KEY from .env
    text = client.transcript_text("https://youtube.com/watch?v=VIDEO_ID")
"""

import os
import requests

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv optional — will fall back to os.environ

BASE_URL = "https://api.supadata.ai/v1"


class SupadataClient:
    """Thin wrapper around the Supadata REST API (21 endpoints)."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.environ.get("SUPADATA_API_KEY")
        if not self.api_key:
            raise ValueError(
                "SUPADATA_API_KEY not set. Add it to your .env file or pass api_key= directly."
            )
        self._headers = {"x-api-key": self.api_key}

    def _get(self, path: str, params: dict | None = None, timeout: int = 30) -> dict:
        resp = requests.get(
            f"{BASE_URL}{path}", params=params, headers=self._headers, timeout=timeout
        )
        resp.raise_for_status()
        return resp.json()

    def _post(self, path: str, json_body: dict | None = None, timeout: int = 30) -> dict:
        resp = requests.post(
            f"{BASE_URL}{path}", json=json_body, headers=self._headers, timeout=timeout
        )
        resp.raise_for_status()
        return resp.json()

    # ── Transcripts ──────────────────────────────────────────────────────────

    def transcript(self, url: str, *, lang: str | None = None, text: bool = False,
                   chunk_size: int | None = None, mode: str | None = None) -> dict:
        """Universal transcript — YouTube, TikTok, Instagram, X, Facebook.

        Returns dict with 'content' (string if text=True, list of segments otherwise),
        'lang', and 'availableLangs'. Videos >20 min return {'jobId': '...'}.
        Credits: 1 (native captions) or 2/min (AI-generated).
        """
        params = {"url": url}
        if lang: params["lang"] = lang
        if text: params["text"] = "true"
        if chunk_size: params["chunkSize"] = chunk_size
        if mode: params["mode"] = mode
        return self._get("/transcript", params)

    def transcript_text(self, url: str, *, lang: str | None = None) -> str | None:
        """Get transcript as plain text string, or None if unavailable.

        This is the most common usage — call this first.
        Credits: 1.
        """
        try:
            data = self.transcript(url, text=True, lang=lang)
            content = data.get("content", "")
            if isinstance(content, str) and content.strip():
                return content.strip()
            if isinstance(content, list) and content:
                return " ".join(item.get("text", "") for item in content).strip()
        except requests.HTTPError:
            pass
        return None

    def transcript_status(self, job_id: str) -> dict:
        """Poll async transcript job. Credits: 0."""
        return self._get(f"/transcript/{job_id}")

    def youtube_transcript_translate(self, url_or_id: str, target_lang: str,
                                     *, text: bool = False) -> dict:
        """Translate YouTube transcript. Credits: 30/min of video."""
        params = {"lang": target_lang}
        if url_or_id.startswith("http"):
            params["url"] = url_or_id
        else:
            params["videoId"] = url_or_id
        if text: params["text"] = "true"
        return self._get("/youtube/transcript/translate", params, timeout=120)

    def youtube_transcript_batch(self, *, video_ids: list | None = None,
                                  playlist_id: str | None = None,
                                  channel_id: str | None = None,
                                  limit: int | None = None) -> dict:
        """Batch transcript extraction (paid plans). Returns {'jobId': '...'}.
        Credits: 1 + 1/video.
        """
        body = {}
        if video_ids: body["videoIds"] = video_ids
        if playlist_id: body["playlistId"] = playlist_id
        if channel_id: body["channelId"] = channel_id
        if limit: body["limit"] = limit
        return self._post("/youtube/transcript/batch", body)

    # ── YouTube Metadata ─────────────────────────────────────────────────────

    def youtube_video(self, url_or_id: str) -> dict:
        """Video metadata — title, views, duration, channel. Credits: 1."""
        return self._get("/youtube/video", {"id": url_or_id})

    def youtube_video_batch(self, *, video_ids: list | None = None,
                             playlist_id: str | None = None,
                             channel_id: str | None = None,
                             limit: int | None = None) -> dict:
        """Batch video metadata (paid plans). Returns {'jobId': '...'}.
        Credits: 1 + 1/video.
        """
        body = {}
        if video_ids: body["videoIds"] = video_ids
        if playlist_id: body["playlistId"] = playlist_id
        if channel_id: body["channelId"] = channel_id
        if limit: body["limit"] = limit
        return self._post("/youtube/video/batch", body)

    def youtube_batch_status(self, job_id: str) -> dict:
        """Poll batch job. Credits: 0."""
        return self._get(f"/youtube/batch/{job_id}")

    def youtube_channel(self, id_or_handle: str) -> dict:
        """Channel metadata — subscribers, video count, total views. Credits: 1."""
        return self._get("/youtube/channel", {"id": id_or_handle})

    def youtube_channel_videos(self, id_or_handle: str, *,
                                limit: int | None = None, type: str | None = None) -> dict:
        """List video IDs from a channel. type: 'all','video','short','live'. Credits: 1."""
        params = {"id": id_or_handle}
        if limit: params["limit"] = limit
        if type: params["type"] = type
        return self._get("/youtube/channel/videos", params)

    def youtube_playlist(self, id_or_url: str) -> dict:
        """Playlist metadata. Credits: 1."""
        return self._get("/youtube/playlist", {"id": id_or_url})

    def youtube_playlist_videos(self, id_or_url: str, *, limit: int | None = None) -> dict:
        """List video IDs from a playlist. Credits: 1."""
        params = {"id": id_or_url}
        if limit: params["limit"] = limit
        return self._get("/youtube/playlist/videos", params)

    def youtube_search(self, query: str, *, upload_date: str | None = None,
                        type: str | None = None, duration: str | None = None,
                        sort_by: str | None = None, limit: int | None = None) -> dict:
        """Search YouTube. Returns results with title, views, duration, channel.

        upload_date: 'all','hour','today','week','month','year'
        type: 'all','video','channel','playlist','movie'
        duration: 'short'(<4m), 'medium'(4-20m), 'long'(>20m)
        sort_by: 'relevance','rating','date','views'
        Credits: 1 per page (~20 results).
        """
        params = {"query": query}
        if upload_date: params["uploadDate"] = upload_date
        if type: params["type"] = type
        if duration: params["duration"] = duration
        if sort_by: params["sortBy"] = sort_by
        if limit: params["limit"] = limit
        return self._get("/youtube/search", params, timeout=60)

    # ── Social Media ─────────────────────────────────────────────────────────

    def metadata(self, url: str) -> dict:
        """Social post metadata — views, likes, comments, author.
        Works with YouTube, TikTok, Instagram, X, Facebook. Credits: 1.
        """
        return self._get("/metadata", {"url": url})

    # ── Structured Extraction ────────────────────────────────────────────────

    def extract(self, url: str, *, prompt: str | None = None,
                schema: dict | None = None) -> dict:
        """AI-powered structured data extraction from video. Returns {'jobId': '...'}.
        Credits: FREE during beta.
        """
        body = {"url": url}
        if prompt: body["prompt"] = prompt
        if schema: body["schema"] = schema
        return self._post("/extract", body)

    def extract_status(self, job_id: str) -> dict:
        """Poll extraction job. Credits: 0."""
        return self._get(f"/extract/{job_id}")

    # ── Web ──────────────────────────────────────────────────────────────────

    def web_scrape(self, url: str, *, no_links: bool = False,
                   lang: str | None = None) -> dict:
        """Scrape webpage to clean Markdown.
        Returns url, content (markdown), name, description, urls. Credits: 1.
        """
        params = {"url": url}
        if no_links: params["noLinks"] = "true"
        if lang: params["lang"] = lang
        return self._get("/web/scrape", params, timeout=60)

    def web_map(self, url: str) -> dict:
        """Discover all URLs linked from a page. Returns {'urls': [...]}. Credits: 1."""
        return self._get("/web/map", {"url": url})

    def web_crawl(self, url: str, *, limit: int | None = None) -> dict:
        """Async full-site crawl (paid plans). Returns {'jobId': '...'}. Credits: 1 + 1/page."""
        body = {"url": url}
        if limit: body["limit"] = limit
        return self._post("/web/crawl", body)

    def web_crawl_status(self, job_id: str, *, skip: int | None = None) -> dict:
        """Poll crawl job. Credits: 0."""
        params = {}
        if skip: params["skip"] = skip
        return self._get(f"/web/crawl/{job_id}", params or None)

    # ── Account ──────────────────────────────────────────────────────────────

    def me(self) -> dict:
        """Account info — plan, credits used, credits remaining. Credits: 1."""
        return self._get("/me")


if __name__ == "__main__":
    # Quick connection test
    client = SupadataClient()
    info = client.me()
    print(f"Connected. Plan: {info.get('plan')} | Credits: {info.get('usedCredits')}/{info.get('maxCredits')}")
````

[VERIFY]
```bash
ls supadata.py
```
Expected: File listed.

---

## TEST

### Quick connection test
```bash
python3 supadata.py
```
Expected output: `Connected. Plan: [your plan] | Credits: [used]/[max]`

If you see a 401 error: check that your API key in `.env` starts with `supa_` and has no extra spaces.
If you see a 402 error: your account needs credits — log in at supadata.ai and check your plan.

### Transcript test

Ask Claude: "Pull the transcript of this YouTube video: https://youtube.com/watch?v=dQw4w9WgXcQ"

Claude should use the Supadata skill, call the API, and return the transcript. If it works, the module is fully installed.

---

## WHAT'S NEXT

Claude can now pull transcripts and content from anywhere. Some things to try:

- **Competitor research:** "Get the transcript of [competitor's video] and summarise the main points"
- **YouTube search:** "Search YouTube for AI agency videos uploaded this month, sorted by views — show me the top 10"
- **Web scraping:** "Scrape [URL] and give me the key points as bullet points"
- **Content repurposing:** "Pull the transcript of [video URL] and rewrite it as a Twitter thread"
- **Channel analysis:** "Get the metadata for all videos on [channel URL] from the last 30 days"

---

> A plug-and-play module from Liam Ottley's AAA Accelerator — the #1 AI business launch
> & AIOS program. Grab this and 15+ more at [aaaaccelerator.com](https://aaaaccelerator.com)
