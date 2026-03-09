"""GitHub Repository Health Analyzer.

Evaluates repository health using ecosystem signals and produces a 0–100
health score for each tracked repository.

    health_score = 0.30 * maintainer_activity
                 + 0.25 * issue_resolution_speed
                 + 0.20 * contributor_count
                 + 0.15 * release_frequency
                 + 0.10 * commit_frequency

Risk classification:
    80–100  → Low Risk
    60–79   → Moderate Risk
    40–59   → High Risk
    <40     → Critical
"""

import logging
from datetime import datetime, timezone

import pandas as pd
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.models import Repository, TechnologyMetrics, RepositoryHealth

logger = logging.getLogger(__name__)

WEIGHTS = {
    "maintainer_activity": 0.30,
    "issue_resolution_speed": 0.25,
    "contributor_count": 0.20,
    "release_frequency": 0.15,
    "commit_frequency": 0.10,
}

RISK_THRESHOLDS: list[tuple[float, str]] = [
    (80, "Low"),
    (60, "Moderate"),
    (40, "High"),
]
DEFAULT_RISK = "Critical"


def _classify_risk(score: float) -> str:
    for threshold, level in RISK_THRESHOLDS:
        if score >= threshold:
            return level
    return DEFAULT_RISK


def _normalize_series(series: pd.Series) -> pd.Series:
    """Min-max normalize a series to [0, 1]."""
    mn, mx = series.min(), series.max()
    if mx == mn:
        return pd.Series(0.5, index=series.index)
    return (series - mn) / (mx - mn)


class RepoHealthAnalyzer:
    """Computes and persists repository health scores."""

    def __init__(self, db: Session) -> None:
        self.db = db

    # ── Signal extraction ─────────────────────────────────────────

    def _build_signal_frame(self) -> pd.DataFrame:
        """Build a DataFrame of raw signals per repository from collected data."""
        settings = get_settings()
        tech_repos = {t["name"]: t["github_repo"] for t in settings.tracked_technologies}

        records: list[dict] = []

        for tech_name, repo_slug in tech_repos.items():
            snapshots = (
                self.db.query(Repository)
                .filter(Repository.technology == tech_name)
                .order_by(Repository.collected_at.desc())
                .limit(2)
                .all()
            )
            if not snapshots:
                continue

            latest = snapshots[0]
            previous = snapshots[1] if len(snapshots) >= 2 else None

            # maintainer_activity: based on commit frequency and recent issue
            # resolution — higher commit_frequency_weekly = more active
            maintainer_activity = latest.commit_frequency_weekly

            # contributor_count: raw contributor number
            contributor_count = float(latest.contributors)

            # commit_frequency: weekly commits (same source, kept separate for
            # independent weight)
            commit_frequency = latest.commit_frequency_weekly

            # issue_resolution_speed: derived from TechnologyMetrics if available
            metrics = (
                self.db.query(TechnologyMetrics)
                .filter(TechnologyMetrics.technology == tech_name)
                .order_by(TechnologyMetrics.last_updated.desc())
                .first()
            )
            issue_resolution_speed = metrics.issue_resolution_rate if metrics else 0.0

            # release_frequency: approximate from stars growth momentum — repos
            # that ship releases frequently also tend to have accelerating stars.
            # When release data is not directly collected, we proxy via the
            # activity_score from TechnologyMetrics.
            release_frequency = metrics.activity_score if metrics else 0.0

            records.append(
                {
                    "repository_name": repo_slug,
                    "maintainer_activity_raw": maintainer_activity,
                    "issue_resolution_speed_raw": issue_resolution_speed,
                    "contributor_count_raw": contributor_count,
                    "release_frequency_raw": release_frequency,
                    "commit_frequency_raw": commit_frequency,
                    "contributors_int": latest.contributors,
                }
            )

        if not records:
            return pd.DataFrame()

        return pd.DataFrame(records)

    # ── Scoring ───────────────────────────────────────────────────

    def compute(self) -> list[dict]:
        """Compute health scores for all repositories. Returns list of dicts."""
        df = self._build_signal_frame()
        if df.empty:
            logger.warning("No repository data to analyze.")
            return []

        # Normalize each signal independently to [0, 1]
        signal_cols = {
            "maintainer_activity": "maintainer_activity_raw",
            "issue_resolution_speed": "issue_resolution_speed_raw",
            "contributor_count": "contributor_count_raw",
            "release_frequency": "release_frequency_raw",
            "commit_frequency": "commit_frequency_raw",
        }
        for norm_col, raw_col in signal_cols.items():
            df[norm_col] = _normalize_series(df[raw_col])

        # Weighted health score scaled to [0, 100]
        df["health_score"] = sum(
            WEIGHTS[col] * df[col] for col in WEIGHTS
        ) * 100

        # Clamp to [0, 100]
        df["health_score"] = df["health_score"].clip(0, 100).round(2)

        # Risk classification
        df["risk_level"] = df["health_score"].apply(_classify_risk)

        now = datetime.now(timezone.utc)
        results: list[dict] = []
        for _, row in df.iterrows():
            results.append(
                {
                    "repository_name": row["repository_name"],
                    "health_score": row["health_score"],
                    "risk_level": row["risk_level"],
                    "maintainer_activity": round(row["maintainer_activity"] * 100, 2),
                    "issue_resolution_speed": round(row["issue_resolution_speed"] * 100, 2),
                    "contributors": int(row["contributors_int"]),
                    "release_frequency": round(row["release_frequency"] * 100, 2),
                    "commit_frequency": round(row["commit_frequency"] * 100, 2),
                    "last_updated": now,
                }
            )

        return results

    # ── Persist ───────────────────────────────────────────────────

    def run(self) -> list[RepositoryHealth]:
        """Compute and persist health scores. Returns persisted ORM objects."""
        results = self.compute()
        if not results:
            return []

        orm_objects: list[RepositoryHealth] = []
        for r in results:
            obj = RepositoryHealth(**r)
            self.db.add(obj)
            orm_objects.append(obj)

        self.db.commit()
        for obj in orm_objects:
            self.db.refresh(obj)

        logger.info("Persisted health scores for %d repositories.", len(orm_objects))
        return orm_objects
