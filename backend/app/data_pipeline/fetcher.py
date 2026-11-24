import asyncio
import hashlib
import html
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Dict, List, Tuple
from urllib.parse import quote_plus

import httpx

try:
    import feedparser  # type: ignore
except ImportError:
    feedparser = None

from app.database import get_cached_mentions, save_mentions

USER_AGENT = "BrandPulse3D-AcademicMonitor/1.0 (+https://localhost)"


def _clean_html(raw: str) -> str:
    if not raw:
        return ""
    text = html.unescape(raw)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _make_id(brand: str, source: str, title: str, text: str) -> str:
    raw = f"{brand.lower()}|{source.lower()}|{title[:80]}|{text[:120]}"
    return hashlib.sha256(raw.encode("utf-8", errors="ignore")).hexdigest()[:16]


def _parse_pubdate(raw_date: str) -> str:
    if not raw_date:
        return datetime.now(timezone.utc).isoformat()
    try:
        dt = parsedate_to_datetime(raw_date)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc).isoformat()
    except Exception:
        try:
            dt = datetime.fromisoformat(raw_date.replace("Z", "+00:00"))
            return dt.astimezone(timezone.utc).isoformat()
        except Exception:
            return datetime.now(timezone.utc).isoformat()


async def fetch_google_news_rss(client: httpx.AsyncClient, brand: str, limit: int = 20) -> List[Dict]:
    query = quote_plus(f'"{brand}" OR {brand} review OR {brand} customers')
    url = f"https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
    items: List[Dict] = []
    try:
        resp = await client.get(url, timeout=8.0)
        if resp.status_code != 200 or not resp.text:
            return []

        if feedparser is not None:
            parsed = feedparser.parse(resp.text)
            for entry in parsed.entries[:limit]:
                title = _clean_html(getattr(entry, "title", ""))
                summary = _clean_html(getattr(entry, "summary", ""))
                source_title = "Google News"
                if hasattr(entry, "source") and isinstance(entry.source, dict):
                    source_title = entry.source.get("title", "Google News")
                elif " - " in title:
                    parts = title.rsplit(" - ", 1)
                    title, source_title = parts[0].strip(), parts[1].strip()
                text = summary if len(summary) > len(title) + 15 else title
                pub = _parse_pubdate(getattr(entry, "published", ""))
                link = getattr(entry, "link", f"https://news.google.com/search?q={quote_plus(brand)}")
                items.append(
                    {
                        "id": _make_id(brand, "Google News", title, text),
                        "brand": brand,
                        "source": "Google News",
                        "author": source_title or "News Desk",
                        "title": title or f"{brand} News Mention",
                        "text": text,
                        "url": link,
                        "published_at": pub,
                    }
                )
        else:
            root = ET.fromstring(resp.text)
            for item in root.findall(".//item")[:limit]:
                title = _clean_html(item.findtext("title", ""))
                desc = _clean_html(item.findtext("description", ""))
                pub = _parse_pubdate(item.findtext("pubDate", ""))
                link = item.findtext("link", f"https://news.google.com/search?q={quote_plus(brand)}")
                source_el = item.find("source")
                author = source_el.text.strip() if source_el is not None and source_el.text else "Google News"
                text = desc if len(desc) > len(title) + 15 else title
                items.append(
                    {
                        "id": _make_id(brand, "Google News", title, text),
                        "brand": brand,
                        "source": "Google News",
                        "author": author,
                        "title": title,
                        "text": text,
                        "url": link,
                        "published_at": pub,
                    }
                )
    except Exception:
        return []
    return items


