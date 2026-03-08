from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.models import TechnologyMomentum, TechnologyLifecycle, EmergingTechnology
from app.models.schemas import (
    TechnologyMomentumSchema,
    TechnologyLifecycleSchema,
    EmergingTechnologySchema,
    CollectionStatusSchema,
)
from app.analytics.momentum_engine import MomentumEngine
from app.analytics.lifecycle_detector import LifecycleDetector
from app.analytics.emerging_detector import EmergingDetector

router = APIRouter(prefix="/analytics", tags=["analytics"])


# ── Momentum ──────────────────────────────────────────────────────

@router.get("/momentum", response_model=list[TechnologyMomentumSchema])
def get_momentum_scores(
    technology: str | None = None,
    db: Session = Depends(get_db),
) -> list[TechnologyMomentum]:
    """Return the latest momentum score per technology."""
    subq = (
        db.query(
            TechnologyMomentum.technology_name,
            func.max(TechnologyMomentum.timestamp).label("max_ts"),
        )
        .group_by(TechnologyMomentum.technology_name)
        .subquery()
    )
    query = (
        db.query(TechnologyMomentum)
        .join(
            subq,
            (TechnologyMomentum.technology_name == subq.c.technology_name)
            & (TechnologyMomentum.timestamp == subq.c.max_ts),
        )
        .order_by(desc(TechnologyMomentum.momentum_score))
    )
    if technology:
        query = query.filter(TechnologyMomentum.technology_name.ilike(technology))
    return query.all()


@router.post("/momentum/run", response_model=CollectionStatusSchema)
def trigger_momentum_engine(db: Session = Depends(get_db)) -> dict[str, str]:
    """Run the momentum scoring engine."""
    engine = MomentumEngine(db)
    results = engine.run()
    return {
        "status": "success",
        "message": f"Computed momentum scores for {len(results)} technologies",
    }


# ── Lifecycle ─────────────────────────────────────────────────────

@router.get("/lifecycle", response_model=list[TechnologyLifecycleSchema])
def get_lifecycle_stages(
    stage: str | None = None,
    technology: str | None = None,
    db: Session = Depends(get_db),
) -> list[TechnologyLifecycle]:
    """Return the latest lifecycle classification per technology."""
    subq = (
        db.query(
            TechnologyLifecycle.technology_name,
            func.max(TechnologyLifecycle.timestamp).label("max_ts"),
        )
        .group_by(TechnologyLifecycle.technology_name)
        .subquery()
    )
    query = (
        db.query(TechnologyLifecycle)
        .join(
            subq,
            (TechnologyLifecycle.technology_name == subq.c.technology_name)
            & (TechnologyLifecycle.timestamp == subq.c.max_ts),
        )
        .order_by(desc(TechnologyLifecycle.momentum_score))
    )
    if stage:
        query = query.filter(TechnologyLifecycle.lifecycle_stage.ilike(stage))
    if technology:
        query = query.filter(TechnologyLifecycle.technology_name.ilike(technology))
    return query.all()


@router.post("/lifecycle/run", response_model=CollectionStatusSchema)
def trigger_lifecycle_detector(db: Session = Depends(get_db)) -> dict[str, str]:
    """Run the lifecycle detector."""
    detector = LifecycleDetector(db)
    results = detector.run()
    return {
        "status": "success",
        "message": f"Classified {len(results)} technologies into lifecycle stages",
    }


# ── Emerging ──────────────────────────────────────────────────────

@router.get("/emerging", response_model=list[EmergingTechnologySchema])
def get_emerging_technologies(
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
) -> list[EmergingTechnology]:
    """Return the latest detected emerging technologies ranked by spike score."""
    subq = (
        db.query(
            EmergingTechnology.technology_name,
            func.max(EmergingTechnology.detected_at).label("max_at"),
        )
        .group_by(EmergingTechnology.technology_name)
        .subquery()
    )
    return (
        db.query(EmergingTechnology)
        .join(
            subq,
            (EmergingTechnology.technology_name == subq.c.technology_name)
            & (EmergingTechnology.detected_at == subq.c.max_at),
        )
        .order_by(desc(EmergingTechnology.growth_spike_score))
        .limit(limit)
        .all()
    )


@router.post("/emerging/run", response_model=CollectionStatusSchema)
def trigger_emerging_detector(db: Session = Depends(get_db)) -> dict[str, str]:
    """Run the emerging technology detector."""
    detector = EmergingDetector(db)
    results = detector.run()
    return {
        "status": "success",
        "message": f"Detected {len(results)} emerging technologies",
    }


# ── Run all analytics ────────────────────────────────────────────

@router.post("/run-all", response_model=CollectionStatusSchema)
def trigger_full_analytics(db: Session = Depends(get_db)) -> dict[str, str]:
    """Run the complete analytics pipeline: momentum → lifecycle → emerging."""
    momentum_results = MomentumEngine(db).run()
    lifecycle_results = LifecycleDetector(db).run()
    emerging_results = EmergingDetector(db).run()
    return {
        "status": "success",
        "message": (
            f"Analytics complete — {len(momentum_results)} momentum, "
            f"{len(lifecycle_results)} lifecycle, "
            f"{len(emerging_results)} emerging"
        ),
    }
