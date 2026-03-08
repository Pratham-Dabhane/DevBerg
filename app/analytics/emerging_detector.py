"""Emerging Technology Detector.

Uses Z-score anomaly detection and Isolation Forest to flag
technologies with sudden growth spikes across:

    - stars_growth
    - contributors_growth
    - community_mentions (SO + HN combined)

Technologies whose growth signals deviate significantly from the
population are ranked by a composite growth_spike_score and
persisted to the `emerging_technologies` table.
"""

import logging
from datetime import datetime, timezone

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.models import TechnologyMomentum, TechnologyMetrics, EmergingTechnology

logger = logging.getLogger(__name__)


def _zscore_flags(series: pd.Series, threshold: float = 1.5) -> pd.Series:
    """Return boolean series where |z-score| > threshold."""
    mean = series.mean()
    std = series.std()
    if std == 0:
        return pd.Series(False, index=series.index)
    z = (series - mean) / std
    return z.abs() > threshold


class EmergingDetector:
    """Detects technologies with anomalous growth spikes."""

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

    def _build_feature_df(self) -> pd.DataFrame:
        mom_map = self._latest_momentum()
        met_map = self._latest_metrics()

        records: list[dict] = []
        for tech, mom in mom_map.items():
            met = met_map.get(tech)
            community_mentions = 0.0
            if met:
                community_mentions = met.stackoverflow_growth + met.hn_mentions_growth

            records.append({
                "technology": tech,
                "stars_growth": mom.stars_growth,
                "contributors_growth": mom.contributors_growth,
                "community_mentions": community_mentions,
            })

        return pd.DataFrame(records) if records else pd.DataFrame()

    def run(self) -> list[EmergingTechnology]:
        df = self._build_feature_df()
        if df.empty:
            logger.warning("No data for emerging detection.")
            return []

        feature_cols = ["stars_growth", "contributors_growth", "community_mentions"]

        # ── Method 1: Z-score anomaly flags ──
        zscore_flags = pd.DataFrame(index=df.index)
        for col in feature_cols:
            zscore_flags[col] = _zscore_flags(df[col])
        df["zscore_spike"] = zscore_flags.any(axis=1)

        # ── Method 2: Isolation Forest ──
        X = df[feature_cols].values
        if len(X) >= 3:
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            clf = IsolationForest(
                contamination=0.2,
                random_state=42,
                n_estimators=100,
            )
            clf.fit(X_scaled)
            raw_scores = clf.decision_function(X_scaled)
            predictions = clf.predict(X_scaled)
            df["iso_score"] = -raw_scores  # higher = more anomalous
            df["iso_spike"] = predictions == -1
        else:
            # Too few samples — fall back to top-percentile
            combined = df[feature_cols].mean(axis=1)
            df["iso_score"] = combined
            df["iso_spike"] = combined > combined.quantile(0.7)

        # ── Composite spike score ──
        # Combine both methods: iso_score weighted 60%, raw growth mean 40%
        growth_mean = df[feature_cols].mean(axis=1)
        # Normalize both to [0, 1]
        iso_norm = (df["iso_score"] - df["iso_score"].min()) / max(df["iso_score"].max() - df["iso_score"].min(), 1e-9)
        gm_norm = (growth_mean - growth_mean.min()) / max(growth_mean.max() - growth_mean.min(), 1e-9)
        df["growth_spike_score"] = (0.6 * iso_norm + 0.4 * gm_norm).clip(0, 1)

        # Only persist technologies flagged by at least one method
        emerging = df[df["zscore_spike"] | df["iso_spike"]].copy()
        emerging = emerging.sort_values("growth_spike_score", ascending=False)

        now = datetime.now(timezone.utc)
        results: list[EmergingTechnology] = []

        for _, row in emerging.iterrows():
            record = EmergingTechnology(
                technology_name=row["technology"],
                growth_spike_score=round(float(row["growth_spike_score"]), 4),
                detected_at=now,
            )
            self.db.add(record)
            results.append(record)

        self.db.commit()
        for r in results:
            self.db.refresh(r)

        logger.info(
            "Emerging detector found %d spiking technologies: %s",
            len(results),
            [r.technology_name for r in results],
        )
        return results
