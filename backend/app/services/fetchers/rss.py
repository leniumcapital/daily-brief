import logging
from datetime import UTC, datetime

import feedparser
import httpx

from app.models import FetchStatus, NewsCategory, Source, SourceType

logger = logging.getLogger(__name__)

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
DEFAULT_HEADERS = {"User-Agent": USER_AGENT, "Accept": "application/rss+xml, application/xml, text/xml, */*"}


class RSSFetcher:
    """Fetch headlines and summaries from official RSS feeds."""

    def __init__(self, client: httpx.AsyncClient | None = None):
        self._client = client

    async def fetch_feed(self, feed_url: str) -> list[dict]:
        if self._client:
            response = await self._client.get(feed_url, headers=DEFAULT_HEADERS, timeout=30.0, follow_redirects=True)
            response.raise_for_status()
            parsed = feedparser.parse(response.text)
        else:
            async with httpx.AsyncClient(headers=DEFAULT_HEADERS, follow_redirects=True) as client:
                response = await client.get(feed_url, timeout=30.0)
                response.raise_for_status()
                parsed = feedparser.parse(response.text)

        if not parsed.entries:
            # Fallback: feedparser can fetch directly with agent string
            parsed = feedparser.parse(feed_url, agent=USER_AGENT)

        items = []
        for entry in parsed.entries:
            items.append(
                {
                    "external_id": entry.get("id") or entry.get("link", ""),
                    "headline": entry.get("title", "").strip(),
                    "summary_snippet": entry.get("summary", "")[:500],
                    "url": entry.get("link", ""),
                    "author": entry.get("author"),
                    "published_at": self._parse_date(entry),
                }
            )
        return items

    @staticmethod
    def _parse_date(entry: dict) -> datetime:
        for key in ("published_parsed", "updated_parsed"):
            parsed = entry.get(key)
            if parsed:
                from time import mktime

                return datetime.fromtimestamp(mktime(parsed), tz=UTC)
        return datetime.now(tz=UTC)


async def refresh_rss_source(source: Source, category: NewsCategory) -> tuple[list[dict], FetchStatus]:
    """Fetch RSS for a source; return items and status (OK or STALE on failure)."""
    if not source.feed_url:
        return [], FetchStatus.ERROR

    fetcher = RSSFetcher()
    try:
        items = await fetcher.fetch_feed(source.feed_url)
        source.last_fetched_at = datetime.now(tz=UTC)
        source.fetch_status = FetchStatus.OK
        source.last_error = None
        for item in items:
            item["category"] = category
            item["source_type"] = SourceType.RSS
        return items, FetchStatus.OK
    except Exception as exc:
        logger.warning("RSS fetch failed for %s: %s", source.name, exc)
        source.fetch_status = FetchStatus.STALE
        source.last_error = str(exc)
        return [], FetchStatus.STALE
