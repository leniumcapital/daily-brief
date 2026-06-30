import logging
from datetime import UTC, datetime

import httpx

from app.models import FetchStatus, NewsCategory, SourceType
from app.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class NewsAPIFetcher:
    """Licensed NewsAPI.org access — headlines by source or category."""

    BASE = "https://newsapi.org/v2"

    def __init__(self, client: httpx.AsyncClient | None = None):
        self._client = client

    @property
    def configured(self) -> bool:
        return bool(settings.newsapi_key)

    async def _get(self, path: str, params: dict) -> dict:
        if not self.configured:
            raise ValueError("NEWSAPI_KEY not configured")
        params = {**params, "apiKey": settings.newsapi_key}
        if self._client:
            response = await self._client.get(f"{self.BASE}/{path}", params=params, timeout=30.0)
        else:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.BASE}/{path}", params=params, timeout=30.0)
        response.raise_for_status()
        data = response.json()
        if data.get("status") != "ok":
            raise ValueError(data.get("message", "NewsAPI error"))
        return data

    async def fetch_source(
        self, source_id: str, category: NewsCategory
    ) -> tuple[list[dict], FetchStatus, str | None]:
        try:
            data = await self._get(
                "top-headlines",
                {"sources": source_id, "pageSize": 20, "language": "en"},
            )
            return self._parse_articles(data, category), FetchStatus.OK, None
        except Exception as exc:
            logger.warning("NewsAPI source '%s' failed: %s", source_id, exc)
            return [], FetchStatus.STALE, str(exc)

    async def fetch_category(
        self, category: NewsCategory
    ) -> tuple[list[dict], FetchStatus, str | None]:
        category_map = {
            NewsCategory.FINANCE_MARKETS: "business",
            NewsCategory.TECHNOLOGY_STARTUPS: "technology",
            NewsCategory.MACRO_POLICY: "general",
            NewsCategory.GENERAL: "general",
        }
        try:
            data = await self._get(
                "top-headlines",
                {
                    "category": category_map.get(category, "general"),
                    "pageSize": 20,
                    "language": "en",
                    "country": "us",
                },
            )
            return self._parse_articles(data, category), FetchStatus.OK, None
        except Exception as exc:
            logger.warning("NewsAPI category '%s' failed: %s", category.value, exc)
            return [], FetchStatus.STALE, str(exc)

    def _parse_articles(self, data: dict, category: NewsCategory) -> list[dict]:
        items = []
        for article in data.get("articles", []):
            headline = (article.get("title") or "").strip()
            if not headline or headline == "[Removed]":
                continue
            items.append(
                {
                    "external_id": article.get("url", ""),
                    "headline": headline,
                    "summary_snippet": (article.get("description") or "")[:500],
                    "url": article.get("url", ""),
                    "author": article.get("author"),
                    "published_at": self._parse_date(article.get("publishedAt")),
                    "category": category,
                    "source_type": SourceType.AGGREGATOR,
                    "outlet": article.get("source", {}).get("name"),
                }
            )
        return items

    @staticmethod
    def _parse_date(value: str | None) -> datetime:
        if not value:
            return datetime.now(tz=UTC)
        return datetime.fromisoformat(value.replace("Z", "+00:00"))


# Backward-compatible alias
AggregatorFetcher = NewsAPIFetcher
