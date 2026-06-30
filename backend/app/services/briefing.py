from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Article, FetchStatus, NewsCategory, Source, SourceType, UserProfile
from app.schemas import (
    BriefingItem,
    BriefingSection,
    ContentType,
    DashboardResponse,
    FetchStatus as SchemaFetchStatus,
)
from app.services.ranking import CATEGORY_LABELS


class BriefingService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_dashboard(self) -> DashboardResponse:
        profile = await self._get_profile()
        stale_sources = await self._get_stale_sources()

        sections = []
        for category in NewsCategory:
            if category == NewsCategory.GENERAL:
                continue
            items = await self._get_items_for_category(category, profile)
            if items:
                sections.append(
                    BriefingSection(
                        category=category,
                        label=CATEGORY_LABELS[category],
                        items=items,
                    )
                )

        twitter_items = await self._get_twitter_items(profile)
        twitter_section = (
            BriefingSection(
                category=NewsCategory.GENERAL,
                label="X / Twitter",
                items=twitter_items,
            )
            if twitter_items
            else None
        )

        return DashboardResponse(
            generated_at=datetime.now(tz=UTC),
            sections=sections,
            twitter_section=twitter_section,
            stale_sources=stale_sources,
        )

    async def _get_profile(self) -> UserProfile | None:
        result = await self.db.execute(select(UserProfile).limit(1))
        return result.scalar_one_or_none()

    async def _get_stale_sources(self) -> list[str]:
        result = await self.db.execute(
            select(Source.name).where(Source.fetch_status != FetchStatus.OK)
        )
        return list(result.scalars().all())

    async def _get_items_for_category(
        self, category: NewsCategory, profile: UserProfile | None
    ) -> list[BriefingItem]:
        result = await self.db.execute(
            select(Article, Source)
            .join(Source)
            .where(Article.category == category)
            .where(Source.source_type != SourceType.TWITTER)
            .order_by(Article.relevance_score.desc())
            .limit(15)
        )
        return [self._to_briefing_item(article, source) for article, source in result.all()]

    async def _get_twitter_items(self, profile: UserProfile | None) -> list[BriefingItem]:
        result = await self.db.execute(
            select(Article, Source)
            .join(Source)
            .where(Source.source_type == SourceType.TWITTER)
            .order_by(Article.published_at.desc())
            .limit(20)
        )
        return [self._to_briefing_item(article, source) for article, source in result.all()]

    def _to_briefing_item(self, article: Article, source: Source) -> BriefingItem:
        return BriefingItem(
            id=article.id,
            headline=article.headline,
            summary=article.ai_summary or "",
            source_name=source.name,
            source_type=source.source_type.value,
            category=article.category,
            content_type=ContentType(article.content_type.value),
            relevance_score=article.relevance_score,
            is_developing=article.is_developing,
            is_serendipity=article.is_serendipity,
            published_at=article.published_at,
            url=article.original_url,
            fetch_status=SchemaFetchStatus(source.fetch_status.value),
        )
