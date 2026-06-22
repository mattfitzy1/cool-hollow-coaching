#!/usr/bin/env python3
"""Fetch a YouTube video's auto-caption transcript + title as JSON.

Usage: python3 fetch_youtube_transcript.py <youtube_url>

Output (stdout, JSON):
    {"video_id": "...", "title": "...", "url": "...", "transcript": "..."}

Exit codes:
    0 - success
    1 - bad URL / could not parse video ID
    2 - transcript unavailable (no captions, disabled, or region-blocked)
    3 - network or oembed failure
"""

import json
import re
import sys
import urllib.parse
import urllib.request


def extract_video_id(url: str) -> str | None:
    patterns = [
        r"(?:v=|/v/|youtu\.be/|/embed/|/shorts/)([0-9A-Za-z_-]{11})",
        r"^([0-9A-Za-z_-]{11})$",
    ]
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    return None


def fetch_title(url: str) -> str:
    oembed = f"https://www.youtube.com/oembed?url={urllib.parse.quote(url)}&format=json"
    with urllib.request.urlopen(oembed, timeout=15) as r:
        data = json.loads(r.read().decode("utf-8"))
    return data.get("title", "Untitled")


def fetch_transcript(video_id: str) -> str:
    from youtube_transcript_api import YouTubeTranscriptApi

    api = YouTubeTranscriptApi()
    fetched = api.fetch(video_id)
    return " ".join(snippet.text.strip() for snippet in fetched if snippet.text.strip())


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: fetch_youtube_transcript.py <url>", file=sys.stderr)
        return 1

    url = sys.argv[1].strip()
    video_id = extract_video_id(url)
    if not video_id:
        print(f"could not extract video id from: {url}", file=sys.stderr)
        return 1

    canonical = f"https://www.youtube.com/watch?v={video_id}"

    try:
        title = fetch_title(canonical)
    except Exception as e:
        print(f"oembed title fetch failed: {e}", file=sys.stderr)
        return 3

    try:
        transcript = fetch_transcript(video_id)
    except Exception as e:
        print(f"transcript unavailable: {e}", file=sys.stderr)
        return 2

    json.dump(
        {"video_id": video_id, "title": title, "url": canonical, "transcript": transcript},
        sys.stdout,
        ensure_ascii=False,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
