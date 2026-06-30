from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql+asyncpg://dailybrief:dailybrief@localhost:5432/dailybrief"
    redis_url: str = "redis://localhost:6379/0"

    anthropic_api_key: str = ""
    x_api_bearer_token: str = ""
    newsapi_key: str = ""

    api_key: str = "dev-key"
    environment: str = "development"
    log_level: str = "INFO"

    x_refresh_interval: int = 300
    rss_refresh_interval: int = 900
    aggregator_refresh_interval: int = 900

    serendipity_ratio: float = 0.1  # share of feed reserved for outside-interests stories


@lru_cache
def get_settings() -> Settings:
    return Settings()
