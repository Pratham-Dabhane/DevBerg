"""Technology Lifecycle Detector.

Classifies each technology into a lifecycle stage based on its
momentum score, growth velocity, and community activity:

    Emerging   — momentum_score > 0.75
    Growth     — 0.55 – 0.75
    Stable     — 0.40 – 0.55
    Declining  — 0.20 – 0.40
    Dead       — < 0.20

A confidence score (0-1) is derived from the agreement between
multiple input signals.
"""

import logging
from datetime import datetime, timezone

import pandas as pd
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.models import TechnologyMomentum, TechnologyMetrics, TechnologyLifecycle

logger = logging.getLogger(__name__)

STAGE_THRESHOLDS = [
    (0.75, "Emerging"),
    (0.55, "Growth"),
    (0.40, "Stable"),
    (0.20, "Declining"),
]
DEFAULT_STAGE = "Dead"


def _classify_stage(momentum: float) -> str:
    for threshold, stage in STAGE_THRESHOLDS:
        if momentum > threshold:
            return stage
    return DEFAULT_STAGE


def _confidence(
    momentum: float,
    growth_velocity: float,
    community_activity: float,
) -> float:
    """
    Confidence is higher when multiple signals agree on the lifecycle stage.

    If the momentum score is high AND growth velocity is positive AND community
    is active, we are more confident in the classification.
    """
    signals = [momentum, growth_velocity, community_activity]
    mean = sum(signals) / len(signals)
    # Variance — lower variance = higher agreement = higher confidence
    variance = sum((s - mean) ** 2 for s in signals) / len(signals)
    # Map variance to confidence: 0 variance ⇒ 1.0, high variance ⇒ lower
    confidence = max(0.0, min(1.0, 1.0 - variance * 4))
    return round(confidence, 4)


class LifecycleDetector:
    """Assigns lifecycle stages to every tracked technology."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def _latest_momentum(self) -> dict[str, TechnologyMomentum]:
        subq = (
            self.db.query(
                TechnologyMomentum.technology_name,
                func.max(TechnologyMomentum.timestamp).label("max_ts"),
            )
            .group_by(TechnologyMomentum.technology_name)
            .subquery()
        )
        rows = (
            self.db.query(TechnologyMomentum)
            .join(
                subq,
                (TechnologyMomentum.technology_name == subq.c.technology_name)
                & (TechnologyMomentum.timestamp == subq.c.max_ts),
            )
            .all()
        )
        return {r.technology_name: r for r in rows}

    def _latest_metrics(self) -> dict[str, TechnologyMetrics]:
        subq = (
            self.db.query(
                TechnologyMetrics.technology,
                func.max(TechnologyMetrics.last_updated).label("max_up"),
            )
            .group_by(TechnologyMetrics.technology)
            .subquery()
        )
        rows = (
            self.db.query(TechnologyMetrics)
            .join(
                subq,
                (TechnologyMetrics.technology == subq.c.technology)
                & (TechnologyMetrics.last_updated == subq.c.max_up),
            )
            .all()
        )
        return {r.technology: r for r in rows}

    def _growth_velocity(self, tech: str) -> float:
        """Rate of change of momentum over the last two snapshots."""
        rows = (
            self.db.query(TechnologyMomentum)
            .filter(TechnologyMomentum.technology_name == tech)
            .order_by(TechnologyMomentum.timestamp.desc())
            .limit(2)
            .all()
        )
        if len(rows) < 2:
            return 0.0
        prev = rows[1].momentum_score
        if prev == 0:
            return 1.0 if rows[0].momentum_score > 0 else 0.0
        return (rows[0].momentum_score - prev) / abs(prev)

    def run(self) -> list[TechnologyLifecycle]:
        momentum_map = self._latest_momentum()
        metrics_map = self._latest_metrics()

        if not momentum_map:
            logger.warning("No momentum data — run the momentum engine first.")
            return []

        now = datetime.now(timezone.utc)
        results: list[TechnologyLifecycle] = []

        for tech, mom in momentum_map.items():
            metric = metrics_map.get(tech)
            growth_vel = self._growth_velocity(tech)

            # Community activity: combine community_score + discussion_velocity
            community = 0.0
            if metric:
                community = min(
                    (metric.community_score + metric.discussion_velocity) / 2, 1.0
                )

            # Normalize growth velocity to [0, 1] range for confidence calc
            gv_norm = max(0.0, min(1.0, (growth_vel + 1.0) / 2.0))

            stage = _classify_stage(mom.momentum_score)
            conf = _confidence(mom.momentum_score, gv_norm, community)

            record = TechnologyLifecycle(
                technology_name=tech,
                lifecycle_stage=stage,
                confidence_score=conf,
                momentum_score=round(mom.momentum_score, 4),
                timestamp=now,
            )
            self.db.add(record)
            results.append(record)

        self.db.commit()
        for r in results:
            self.db.refresh(r)

        logger.info(
            "Lifecycle classification complete: %s",
            {r.technology_name: r.lifecycle_stage for r in results},
        )
        return results
