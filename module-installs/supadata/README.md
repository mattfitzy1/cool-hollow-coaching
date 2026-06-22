# Supadata — AIOS Module

**Pull transcripts, search YouTube, scrape web pages — Claude gets internet access via the Supadata API.**

---

## What This Is

A Claude Code skill that gives Claude the ability to fetch content from the internet — YouTube transcripts, social media metadata, web pages, search results — using the Supadata API.

By default Claude can't access URLs or pull live content. This module changes that. Once installed, Claude knows all 21 Supadata endpoints and can call them any time you ask.

## What Claude Can Do

- Pull the full transcript of any YouTube, TikTok, Instagram, X, or Facebook video
- Search YouTube and return results with view counts, durations, upload dates
- Get channel stats — subscriber count, total views, video count
- List all video IDs from a channel or playlist
- Get metadata from any social post — views, likes, comments, author
- Scrape any webpage and return clean markdown
- Extract structured data from video content (free during beta)

## What's In The Box

```
supadata/
├── INSTALL.md     # Give this to Claude Code to set up
├── README.md      # This file
```

The INSTALL.md embeds everything — the skill definition, the full Python client, and all setup steps. No extra files needed.

## Setup

**Hand the folder to Claude Code and say:**

> "Read INSTALL.md and help me set this up step by step."

Takes 5-10 minutes. You'll need a free Supadata account (supadata.ai).

**Requirements:** Claude Code CLI, Python 3, `pip install requests python-dotenv`.

## Cost

Credit-based. Most operations cost 1 credit. Free plan available at supadata.ai.

| Operation | Credits |
|-----------|---------|
| Transcript (any platform) | 1 |
| YouTube search (per page ~20 results) | 1 |
| Web scrape | 1 |
| Video / channel / playlist metadata | 1 |
| Batch operations | 1 + 1/item |
| AI extraction from video | Free (beta) |

---

> Part of the AAA Accelerator AIOS Module Library.
> [aaaaccelerator.com](https://aaaaccelerator.com)
