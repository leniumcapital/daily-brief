import logging

from app.models import FetchStatus, NewsCategory, SourceType
from app.services.fetchers.aggregator import NewsAPIFetcher
from app.services.fetchers.guardian import GuardianFetcher
from app.services.fetchers.rss import fetch_rss

logger = logging.getLogger(__name__)


class SourceConnector:
    """Try each configured provider for an outlet until one returns articles."""

    def __init__(self):
        self._newsapi = NewsAPIFetcher()
        self._guardian = GuardianFetcher()

    async def fetch_source(
        self, name: str, source_config: dict
    ) -> tuple[list[dict], FetchStatus, str, str | None]:
        """
        Returns: items, status, provider_used, error_message
        """
        category = NewsCategory(source_config["category"])
        providers = source_config.get("providers", [])
        last_error: str | None = None

        for provider in providers:
            ptype = provider.get("type")
            try:
                if ptype == "newsapi":
                    items, status, err = await self._newsapi.fetch_source(
                        provider["source_id"], category
                    )
                elif ptype == "guardian":
                    items, status, err = await self._guardian.fetch_section(
                        provider.get("section", "world"), category
                    )
                elif ptype == "rss":
                    items, status, err = await fetch_rss(provider["url"], category)
                else:
                    continue

                if items:
                    for item in items:
                        item.setdefault("source_type", SourceType.RSS)
                    return items, status, ptype, None

                last_error = err or f"{ptype} returned no articles"
            except Exception as exc:
                last_error = str(exc)
                logger.warning("Provider %s failed for %s: %s", ptype, name, exc)

        return [], FetchStatus.STALE, "none", last_error

    async def check_source(self, name: str, source_config: dict) -> dict:
        """Test connectivity without persisting — used by /sources/status."""
        items, status, provider, error = await self.fetch_source(name, source_config)
        return {
            "name": name,
            "category": source_config.get("category"),
            "status": status.value,
            "provider": provider,
            "article_count": len(items),
            "error": error,
        }
