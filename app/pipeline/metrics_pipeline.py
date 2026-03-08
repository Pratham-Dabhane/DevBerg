import logging
from datetime import datetime, timezone

import pandas as pd
from sqlalchemy.orm import Session

from app.models.models import (
    HackerNewsMention,
    Repository,
    StackOverflowStats,
    TechMention,
    TechnologyMetrics,
)

logger = logging.getLogger(__name__)


def _safe_growth_rate(current: float, previous: float) -> float:
    """Compute growth rate, handling zero-division."""
    if previous == 0:
        return 1.0 if current > 0 else 0.0
    return (current - previous) / previous


def _normalize_series(series: pd.Series) -> pd.Series:
    """Min-max normalize a pandas Series to [0, 1]."""
    min_val = series.min()
    max_val = series.max()
    if max_val == min_val:
        return pd.Series(0.5, index=series.index)
    return (series - min_val) / (max_val - min_val)


class MetricsPipeline:
    """Transforms raw ecosystem data into normalized technology signals."""

    def __init__(self, db: Session) -> None:
        self.db = db

    # ── Data loaders ──────────────────────────────────────────────

    def _load_github_data(self) -> pd.DataFrame:
        """Load the two most recent snapshots per technology for growth calc."""
        rows = (
            self.db.query(Repository)
            .order_by(Repository.technology, Repository.collected_at.desc())
            .all()
        )
        if not rows:
            return pd.DataFrame()

        data = [
            {
                "technology": r.technology,
                "stars": r.stars,
                "forks": r.forks,
                "open_issues": r.open_issues,
                "contributors": r.contributors,
                "commit_frequency_weekly": r.commit_frequency_weekly,
                "collected_at": r.collected_at,
            }
            for r in rows
        ]
        return pd.DataFrame(data)

    def _load_stackoverflow_data(self) -> pd.DataFrame:
        rows = (
            self.db.query(StackOverflowStats)
            .order_by(StackOverflowStats.technology, StackOverflowStats.collected_at.desc())
            .all()
        )
        if not rows:
            return pd.DataFrame()

        data = [
            {
                "technology": r.technology,
                "question_count": r.question_count,
                "new_questions_last_30_days": r.new_questions_last_30_days,
                "collected_at": r.collected_at,
            }
            for r in rows
        ]
        return pd.DataFrame(data)

    def _load_hackernews_data(self) -> pd.DataFrame:
        rows = (
            self.db.query(TechMention)
            .filter(TechMention.source == "hackernews")
            .order_by(TechMention.technology, TechMention.collected_at.desc())
            .all()
        )
        if not rows:
            return pd.DataFrame()

        data = [
            {
                "technology": r.technology,
                "mention_count": r.mention_count,
                "total_upvotes": r.total_upvotes,
                "total_comments": r.total_comments,
                "collected_at": r.collected_at,
            }
            for r in rows
        ]
        return pd.DataFrame(data)

    # ── Feature extraction ────────────────────────────────────────

    def _compute_github_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Compute per-technology GitHub growth metrics from snapshot pairs."""
        records: list[dict] = []

        for tech, group in df.groupby("technology"):
            sorted_group = group.sort_values("collected_at", ascending=False)
            latest = sorted_group.iloc[0]

            if len(sorted_group) >= 2:
                previous = sorted_group.iloc[1]
                stars_growth = _safe_growth_rate(latest["stars"], previous["stars"])
                contributors_growth = _safe_growth_rate(
                    latest["contributors"], previous["contributors"]
                )
            else:
                # Single snapshot — use absolute values as proxy
                stars_growth = latest["stars"] / max(latest["stars"], 1)
                contributors_growth = latest["contributors"] / max(latest["contributors"], 1)

            # Commit activity: weekly commit frequency as raw signal
            commit_activity = latest["commit_frequency_weekly"]

            # Issue resolution: inverse of open issues relative to stars
            # Higher stars with fewer open issues = better resolution
            issue_ratio = latest["open_issues"] / max(latest["stars"], 1)
            issue_resolution = 1.0 - min(issue_ratio, 1.0)

            records.append(
                {
                    "technology": tech,
                    "stars_growth_rate": stars_growth,
                    "contributors_growth_rate": contributors_growth,
                    "commit_activity_score": commit_activity,
                    "issue_resolution_rate": issue_resolution,
                }
            )

        return pd.DataFrame(records)

    def _compute_stackoverflow_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Compute StackOverflow growth signal per technology."""
        records: list[dict] = []

        for tech, group in df.groupby("technology"):
            sorted_group = group.sort_values("collected_at", ascending=False)
            latest = sorted_group.iloc[0]

            if len(sorted_group) >= 2:
                previous = sorted_group.iloc[1]
                so_growth = _safe_growth_rate(
                    latest["question_count"], previous["question_count"]
                )
            else:
                # Use new-questions ratio as proxy for growth
                so_growth = latest["new_questions_last_30_days"] / max(
                    latest["question_count"], 1
                )

            records.append(
                {
                    "technology": tech,
                    "stackoverflow_growth": so_growth,
                    "new_questions_30d": latest["new_questions_last_30_days"],
                }
            )

        return pd.DataFrame(records)

    def _compute_hackernews_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Compute HackerNews community signals per technology."""
        records: list[dict] = []

        for tech, group in df.groupby("technology"):
            sorted_group = group.sort_values("collected_at", ascending=False)
            latest = sorted_group.iloc[0]

            if len(sorted_group) >= 2:
                previous = sorted_group.iloc[1]
                hn_growth = _safe_growth_rate(
                    latest["mention_count"], previous["mention_count"]
                )
            else:
                hn_growth = latest["mention_count"] / max(latest["mention_count"], 1)

            # Discussion velocity: comments-per-upvote ratio (engagement depth)
            discussion_velocity = latest["total_comments"] / max(
                latest["total_upvotes"], 1
            )

            records.append(
                {
                    "technology": tech,
                    "hn_mentions_growth": hn_growth,
                    "discussion_velocity": discussion_velocity,
                    "total_upvotes": latest["total_upvotes"],
                    "total_comments": latest["total_comments"],
                }
            )

        return pd.DataFrame(records)

    # ── Normalization & composite scores ──────────────────────────

    def _build_composite_scores(self, merged: pd.DataFrame) -> pd.DataFrame:
        """Normalize all signals to [0,1] and compute composite scores."""
        df = merged.copy()

        # Normalize individual signals
        signal_cols = [
            "stars_growth_rate",
            "contributors_growth_rate",
            "commit_activity_score",
            "issue_resolution_rate",
            "stackoverflow_growth",
            "hn_mentions_growth",
            "discussion_velocity",
        ]
        for col in signal_cols:
            df[col] = _normalize_series(df[col])

        # Momentum: driven by GitHub growth and commit activity
        df["momentum_score"] = (
            df["stars_growth_rate"] * 0.3
            + df["contributors_growth_rate"] * 0.25
            + df["commit_activity_score"] * 0.25
            + df["issue_resolution_rate"] * 0.2
        )

        # Community: driven by SO and HN engagement
        df["community_score"] = (
            df["stackoverflow_growth"] * 0.35
            + df["hn_mentions_growth"] * 0.35
            + df["discussion_velocity"] * 0.30
        )

        # Activity: holistic blend of all signals
        df["activity_score"] = (
            df["commit_activity_score"] * 0.25
            + df["stars_growth_rate"] * 0.15
            + df["stackoverflow_growth"] * 0.20
            + df["hn_mentions_growth"] * 0.15
            + df["discussion_velocity"] * 0.10
            + df["contributors_growth_rate"] * 0.15
        )

        # Final normalization of composite scores
        for score_col in ["momentum_score", "community_score", "activity_score"]:
            df[score_col] = _normalize_series(df[score_col])

        return df

    # ── Pipeline execution ────────────────────────────────────────

    def run(self) -> list[TechnologyMetrics]:
        """Execute the full pipeline: load → transform → normalize → store."""
        logger.info("Starting metrics pipeline...")

        gh_df = self._load_github_data()
        so_df = self._load_stackoverflow_data()
        hn_df = self._load_hackernews_data()

        if gh_df.empty and so_df.empty and hn_df.empty:
            logger.warning("No source data found — skipping pipeline run.")
            return []

        # Compute per-source features
        gh_features = self._compute_github_features(gh_df) if not gh_df.empty else pd.DataFrame()
        so_features = self._compute_stackoverflow_features(so_df) if not so_df.empty else pd.DataFrame()
        hn_features = self._compute_hackernews_features(hn_df) if not hn_df.empty else pd.DataFrame()

        # Merge all features on technology
        frames = [f for f in [gh_features, so_features, hn_features] if not f.empty]
        if not frames:
            logger.warning("No features computed — skipping pipeline run.")
            return []

        merged = frames[0]
        for frame in frames[1:]:
            merged = merged.merge(frame, on="technology", how="outer")
        merged = merged.fillna(0.0)

        # Normalize and compute composite scores
        scored = self._build_composite_scores(merged)

        # Persist results
        now = datetime.now(timezone.utc)
        results: list[TechnologyMetrics] = []

        for _, row in scored.iterrows():
            record = TechnologyMetrics(
                technology=row["technology"],
                stars_growth_rate=round(row["stars_growth_rate"], 4),
                contributors_growth_rate=round(row["contributors_growth_rate"], 4),
                commit_activity_score=round(row["commit_activity_score"], 4),
                issue_resolution_rate=round(row["issue_resolution_rate"], 4),
                stackoverflow_growth=round(row["stackoverflow_growth"], 4),
                hn_mentions_growth=round(row["hn_mentions_growth"], 4),
                discussion_velocity=round(row["discussion_velocity"], 4),
                momentum_score=round(row["momentum_score"], 4),
                community_score=round(row["community_score"], 4),
                activity_score=round(row["activity_score"], 4),
                last_updated=now,
            )
            self.db.add(record)
            results.append(record)

        self.db.commit()
        for r in results:
            self.db.refresh(r)

        logger.info(
            "Pipeline complete — processed %d technologies. Scores: %s",
            len(results),
            {r.technology: f"m={r.momentum_score:.2f} c={r.community_score:.2f} a={r.activity_score:.2f}" for r in results},
        )
        return results
