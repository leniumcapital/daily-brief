from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.settings import get_settings
from app.database import get_db
from app.schemas import DashboardResponse, SourceRankingUpdate, UserProfileUpdate
from app.services.briefing import BriefingService

router = APIRouter()
settings = get_settings()


def verify_api_key(x_api_key: str = Header(default="")) -> None:
    if settings.environment != "development" and x_api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    _: None = Depends(verify_api_key),
):
    service = BriefingService(db)
    return await service.get_dashboard()


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
