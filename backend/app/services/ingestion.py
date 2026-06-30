import logging

from app.config.source_rankings import get_all_sources, get_twitter_config
from app.models import FetchStatus, NewsCategory, SourceType
from app.services.fetchers.aggregator import NewsAPIFetcher
from app.services.fetchers.twitter import TwitterFetcher
from app.services.persistence import save_items
from app.services.source_connector import SourceConnector
from app.services.summarizer import Summarizer

logger = logging.getLogger(__name__)


async def run_ingestion_cycle(stream: str = "all") -> dict:
    """Fetch, summarize, and persist content from all configured sources."""
    summarizer = Summarizer()
    stats: dict[str, int] = {}

    if stream in ("all", "sources", "rss"):
        stats["sources"] = await _ingest_all_sources(summarizer)
    if stream in ("all", "twitter"):
        stats["twitter"] = await _ingest_twitter(summarizer)
    if stream in ("all", "aggregator"):
        stats["aggregator"] = await _ingest_newsapi_categories(summarizer)

    total = sum(stats.values())
    logger.info("Ingestion complete for stream=%s, %d new articles", stream, total)
    return {"stream": stream, "new_articles": total, "by_source": stats}


async def _ingest_all_sources(summarizer: Summarizer) -> int:
    connector = SourceConnector()
    sources = get_all_sources()
    total = 0

    for name, config in sources.items():
        items, status, provider, error = await connector.fetch_source(name, config)
        category = NewsCategory(config["category"])

        for item in items:
            item["category"] = category
            result = await summarizer.summarize(
                item["headline"],
                item.get("summary_snippet", ""),
                name,
                interests={},
            )
            item.update(result)

        feed_url = next(
            (p["url"] for p in config.get("providers", []) if p.get("type") == "rss"),
            None,
        )
        count = await save_items(
            name,
            SourceType.RSS if provider == "rss" else SourceType.AGGREGATOR,
            items,
            feed_url=feed_url,
            fetch_status=status,
            last_error=error if not items else None,
        )
        total += count
        logger.info(
            "Ingested %d new from %s via %s (fetched=%d, status=%s%s)",
            count,
            name,
            provider,
            len(items),
            status.value,
            f", error={error}" if error and not items else "",
        )

    return total


async def _ingest_twitter(summarizer: Summarizer) -> int:
    twitter_cfg = get_twitter_config()
    accounts = [a.lstrip("@") for a in twitter_cfg.get("accounts", [])]
    keywords = twitter_cfg.get("keywords", [])

    fetcher = TwitterFetcher()
    items = await fetcher.fetch_accounts(accounts)
    items += await fetcher.search_keywords(keywords)

    for item in items:
        item["category"] = NewsCategory.GENERAL
        result = await summarizer.summarize(
            item["headline"],
            item.get("summary_snippet", ""),
            "X/Twitter",
            interests={},
        )
        item.update(result)

    count = await save_items("X/Twitter", SourceType.TWITTER, items)
    logger.info("Twitter: fetched %d items from %d accounts", len(items), len(accounts))
    return count


async def _ingest_newsapi_categories(summarizer: Summarizer) -> int:
    """Supplement with category-wide NewsAPI pulls when key is set."""
    fetcher = NewsAPIFetcher()
    if not fetcher.configured:
        return 0

    total = 0
    for category in NewsCategory:
        items, status, _ = await fetcher.fetch_category(category)
        for item in items:
            result = await summarizer.summarize(
                item["headline"],
                item.get("summary_snippet", ""),
                item.get("outlet", "NewsAPI"),
                interests={},
            )
            item.update(result)
        total += await save_items(
            f"NewsAPI ({category.value})",
            SourceType.AGGREGATOR,
            items,
            fetch_status=status,
        )
    return total
