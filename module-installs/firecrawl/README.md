# Firecrawl — AIOS Module

**Scrape any webpage, search the web, crawl entire sites — Claude gets full internet access via the Firecrawl CLI.**

---

## What This Is

A Claude Code skill that gives Claude the ability to read any URL, search the web with full page content, crawl documentation sites, and extract structured data from complex pages — all from the command line.

One command is usually all it takes. `firecrawl scrape "url"` for a specific page, `firecrawl search "query" --scrape` when you don't have a URL yet. The CLI handles the messy cases too: JavaScript-rendered pages, Cloudflare-protected sites, PDFs, paginated content, and pages that need clicks or logins.

## What Claude Can Do

- Scrape any webpage → clean markdown
- Search the web and pull full page content (not just snippets)
- Discover all URLs on a domain to find the right subpage
- Crawl entire site sections in bulk (all /docs/, all /blog/, etc.)
- Extract structured data from pages with AI prompting
- Interact with pages that need clicks, form fills, or scrolling

## What's In The Box

```
firecrawl/
├── INSTALL.md     # Give this to Claude Code to set up
└── README.md      # This file
```

Everything needed is embedded inline in INSTALL.md — no extra files.

## Setup

**Hand the folder to Claude Code and say:**

> "Read INSTALL.md and help me set this up step by step."

Takes 5-10 minutes. You'll need a free Firecrawl account at firecrawl.dev.

**Requirements:** Node.js 18+, npm. Works on macOS and Windows.

## Cost

Credit-based. Check your balance with `firecrawl --status`. Top up at firecrawl.dev.

---

> Part of the AAA Accelerator AIOS Module Library.
> [aaaaccelerator.com](https://aaaaccelerator.com)
