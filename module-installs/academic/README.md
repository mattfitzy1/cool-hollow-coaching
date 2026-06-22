# Academic Paper Search — AIOS Module

**Search 250M+ scholarly papers, get abstracts, traverse citation graphs, and find free PDFs of paywalled research. Zero auth required.**

---

## What This Is

A Claude Code skill that gives Claude the ability to search academic literature using OpenAlex (the largest open scholarly database) and find free legal copies of paywalled papers via Unpaywall.

No API key. No account. No cost. Both OpenAlex and Unpaywall are completely free and open.

## What Claude Can Do

- Search 250 million+ scholarly papers by topic, year, citation count
- Get full abstracts, author info, journal names, and publication metadata
- Traverse citation graphs (find what cites a given paper, or what it references)
- Find free legal PDFs of paywalled papers via Unpaywall
- Run full research pipelines that combine search, enrichment, and PDF discovery in one call
- Filter by open access only, minimum citation count, date range

## What's In The Box

```
academic/
├── INSTALL.md     # Give this to Claude Code to set up
├── README.md      # This file
```

The INSTALL.md embeds everything: the skill definition, the full Python client, and all setup steps. No extra files needed.

## Setup

**Hand the folder to Claude Code and say:**

> "Read INSTALL.md and help me set this up step by step."

Takes 2-3 minutes. No API key needed.

**Requirements:** Claude Code CLI, Python 3, `pip install requests python-dotenv`.

## Cost

Free. OpenAlex and Unpaywall are open, publicly funded research infrastructure. No credits, no billing, no limits beyond basic rate limiting (100 requests/second for OpenAlex).

---

> Part of the AAA Accelerator AIOS Module Library.
> [aaaaccelerator.com](https://aaaaccelerator.com)
