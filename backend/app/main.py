import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.settings import get_settings
from app.database import Base, engine
from app.models import Article, CategorySourceRanking, Source, StoryCluster, UserProfile  # noqa: F401
from app.services.scheduler import create_scheduler

settings = get_settings()
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables ready")

    scheduler = create_scheduler()
    scheduler.start()
    logger.info("Scheduler started")

    # Populate dashboard on first boot
    import asyncio

    from app.services.ingestion import run_ingestion_cycle
    from app.services.seed import seed_if_empty

    async def bootstrap_content() -> None:
        await run_ingestion_cycle("all")
        await seed_if_empty()

    asyncio.create_task(bootstrap_content())
    logger.info("Initial content bootstrap triggered")

    yield
    scheduler.shutdown()
    logger.info("Scheduler stopped")


app = FastAPI(
    title="Daily Brief",
    description="Personalized news curation agent",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")
