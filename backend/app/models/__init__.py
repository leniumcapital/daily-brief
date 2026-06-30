import enum
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ContentType(str, enum.Enum):
    REPORTING = "reporting"
    OPINION = "opinion"
    ANALYSIS = "analysis"
    SOCIAL = "social"


class SourceType(str, enum.Enum):
    RSS = "rss"
    TWITTER = "twitter"
    AGGREGATOR = "aggregator"


class FetchStatus(str, enum.Enum):
    OK = "ok"
    STALE = "stale"
    ERROR = "error"


class NewsCategory(str, enum.Enum):
    FINANCE_MARKETS = "finance_markets"
    TECHNOLOGY_STARTUPS = "technology_startups"
    MACRO_POLICY = "macro_policy"
    GENERAL = "general"


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), default="default")
    category_weights: Mapped[dict] = mapped_column(JSONB, default=dict)
    tracked_tickers: Mapped[list] = mapped_column(JSONB, default=list)
    tracked_companies: Mapped[list] = mapped_column(JSONB, default=list)
    tracked_figures: Mapped[list] = mapped_column(JSONB, default=list)
    excluded_sources: Mapped[list] = mapped_column(JSONB, default=list)
    excluded_topics: Mapped[list] = mapped_column(JSONB, default=list)
    twitter_accounts: Mapped[list] = mapped_column(JSONB, default=list)
    twitter_keywords: Mapped[list] = mapped_column(JSONB, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True)
    source_type: Mapped[SourceType] = mapped_column(Enum(SourceType))
    url: Mapped[str | None] = mapped_column(String(500))
    feed_url: Mapped[str | None] = mapped_column(String(500))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_fetched_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    fetch_status: Mapped[FetchStatus] = mapped_column(Enum(FetchStatus), default=FetchStatus.OK)
    last_error: Mapped[str | None] = mapped_column(Text)

    articles: Mapped[list["Article"]] = relationship(back_populates="source")


class CategorySourceRanking(Base):
    """Ranked preferred sources per category — configurable, not hardcoded."""

    __tablename__ = "category_source_rankings"
    __table_args__ = (UniqueConstraint("category", "source_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    category: Mapped[NewsCategory] = mapped_column(Enum(NewsCategory))
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"))
    rank: Mapped[int] = mapped_column(Integer)  # 1 = highest preference

    source: Mapped["Source"] = relationship()


class StoryCluster(Base):
    """Groups duplicate coverage of the same underlying event."""

    __tablename__ = "story_clusters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    primary_article_id: Mapped[int | None] = mapped_column(ForeignKey("articles.id"))
    category: Mapped[NewsCategory] = mapped_column(Enum(NewsCategory))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    articles: Mapped[list["Article"]] = relationship(
        back_populates="cluster", foreign_keys="Article.cluster_id"
    )


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"))
    cluster_id: Mapped[int | None] = mapped_column(ForeignKey("story_clusters.id"))

    external_id: Mapped[str] = mapped_column(String(500))
    headline: Mapped[str] = mapped_column(String(500))
    original_url: Mapped[str] = mapped_column(String(1000))
    author: Mapped[str | None] = mapped_column(String(200))
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    category: Mapped[NewsCategory] = mapped_column(Enum(NewsCategory))
    content_type: Mapped[ContentType] = mapped_column(Enum(ContentType), default=ContentType.REPORTING)
    is_developing: Mapped[bool] = mapped_column(Boolean, default=False)
    is_serendipity: Mapped[bool] = mapped_column(Boolean, default=False)

    ai_summary: Mapped[str | None] = mapped_column(Text)
    relevance_score: Mapped[float] = mapped_column(Float, default=0.0)
    embedding: Mapped[list[float] | None] = mapped_column(JSONB)

    raw_metadata: Mapped[dict] = mapped_column(JSONB, default=dict)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    source: Mapped["Source"] = relationship(back_populates="articles")
    cluster: Mapped["StoryCluster | None"] = relationship(
        back_populates="articles", foreign_keys=[cluster_id]
    )

    __table_args__ = (UniqueConstraint("source_id", "external_id"),)
