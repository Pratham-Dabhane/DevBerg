from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.ml.recommender import Recommender
from app.ml.investment_forecaster import InvestmentForecaster
from app.ml.insight_generator import InsightGenerator
from app.models.models import TechnologyForecast
from app.models.schemas import (
    CollectionStatusSchema,
    NLInsightSchema,
    RecommendationSchema,
    SkillProfileInput,
    TechnologyForecastSchema,
)

router = APIRouter(prefix="/ai", tags=["ai"])


# ── POST /ai/recommend ───────────────────────────────────────────

@router.post("/recommend", response_model=list[RecommendationSchema])
def recommend_technologies(
    body: SkillProfileInput,
    top_n: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
) -> list[dict]:
    """Return personalized technology recommendations based on a skill profile."""
    recommender = Recommender(db)
    return recommender.recommend(body.skills, top_n=top_n)


# ── GET /ai/forecast ──────────────────────────────────────────────

@router.get("/forecast", response_model=list[TechnologyForecastSchema])
def get_forecasts(
    technology: str | None = None,
    horizon: int | None = None,
    db: Session = Depends(get_db),
) -> list[TechnologyForecast]:
    """Return the latest investment growth forecasts."""
    subq = (
        db.query(
            TechnologyForecast.technology,
            TechnologyForecast.horizon_months,
            func.max(TechnologyForecast.created_at).label("max_ts"),
        )
        .group_by(TechnologyForecast.technology, TechnologyForecast.horizon_months)
        .subquery()
    )
    query = (
        db.query(TechnologyForecast)
        .join(
            subq,
            (TechnologyForecast.technology == subq.c.technology)
            & (TechnologyForecast.horizon_months == subq.c.horizon_months)
            & (TechnologyForecast.created_at == subq.c.max_ts),
        )
    )
    if technology:
        query = query.filter(TechnologyForecast.technology.ilike(technology))
    if horizon:
        query = query.filter(TechnologyForecast.horizon_months == horizon)

    return (
        query
        .order_by(desc(TechnologyForecast.predicted_growth_pct))
        .all()
    )


@router.post("/forecast/run", response_model=CollectionStatusSchema)
def trigger_forecasts(db: Session = Depends(get_db)) -> dict[str, str]:
    """Run the investment forecaster for all tracked technologies."""
    forecaster = InvestmentForecaster(db)
    results = forecaster.run()
    return {
        "status": "success",
        "message": f"Generated {len(results)} forecasts",
    }


# ── GET /ai/insights ─────────────────────────────────────────────

@router.get("/insights", response_model=list[NLInsightSchema])
def get_nl_insights(
    category: str | None = None,
    db: Session = Depends(get_db),
) -> list[dict]:
    """Return natural-language insights from all analytics modules."""
    generator = InsightGenerator(db)
    insights = generator.generate()
    if category:
        insights = [i for i in insights if i["category"] == category.lower()]
    return insights
