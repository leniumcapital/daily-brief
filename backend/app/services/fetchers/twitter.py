import logging
from datetime import UTC, datetime

from app.config import get_settings
from app.models import FetchStatus, SourceType

logger = logging.getLogger(__name__)
settings = get_settings()


class TwitterFetcher:
    """Fetch tweets via official X API v2 (tweepy). No scraping."""

    def __init__(self):
        self._client = None
        if settings.x_api_bearer_token:
            import tweepy

            self._client = tweepy.Client(bearer_token=settings.x_api_bearer_token)

    async def fetch_accounts(self, accounts: list[str]) -> list[dict]:
        if not self._client or not accounts:
            return []

        items = []
        try:
            users = self._client.get_users(usernames=accounts)
            if not users.data:
                return []

            user_ids = [u.id for u in users.data]
            tweets = self._client.get_users_tweets(
                ids=user_ids,
                max_results=10,
                tweet_fields=["created_at", "author_id"],
                exclude=["retweets", "replies"],
            )
            if tweets.data:
                for tweet in tweets.data:
                    items.append(
                        {
                            "external_id": str(tweet.id),
                            "headline": tweet.text[:120] + ("..." if len(tweet.text) > 120 else ""),
                            "summary_snippet": tweet.text[:280],
                            "url": f"https://x.com/i/status/{tweet.id}",
                            "author": str(tweet.author_id),
                            "published_at": tweet.created_at or datetime.now(tz=UTC),
                            "source_type": SourceType.TWITTER,
                            "raw_text": tweet.text,
                        }
                    )
        except Exception as exc:
            logger.warning("Twitter fetch failed: %s", exc)
            return []

        return items

    async def search_keywords(self, keywords: list[str]) -> list[dict]:
        if not self._client or not keywords:
            return []

        items = []
        for keyword in keywords[:5]:  # rate-limit conscious
            try:
                tweets = self._client.search_recent_tweets(
                    query=keyword,
                    max_results=10,
                    tweet_fields=["created_at", "author_id"],
                )
                if tweets.data:
                    for tweet in tweets.data:
                        items.append(
                            {
                                "external_id": str(tweet.id),
                                "headline": tweet.text[:120],
                                "summary_snippet": tweet.text[:280],
                                "url": f"https://x.com/i/status/{tweet.id}",
                                "published_at": tweet.created_at or datetime.now(tz=UTC),
                                "source_type": SourceType.TWITTER,
                                "raw_text": tweet.text,
                            }
                        )
            except Exception as exc:
                logger.warning("Twitter search failed for '%s': %s", keyword, exc)

        return items
