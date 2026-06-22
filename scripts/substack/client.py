"""
Substack Search & Content Client

Usage:
    from scripts.substack.client import SubstackClient
    client = SubstackClient()
    results = client.search("AI coding agents")
    post = client.get_post("oneusefulthing", "the-shape-of-the-thing")
"""

import json
import os
import re
import subprocess
import time
from datetime import datetime, timezone
from html import unescape
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

_last_substack_request = 0.0


def _rate_limit(min_delay=2.0):
    global _last_substack_request
    elapsed = time.time() - _last_substack_request
    if elapsed < min_delay:
        time.sleep(min_delay - elapsed)
    _last_substack_request = time.time()


def _strip_html(html):
    if not html:
        return ""
    text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
    text = re.sub(r'<br\s*/?>', '\n', text)
    text = re.sub(r'</p>', '\n\n', text)
    text = re.sub(r'</h[1-6]>', '\n\n', text)
    text = re.sub(r'</li>', '\n', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = unescape(text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


class SubstackClient:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept": "application/json",
        })

    def search(self, query, limit=10):
        try:
            result = subprocess.run(
                ["firecrawl", "search", f"{query} site:substack.com",
                 "--limit", str(limit), "--json"],
                capture_output=True, text=True, timeout=60,
                cwd=str(Path(__file__).resolve().parent.parent.parent),
            )
            if result.returncode != 0:
                return []
            data = json.loads(result.stdout)
            items = []
            if isinstance(data, dict):
                web = data.get("data", {}).get("web", data.get("results", []))
                if isinstance(web, list):
                    items = web
            elif isinstance(data, list):
                items = data
            results = []
            for item in items[:limit]:
                url = item.get("url", item.get("metadata", {}).get("sourceURL", ""))
                title = item.get("title", item.get("metadata", {}).get("title", ""))
                desc = item.get("description", item.get("metadata", {}).get("description", ""))
                pub, slug = self._parse_substack_url(url)
                results.append({"title": title, "url": url, "description": desc,
                               "publication": pub, "slug": slug})
            return results
        except Exception as e:
            print(f"Firecrawl search failed: {e}")
            return []

    def _parse_substack_url(self, url):
        match = re.search(r'(?:https?://)?([^./]+)\.substack\.com/p/([^/?#]+)', url)
        if match:
            return match.group(1), match.group(2)
        match = re.search(r'open\.substack\.com/pub/([^/]+)/p/([^/?#]+)', url)
        if match:
            return match.group(1), match.group(2)
        slug = ""
        pub = ""
        match = re.search(r'/p/([^/?#]+)', url)
        if match:
            slug = match.group(1)
            domain_match = re.search(r'https?://(?:www\.)?([^./]+)', url)
            if domain_match:
                pub = domain_match.group(1)
        return pub, slug

    def _api_get(self, base_url, path, params=None):
        _rate_limit()
        url = f"https://{base_url}/api/v1{path}"
        try:
            resp = self.session.get(url, params=params or {}, timeout=15)
            if resp.status_code == 429:
                time.sleep(10)
                resp = self.session.get(url, params=params or {}, timeout=15)
            if resp.status_code != 200:
                return None
            return resp.json()
        except Exception:
            return None

    def list_posts(self, publication, limit=12, offset=0, sort="new"):
        for base in [f"{publication}.substack.com", f"www.{publication}.com", publication]:
            data = self._api_get(base, "/archive", {"sort": sort, "limit": limit, "offset": offset})
            if data and isinstance(data, list):
                return [{"title": p.get("title", ""), "slug": p.get("slug", ""),
                         "date": p.get("post_date", ""), "wordcount": p.get("wordcount", 0),
                         "reactions": p.get("reactions", {}), "subtitle": p.get("subtitle", ""),
                         "audience": p.get("audience", ""), "comment_count": p.get("comment_count", 0),
                         "publication": publication,
                         "url": f"https://{base}/p/{p.get('slug', '')}"} for p in data]
        return []

    def get_post(self, publication, slug, as_text=True):
        for base in [f"{publication}.substack.com", f"www.{publication}.com", publication]:
            data = self._api_get(base, f"/posts/{slug}")
            if data and isinstance(data, dict) and data.get("title"):
                body_html = data.get("body_html", "") or ""
                body = _strip_html(body_html) if as_text else body_html
                return {"title": data.get("title", ""), "slug": slug,
                        "date": data.get("post_date", ""), "body": body,
                        "body_length": len(body), "wordcount": data.get("wordcount", 0),
                        "reactions": data.get("reactions", {}),
                        "comment_count": data.get("comment_count", 0),
                        "subtitle": data.get("subtitle", ""),
                        "audience": data.get("audience", ""),
                        "publication": publication,
                        "url": f"https://{base}/p/{slug}",
                        "canonical_url": data.get("canonical_url", "")}
        return None

    def research(self, query, max_posts=5, search_limit=10):
        search_results = self.search(query, limit=search_limit)
        extracted = []
        for result in search_results[:max_posts]:
            pub = result.get("publication", "")
            slug = result.get("slug", "")
            if not pub or not slug:
                continue
            post = self.get_post(pub, slug)
            if post and post.get("body"):
                extracted.append(post)
        return {"query": query, "search_results_count": len(search_results),
                "search_results": search_results, "extracted_count": len(extracted),
                "extracted_posts": extracted}

    def discover_publications(self, query, limit=10):
        results = self.search(query, limit=limit)
        pubs = {}
        for r in results:
            pub = r.get("publication", "")
            if pub and pub not in pubs and pub != "open":
                pubs[pub] = {"publication": pub, "url": f"https://{pub}.substack.com",
                            "found_via": r.get("title", "")}
        return list(pubs.values())
