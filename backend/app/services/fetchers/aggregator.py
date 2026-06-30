import logging
from datetime import UTC, datetime

import httpx

from app.config import get_settings
from app.models import FetchStatus, NewsCategory, SourceType

logger = logging.getLogger(__name__)
settings = get_settings()


class AggregatorFetcher:
    """Licensed aggregator APIs (e.g. NewsAPI) for headline-level content."""

    NEWSAPI_BASE = "https://newsapi.org/v2"

    def __init__(self, client: httpx.AsyncClient | None = None):
        self._client = client

    async def fetch_top_headlines(
        self, category: NewsCategory, sources: str | None = None
    ) -> tuple[list[dict], FetchStatus]:
        if not settings.newsapi_key:
            logger.info("NewsAPI key not configured; skipping aggregator fetch")
            return [], FetchStatus.ERROR

        params = {
            "apiKey": settings.newsapi_key,
            "language": "en",
            "pageSize": 20,
        }
        category_map = {
            NewsCategory.FINANCE_MARKETS: "business",
            NewsCategory.TECHNOLOGY_STARTUPS: "technology",
            NewsCategory.MACRO_POLICY: "general",
        }
        if cat := category_map.get(category):
            params["category"] = cat
        if sources:
            params["sources"] = sources

        try:
            if self._client:
                response = await self._client.get(
                    f"{self.NEWSAPI_BASE}/top-headlines", params=params, timeout=30.0
                )
            else:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{self.NEWSAPI_BASE}/top-headlines", params=params, timeout=30.0
                    )
            response.raise_for_status()
            data = response.json()

            items = []
            for article in data.get("articles", []):
                items.append(
                    {
                        "external_id": article.get("url", ""),
                        "headline": article.get("title", "").strip(),
                        "summary_snippet": (article.get("description") or "")[:500],
                        "url": article.get("url", ""),
                        "author": article.get("author"),
                        "published_at": self._parse_date(article.get("publishedAt")),
                        "category": category,
                        "source_type": SourceType.AGGREGATOR,
                    }
                )
            return items, FetchStatus.OK
        except Exception as exc:
            logger.warning("Aggregator fetch failed: %s", exc)
            return [], FetchStatus.STALE

    @staticmethod
    def _parse_date(value: str | None) -> datetime:
        if not value:
            return datetime.now(tz=UTC)
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
