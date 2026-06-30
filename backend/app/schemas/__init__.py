from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, HttpUrl


class ContentType(str, Enum):
    REPORTING = "reporting"
    OPINION = "opinion"
    ANALYSIS = "analysis"
    SOCIAL = "social"


class NewsCategory(str, Enum):
    FINANCE_MARKETS = "finance_markets"
    TECHNOLOGY_STARTUPS = "technology_startups"
    MACRO_POLICY = "macro_policy"
    GENERAL = "general"


class FetchStatus(str, Enum):
    OK = "ok"
    STALE = "stale"
    ERROR = "error"


class AlternateCoverage(BaseModel):
    source_name: str
    headline: str
    url: HttpUrl
    framing_note: str | None = None


class BriefingItem(BaseModel):
    id: int
    headline: str
    summary: str
    source_name: str
    source_type: str
    category: NewsCategory
    content_type: ContentType
    relevance_score: float = Field(ge=0.0, le=1.0)
    is_developing: bool = False
    is_serendipity: bool = False
    published_at: datetime
    url: HttpUrl
    alternate_coverage: list[AlternateCoverage] = []
    fetch_status: FetchStatus = FetchStatus.OK


class BriefingSection(BaseModel):
    category: NewsCategory
    label: str
    items: list[BriefingItem]


class DashboardResponse(BaseModel):
    generated_at: datetime
    sections: list[BriefingSection]
    twitter_section: BriefingSection | None = None
    stale_sources: list[str] = []


class UserProfileUpdate(BaseModel):
    category_weights: dict[str, float] | None = None
    tracked_tickers: list[str] | None = None
    tracked_companies: list[str] | None = None
    tracked_figures: list[str] | None = None
    excluded_sources: list[str] | None = None
    excluded_topics: list[str] | None = None
    twitter_accounts: list[str] | None = None
    twitter_keywords: list[str] | None = None


class SourceRankingUpdate(BaseModel):
    category: NewsCategory
    source_name: str
    rank: int = Field(ge=1)
