from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.schemas import (
    HealthReportSchema,
    EmergingTechSchema,
    TrendInsightSchema,
)
from app.analytics.insights_engine import InsightsEngine

router = APIRouter(prefix="/insights", tags=["insights"])


@router.get("/health", response_model=list[HealthReportSchema])
def get_health_scores(db: Session = Depends(get_db)) -> list[dict]:
    """
    Repo Health Score per technology.

    Returns a 0-100 score broken down into:
    maintainer_activity, release_frequency, issue_resolution_speed,
    contributor_diversity — plus risk level and readable insights.
    """
    engine = InsightsEngine(db)
    reports = engine.compute_health_scores()
    return [
        {
            "technology": r.technology,
            "health_score": r.health_score,
            "risk_level": r.risk_level,
            "maintainer_activity": r.maintainer_activity,
            "release_frequency": r.release_frequency,
            "issue_resolution_speed": r.issue_resolution_speed,
            "contributor_diversity": r.contributor_diversity,
            "insights": r.insights,
        }
        for r in reports
    ]


@router.get("/emerging", response_model=list[EmergingTechSchema])
def get_emerging_technologies(
    top: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
) -> list[dict]:
    """
    Emerging Tech Radar — top N technologies ranked by
    composite momentum + predicted growth.
    """
    engine = InsightsEngine(db)
    techs = engine.detect_emerging_radar(top_n=top)
    return [
        {
            "rank": t.rank,
            "technology": t.technology,
            "momentum_score": t.momentum_score,
            "predicted_growth": t.predicted_growth,
            "trend_direction": t.trend_direction,
            "signals": t.signals,
        }
        for t in techs
    ]


@router.get("/trends", response_model=list[TrendInsightSchema])
def get_trend_insights(
    technology: str | None = None,
    category: str | None = None,
    db: Session = Depends(get_db),
) -> list[dict]:
    """
    Human-readable trend insights across all tracked technologies.

    Filter by technology name or category (growth / decline / anomaly / milestone).
    """
    engine = InsightsEngine(db)
    insights = engine.generate_trend_insights()

    if technology:
        insights = [i for i in insights if i.technology.lower() == technology.lower()]
    if category:
        insights = [i for i in insights if i.category.lower() == category.lower()]

    return [
        {
            "technology": i.technology,
            "category": i.category,
            "message": i.message,
            "severity": i.severity,
            "data": i.data,
        }
        for i in insights
    ]


@router.get("/risks", response_model=list[TrendInsightSchema])
def get_risk_insights(db: Session = Depends(get_db)) -> list[dict]:
    """
    Technology Risk Detection — surfaces only warning/critical insights
    for abandoned or declining repositories.
    """
    engine = InsightsEngine(db)
    risks = engine.detect_risks()
    return [
        {
            "technology": i.technology,
            "category": i.category,
            "message": i.message,
            "severity": i.severity,
            "data": i.data,
        }
        for i in risks
    ]
