# Academic Paper Search — AIOS Module Installer

> A plug-and-play module from the AAA Accelerator.
> Grab this and 15+ more at [aaaaccelerator.com](https://aaaaccelerator.com)

---

## FOR CLAUDE

You are helping a user install this AIOS Module. Follow these rules:

**Behavior:**
- Assume the user is non-technical unless they tell you otherwise
- Explain what you are doing at each step in plain English BEFORE doing it
- Celebrate small wins ("Academic search is connected — Claude can now search 250 million research papers!")
- If something fails, do not dump error logs — explain the problem simply and suggest the fix
- Never skip verification steps — if a check fails, stop and help the user fix it
- Use encouraging language throughout

**Pacing:**
- Do NOT rush. Pause after major milestones.
- After prerequisites: "Everything looks good. Ready to install?"
- After installation: "Files are in place. Let's run a quick test."
- After test: "You're all set! Here's what Claude can do with Academic Search."

**Error handling:**
- If Python isn't installed: guide to python.org
- If pip install fails: suggest `pip3 install --user requests python-dotenv`
- If test returns connection error: check internet connection
- Never say "check the logs" — find the problem and explain it

---

## OVERVIEW

This module gives Claude the ability to search 250M+ scholarly papers via OpenAlex, the largest open academic database. It finds papers by topic, retrieves abstracts, traverses citation graphs, and locates free legal PDFs of paywalled papers through Unpaywall.

Here's the problem it solves: Claude can't search academic literature by default. If you want Claude to find research papers, pull abstracts, check citation counts, or locate free copies of paywalled articles, it can't. This module fixes that. Once installed, Claude knows how to call OpenAlex and Unpaywall and can do it any time you ask.

**What Claude can do after this is installed:**
- Search 250 million+ scholarly papers by topic, year, citation count
- Get full abstracts, author names, institutions, journal names
- Traverse citation graphs (what cites this paper? what does it reference?)
- Find free legal PDFs of paywalled papers via Unpaywall
- Run full research pipelines that combine search, enrichment, and PDF discovery
- Filter by open access only, minimum citations, date range, sort by relevance or citation count

**Where it installs:** Into `.claude/skills/` in your current workspace, plus a reusable `scripts/academic/client.py` that your own code can import.

**Setup time:** 2-3 minutes. No API key needed.

**Running cost:** Free. OpenAlex and Unpaywall are open, publicly funded research infrastructure.

---

## PREREQUISITES

### Claude Code CLI
```bash
claude --version
```
If not installed:
```bash
npm install -g @anthropic-ai/claude-code
```

### Workspace .claude/ folder
```bash
ls .claude/
```
If it doesn't exist:
```bash
mkdir -p .claude/skills
```

### Python and pip
```bash
python3 --version && pip3 --version
```
If Python isn't installed: download from https://python.org (click Downloads, install the latest version).

### Install Python dependencies
```bash
pip3 install requests python-dotenv
```

[VERIFY] All checks pass without errors.

Ask: "Everything looks good. Ready to install?"

---

## API KEY SETUP

No API key is required. OpenAlex and Unpaywall are completely free and open.

**Optional (recommended):** Add your email for polite OpenAlex access. This gets you into the fast lane (higher rate limits, priority routing):

Check if you already have a `.env` file:
```bash
ls .env
```

**If the file exists** — add this line to it:
```
OPENALEX_EMAIL=your@email.com
```

**If it doesn't exist** — create it:
```bash
echo "OPENALEX_EMAIL=your@email.com" > .env
```

Replace `your@email.com` with your actual email address. This is optional but OpenAlex recommends it for better service.

---

## INSTALL

### Step 1: Create the folder structure

```bash
mkdir -p .claude/skills/academic
mkdir -p scripts/academic
```

### Step 2: Install the Academic Search skill

Write the following file to `.claude/skills/academic/SKILL.md`:

````markdown
---
name: academic
description: >
  Academic paper search and content extraction via OpenAlex (250M+ papers).
  Search scholarly articles, find research papers, get abstracts, citation graphs,
  find free PDFs of paywalled papers. Academic research, scientific papers,
  peer-reviewed articles, literature review, citations, scholarly search.
  For web articles use Firecrawl. For YouTube/social use Supadata.
user-invocable: false
---

# Academic Paper Search

OpenAlex-powered search across 250M+ scholarly works. Zero auth required. Includes Unpaywall for finding free PDFs and citation graph traversal.

## Setup

```python
import importlib.util, os
spec = importlib.util.spec_from_file_location("academic_client",
    os.path.join(os.path.dirname(os.path.abspath(".")), "scripts/academic/client.py"))
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
client = mod.AcademicClient()
```

**No env vars needed.** OpenAlex and Unpaywall are free, no auth. Optionally set `OPENALEX_EMAIL` in `.env` for polite pool access (higher rate limits).

## Method Reference

| Method | What | Source |
|--------|------|--------|
| `search(query, limit, year_from, ...)` | Search 250M+ papers by topic | OpenAlex |
| `get_paper(doi=)` | Get paper by DOI | OpenAlex |
| `get_citations(openalex_id, limit)` | Papers that cite a given paper | OpenAlex |
| `find_free_pdf(doi)` | Find free legal PDF of paywalled paper | Unpaywall |
| `get_full_text(url)` | Scrape article page for full text | Firecrawl |
| `research(query, max_papers, ...)` | Full pipeline: search, enrich, extract | All |

## Full Research Pipeline

```python
result = client.research(
    "AI code generation testing verification",
    max_papers=5,
    year_from=2024,
    find_free_pdfs=True,       # look up free PDFs for paywalled papers
    extract_full_text=False,    # set True to scrape full articles (slower)
)

print(f"Found {result['total_found']} papers")
for p in result["papers"]:
    print(f"\n[{p['cited_by']} cites] {p['title']}")
    print(f"  {p['year']} | {', '.join(a['name'] for a in p['authors'][:2])}")
    print(f"  Abstract: {p['abstract'][:200]}...")
```

## Search Parameters

```python
# Basic search (relevance-ranked, 2024+)
papers = client.search("transformer architecture", year_from=2024)

# Highly cited open access papers only
papers = client.search(
    "large language models",
    limit=10,
    year_from=2023,
    open_access_only=True,
    cited_by_min=100,
    sort="cited_by_count:desc",
)

# Recent papers sorted by date
papers = client.search(
    "AI agents software engineering",
    sort="publication_date:desc",
    year_from=2025,
)
```

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `query` | str | required | Search topic |
| `limit` | int | 10 | Max 200 per page |
| `year_from` | int | None | Minimum publication year |
| `year_to` | int | None | Maximum publication year |
| `open_access_only` | bool | False | Only OA papers |
| `cited_by_min` | int | None | Minimum citation count |
| `sort` | str | `relevance_score:desc` | Also: `cited_by_count:desc`, `publication_date:desc` |

## Paper Fields

| Field | Type | What |
|-------|------|------|
| `title` | str | Paper title |
| `abstract` | str | Reconstructed from inverted index (some papers lack this) |
| `year` | int | Publication year |
| `cited_by` | int | Citation count |
| `doi` | str | DOI (without https://doi.org/ prefix) |
| `open_access` | bool | Is it freely accessible? |
| `oa_url` | str | Open access URL (if available) |
| `authors` | list | `[{"name": "...", "institution": "..."}]` |
| `venue` | str | Journal/conference name |
| `type` | str | article, preprint, book-chapter, etc. |
| `openalex_id` | str | OpenAlex identifier (for citation lookups) |

## Citation Graph

```python
# Find what cites a paper
paper = client.search("attention is all you need", limit=1, year_from=2017, year_to=2017)
citing = client.get_citations(paper[0]["openalex_id"], limit=10)
for c in citing:
    print(f"[{c['cited_by']} cites] {c['title']}")
```

## Finding Free PDFs

```python
# Unpaywall finds free legal copies of paywalled papers
pdf_url = client.find_free_pdf("10.1145/3650212.3680384")
# Returns URL to free PDF, or None
```

The `research()` pipeline does this automatically for paywalled papers when `find_free_pdfs=True`.

## Rate Limits

| API | Limit | Notes |
|-----|-------|-------|
| OpenAlex | 100 req/s (shared) | Include email in User-Agent for polite pool |
| Unpaywall | 100K req/day | Generous |
| Client delay | 200ms between requests | Enforced automatically |
````

[VERIFY]
```bash
cat .claude/skills/academic/SKILL.md | head -5
```
Expected: File starts with `---` (YAML frontmatter).

### Step 3: Install the Python client

Write an empty `__init__.py` file to `scripts/academic/__init__.py`:

```python
```

Then write the following file to `scripts/academic/client.py`:

````python
"""
Academic Paper Search Client — OpenAlex-powered research engine.

Usage:
    from scripts.academic.client import AcademicClient
    client = AcademicClient()
    papers = client.search("autonomous AI coding agents", limit=10, year_from=2024)
"""

import json
import os
import re
import subprocess
import time
from pathlib import Path

import requests
from dotenv import load_dotenv


def _find_and_load_env():
    current = Path(__file__).resolve().parent
    for _ in range(5):
        candidate = current / ".env"
        if candidate.exists():
            load_dotenv(candidate)
            return
        current = current.parent

_find_and_load_env()

_last_request = 0.0


def _rate_limit(delay=0.2):
    global _last_request
    elapsed = time.time() - _last_request
    if elapsed < delay:
        time.sleep(delay - elapsed)
    _last_request = time.time()


def _reconstruct_abstract(inverted_index):
    if not inverted_index:
        return ""
    word_positions = []
    for word, positions in inverted_index.items():
        for pos in positions:
            word_positions.append((pos, word))
    word_positions.sort()
    return " ".join(w for _, w in word_positions)


class AcademicClient:
    OPENALEX_BASE = "https://api.openalex.org"
    UNPAYWALL_BASE = "https://api.unpaywall.org/v2"
    EMAIL = os.getenv("OPENALEX_EMAIL", "user@example.com")

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": f"AIOS-Research/1.0 (mailto:{self.EMAIL})",
            "Accept": "application/json",
        })

    def search(self, query, limit=10, year_from=None, year_to=None,
               open_access_only=False, sort="relevance_score:desc", cited_by_min=None):
        _rate_limit()
        filters = []
        if year_from:
            filters.append(f"from_publication_date:{year_from}-01-01")
        if year_to:
            filters.append(f"to_publication_date:{year_to}-12-31")
        if open_access_only:
            filters.append("open_access.is_oa:true")
        if cited_by_min:
            filters.append(f"cited_by_count:>{cited_by_min}")
        params = {"search": query, "per_page": min(limit, 200), "sort": sort}
        if filters:
            params["filter"] = ",".join(filters)
        try:
            resp = self.session.get(f"{self.OPENALEX_BASE}/works", params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"OpenAlex search failed: {e}")
            return []
        papers = []
        for r in data.get("results", []):
            abstract = _reconstruct_abstract(r.get("abstract_inverted_index", {}))
            authors = []
            for a in r.get("authorships", [])[:5]:
                name = a.get("author", {}).get("display_name", "")
                institution = ""
                insts = a.get("institutions", [])
                if insts:
                    institution = insts[0].get("display_name", "")
                if name:
                    authors.append({"name": name, "institution": institution})
            oa = r.get("open_access", {})
            location = r.get("primary_location", {}) or {}
            source = location.get("source", {}) or {}
            doi = r.get("doi", "")
            doi_short = doi.replace("https://doi.org/", "") if doi and doi.startswith("https://doi.org/") else doi
            papers.append({
                "title": r.get("title", ""), "abstract": abstract,
                "year": r.get("publication_year"), "cited_by": r.get("cited_by_count", 0),
                "doi": doi_short, "doi_url": doi,
                "open_access": oa.get("is_oa", False), "oa_url": oa.get("oa_url", ""),
                "authors": authors, "venue": source.get("display_name", ""),
                "type": r.get("type", ""), "openalex_id": r.get("id", ""),
            })
        return papers

    def get_paper(self, doi=None, openalex_id=None):
        _rate_limit()
        if doi:
            url = f"{self.OPENALEX_BASE}/works/doi:{doi}"
        elif openalex_id:
            url = f"{self.OPENALEX_BASE}/works/{openalex_id}"
        else:
            return None
        try:
            resp = self.session.get(url, timeout=15)
            if resp.status_code != 200:
                return None
            r = resp.json()
        except Exception:
            return None
        abstract = _reconstruct_abstract(r.get("abstract_inverted_index", {}))
        authors = [{"name": a.get("author", {}).get("display_name", "")} for a in r.get("authorships", [])[:10]]
        oa = r.get("open_access", {})
        location = r.get("primary_location", {}) or {}
        source = location.get("source", {}) or {}
        doi_val = r.get("doi", "")
        if doi_val and doi_val.startswith("https://doi.org/"):
            doi_val = doi_val.replace("https://doi.org/", "")
        return {
            "title": r.get("title", ""), "abstract": abstract,
            "year": r.get("publication_year"), "cited_by": r.get("cited_by_count", 0),
            "doi": doi_val, "open_access": oa.get("is_oa", False),
            "oa_url": oa.get("oa_url", ""), "authors": authors,
            "venue": source.get("display_name", ""), "type": r.get("type", ""),
            "referenced_works_count": len(r.get("referenced_works", [])),
            "related_works": r.get("related_works", [])[:5],
        }

    def get_citations(self, openalex_id, limit=10):
        _rate_limit()
        try:
            resp = self.session.get(
                f"{self.OPENALEX_BASE}/works",
                params={"filter": f"cites:{openalex_id}", "per_page": limit, "sort": "cited_by_count:desc"},
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception:
            return []
        return [{"title": r.get("title", ""), "year": r.get("publication_year"),
                 "cited_by": r.get("cited_by_count", 0),
                 "doi": (r.get("doi", "") or "").replace("https://doi.org/", ""),
                 "openalex_id": r.get("id", "")} for r in data.get("results", [])]

    def find_free_pdf(self, doi):
        _rate_limit()
        clean_doi = doi.replace("https://doi.org/", "")
        try:
            resp = self.session.get(
                f"{self.UNPAYWALL_BASE}/{clean_doi}",
                params={"email": self.EMAIL}, timeout=10,
            )
            if resp.status_code != 200:
                return None
            data = resp.json()
            best = data.get("best_oa_location", {}) or {}
            return best.get("url_for_pdf") or best.get("url")
        except Exception:
            return None

    def get_full_text(self, url):
        try:
            result = subprocess.run(
                ["firecrawl", "scrape", url, "--json"],
                capture_output=True, text=True, timeout=30,
            )
            if result.returncode != 0:
                return None
            data = json.loads(result.stdout)
            if isinstance(data, dict):
                return data.get("markdown", data.get("content", ""))
            elif isinstance(data, list) and data:
                return data[0].get("markdown", "")
            return None
        except Exception:
            return None

    def research(self, query, max_papers=5, search_limit=15, year_from=2024,
                 extract_full_text=False, find_free_pdfs=True):
        papers = self.search(query, limit=search_limit, year_from=year_from)
        top_papers = papers[:max_papers]
        if find_free_pdfs:
            for paper in top_papers:
                if not paper.get("open_access") and paper.get("doi"):
                    pdf_url = self.find_free_pdf(paper["doi"])
                    if pdf_url:
                        paper["free_pdf_url"] = pdf_url
                        paper["open_access"] = True
        if extract_full_text:
            for paper in top_papers:
                url = paper.get("oa_url") or paper.get("free_pdf_url")
                if url:
                    text = self.get_full_text(url)
                    if text:
                        paper["full_text"] = text[:50000]
                        paper["full_text_length"] = len(text)
        return {"query": query, "total_found": len(papers), "papers_processed": len(top_papers), "papers": top_papers}


if __name__ == "__main__":
    # Quick connection test
    client = AcademicClient()
    results = client.search("artificial intelligence", limit=3, year_from=2024)
    if results:
        print(f"Connected to OpenAlex. Found papers. First result:")
        print(f"  Title: {results[0]['title']}")
        print(f"  Year: {results[0]['year']} | Cited by: {results[0]['cited_by']}")
    else:
        print("Connection failed. Check your internet connection.")
````

[VERIFY]
```bash
ls scripts/academic/client.py scripts/academic/__init__.py
```
Expected: Both files listed.

Ask: "Files are in place. Let's run a quick test to make sure everything works."

---

## TEST

### Quick connection test
```bash
python3 scripts/academic/client.py
```
Expected output: `Connected to OpenAlex. Found papers. First result:` followed by a paper title and citation count.

If you see a connection error: check your internet connection. OpenAlex is a public API, no authentication needed.

### Full test with Claude

Ask Claude: "Search for academic papers about AI code generation from 2024 onwards"

Claude should use the Academic Search skill, call the OpenAlex API, and return a list of papers with titles, authors, abstracts, and citation counts. If it works, the module is fully installed.

---

## WHAT'S NEXT

Claude can now search academic literature any time you ask. Some things to try:

- **Literature review:** "Find the 10 most cited papers on retrieval-augmented generation from the last two years"
- **Free PDF hunting:** "Find a free PDF of this paper: [paste DOI]"
- **Citation graph:** "What are the most influential papers that cite 'Attention Is All You Need'?"
- **Research pipeline:** "Research the current state of AI agents in software engineering, find the top 5 papers from 2024+, and summarize each one"
- **Filtering:** "Find open access papers about large language model evaluation with at least 50 citations"

---

> A plug-and-play module from Liam Ottley's AAA Accelerator, the #1 AI business launch
> & AIOS program. Grab this and 15+ more at [aaaaccelerator.com](https://aaaaccelerator.com)
