import json
import logging

from anthropic import AsyncAnthropic

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

SUMMARIZE_PROMPT = """You are a news curator. Given a headline and optional snippet from a news source,
write an ORIGINAL 2-3 sentence summary in your own words. Do NOT copy phrasing from the source.

Also classify the content and assess relevance to the user's interests.

Respond with JSON only:
{
  "summary": "...",
  "content_type": "reporting|opinion|analysis|social",
  "is_developing": false,
  "relevance_score": 0.0-1.0
}

User interests: {interests}
Headline: {headline}
Snippet: {snippet}
Source: {source}
"""


class Summarizer:
    def __init__(self):
        self._client = AsyncAnthropic(api_key=settings.anthropic_api_key) if settings.anthropic_api_key else None

    async def summarize(
        self,
        headline: str,
        snippet: str,
        source: str,
        interests: dict,
    ) -> dict:
        if not self._client:
            return {
                "summary": snippet[:300] if snippet else headline,
                "content_type": "reporting",
                "is_developing": False,
                "relevance_score": 0.5,
            }

        prompt = SUMMARIZE_PROMPT.format(
            interests=json.dumps(interests),
            headline=headline,
            snippet=snippet or "(none)",
            source=source,
        )

        try:
            response = await self._client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}],
            )
            text = response.content[0].text
            return json.loads(text)
        except Exception as exc:
            logger.warning("Summarization failed: %s", exc)
            return {
                "summary": snippet[:300] if snippet else headline,
                "content_type": "reporting",
                "is_developing": False,
                "relevance_score": 0.5,
            }
