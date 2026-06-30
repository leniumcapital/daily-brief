import asyncio
import logging
import re
from html import unescape

import feedparser

from app.models import FetchStatus, NewsCategory, SourceType

logger = logging.getLogger(__name__)

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


def strip_html(text: str) -> str:
    clean = re.sub(r"<[^>]+>", " ", text or "")
    return unescape(re.sub(r"\s+", " ", clean)).strip()


class RSSFetcher:
    """Fetch headlines via official RSS feeds (feedparser + browser User-Agent)."""

    async def fetch_feed(self, feed_url: str) -> list[dict]:
        loop = asyncio.get_running_loop()
        parsed = await loop.run_in_executor(
            None, lambda: feedparser.parse(feed_url, agent=USER_AGENT)
        )

        if getattr(parsed, "bozo", False) and not parsed.entries:
            raise ValueError(parsed.get("bozo_exception", "Invalid RSS feed"))

        items = []
        for entry in parsed.entries[:25]:
            headline = strip_html(entry.get("title", ""))
            if not headline:
                continue
            items.append(
                {
                    "external_id": entry.get("id") or entry.get("link", ""),
                    "headline": headline,
                    "summary_snippet": strip_html(entry.get("summary", ""))[:500],
                    "url": entry.get("link", ""),
                    "author": entry.get("author"),
                    "published_at": self._parse_date(entry),
                    "source_type": SourceType.RSS,
                }
            )
        return items

    @staticmethod
    def _parse_date(entry: dict):
        from datetime import UTC, datetime
        from time import mktime

        for key in ("published_parsed", "updated_parsed"):
            parsed = entry.get(key)
            if parsed:
                return datetime.fromtimestamp(mktime(parsed), tz=UTC)
        return datetime.now(tz=UTC)


async def fetch_rss(url: str, category: NewsCategory) -> tuple[list[dict], FetchStatus, str | None]:
    fetcher = RSSFetcher()
    try:
        items = await fetcher.fetch_feed(url)
        for item in items:
            item["category"] = category
        return items, FetchStatus.OK, None
    except Exception as exc:
        logger.warning("RSS fetch failed for %s: %s", url, exc)
        return [], FetchStatus.STALE, str(exc)
