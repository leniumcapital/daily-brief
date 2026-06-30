import logging

from app.config.source_rankings import load_source_rankings
from app.models import FetchStatus, NewsCategory, SourceType
from app.services.fetchers.aggregator import AggregatorFetcher
from app.services.fetchers.rss import refresh_rss_source
from app.services.fetchers.twitter import TwitterFetcher
from app.services.persistence import save_items
from app.services.summarizer import Summarizer

logger = logging.getLogger(__name__)


async def run_ingestion_cycle(stream: str = "all") -> dict:
    """Fetch, summarize, and persist content from configured sources."""
    config = load_source_rankings()
    summarizer = Summarizer()
    stats: dict[str, int] = {}

    if stream in ("all", "rss"):
        stats["rss"] = await _ingest_rss(config, summarizer)
    if stream in ("all", "twitter"):
        stats["twitter"] = await _ingest_twitter(summarizer)
    if stream in ("all", "aggregator"):
        stats["aggregator"] = await _ingest_aggregator(summarizer)

    total = sum(stats.values())
    logger.info("Ingestion complete for stream=%s, %d new articles", stream, total)
    return {"stream": stream, "new_articles": total, "by_source": stats}


async def _ingest_rss(config: dict, summarizer: Summarizer) -> int:
    from app.models import Source, SourceType

    feeds = config.get("rss_feeds", {})
    total = 0
    for name, feed_config in feeds.items():
        source = Source(
            name=name,
            source_type=SourceType.RSS,
            feed_url=feed_config["url"],
        )
        category = NewsCategory(feed_config["category"])
        items, status = await refresh_rss_source(source, category)
        for item in items:
            item["category"] = category
            result = await summarizer.summarize(
                item["headline"],
                item.get("summary_snippet", ""),
                name,
                interests={},
            )
            item.update(result)
        total += await save_items(
            name,
            SourceType.RSS,
            items,
            feed_url=feed_config["url"],
            fetch_status=status,
        )
        logger.info("RSS: fetched %d items from %s (status=%s)", len(items), name, status)
    return total


async def _ingest_twitter(summarizer: Summarizer) -> int:
    fetcher = TwitterFetcher()
    items = await fetcher.fetch_accounts([])
    items += await fetcher.search_keywords([])
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
    logger.info("Twitter: fetched %d items", len(items))
    return count


async def _ingest_aggregator(summarizer: Summarizer) -> int:
    fetcher = AggregatorFetcher()
    total = 0
    for category in NewsCategory:
        items, status = await fetcher.fetch_top_headlines(category)
        for item in items:
            item["category"] = category
            result = await summarizer.summarize(
                item["headline"],
                item.get("summary_snippet", ""),
                "NewsAPI",
                interests={},
            )
            item.update(result)
        total += await save_items(
            f"NewsAPI ({category.value})",
            SourceType.AGGREGATOR,
            items,
            fetch_status=status,
        )
        logger.info(
            "Aggregator: fetched %d items for %s (status=%s)", len(items), category.value, status
        )
    return total
