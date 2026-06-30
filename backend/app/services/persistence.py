import logging
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import SessionLocal
from app.models import Article, ContentType, FetchStatus, NewsCategory, Source, SourceType

logger = logging.getLogger(__name__)

CONTENT_TYPE_MAP = {
    "reporting": ContentType.REPORTING,
    "opinion": ContentType.OPINION,
    "analysis": ContentType.ANALYSIS,
    "social": ContentType.SOCIAL,
}


async def get_or_create_source(
    db: AsyncSession,
    name: str,
    source_type: SourceType,
    feed_url: str | None = None,
    fetch_status: FetchStatus = FetchStatus.OK,
) -> Source:
    result = await db.execute(select(Source).where(Source.name == name))
    source = result.scalar_one_or_none()
    if source:
        source.last_fetched_at = datetime.now(tz=UTC)
        source.fetch_status = fetch_status
        if feed_url:
            source.feed_url = feed_url
        return source

    source = Source(
        name=name,
        source_type=source_type,
        feed_url=feed_url,
        last_fetched_at=datetime.now(tz=UTC),
        fetch_status=fetch_status,
    )
    db.add(source)
    await db.flush()
    return source


async def upsert_article(db: AsyncSession, source: Source, item: dict) -> bool:
    """Insert article if new. Returns True if inserted."""
    external_id = item.get("external_id") or item.get("url", "")
    if not external_id or not item.get("headline"):
        return False

    result = await db.execute(
        select(Article).where(
            Article.source_id == source.id,
            Article.external_id == external_id,
        )
    )
    if result.scalar_one_or_none():
        return False

    category = item.get("category", NewsCategory.GENERAL)
    if isinstance(category, str):
        category = NewsCategory(category)

    content_type_raw = item.get("content_type", "reporting")
    content_type = CONTENT_TYPE_MAP.get(content_type_raw, ContentType.REPORTING)

    published_at = item.get("published_at")
    if not isinstance(published_at, datetime):
        published_at = datetime.now(tz=UTC)

    article = Article(
        source_id=source.id,
        external_id=external_id,
        headline=item["headline"],
        original_url=item.get("url", ""),
        author=item.get("author"),
        published_at=published_at,
        category=category,
        content_type=content_type,
        is_developing=bool(item.get("is_developing", False)),
        ai_summary=item.get("summary") or item.get("summary_snippet", "")[:300],
        relevance_score=float(item.get("relevance_score", 0.5)),
        raw_metadata={"snippet": item.get("summary_snippet", "")},
    )
    db.add(article)
    return True


async def save_items(
    source_name: str,
    source_type: SourceType,
    items: list[dict],
    feed_url: str | None = None,
    fetch_status: FetchStatus = FetchStatus.OK,
) -> int:
    """Persist fetched items. Returns count of newly inserted articles."""
    inserted = 0
    async with SessionLocal() as db:
        source = await get_or_create_source(
            db, source_name, source_type, feed_url=feed_url, fetch_status=fetch_status
        )
        for item in items:
            if await upsert_article(db, source, item):
                inserted += 1
        await db.commit()
    logger.info("Saved %d new articles from %s", inserted, source_name)
    return inserted
