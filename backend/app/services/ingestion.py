import logging

from app.config.source_rankings import load_source_rankings
from app.services.fetchers.aggregator import AggregatorFetcher
from app.services.fetchers.rss import refresh_rss_source
from app.services.fetchers.twitter import TwitterFetcher
from app.services.ranking import apply_serendipity, rank_articles
from app.services.summarizer import Summarizer

logger = logging.getLogger(__name__)


async def run_ingestion_cycle(stream: str = "all") -> None:
    """Fetch, summarize, deduplicate, and cache content from configured sources."""
    config = load_source_rankings()
    summarizer = Summarizer()

    if stream in ("all", "rss"):
        await _ingest_rss(config, summarizer)
    if stream in ("all", "twitter"):
        await _ingest_twitter(summarizer)
    if stream in ("all", "aggregator"):
        await _ingest_aggregator(summarizer)

    logger.info("Ingestion cycle complete for stream=%s", stream)


async def _ingest_rss(config: dict, summarizer: Summarizer) -> None:
    from app.models import NewsCategory, Source, SourceType

    feeds = config.get("rss_feeds", {})
    for name, feed_config in feeds.items():
        source = Source(
            name=name,
            source_type=SourceType.RSS,
            feed_url=feed_config["url"],
        )
        category = NewsCategory(feed_config["category"])
        items, status = await refresh_rss_source(source, category)
        for item in items:
            result = await summarizer.summarize(
                item["headline"],
                item.get("summary_snippet", ""),
                name,
                interests={},
            )
            item.update(result)
        logger.info("RSS: fetched %d items from %s (status=%s)", len(items), name, status)


async def _ingest_twitter(summarizer: Summarizer) -> None:
    fetcher = TwitterFetcher()
    # Default accounts/keywords loaded from profile in production
    items = await fetcher.fetch_accounts([])
    items += await fetcher.search_keywords([])
    for item in items:
        result = await summarizer.summarize(
            item["headline"],
            item.get("summary_snippet", ""),
            "X/Twitter",
            interests={},
        )
        item.update(result)
    logger.info("Twitter: fetched %d items", len(items))


async def _ingest_aggregator(summarizer: Summarizer) -> None:
    from app.models import NewsCategory

    fetcher = AggregatorFetcher()
    for category in NewsCategory:
        items, status = await fetcher.fetch_top_headlines(category)
        for item in items:
            result = await summarizer.summarize(
                item["headline"],
                item.get("summary_snippet", ""),
                "NewsAPI",
                interests={},
            )
            item.update(result)
        logger.info(
            "Aggregator: fetched %d items for %s (status=%s)", len(items), category.value, status
        )
