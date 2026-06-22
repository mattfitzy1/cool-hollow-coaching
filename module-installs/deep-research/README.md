# Deep Research -- AIOS Module

**Multi-platform deep research system using parallel AI agents. Searches 7 platforms simultaneously, scores every source, cross-references findings, and produces a critically reviewed synthesis report.**

---

## What This Is

The capstone research module for AIOS. Deep Research launches parallel AI agents that each go 3+ levels deep across different research angles. It covers 7 platforms: web (Firecrawl), YouTube (Supadata), Reddit, X/Twitter, academic papers, podcasts, and Substack newsletters.

It works in two phases. First, a fast recon agent scans all platforms to find where the signal lives. You review the recon and confirm the research plan. Then parallel topic agents (each running on Claude Opus at max effort) go deep on specific angles. A critic agent reviews all reports for quality issues. A synthesis agent produces the master report with confidence labels on every finding.

Every source gets scored on a 9-point scale (recency, source type, specificity, independence). Claims need two independent sources to enter the final report. Single-source claims get labeled. The critic catches echo chambers, recency bias, AI-generated content signals, and cross-report contradictions.

This module bundles 5 research platform clients, 5 matching skill files, the Deep Research orchestrator skill, and 4 prompt templates (recon, topic-agent, critic, synthesis). Everything installs from one INSTALL.md file.

## What Claude Can Do After Install

- Run a full deep research operation on any topic with `/deep-research "your topic"`
- Search Reddit (zero auth, public endpoints)
- Search X/Twitter via Grok semantic search with engagement enrichment
- Search 250M+ academic papers via OpenAlex with free PDF discovery
- Find and transcribe podcast episodes across YouTube and podcast platforms
- Search and extract Substack newsletter content
- Score every source, triangulate claims, identify contradictions
- Produce synthesis reports with confidence-weighted findings

## What's In The Box

```
deep-research/
├── INSTALL.md     # Give this to Claude Code to set up (installs everything)
└── README.md      # This file
```

INSTALL.md embeds all 5 client scripts, all 5 skill files, the orchestrator skill, 4 prompt templates, and the `/deep-research` command. One file installs the entire system.

## Prerequisites

**Required before installing this module:**
- **Firecrawl module** installed (web search and scraping)
- **Supadata module** installed (YouTube transcripts and search)

Install those two first. They provide the foundation that several research clients depend on.

## Setup

**Hand the folder to Claude Code and say:**

> "Read INSTALL.md and help me set this up step by step."

Setup time: 10-15 minutes. It's a bigger install (5 research platforms + orchestrator), but each step is straightforward.

**API keys needed:**
- `XAI_API_KEY` (required for X-Search) -- free at console.x.ai
- `X_BEARER_TOKEN` (optional, for engagement metrics) -- developer.x.com
- `OPENALEX_EMAIL` (optional, recommended) -- just your email address

Reddit, Academic, Substack, and Podcast-Search don't need their own API keys.

## Cost

- **Reddit:** Free (public endpoints)
- **X-Search (Grok):** ~$0.004-0.01 per search call
- **Academic:** Free (OpenAlex + Unpaywall)
- **Podcast-Search:** Uses Firecrawl + Supadata credits
- **Substack:** Uses Firecrawl credits for discovery, Substack API is free
- **A typical deep research run** with 4 topic agents costs roughly $0.05-0.20 in API calls

---

> Part of the AAA Accelerator AIOS Module Library.
> [aaaaccelerator.com](https://aaaaccelerator.com)
