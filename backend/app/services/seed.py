"""Seed sample articles in development when the database is empty."""

import logging
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select

from app.database import SessionLocal
from app.models import Article, ContentType, NewsCategory, Source, SourceType
from app.settings import get_settings

logger = logging.getLogger(__name__)

SAMPLES = [
    {
        "source": "Bloomberg",
        "type": SourceType.RSS,
        "category": NewsCategory.FINANCE_MARKETS,
        "headline": "Markets steady as investors weigh rate outlook",
        "summary": "Equity indexes held near recent highs while bond yields moved modestly ahead of central bank commentary. Traders are focused on inflation data and whether policymakers signal a slower pace of cuts.",
        "url": "https://www.bloomberg.com/markets",
    },
    {
        "source": "TechCrunch",
        "type": SourceType.RSS,
        "category": NewsCategory.TECHNOLOGY_STARTUPS,
        "headline": "AI startups race to close enterprise deals ahead of summer",
        "summary": "Several venture-backed companies announced new partnerships with Fortune 500 firms, signaling that enterprise AI budgets remain active despite broader funding caution in the private markets.",
        "url": "https://techcrunch.com",
    },
    {
        "source": "The Information",
        "type": SourceType.RSS,
        "category": NewsCategory.TECHNOLOGY_STARTUPS,
        "headline": "Series B round values infra startup at $1.2B amid AI buildout",
        "summary": "The company raised $180M to expand GPU cloud capacity, joining a wave of funding for infrastructure plays serving model training demand from mid-size AI labs.",
        "url": "https://www.theinformation.com",
    },
    {
        "source": "Financial Times",
        "type": SourceType.RSS,
        "category": NewsCategory.MACRO_POLICY,
        "headline": "Governments coordinate response to trade policy uncertainty",
        "summary": "Officials from multiple economies discussed tariff impacts and supply-chain adjustments in a closed-door forum. Analysts expect further policy statements later this week.",
        "url": "https://www.ft.com",
    },
]


async def seed_if_empty() -> int:
    settings = get_settings()
    if settings.environment != "development":
        return 0

    async with SessionLocal() as db:
        count = await db.scalar(select(func.count()).select_from(Article))
        if count and count > 0:
            return 0

        inserted = 0
        now = datetime.now(tz=UTC)
        for i, sample in enumerate(SAMPLES):
            result = await db.execute(select(Source).where(Source.name == sample["source"]))
            source = result.scalar_one_or_none()
            if not source:
                source = Source(name=sample["source"], source_type=sample["type"])
                db.add(source)
                await db.flush()

            article = Article(
                source_id=source.id,
                external_id=f"seed-{i}",
                headline=sample["headline"],
                original_url=sample["url"],
                published_at=now - timedelta(hours=i + 1),
                category=sample["category"],
                content_type=ContentType.REPORTING,
                ai_summary=sample["summary"],
                relevance_score=0.85 - (i * 0.05),
            )
            db.add(article)
            inserted += 1

        await db.commit()
        logger.info("Seeded %d sample articles for development", inserted)
        return inserted
