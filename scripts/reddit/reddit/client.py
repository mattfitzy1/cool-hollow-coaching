"""
Reddit Search & Content Extraction Client
==========================================
Zero-auth Reddit research via public .json endpoints.

Usage:
    from scripts.reddit.client import RedditClient
    client = RedditClient()
    result = client.research("AI automation agencies", time_filter="year", max_threads=5)
"""

import re
import time
from datetime import datetime, timezone
from urllib.parse import quote_plus

import requests


class RedditClient:
    """Reddit search and extraction via public .json endpoints. No API key needed."""

    BASE = "https://www.reddit.com"
    HEADERS = {"User-Agent": "AIOS-Reddit/1.0 (research agent)"}
    MIN_INTERVAL = 6.5

    def __init__(self):
        self._last_request = 0.0

    def _get(self, url, params=None):
        elapsed = time.time() - self._last_request
        if elapsed < self.MIN_INTERVAL:
            time.sleep(self.MIN_INTERVAL - elapsed)
        resp = requests.get(
            url, params=params or {}, headers=self.HEADERS, timeout=30
        )
        self._last_request = time.time()
        if resp.status_code == 429:
            time.sleep(65)
            resp = requests.get(
                url, params=params or {}, headers=self.HEADERS, timeout=30
            )
            self._last_request = time.time()
        resp.raise_for_status()
        return resp.json()

    def search(self, query, sort="relevance", time_filter="year", limit=15,
               subreddit="all"):
        """Search r/all or a specific subreddit."""
        params = {
            "q": query,
            "sort": sort,
            "t": time_filter,
            "limit": min(limit, 100),
            "restrict_sr": "on" if subreddit != "all" else "off",
        }
        data = self._get(
            f"{self.BASE}/r/{subreddit}/search.json", params
        )
        return [
            self._parse_post(p["data"])
            for p in data.get("data", {}).get("children", [])
        ]

    def search_subreddit(self, subreddit, query, sort="relevance",
                         time_filter="year", limit=10):
        """Search within one subreddit."""
        return self.search(
            query, sort=sort, time_filter=time_filter,
            limit=limit, subreddit=subreddit
        )

    def find_subreddits(self, query, limit=5):
        """Auto-detect relevant subreddits for a topic."""
        data = self._get(
            f"{self.BASE}/subreddits/search.json",
            params={"q": query, "limit": limit},
        )
        return [
            {
                "name": s["data"].get("display_name"),
                "subscribers": s["data"].get("subscribers", 0),
                "description": (
                    s["data"].get("public_description") or ""
                )[:200],
                "url": f"/r/{s['data'].get('display_name')}",
                "active_users": s["data"].get("accounts_active", 0),
            }
            for s in data.get("data", {}).get("children", [])
        ]

    def hot(self, subreddit="all", limit=10):
        """Hot posts from a subreddit."""
        data = self._get(
            f"{self.BASE}/r/{subreddit}/hot.json",
            params={"limit": limit},
        )
        return [
            self._parse_post(p["data"])
            for p in data.get("data", {}).get("children", [])
        ]

    def top(self, subreddit="all", time_filter="week", limit=10):
        """Top posts by time period."""
        data = self._get(
            f"{self.BASE}/r/{subreddit}/top.json",
            params={"t": time_filter, "limit": limit},
        )
        return [
            self._parse_post(p["data"])
            for p in data.get("data", {}).get("children", [])
        ]

    def extract_thread(self, url, comment_limit=25):
        """Full post body + top N comments with scores."""
        clean_url = url.rstrip("/")
        if not clean_url.startswith("http"):
            clean_url = f"{self.BASE}{clean_url}"
        clean_url = re.sub(
            r'https?://(?:old\.|new\.)?reddit\.com',
            self.BASE,
            clean_url,
        )
        json_url = clean_url + ".json"
        data = self._get(
            json_url, params={"limit": comment_limit, "sort": "best"}
        )
        if not isinstance(data, list) or len(data) < 2:
            return {"error": "Unexpected response format", "url": url}
        post_data = data[0]["data"]["children"][0]["data"]
        post = self._parse_post(post_data, full_text=True)
        comments = []
        for c in data[1]["data"]["children"]:
            if c.get("kind") == "t1":
                cd = c["data"]
                comments.append({
                    "author": cd.get("author"),
                    "body": cd.get("body", ""),
                    "score": cd.get("score", 0),
                    "created_utc": cd.get("created_utc"),
                    "is_op": cd.get("author") == post.get("author"),
                    "controversiality": cd.get("controversiality", 0),
                })
        comments.sort(key=lambda x: x.get("score", 0), reverse=True)
        post["comments"] = comments[:comment_limit]
        post["comments_extracted"] = len(comments[:comment_limit])
        return post

    def research(self, query, time_filter="year", max_threads=5,
                 max_comments=25, subreddits=None,
                 auto_detect_subreddits=True, max_subreddits=3):
        """Full pipeline: detect subreddits, search, rank, extract top threads."""
        detected_subs = []
        all_posts = []

        if subreddits:
            detected_subs = [{"name": s} for s in subreddits]
        elif auto_detect_subreddits:
            detected_subs = self.find_subreddits(
                query, limit=max_subreddits + 2
            )
            detected_subs = [
                s for s in detected_subs
                if s.get("subscribers", 0) > 100
            ][:max_subreddits]

        sub_names = [s["name"] for s in detected_subs]

        # Search r/all first
        r_all_posts = self.search(
            query, sort="relevance", time_filter=time_filter, limit=15
        )
        all_posts.extend(r_all_posts)

        # Then search each detected subreddit
        for sub_name in sub_names:
            try:
                sub_posts = self.search_subreddit(
                    sub_name, query, time_filter=time_filter, limit=10
                )
                all_posts.extend(sub_posts)
            except Exception:
                pass

        # Deduplicate by URL
        seen_urls = set()
        unique_posts = []
        for p in all_posts:
            if p["url"] not in seen_urls:
                seen_urls.add(p["url"])
                unique_posts.append(p)

        # Rank by weighted engagement
        unique_posts.sort(
            key=lambda p: (
                p.get("score", 0) * 0.6
                + p.get("num_comments", 0) * 0.4
            ),
            reverse=True,
        )

        # Extract top threads
        threads = []
        for post in unique_posts[:max_threads]:
            try:
                thread = self.extract_thread(
                    post["url"], comment_limit=max_comments
                )
                threads.append(thread)
            except Exception as e:
                post["comments"] = []
                post["comments_extracted"] = 0
                post["extraction_error"] = str(e)
                threads.append(post)

        return {
            "query": query,
            "time_filter": time_filter,
            "subreddits_searched": ["all"] + sub_names,
            "subreddits_detected": detected_subs,
            "posts_found": len(unique_posts),
            "threads_extracted": len(threads),
            "threads": threads,
        }

    def _parse_post(self, data, full_text=False):
        """Parse a Reddit post data dict into a clean format."""
        text_limit = 10000 if full_text else 300
        return {
            "title": data.get("title"),
            "subreddit": data.get("subreddit"),
            "score": data.get("score", 0),
            "num_comments": data.get("num_comments", 0),
            "url": f"https://reddit.com{data.get('permalink', '')}",
            "created_utc": data.get("created_utc"),
            "selftext": (data.get("selftext") or "")[:text_limit],
            "author": data.get("author"),
            "upvote_ratio": data.get("upvote_ratio"),
            "link_url": (
                data.get("url") if not data.get("is_self") else None
            ),
        }
