import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database.session import engine
from app.models.models import Base
from app.api.routes import router
from app.api.insights_routes import router as insights_router
from app.api.analytics_routes import router as analytics_router
from app.api.repo_health_routes import router as repo_health_router
from app.graph.graph_api import router as graph_router
from app.api.ai_routes import router as ai_router
from app.services.collector import run_collection, run_pipeline, run_trend_engine, run_analytics, run_repo_health, run_graph_analysis, run_investment_forecasts, run_discovery, seed_registry

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

    # Seed the technology registry on first run
    seed_registry()

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
    scheduler.add_job(
        run_trend_engine,
        "interval",
        hours=24,
        id="trend_engine",
        replace_existing=True,
    )
    scheduler.add_job(
        run_analytics,
        "interval",
        hours=24,
        id="analytics_engine",
        replace_existing=True,
    )
    scheduler.add_job(
        run_repo_health,
        "interval",
        hours=24,
        id="repo_health_analyzer",
        replace_existing=True,
    )
    scheduler.add_job(
        run_graph_analysis,
        "interval",
        hours=24,
        id="graph_analysis",
        replace_existing=True,
    )
    scheduler.add_job(
        run_investment_forecasts,
        "interval",
        hours=24,
        id="investment_forecasts",
        replace_existing=True,
    )
    scheduler.add_job(
        run_discovery,
        "interval",
        hours=48,
        id="tech_discovery",
        replace_existing=True,
    )
    scheduler.start()
    logger.info(
        "Scheduler started — collecting every %d hours, pipeline & analytics daily.",
        settings.collection_interval_hours,
    )

    yield

    # Shutdown
    scheduler.shutdown(wait=False)
    logger.info("Scheduler stopped.")


app = FastAPI(
    title="DevPulse AI — Developer Ecosystem Tracker",
    description="Dynamically tracks 60+ technologies across AI, backend, frontend, systems, databases, DevOps, mobile, and tooling ecosystems.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(insights_router)
app.include_router(analytics_router)
app.include_router(repo_health_router)
app.include_router(graph_router)
app.include_router(ai_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "healthy"}
