from datetime import UTC, datetime, timedelta
import random

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.settings import get_settings
from app.database import get_db
from app.schemas import DashboardResponse, SourceRankingUpdate, UserProfileUpdate
from app.services.briefing import BriefingService

router = APIRouter()
settings = get_settings()

DEFAULT_WATCHLIST = [
    {"symbol": "SPY", "name": "S&P 500", "base": 542.0},
    {"symbol": "QQQ", "name": "Nasdaq 100", "base": 468.0},
    {"symbol": "BTC", "name": "Bitcoin", "base": 67200.0},
    {"symbol": "10Y", "name": "US 10Y Yield", "base": 4.32},
]


def verify_api_key(x_api_key: str = Header(default="")) -> None:
    if settings.environment != "development" and x_api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.post("/refresh")
async def refresh_feeds(_: None = Depends(verify_api_key)):
    from app.services.ingestion import run_ingestion_cycle

    return await run_ingestion_cycle("all")


@router.get("/sources/status")
async def sources_status(_: None = Depends(verify_api_key)):
    """Test connectivity to every configured news outlet."""
    from app.config.source_rankings import get_all_sources, get_twitter_config
    from app.services.source_connector import SourceConnector

    connector = SourceConnector()
    sources = get_all_sources()
    results = []
    for name, config in sources.items():
        results.append(await connector.check_source(name, config))

    connected = sum(1 for r in results if r["article_count"] > 0)
    twitter_cfg = get_twitter_config()
    return {
        "total_sources": len(results),
        "connected": connected,
        "newsapi_configured": bool(settings.newsapi_key),
        "guardian_configured": bool(settings.guardian_api_key),
        "x_configured": bool(settings.x_api_bearer_token),
        "twitter_accounts": twitter_cfg.get("accounts", []),
        "sources": results,
    }


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    _: None = Depends(verify_api_key),
):
    service = BriefingService(db)
    return await service.get_dashboard()


@router.get("/markets")
async def get_markets(_: None = Depends(verify_api_key)):
    tickers = []
    for item in DEFAULT_WATCHLIST:
        random.seed(int(item["base"] * 100) + datetime.now(tz=UTC).day)
        now = datetime.now(tz=UTC)
        history = []
        price = item["base"] * (1 + random.uniform(-0.02, 0.02))
        for i in range(24):
            price *= 1 + random.uniform(-0.004, 0.004)
            history.append(
                {
                    "time": (now - timedelta(hours=24 - i)).strftime("%H:%M"),
                    "value": round(price, 2 if price < 1000 else 0),
                }
            )
        current = history[-1]["value"]
        open_price = history[0]["value"]
        change = round(current - open_price, 2)
        change_pct = round((change / open_price) * 100, 2) if open_price else 0
        tickers.append(
            {
                "symbol": item["symbol"],
                "name": item["name"],
                "price": current,
                "change": change,
                "changePct": change_pct,
                "history": history,
            }
        )
    return {"tickers": tickers, "updated_at": datetime.now(tz=UTC).isoformat()}


@router.put("/profile")
async def update_profile(
    update: UserProfileUpdate,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(verify_api_key),
):
    # TODO: persist profile updates
    return {"status": "updated", "fields": update.model_dump(exclude_none=True)}


@router.put("/rankings")
async def update_ranking(
    update: SourceRankingUpdate,
    _: None = Depends(verify_api_key),
):
    # TODO: persist ranking changes to DB and YAML
    return {"status": "updated", "ranking": update.model_dump()}
