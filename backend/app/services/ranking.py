import random

from app.settings import get_settings
from app.models import NewsCategory

settings = get_settings()

CATEGORY_LABELS = {
    NewsCategory.FINANCE_MARKETS: "Finance & Markets",
    NewsCategory.TECHNOLOGY_STARTUPS: "Technology & Startups",
    NewsCategory.MACRO_POLICY: "Macro & Policy",
    NewsCategory.GENERAL: "General",
}


def score_relevance(
    article: dict,
    profile: dict,
    category_weights: dict[str, float],
) -> float:
    """Score article relevance using profile weights and tracked entities."""
    base = article.get("relevance_score", 0.5)
    category = article.get("category", NewsCategory.GENERAL)
    weight = category_weights.get(category.value if hasattr(category, "value") else str(category), 1.0)
    score = base * weight

    text = f"{article.get('headline', '')} {article.get('summary_snippet', '')}".lower()
    for ticker in profile.get("tracked_tickers", []):
        if ticker.lower() in text:
            score = min(1.0, score + 0.2)
    for company in profile.get("tracked_companies", []):
        if company.lower() in text:
            score = min(1.0, score + 0.15)

    return round(min(1.0, score), 3)


def rank_articles(articles: list[dict], profile: dict, category_weights: dict) -> list[dict]:
    """Rank articles by relevance score descending."""
    for article in articles:
        article["relevance_score"] = score_relevance(article, profile, category_weights)
    return sorted(articles, key=lambda a: a["relevance_score"], reverse=True)


def apply_serendipity(articles: list[dict], ratio: float | None = None) -> list[dict]:
    """Mark a small fraction of outside-interest stories for serendipity slot."""
    ratio = ratio or settings.serendipity_ratio
    if not articles:
        return articles

    low_relevance = [a for a in articles if a.get("relevance_score", 0) < 0.4]
    if not low_relevance:
        return articles

    count = max(1, int(len(articles) * ratio))
    picks = random.sample(low_relevance, min(count, len(low_relevance)))
    pick_ids = {id(a) for a in picks}
    for article in articles:
        if id(article) in pick_ids:
            article["is_serendipity"] = True
    return articles
