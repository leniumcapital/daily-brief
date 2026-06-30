from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE, env_file_encoding="utf-8", extra="ignore"
    )

    database_url: str = "postgresql+asyncpg://kirillpopov@localhost:5432/dailybrief"
    redis_url: str = "redis://localhost:6379/0"

    anthropic_api_key: str = ""
    x_api_bearer_token: str = ""
    newsapi_key: str = ""
    guardian_api_key: str = ""

    api_key: str = "dev-key"
    environment: str = "development"
    log_level: str = "INFO"

    x_refresh_interval: int = 300
    rss_refresh_interval: int = 900
    aggregator_refresh_interval: int = 900

    serendipity_ratio: float = 0.1


@lru_cache
def get_settings() -> Settings:
    return Settings()
