"""Trend detection engine — orchestrates momentum, anomaly, and forecasting modules."""

import logging
from datetime import datetime, timezone

import pandas as pd
from sqlalchemy.orm import Session

from app.models.models import TechnologyMetrics, TechnologyPrediction
from app.ml.momentum import compute_momentum_scores
from app.ml.anomaly import detect_emerging_technologies
from app.ml.forecasting import forecast_technology_growth

logger = logging.getLogger(__name__)


class TrendEngine:
    """Orchestrates ML modules to produce technology predictions."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def _load_metrics_history(self) -> pd.DataFrame:
        """Load all technology_metrics records as a DataFrame."""
        rows = (
            self.db.query(TechnologyMetrics)
            .order_by(TechnologyMetrics.technology, TechnologyMetrics.last_updated)
            .all()
        )
        if not rows:
            return pd.DataFrame()

        data = [
            {
                "technology": r.technology,
                "stars_growth_rate": r.stars_growth_rate,
                "contributors_growth_rate": r.contributors_growth_rate,
                "commit_activity_score": r.commit_activity_score,
                "issue_resolution_rate": r.issue_resolution_rate,
                "stackoverflow_growth": r.stackoverflow_growth,
                "hn_mentions_growth": r.hn_mentions_growth,
                "discussion_velocity": r.discussion_velocity,
                "momentum_score": r.momentum_score,
                "community_score": r.community_score,
                "activity_score": r.activity_score,
                "last_updated": r.last_updated,
            }
            for r in rows
        ]
        return pd.DataFrame(data)

    def run(self) -> list[TechnologyPrediction]:
        """Execute the full trend detection pipeline."""
        logger.info("Starting trend detection engine...")

        metrics_df = self._load_metrics_history()
        if metrics_df.empty:
            logger.warning("No metrics data found — run the metrics pipeline first.")
            return []

        # Step 1: Compute weighted momentum scores
        momentum_df = compute_momentum_scores(metrics_df)

        # Step 2: Detect emerging technologies via anomaly detection
        anomaly_df = detect_emerging_technologies(metrics_df)

        # Step 3: Forecast growth using time-series analysis
        forecasts = forecast_technology_growth(metrics_df)
        forecast_df = pd.DataFrame(
            [
                {
                    "technology": f.technology,
                    "predicted_growth": f.predicted_growth,
                    "confidence_score": f.confidence_score,
                    "trend_direction": f.trend_direction,
                }
                for f in forecasts
            ]
        )

        # Merge all results
        result_df = momentum_df.merge(anomaly_df, on="technology", how="outer")
        if not forecast_df.empty:
            result_df = result_df.merge(forecast_df, on="technology", how="outer")
        result_df = result_df.fillna(
            {
                "momentum_score": 0.0,
                "is_emerging": False,
                "anomaly_score": 0.0,
                "predicted_growth": 0.0,
                "confidence_score": 0.2,
                "trend_direction": "stable",
            }
        )

        # Persist predictions
        now = datetime.now(timezone.utc)
        predictions: list[TechnologyPrediction] = []

        for _, row in result_df.iterrows():
            prediction = TechnologyPrediction(
                technology=row["technology"],
                predicted_growth=round(float(row["predicted_growth"]), 4),
                confidence_score=round(float(row["confidence_score"]), 4),
                trend_direction=row["trend_direction"],
                momentum_score=round(float(row["momentum_score"]), 4),
                is_emerging=1 if row["is_emerging"] else 0,
                forecast_horizon_months=6,
                created_at=now,
            )
            self.db.add(prediction)
            predictions.append(prediction)

        self.db.commit()
        for p in predictions:
            self.db.refresh(p)

        logger.info(
            "Trend engine complete — %d predictions stored: %s",
            len(predictions),
            {
                p.technology: f"growth={p.predicted_growth:.4f} dir={p.trend_direction} emerging={bool(p.is_emerging)}"
                for p in predictions
            },
        )
        return predictions
