from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database.session import get_db
from app.models.models import Repository, StackOverflowStats, HackerNewsMention, TechMention, TechnologyMetrics, TechnologyPrediction, TrackedTechnology
from app.models.schemas import (
    RepositorySchema,
    StackOverflowStatsSchema,
    HackerNewsMentionSchema,
    TechMentionSchema,
    TechnologyMetricsSchema,
    TechnologyPredictionSchema,
    CollectionStatusSchema,
)
from app.services.github_service import GitHubService
from app.services.stackoverflow_service import StackOverflowService
from app.services.hackernews_service import HackerNewsService
from app.pipeline.metrics_pipeline import MetricsPipeline
from app.ml.trend_engine import TrendEngine

router = APIRouter(prefix="/api/v1", tags=["ecosystem"])


# ── Tracked technologies ──────────────────────────────────────────

@router.get("/technologies")
def list_tracked_technologies(
    db: Session = Depends(get_db),
) -> list[dict]:
    """Return all active tracked technologies with name and category."""
    techs = (
        db.query(TrackedTechnology)
        .filter(TrackedTechnology.is_active.is_(True))
        .order_by(TrackedTechnology.category, TrackedTechnology.name)
        .all()
    )
    return [{"name": t.name, "category": t.category or "Other"} for t in techs]


# ── GitHub endpoints ──────────────────────────────────────────────

