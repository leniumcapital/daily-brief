import logging
from datetime import UTC, datetime

import httpx

from app.models import FetchStatus, NewsCategory, SourceType
from app.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class GuardianFetcher:
    """The Guardian Open Platform API — free tier with API key."""

    BASE = "https://content.guardianapis.com"

    def __init__(self, client: httpx.AsyncClient | None = None):
        self._client = client

    @property
    def configured(self) -> bool:
        return bool(settings.guardian_api_key)

    async def fetch_section(
        self, section: str, category: NewsCategory
    ) -> tuple[list[dict], FetchStatus, str | None]:
        if not self.configured:
            return [], FetchStatus.ERROR, "GUARDIAN_API_KEY not configured"

        params = {
            "api-key": settings.guardian_api_key,
            "section": section,
            "page-size": 20,
            "order-by": "newest",
            "show-fields": "headline,trailText,shortUrl,byline",
        }
        try:
            if self._client:
                response = await self._client.get(f"{self.BASE}/search", params=params, timeout=30.0)
            else:
                async with httpx.AsyncClient() as client:
                    response = await client.get(f"{self.BASE}/search", params=params, timeout=30.0)
            response.raise_for_status()
            data = response.json()
            if data.get("response", {}).get("status") != "ok":
                raise ValueError("Guardian API error")

            items = []
            for result in data.get("response", {}).get("results", []):
                fields = result.get("fields", {})
                headline = fields.get("headline", "").strip()
                if not headline:
                    continue
                items.append(
                    {
                        "external_id": result.get("id", ""),
                        "headline": headline,
                        "summary_snippet": (fields.get("trailText") or "")[:500],
                        "url": fields.get("shortUrl") or result.get("webUrl", ""),
                        "author": fields.get("byline"),
                        "published_at": self._parse_date(result.get("webPublicationDate")),
                        "category": category,
                        "source_type": SourceType.AGGREGATOR,
                    }
                )
            return items, FetchStatus.OK, None
        except Exception as exc:
            logger.warning("Guardian fetch failed (section=%s): %s", section, exc)
            return [], FetchStatus.STALE, str(exc)

    @staticmethod
    def _parse_date(value: str | None) -> datetime:
        if not value:
            return datetime.now(tz=UTC)
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
