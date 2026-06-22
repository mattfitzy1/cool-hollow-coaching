# Firecrawl — AIOS Module Installer

> A plug-and-play module from the AAA Accelerator.
> Grab this and 15+ more at [aaaaccelerator.com](https://aaaaccelerator.com)

---

## FOR CLAUDE

You are helping a user install this AIOS Module. Follow these rules:

**Behavior:**
- Assume the user is non-technical unless they tell you otherwise
- Explain what you are doing at each step in plain English BEFORE doing it
- Celebrate small wins ("Firecrawl is connected — Claude can now scrape any website or search the web!")
- If something fails, do not dump error logs — explain the problem simply and suggest the fix
- Never skip verification steps — if a check fails, stop and help the user fix it
- Use encouraging language throughout

**Pacing:**
- Do NOT rush. Pause after major milestones.
- After prerequisites: "Everything looks good. Ready to install?"
- After API key setup: "Key is saved. Now let's install the CLI and skill."
- After installation: "All done. Let's run a quick test."
- After test: "You're all set. Here's what Claude can do with Firecrawl."

**Error handling:**
- If Node.js is missing or too old: guide them to nodejs.org
- If `npm install -g` fails with permissions: suggest `sudo npm install -g` on Mac, or run terminal as Administrator on Windows
- If `firecrawl` command not found after install: close and reopen the terminal, then try again
- If API key returns 401: key is wrong or not saved correctly in .env
- If credits are exhausted: direct to firecrawl.dev to top up
- Never say "check the logs" — find the problem and explain it

---

## OVERVIEW

This module gives Claude the ability to scrape any webpage, search the web and pull full page content, crawl entire documentation sites, and extract structured data from complex pages — all from the CLI, without writing any code.

The problem it solves: Claude can't read URLs by default. When you ask it to research a competitor, pull content from a doc page, or grab information from any website, it can't. This module fixes that. Once installed, Claude uses the Firecrawl CLI to turn any URL into clean, LLM-ready content — and handles the tricky cases too (JavaScript-heavy pages, Cloudflare-protected sites, PDFs, multi-page crawls).

**What Claude can do after this is installed:**
- Scrape any webpage and get clean markdown back
- Search the web and pull full page content (not just snippets)
- Discover all URLs on a domain to find the right subpage
- Crawl entire site sections (like all /docs/ pages) in one command
- Extract structured data from pages with AI (pricing tiers, contact info, specs)
- Interact with pages that require clicks, logins, or scrolling via a cloud browser

**Where it installs:** Into `.claude/skills/` in your current workspace.

**Setup time:** 5-10 minutes (Node.js + API key + CLI install).

**Running cost:** Credit-based. Check your balance at firecrawl.dev. Most scrapes cost 1 credit.

---

## SCOPING

This module installs as one unit — the CLI tool and the skill file together. Nothing optional to skip.

Ask: "Ready to install? Takes about 5-10 minutes."

---

## PREREQUISITES

### Node.js 18+

**macOS:**
```bash
node --version
```

**Windows (PowerShell):**
```powershell
node --version
```

Expected: `v18.x.x` or higher. If not installed or too old:
- macOS: `brew install node` or download from nodejs.org
- Windows: Download the LTS installer from nodejs.org (check "Add to PATH")

### npm

```bash
npm --version
```

npm comes with Node.js. If this fails, reinstall Node.js from nodejs.org.

[VERIFY] Both checks pass.

Ask: "Node and npm are ready. Let's get your API key."

---

## API KEY SETUP

### Get your Firecrawl API key

1. Go to firecrawl.dev
2. Click **Sign Up** (or Sign In if you have an account)
3. Once logged in, go to your **Dashboard**
4. Find your **API Key** (starts with `fc-`)
5. Copy it

### Add it to your workspace

Check if you already have a `.env` file:

**macOS/Linux:**
```bash
ls .env
```

**Windows:**
```powershell
Test-Path .env
```

**If the file exists** — add this line to it:
```
FIRECRAWL_API_KEY=fc-your_key_here
```

**If it doesn't exist** — create it:

macOS/Linux:
```bash
echo "FIRECRAWL_API_KEY=fc-your_key_here" > .env
```

Windows (PowerShell):
```powershell
"FIRECRAWL_API_KEY=fc-your_key_here" | Out-File -FilePath .env -Encoding utf8
```

Replace `fc-your_key_here` with your actual key.

[VERIFY]
```bash
grep FIRECRAWL_API_KEY .env
```
Expected: The line with your key appears.

Ask: "Key is saved. Now let's install the Firecrawl CLI."

---

## INSTALL

### Step 1: Install the Firecrawl CLI

```bash
npm install -g firecrawl-cli
```

This installs the `firecrawl` command globally.

**If you get a permissions error on macOS:**
```bash
sudo npm install -g firecrawl-cli
```

**If you get a permissions error on Windows:** Close PowerShell, right-click it, choose "Run as Administrator", then run the install command again.

[VERIFY]
```bash
firecrawl --version
```
Expected: A version number. If you get "command not found", close and reopen your terminal and try again.

### Step 2: Connect your API key to the CLI

```bash
firecrawl init
```

When prompted for your API key, paste the key from your `.env` file (starts with `fc-`).

[VERIFY]
```bash
firecrawl --status
```
Expected: Shows your plan and remaining credits. If it shows an error, the API key is wrong — double-check it from your Firecrawl dashboard.

### Step 3: Create the skill folder

```bash
mkdir -p .claude/skills/firecrawl
```

### Step 4: Install the Firecrawl skill

Write the following file to `.claude/skills/firecrawl/SKILL.md`:

````markdown
---
name: firecrawl
description: >
  Web scraping, search, and crawling via the Firecrawl CLI. Use when asked to scrape a URL,
  fetch a page, read an article, research a topic online, look something up, search the web,
  find information about a website, check a competitor, pull documentation, extract data from
  a site, get the content of a URL, web search, or fetch any webpage. Handles JS-heavy pages,
  bot-protected sites (Cloudflare), PDFs, and multi-page crawls. Trigger words: scrape, fetch,
  search the web, read this URL, get this page, crawl, research online, competitor research,
  pricing page, docs page, download a site, find articles about, web research, browse, extract
  from this URL.
user-invocable: false
---

# Firecrawl

Web scraping CLI. Turns any URL into clean LLM-ready markdown. 8 commands, all via the `firecrawl` CLI.

## Command Reference

| Command | What it does | When to use |
|---------|-------------|-------------|
| `firecrawl scrape "<url>"` | Single page → clean markdown | Have a URL, need its content |
| `firecrawl search "query" --scrape` | Search + pull full page content | No URL yet, need to find + read pages |
| `firecrawl crawl "<url>" --limit N` | Bulk extract entire site section | Need all /docs/ or all /blog/ pages |
| `firecrawl map "<url>"` | Discover all URLs in a domain | Need to find a specific subpage |
| `firecrawl agent "<url>" --prompt "..."` | AI-powered structured extraction | Need structured data (pricing, specs, contacts) |
| `firecrawl browser "<url>"` | Interactive — clicks, forms, scroll | Scrape failed, content needs interaction |
| `firecrawl download "<url>"` | Save entire site as local files | Offline reference, bulk archival |
| `firecrawl credit-usage` | Check credit consumption | Monitor usage |

## Escalation Pattern

Follow this order — start simple, escalate only if needed:

1. **No URL yet** → `firecrawl search "query" --scrape --limit 3`
2. **Have a URL** → `firecrawl scrape "<url>"`
3. **Large site, need a specific subpage** → `firecrawl map "<url>" --search "keyword"` then scrape the match
4. **Need bulk content from a section** → `firecrawl crawl "<url>" --limit 20`
5. **Scrape failed (JS gating, modals, login, pagination)** → `firecrawl browser "<url>"`

## Common Patterns

### Research a topic (no URL)
```bash
firecrawl search "AI agency pricing models 2025" --scrape --limit 5 -o .firecrawl/search-results.json
```

### Scrape a specific page
```bash
firecrawl scrape "https://competitor.com/pricing" -o .firecrawl/competitor-pricing.md
```

### Pull all docs from a site
```bash
firecrawl crawl "https://docs.example.com" --limit 50 -o .firecrawl/docs/
```

### Extract structured data with AI
```bash
firecrawl agent "https://example.com" --prompt "Extract: company name, pricing tiers, features per tier" -o .firecrawl/extracted.json
```

### Find a specific subpage on a large site
```bash
firecrawl map "https://example.com" --search "pricing"
# Then scrape the matching URL
```

### Parallel scrapes (faster)
```bash
firecrawl scrape "<url-1>" -o .firecrawl/1.md &
firecrawl scrape "<url-2>" -o .firecrawl/2.md &
firecrawl scrape "<url-3>" -o .firecrawl/3.md &
wait
```

## Output Rules

- Always write to a temp folder with `-o` — never dump large content inline into the conversation
- Use `.firecrawl/` as a scratch folder for session work
- For content worth keeping, move it somewhere permanent when done
- Never read entire large files at once — use `head -100` or search for specific sections first
- `search --scrape` already fetches full page content — don't re-scrape those same URLs

```bash
# Extract URLs from search output
jq -r '.data.web[].url' .firecrawl/search.json

# Check file size before reading
wc -l .firecrawl/file.md && head -100 .firecrawl/file.md

# Clean up temp files when done
rm -rf .firecrawl/*
```

## Important: Always Quote URLs

URLs with `?` and `&` characters must be quoted in bash — they're shell special characters:
```bash
# Correct
firecrawl scrape "https://example.com/page?id=123&ref=abc"

# Wrong — shell will break the URL
firecrawl scrape https://example.com/page?id=123&ref=abc
```

## Credits

Each scrape/search/crawl costs credits. Check balance:
```bash
firecrawl --status
firecrawl credit-usage
```

Top up at firecrawl.dev if you run low.
````

[VERIFY]
```bash
cat .claude/skills/firecrawl/SKILL.md | head -5
```
Expected: File starts with `---` (YAML frontmatter).

---

## TEST

### Quick test — scrape a page

```bash
mkdir -p .firecrawl
firecrawl scrape "https://example.com" -o .firecrawl/test.md && head -20 .firecrawl/test.md
```

Expected: The first 20 lines of example.com's content in clean markdown. If it works, the CLI is connected and credits are flowing.

### Ask Claude to use it

Say: "Search the web for AI agency pricing models and summarise the top 3 results."

Claude should run `firecrawl search "AI agency pricing models" --scrape --limit 3`, read the results, and give you a summary. If it does, the skill is working.

---

## WHAT'S NEXT

Claude can now research anything on the web. Some things to try:

- **Competitor research:** "Scrape [competitor URL] and tell me their pricing and main features"
- **Market research:** "Search for the top AI automation tools in 2025 and compare their approaches"
- **Docs reading:** "Crawl the docs at [docs URL] and explain how their API authentication works"
- **Data extraction:** "Extract the names, roles, and LinkedIn URLs from [company team page]"
- **Content research:** "Find 5 recent articles about AI agents and pull key quotes from each"

---

> A plug-and-play module from Liam Ottley's AAA Accelerator — the #1 AI business launch
> & AIOS program. Grab this and 15+ more at [aaaaccelerator.com](https://aaaaccelerator.com)
