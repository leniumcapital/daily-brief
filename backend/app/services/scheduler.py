import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.settings import get_settings
from app.services.ingestion import run_ingestion_cycle

logger = logging.getLogger(__name__)
settings = get_settings()


def create_scheduler() -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()

    scheduler.add_job(
        run_ingestion_cycle,
        "interval",
        seconds=settings.rss_refresh_interval,
        id="sources_ingestion",
        kwargs={"stream": "sources"},
        replace_existing=True,
    )
    scheduler.add_job(
        run_ingestion_cycle,
        "interval",
        seconds=settings.x_refresh_interval,
        id="twitter_ingestion",
        kwargs={"stream": "twitter"},
        replace_existing=True,
    )
    scheduler.add_job(
        run_ingestion_cycle,
        "interval",
        seconds=settings.aggregator_refresh_interval,
        id="aggregator_ingestion",
        kwargs={"stream": "aggregator"},
        replace_existing=True,
    )

    return scheduler
