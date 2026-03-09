"""Natural Language Insight Generator.

Produces human-readable insights from analytics data using rule-based
templates.  Each insight has a technology, category, severity and
narrative text.
"""

import logging
from datetime import datetime, timezone

from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.models.models import (
    TechnologyMomentum,
    TechnologyLifecycle,
    TechnologyForecast,
    RepositoryHealth,
    TechnologyGraphMetrics,
)

logger = logging.getLogger(__name__)


def _pct_fmt(value: float) -> str:
    sign = "+" if value > 0 else ""
    return f"{sign}{value:.0f}%"


class InsightGenerator:
    """Generates natural-language insights from all analytics modules."""

    def __init__(self, db: Session) -> None:
        self.db = db

    # ── Data loaders (latest snapshot per tech) ───────────────────

    def _latest_momentum(self) -> list[TechnologyMomentum]:
        subq = (
            self.db.query(
                TechnologyMomentum.technology_name,
                func.max(TechnologyMomentum.timestamp).label("max_ts"),
            )
            .group_by(TechnologyMomentum.technology_name)
            .subquery()
        )
        return (
            self.db.query(TechnologyMomentum)
            .join(subq, (TechnologyMomentum.technology_name == subq.c.technology_name)
                  & (TechnologyMomentum.timestamp == subq.c.max_ts))
            .all()
        )

    def _latest_lifecycle(self) -> list[TechnologyLifecycle]:
        subq = (
            self.db.query(
                TechnologyLifecycle.technology_name,
                func.max(TechnologyLifecycle.timestamp).label("max_ts"),
            )
            .group_by(TechnologyLifecycle.technology_name)
            .subquery()
        )
        return (
            self.db.query(TechnologyLifecycle)
            .join(subq, (TechnologyLifecycle.technology_name == subq.c.technology_name)
                  & (TechnologyLifecycle.timestamp == subq.c.max_ts))
            .all()
        )

    def _latest_forecasts(self) -> list[TechnologyForecast]:
        subq = (
            self.db.query(
                TechnologyForecast.technology,
                TechnologyForecast.horizon_months,
                func.max(TechnologyForecast.created_at).label("max_ts"),
            )
            .group_by(TechnologyForecast.technology, TechnologyForecast.horizon_months)
            .subquery()
        )
        return (
            self.db.query(TechnologyForecast)
            .join(subq, (TechnologyForecast.technology == subq.c.technology)
                  & (TechnologyForecast.horizon_months == subq.c.horizon_months)
                  & (TechnologyForecast.created_at == subq.c.max_ts))
            .all()
        )

    def _latest_health(self) -> list[RepositoryHealth]:
        subq = (
            self.db.query(
                RepositoryHealth.repository_name,
                func.max(RepositoryHealth.last_updated).label("max_ts"),
            )
            .group_by(RepositoryHealth.repository_name)
            .subquery()
        )
        return (
            self.db.query(RepositoryHealth)
            .join(subq, (RepositoryHealth.repository_name == subq.c.repository_name)
                  & (RepositoryHealth.last_updated == subq.c.max_ts))
            .all()
        )

    def _latest_graph(self) -> list[TechnologyGraphMetrics]:
        subq = (
            self.db.query(
                TechnologyGraphMetrics.technology_name,
                func.max(TechnologyGraphMetrics.last_updated).label("max_ts"),
            )
            .group_by(TechnologyGraphMetrics.technology_name)
            .subquery()
        )
        return (
            self.db.query(TechnologyGraphMetrics)
            .join(subq, (TechnologyGraphMetrics.technology_name == subq.c.technology_name)
                  & (TechnologyGraphMetrics.last_updated == subq.c.max_ts))
            .all()
        )

    # ── Insight generators ────────────────────────────────────────

    def _momentum_insights(self) -> list[dict]:
        insights: list[dict] = []
        for m in self._latest_momentum():
            if m.momentum_score >= 0.55:
                insights.append({
                    "technology": m.technology_name,
                    "insight": (
                        f"{m.technology_name} has a momentum score of {m.momentum_score:.2f}, "
                        f"with contributor growth at {m.contributors_growth*100:.0f}% "
                        f"and stars growth at {m.stars_growth*100:.0f}%, "
                        f"indicating strong ecosystem adoption."
                    ),
                    "category": "momentum",
                    "severity": "positive",
                })
            elif m.momentum_score <= 0.35:
                insights.append({
                    "technology": m.technology_name,
                    "insight": (
                        f"{m.technology_name} momentum has dropped to {m.momentum_score:.2f}. "
                        f"Community engagement and growth signals are weakening."
                    ),
                    "category": "momentum",
                    "severity": "warning",
                })
        return insights

    def _lifecycle_insights(self) -> list[dict]:
        insights: list[dict] = []
        for lc in self._latest_lifecycle():
            if lc.lifecycle_stage == "Emerging":
                insights.append({
                    "technology": lc.technology_name,
                    "insight": (
                        f"{lc.technology_name} is classified as Emerging with "
                        f"{lc.confidence_score*100:.0f}% confidence — early adoption "
                        f"opportunity with high momentum ({lc.momentum_score:.2f})."
                    ),
                    "category": "lifecycle",
                    "severity": "positive",
                })
            elif lc.lifecycle_stage == "Declining":
                insights.append({
                    "technology": lc.technology_name,
                    "insight": (
                        f"{lc.technology_name} is in a Declining phase "
                        f"(confidence {lc.confidence_score*100:.0f}%). "
                        f"Consider evaluating migration paths."
                    ),
                    "category": "lifecycle",
                    "severity": "critical",
                })
        return insights

    def _forecast_insights(self) -> list[dict]:
        insights: list[dict] = []
        for fc in self._latest_forecasts():
            if fc.horizon_months == 6 and abs(fc.predicted_growth_pct) > 10:
                direction = "growth" if fc.predicted_growth_pct > 0 else "decline"
                sev = "positive" if fc.predicted_growth_pct > 0 else "warning"
                insights.append({
                    "technology": fc.technology,
                    "insight": (
                        f"{fc.technology} is predicted to see {_pct_fmt(fc.predicted_growth_pct)} "
                        f"{direction} over the next 6 months "
                        f"(model: {fc.model_used}, confidence: {fc.confidence_score*100:.0f}%)."
                    ),
                    "category": "forecast",
                    "severity": sev,
                })
        return insights

    def _health_insights(self) -> list[dict]:
        insights: list[dict] = []
        for h in self._latest_health():
            if h.risk_level == "Critical":
                insights.append({
                    "technology": h.repository_name,
                    "insight": (
                        f"{h.repository_name} has a Critical health score of {h.health_score:.0f}/100. "
                        f"Maintainer activity is low and issue resolution is slow."
                    ),
                    "category": "health",
                    "severity": "critical",
                })
            elif h.risk_level == "Low":
                insights.append({
                    "technology": h.repository_name,
                    "insight": (
                        f"{h.repository_name} is in excellent health (score {h.health_score:.0f}/100) "
                        f"with {h.contributors} active contributors."
                    ),
                    "category": "health",
                    "severity": "positive",
                })
        return insights

    def _graph_insights(self) -> list[dict]:
        insights: list[dict] = []
        top = sorted(self._latest_graph(), key=lambda g: g.ecosystem_influence, reverse=True)[:3]
        for g in top:
            insights.append({
                "technology": g.technology_name,
                "insight": (
                    f"{g.technology_name} ranks as a top ecosystem influencer "
                    f"(influence: {g.ecosystem_influence:.4f}, PageRank: {g.pagerank:.4f}) "
                    f"in the {g.cluster_label}."
                ),
                "category": "graph",
                "severity": "info",
            })
        return insights

    # ── Public API ────────────────────────────────────────────────

    def generate(self) -> list[dict]:
        """Generate all insights from all analytics modules."""
        all_insights: list[dict] = []
        all_insights.extend(self._momentum_insights())
        all_insights.extend(self._lifecycle_insights())
        all_insights.extend(self._forecast_insights())
        all_insights.extend(self._health_insights())
        all_insights.extend(self._graph_insights())

        logger.info("Generated %d insights.", len(all_insights))
        return all_insights
