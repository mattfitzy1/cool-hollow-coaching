# X-Search — AIOS Module

**X/Twitter search and content intelligence via two layers: Grok x_search for discovery + X API v2 for engagement data.**

---

## What This Is

A Claude Code skill that gives Claude the ability to search X (Twitter) for any topic, get synthesized answers with source tweets, and pull engagement metrics on the posts that matter.

Two layers working together. Layer 1 uses Grok's x_search through the xAI Responses API for semantic search, synthesized insights, and post citations. Layer 2 uses the X API v2 for raw tweet data with likes, retweets, replies, and impressions. Use one layer or both depending on what you need.

## What Claude Can Do

- Search X for any topic and get a synthesized answer with cited posts
- Filter searches by date range, specific accounts, or excluded accounts
- Look up engagement metrics on any tweet (likes, retweets, replies, impressions)
- Search recent tweets with X API operators (boolean, account filters, content types)
- Look up user profiles with follower counts and verification status
- Run the full pipeline: discover with Grok, then enrich top posts with engagement data

## What's In The Box

```
x-search/
├── INSTALL.md     # Give this to Claude Code to set up
└── README.md      # This file
```

Everything needed is embedded inline in INSTALL.md, including the full Python client and skill definition.

## Setup

**Hand the folder to Claude Code and say:**

> "Read INSTALL.md and help me set this up step by step."

Takes 5-10 minutes. You'll need an xAI API key from console.x.ai. The X bearer token (for engagement metrics) is optional.

**Requirements:** Python 3, `pip install requests python-dotenv`.

## Cost

- **xAI (Layer 1):** ~$0.004-0.01 per search call. Pay-as-you-go at console.x.ai.
- **X API v2 (Layer 2):** Rate-limited, no per-call cost on the pay-per-use plan. Sign up at developer.x.com.

---

> Part of the AAA Accelerator AIOS Module Library.
> [aaaaccelerator.com](https://aaaaccelerator.com)
