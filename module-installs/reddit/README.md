# Reddit Research -- AIOS Module

**Zero-auth Reddit research -- Claude can search posts, auto-detect subreddits, and extract full threads with scored comments. No API key needed.**

---

## What This Is

A Claude Code skill that gives Claude the ability to search Reddit, find relevant communities, and pull full post content with comment trees. All via Reddit's public .json endpoints, so there's no API key, no OAuth app, no approval wait.

One call does everything. `research("AI automation agencies")` auto-detects the right subreddits, searches across Reddit, ranks by engagement, and extracts the top threads with scored comments. You can also search individual subreddits, browse hot/top posts, or extract a single thread.

## What Claude Can Do

- Search all of Reddit or specific subreddits
- Auto-detect relevant communities for any topic
- Extract full thread content with top comments and scores
- Browse hot, top, and new posts from any subreddit
- Run a complete research pipeline in one call (detect, search, rank, extract)

## What's In The Box

```
reddit/
├── INSTALL.md     # Give this to Claude Code to set up
└── README.md      # This file
```

Everything needed is embedded inline in INSTALL.md, including the full Python client.

## Setup

**Hand the folder to Claude Code and say:**

> "Read INSTALL.md and help me set this up step by step."

Takes 2-3 minutes. No accounts or API keys required.

**Requirements:** Python 3, `pip install requests`.

## Cost

Free. Uses Reddit's public .json endpoints. Rate limited to 10 requests/minute (the client handles this automatically).

---

> Part of the AAA Accelerator AIOS Module Library.
> [aaaaccelerator.com](https://aaaaccelerator.com)
