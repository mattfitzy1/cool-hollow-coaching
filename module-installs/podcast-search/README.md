# Podcast Search — AIOS Module

**Find podcast episodes on any topic, rank by quality, extract full transcripts.**

---

## What This Is

A Claude Code skill that searches for podcast episodes across the internet, scores them by quality (0-100), and pulls full transcripts from YouTube. Two discovery layers work in parallel: Google search via Firecrawl finds episodes across Apple Podcasts, Spotify, YouTube, and podcast sites, while Supadata searches YouTube directly and handles transcript extraction.

Give Claude a topic and it returns ranked episodes with quality scores based on view count, duration, and source authority. The best episodes get their transcripts pulled automatically.

## What Claude Can Do

- Search for podcast episodes on any topic across all major platforms
- Rank discovered episodes by quality (views, duration, authority signals)
- Pull full transcripts from YouTube episodes
- Run the full pipeline in one call: discover, rank, extract top transcripts

## What's In The Box

```
podcast-search/
├── INSTALL.md     # Give this to Claude Code to set up
└── README.md      # This file
```

Everything needed is embedded inline in INSTALL.md, including the full Python client and skill definition.

## Prerequisites

This module depends on two other AIOS modules:
- **Firecrawl module** (provides web search for episode discovery)
- **Supadata module** (provides YouTube search and transcript extraction)

Both are available separately in the Module Library. Install them first if you haven't already.

## Setup

**Hand the folder to Claude Code and say:**

> "Read INSTALL.md and help me set this up step by step."

Takes about 5 minutes. No additional API keys needed beyond what Firecrawl and Supadata already use.

**Requirements:** Python 3, `pip install requests python-dotenv`, Firecrawl module installed, Supadata module installed.

## Cost

Uses credits from your existing Firecrawl and Supadata accounts. A typical research query (10 search results + 10 YouTube results + 3 transcripts) costs roughly 5 Firecrawl credits and 14 Supadata credits.

---

> Part of the AAA Accelerator AIOS Module Library.
> [aaaaccelerator.com](https://aaaaccelerator.com)