@router.get("/repositories", response_model=list[RepositorySchema])
def list_repositories(
    technology: str | None = None,
    limit: int = Query(default=50, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[Repository]:
    query = db.query(Repository).order_by(desc(Repository.collected_at))
    if technology:
        query = query.filter(Repository.technology.ilike(technology))
    return query.limit(limit).all()


@router.post("/collect/github", response_model=CollectionStatusSchema)
def trigger_github_collection(db: Session = Depends(get_db)) -> dict[str, str]:
    svc = GitHubService(db)
    results = svc.collect_all()
    return {
        "status": "success",
        "message": f"Collected data for {len(results)} repositories",
    }


# ── StackOverflow endpoints ──────────────────────────────────────

@router.get("/stackoverflow", response_model=list[StackOverflowStatsSchema])
def list_stackoverflow_stats(
    technology: str | None = None,
    limit: int = Query(default=50, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[StackOverflowStats]:
    query = db.query(StackOverflowStats).order_by(desc(StackOverflowStats.collected_at))
    if technology:
        query = query.filter(StackOverflowStats.technology.ilike(technology))
    return query.limit(limit).all()


@router.post("/collect/stackoverflow", response_model=CollectionStatusSchema)
def trigger_stackoverflow_collection(db: Session = Depends(get_db)) -> dict[str, str]:
    svc = StackOverflowService(db)
    results = svc.collect_all()
    return {
        "status": "success",
        "message": f"Collected data for {len(results)} tags",
    }


# ── HackerNews endpoints ─────────────────────────────────────────

@router.get("/hackernews", response_model=list[HackerNewsMentionSchema])
def list_hackernews_mentions(
    technology: str | None = None,
    limit: int = Query(default=50, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[HackerNewsMention]:
    query = db.query(HackerNewsMention).order_by(desc(HackerNewsMention.collected_at))
    if technology:
        query = query.filter(HackerNewsMention.technology.ilike(technology))
    return query.limit(limit).all()


@router.post("/collect/hackernews", response_model=CollectionStatusSchema)
def trigger_hackernews_collection(db: Session = Depends(get_db)) -> dict[str, str]:
    svc = HackerNewsService(db)
    results = svc.collect_all()
    return {
        "status": "success",
        "message": f"Collected {len(results)} HackerNews mentions",
    }


# ── Aggregate tech mentions ──────────────────────────────────────

@router.get("/mentions", response_model=list[TechMentionSchema])
def list_tech_mentions(
    technology: str | None = None,
    source: str | None = None,
    limit: int = Query(default=50, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[TechMention]:
    query = db.query(TechMention).order_by(desc(TechMention.collected_at))
    if technology:
        query = query.filter(TechMention.technology.ilike(technology))
    if source:
        query = query.filter(TechMention.source.ilike(source))
    return query.limit(limit).all()


# ── Full collection trigger ───────────────────────────────────────

@router.post("/collect/all", response_model=CollectionStatusSchema)
def trigger_full_collection(db: Session = Depends(get_db)) -> dict[str, str]:
    gh_results = GitHubService(db).collect_all()
    so_results = StackOverflowService(db).collect_all()
    hn_results = HackerNewsService(db).collect_all()
    return {
        "status": "success",
        "message": (
            f"Collected {len(gh_results)} repos, "
            f"{len(so_results)} SO tags, "
            f"{len(hn_results)} HN mentions"
        ),
    }


# ── Metrics pipeline endpoints ────────────────────────────────────

@router.get("/metrics", response_model=list[TechnologyMetricsSchema])
def list_technology_metrics(
    technology: str | None = None,
    limit: int = Query(default=50, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[TechnologyMetrics]:
    query = db.query(TechnologyMetrics).order_by(desc(TechnologyMetrics.last_updated))
    if technology:
        query = query.filter(TechnologyMetrics.technology.ilike(technology))
    return query.limit(limit).all()


@router.get("/metrics/latest", response_model=list[TechnologyMetricsSchema])
def list_latest_metrics(
    db: Session = Depends(get_db),
) -> list[TechnologyMetrics]:
    """Return only the most recent metric record per technology."""
    from sqlalchemy import func

    subq = (
        db.query(
            TechnologyMetrics.technology,
            func.max(TechnologyMetrics.last_updated).label("max_updated"),
        )
        .group_by(TechnologyMetrics.technology)
        .subquery()
    )
    rows = (
        db.query(TechnologyMetrics)
        .join(
            subq,
            (TechnologyMetrics.technology == subq.c.technology)
            & (TechnologyMetrics.last_updated == subq.c.max_updated),
        )
        .order_by(desc(TechnologyMetrics.momentum_score))
        .all()
    )
    return rows


@router.post("/pipeline/run", response_model=CollectionStatusSchema)
def trigger_pipeline(db: Session = Depends(get_db)) -> dict[str, str]:
    pipeline = MetricsPipeline(db)
    results = pipeline.run()
    return {
        "status": "success",
        "message": f"Pipeline processed {len(results)} technologies",
    }


# ── Trend detection & predictions ───────────────────────────────

@router.post("/predictions/run", response_model=CollectionStatusSchema)
def trigger_trend_engine(db: Session = Depends(get_db)) -> dict[str, str]:
    engine = TrendEngine(db)
    results = engine.run()
    return {
        "status": "success",
        "message": f"Generated {len(results)} technology predictions",
    }


@router.get("/predictions", response_model=list[TechnologyPredictionSchema])
def list_predictions(
    technology: str | None = None,
    trend: str | None = None,
    limit: int = Query(default=50, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[TechnologyPrediction]:
    query = db.query(TechnologyPrediction).order_by(desc(TechnologyPrediction.created_at))
    if technology:
        query = query.filter(TechnologyPrediction.technology.ilike(technology))
    if trend:
        query = query.filter(TechnologyPrediction.trend_direction.ilike(trend))
    return query.limit(limit).all()


@router.get("/predictions/latest", response_model=list[TechnologyPredictionSchema])
def list_latest_predictions(
    db: Session = Depends(get_db),
) -> list[TechnologyPrediction]:
    """Return the most recent prediction per technology, ranked by momentum."""
    from sqlalchemy import func

    subq = (
        db.query(
            TechnologyPrediction.technology,
            func.max(TechnologyPrediction.created_at).label("max_created"),
        )
        .group_by(TechnologyPrediction.technology)
        .subquery()
    )
    rows = (
        db.query(TechnologyPrediction)
        .join(
            subq,
            (TechnologyPrediction.technology == subq.c.technology)
            & (TechnologyPrediction.created_at == subq.c.max_created),
        )
        .order_by(desc(TechnologyPrediction.momentum_score))
        .all()
    )
    return rows


@router.get("/predictions/emerging", response_model=list[TechnologyPredictionSchema])
def list_emerging_technologies(
    db: Session = Depends(get_db),
) -> list[TechnologyPrediction]:
    """Return technologies flagged as emerging by anomaly detection."""
    from sqlalchemy import func

    subq = (
        db.query(
            TechnologyPrediction.technology,
            func.max(TechnologyPrediction.created_at).label("max_created"),
        )
        .group_by(TechnologyPrediction.technology)
        .subquery()
    )
    rows = (
        db.query(TechnologyPrediction)
        .join(
            subq,
            (TechnologyPrediction.technology == subq.c.technology)
            & (TechnologyPrediction.created_at == subq.c.max_created),
        )
        .filter(TechnologyPrediction.is_emerging == 1)
        .order_by(desc(TechnologyPrediction.predicted_growth))
        .all()
    )
    return rows
