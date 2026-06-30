import logging
from datetime import timedelta

import numpy as np

logger = logging.getLogger(__name__)

SIMILARITY_THRESHOLD = 0.85
TIME_WINDOW = timedelta(hours=6)


def cosine_similarity(a: list[float], b: list[float]) -> float:
    va, vb = np.array(a), np.array(b)
    denom = np.linalg.norm(va) * np.linalg.norm(vb)
    if denom == 0:
        return 0.0
    return float(np.dot(va, vb) / denom)


def find_duplicate_cluster(
    article_embedding: list[float],
    article_published_at,
    existing_clusters: list[dict],
) -> int | None:
    """Return cluster_id if article matches an existing story, else None."""
    for cluster in existing_clusters:
        if abs(article_published_at - cluster["published_at"]) > TIME_WINDOW:
            continue
        if cosine_similarity(article_embedding, cluster["embedding"]) >= SIMILARITY_THRESHOLD:
            return cluster["id"]
    return None


def pick_primary_article(articles: list[dict], source_rankings: dict[str, int]) -> dict:
    """Select highest-ranked source version as primary; others become alternate coverage."""

    def rank_key(article: dict) -> int:
        return source_rankings.get(article["source_name"], 999)

    sorted_articles = sorted(articles, key=rank_key)
    primary = sorted_articles[0]
    alternates = []
    for alt in sorted_articles[1:]:
        alternates.append(
            {
                "source_name": alt["source_name"],
                "headline": alt["headline"],
                "url": alt["url"],
                "framing_note": None,
            }
        )
    primary["alternate_coverage"] = alternates
    return primary
