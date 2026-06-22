"""
X/Twitter Search Client — Two-layer architecture.

Layer 1: Grok x_search (xAI Responses API) — semantic search, synthesized insights, citations
Layer 2: X API v2 — raw tweet data, engagement metrics, user profiles

Usage:
    from scripts.x_search.client import XSearchClient
    client = XSearchClient()
    result = client.search("AI automation agencies", days_back=7)
"""

import json
import os
import re
from datetime import datetime, timedelta, timezone
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


class XSearchClient:
    """Two-layer X/Twitter search: Grok discovery + X API v2 data."""

    def __init__(self):
        self.xai_key = os.getenv("XAI_API_KEY")
        self.x_bearer = os.getenv("X_BEARER_TOKEN")
        if not self.xai_key:
            raise ValueError("XAI_API_KEY not set in .env")
        self.xai_base = "https://api.x.ai/v1"
        self.x_api_base = "https://api.x.com/2"

    def search(self, query, days_back=None, from_date=None, to_date=None,
               allowed_handles=None, excluded_handles=None,
               enable_images=False, enable_video=False, model="grok-4"):
        x_search_config = {}
        if days_back:
            from_date = (datetime.now(timezone.utc) - timedelta(days=days_back)).strftime("%Y-%m-%d")
        if from_date:
            x_search_config["from_date"] = from_date
        if to_date:
            x_search_config["to_date"] = to_date
        if allowed_handles:
            x_search_config["allowed_x_handles"] = allowed_handles[:10]
        if excluded_handles:
            x_search_config["excluded_x_handles"] = excluded_handles[:10]
        if enable_images:
            x_search_config["enable_image_understanding"] = True
        if enable_video:
            x_search_config["enable_video_understanding"] = True
        tool = {"type": "x_search"}
        if x_search_config:
            tool.update(x_search_config)
        payload = {
            "model": model,
            "input": [{"role": "user", "content": query}],
            "tools": [tool],
        }
        resp = requests.post(
            f"{self.xai_base}/responses",
            headers={"Authorization": f"Bearer {self.xai_key}", "Content-Type": "application/json"},
            json=payload, timeout=90,
        )
        resp.raise_for_status()
        data = resp.json()
        answer = ""
        for item in data.get("output", []):
            if item.get("type") == "message":
                for c in item.get("content", []):
                    if c.get("type") == "output_text":
                        answer += c.get("text", "")
        return {
            "answer": answer,
            "citations": self._extract_citations_from_text(answer),
            "model": data.get("model", model),
            "usage": data.get("usage", {}),
        }

    def _extract_citations_from_text(self, text):
        urls = re.findall(r'https?://(?:x\.com|twitter\.com)/[^\s\)\]\[\'\"]+', text)
        urls = [u.rstrip(".,;") for u in urls]
        return list(set(urls))

    def _x_api_get(self, path, params=None):
        if not self.x_bearer:
            raise ValueError("X_BEARER_TOKEN not set in .env. Get one at https://developer.x.com")
        resp = requests.get(
            f"{self.x_api_base}{path}",
            headers={"Authorization": f"Bearer {self.x_bearer}"},
            params=params or {}, timeout=30,
        )
        if resp.status_code == 429:
            reset = resp.headers.get("x-rate-limit-reset", "unknown")
            raise RuntimeError(f"X API rate limited. Resets at {reset}")
        resp.raise_for_status()
        return resp.json()

    def lookup_tweets(self, tweet_ids, include_metrics=True, include_author=True):
        if not tweet_ids:
            return []
        params = {"ids": ",".join(tweet_ids[:100])}
        tweet_fields = ["created_at", "text", "author_id", "conversation_id", "lang"]
        if include_metrics:
            tweet_fields.append("public_metrics")
        params["tweet.fields"] = ",".join(tweet_fields)
        expansions = []
        if include_author:
            expansions.append("author_id")
            params["user.fields"] = "username,name,verified,public_metrics,profile_image_url"
        if expansions:
            params["expansions"] = ",".join(expansions)
        data = self._x_api_get("/tweets", params)
        tweets = data.get("data", [])
        if include_author and "includes" in data:
            users_map = {u["id"]: u for u in data["includes"].get("users", [])}
            for tweet in tweets:
                author_id = tweet.get("author_id")
                if author_id and author_id in users_map:
                    tweet["author"] = users_map[author_id]
        return tweets

    def search_recent(self, query, max_results=10, sort_order="relevancy",
                      start_time=None, end_time=None, next_token=None):
        params = {
            "query": query[:512], "max_results": min(max_results, 100),
            "sort_order": sort_order,
            "tweet.fields": "created_at,text,author_id,public_metrics,conversation_id,lang",
            "expansions": "author_id",
            "user.fields": "username,name,verified,public_metrics",
        }
        if start_time: params["start_time"] = start_time
        if end_time: params["end_time"] = end_time
        if next_token: params["next_token"] = next_token
        data = self._x_api_get("/tweets/search/recent", params)
        tweets = data.get("data", [])
        if "includes" in data:
            users_map = {u["id"]: u for u in data["includes"].get("users", [])}
            for tweet in tweets:
                author_id = tweet.get("author_id")
                if author_id and author_id in users_map:
                    tweet["author"] = users_map[author_id]
        return {"tweets": tweets, "meta": data.get("meta", {})}

    def lookup_users(self, usernames=None, user_ids=None):
        params = {"user.fields": "created_at,description,public_metrics,verified,verified_type,profile_image_url,url,location"}
        if usernames:
            params["usernames"] = ",".join(usernames[:100])
            path = "/users/by"
        elif user_ids:
            params["ids"] = ",".join(user_ids[:100])
            path = "/users"
        else:
            return []
        data = self._x_api_get(path, params)
        return data.get("data", [])

    def discover_and_enrich(self, query, days_back=7, max_enrich=10, **search_kwargs):
        discovery = self.search(query, days_back=days_back, **search_kwargs)
        tweet_ids = self._extract_tweet_ids(discovery["citations"])
        enriched = []
        if tweet_ids and self.x_bearer:
            enriched = self.lookup_tweets(tweet_ids[:max_enrich])
        return {
            "answer": discovery["answer"], "citations": discovery["citations"],
            "enriched_tweets": enriched, "usage": discovery["usage"],
        }

    def _extract_tweet_ids(self, urls):
        ids = []
        for url in urls:
            match = re.search(r'/status/(\d+)', url)
            if match:
                ids.append(match.group(1))
        return list(set(ids))
