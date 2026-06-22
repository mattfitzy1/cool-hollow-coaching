# Substack Search — AIOS Module

**Search any Substack newsletter and extract full article content. Two layers: Firecrawl discovers posts via Google, Substack's undocumented API pulls the full text with metadata.**

---

## What This Is

A Claude Code skill that gives Claude the ability to search Substack newsletters on any topic, discover publications, browse post archives, and read full article content with engagement data (reactions, word count, comments).

No Substack API key needed. The module uses Substack's public endpoints for content extraction and your existing Firecrawl setup for discovery.

## What Claude Can Do

- Search for Substack posts on any topic
- Read full newsletter articles with metadata
- Browse a publication's archive (sorted by newest or top)
- Discover which publications write about a given topic
- Run a full research pipeline: search, discover, extract in one call

## What's In The Box

```
substack/
├── INSTALL.md     # Give this to Claude Code to set up
└── README.md      # This file
```

Everything needed is embedded inline in INSTALL.md, including the Python client and skill file.

## Setup

**Hand the folder to Claude Code and say:**

> "Read INSTALL.md and help me set this up step by step."

Takes 3-5 minutes.

**Prerequisite:** Firecrawl module installed (the search layer depends on it for Google discovery).

**Requirements:** Python 3, pip, `requests` and `python-dotenv` packages. Works on macOS and Windows.

## Cost

Zero. No API key, no credits, no auth. The only cost is Firecrawl credits for the search step (typically 1 credit per search).

---

> Part of the AAA Accelerator AIOS Module Library.
> [aaaaccelerator.com](https://aaaaccelerator.com)
