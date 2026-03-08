import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI

from app.config import get_settings
from app.database.session import engine
from app.models.models import Base
from app.api.routes import router
from app.services.collector import run_collection, run_pipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created.")

    settings = get_settings()
    scheduler.add_job(
        run_collection,
        "interval",
        hours=settings.collection_interval_hours,
        id="data_collection",
        replace_existing=True,
    )
    scheduler.add_job(
        run_pipeline,
        "interval",
        hours=24,
        id="metrics_pipeline",
        replace_existing=True,
    )
    scheduler.start()
    logger.info(
        "Scheduler started — collecting every %d hours, pipeline daily.",
        settings.collection_interval_hours,
    )

    yield

    # Shutdown
    scheduler.shutdown(wait=False)
    logger.info("Scheduler stopped.")


app = FastAPI(
    title="DevBerg — Developer Ecosystem Tracker",
    description="Collects and serves developer ecosystem data from GitHub, StackOverflow, and HackerNews.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "healthy"}