async def fetch_bluesky_posts(client: httpx.AsyncClient, brand: str, limit: int = 18) -> List[Dict]:
    url = "https://public.api.bsky.app/xrpc/app.bsky.feed.searchPosts"
    params = {"q": brand, "limit": limit, "lang": "en"}
    items: List[Dict] = []
    try:
        resp = await client.get(url, params=params, timeout=7.0)
        if resp.status_code != 200:
            return []
        data = resp.json()
        for post in data.get("posts", []):
            record = post.get("record", {})
            text = _clean_html(record.get("text", ""))
            if len(text) < 15:
                continue
            author_obj = post.get("author", {})
            handle = author_obj.get("handle", "bsky_user")
            uri = post.get("uri", "")
            rkey = uri.split("/")[-1] if "/" in uri else ""
            post_url = f"https://bsky.app/profile/{handle}/post/{rkey}" if rkey else f"https://bsky.app/search?q={quote_plus(brand)}"
            pub = _parse_pubdate(record.get("createdAt", ""))
            title = text[:90] + ("..." if len(text) > 90 else "")
            items.append(
                {
                    "id": _make_id(brand, "Bluesky", title, text),
                    "brand": brand,
                    "source": "Bluesky",
                    "author": f"@{handle}",
                    "title": title,
                    "text": text,
                    "url": post_url,
                    "published_at": pub,
                }
            )
    except Exception:
        return []
    return items


async def fetch_hackernews_mentions(client: httpx.AsyncClient, brand: str, limit: int = 12) -> List[Dict]:
    url = "https://hn.algolia.com/api/v1/search_by_date"
    params = {"query": brand, "tags": "(story,comment)", "hitsPerPage": limit}
    items: List[Dict] = []
    try:
        resp = await client.get(url, params=params, timeout=7.0)
        if resp.status_code != 200:
            return []
        data = resp.json()
        for hit in data.get("hits", []):
            story_title = _clean_html(hit.get("title") or hit.get("story_title") or f"{brand} Discussion")
            comment_text = _clean_html(hit.get("comment_text") or hit.get("story_text") or "")
            text = comment_text if len(comment_text) >= 20 else story_title
            if len(text) < 15:
                continue
            oid = hit.get("objectID", "")
            post_url = hit.get("url") or f"https://news.ycombinator.com/item?id={oid}"
            pub = _parse_pubdate(hit.get("created_at", ""))
            items.append(
                {
                    "id": _make_id(brand, "Hacker News", story_title, text),
                    "brand": brand,
                    "source": "Hacker News",
                    "author": hit.get("author", "hn_user"),
                    "title": story_title[:160],
                    "text": text[:650],
                    "url": post_url,
                    "published_at": pub,
                }
            )
    except Exception:
        return []
    return items


async def fetch_brand_mentions_hybrid(
    brand: str,
    force_live: bool = True,
    max_total: int = 55,
) -> Tuple[List[Dict], str]:
    clean_brand = brand.strip()
    live_items: List[Dict] = []

    if force_live:
        headers = {"User-Agent": USER_AGENT, "Accept": "application/json, application/xml, text/xml"}
        async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
            results = await asyncio.gather(
                fetch_google_news_rss(client, clean_brand, limit=20),
                fetch_bluesky_posts(client, clean_brand, limit=18),
                fetch_hackernews_mentions(client, clean_brand, limit=12),
                return_exceptions=True,
            )
            for res in results:
                if isinstance(res, list):
                    live_items.extend(res)

    if live_items:
        save_mentions(clean_brand, live_items, is_seeded=0)

    cached_items = get_cached_mentions(clean_brand, limit=max_total)

    if live_items and len(cached_items) > len(live_items):
        return cached_items[:max_total], "HYBRID_CACHE"
    if live_items:
        return live_items[:max_total], "LIVE_WEB"
    if cached_items:
        has_seed = any(item.get("is_seeded") == 1 for item in cached_items)
        return cached_items[:max_total], ("SEEDED_DEFAULT" if has_seed else "HYBRID_CACHE")

    now_iso = datetime.now(timezone.utc).isoformat()
    offline_notice = [
        {
            "id": _make_id(clean_brand, "Offline Fallback", f"{clean_brand} overview", "offline"),
            "brand": clean_brand,
            "source": "Local Fallback",
            "author": "System Monitor",
            "title": f"No live network response received for {clean_brand}",
            "text": f"Live internet sources could not be reached for {clean_brand}. Connect to the internet or select one of the preloaded brands (Apple, Tesla, Samsung, Zomato, Swiggy, Nike).",
            "url": "",
            "published_at": now_iso,
        }
    ]
    return offline_notice, "SEEDED_DEFAULT"
