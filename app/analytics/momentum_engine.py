"""Technology Momentum Score engine.

Calculates a weighted momentum score per tracked technology:

    momentum = 0.35 * stars_growth
             + 0.25 * contributors_growth
             + 0.20 * stackoverflow_growth
             + 0.10 * hn_mentions
             + 0.10 * commit_activity

All signals are min-max normalized to [0, 1] before weighting.
"""

import logging
from datetime import datetime, timezone

import pandas as pd
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.models import (
    Repository,
    StackOverflowStats,
    TechMention,
    TechnologyMetrics,
    TechnologyMomentum,
)

logger = logging.getLogger(__name__)

WEIGHTS = {
    "stars_growth": 0.35,
    "contributors_growth": 0.25,
    "stackoverflow_growth": 0.20,
    "hn_mentions": 0.10,
    "commit_activity": 0.10,
}


def _normalize(series: pd.Series) -> pd.Series:
    """Min-max normalize a series to [0, 1]."""
    mn, mx = series.min(), series.max()
    if mx == mn:
        return pd.Series(0.5, index=series.index)
    return (series - mn) / (mx - mn)


def _safe_growth(current: float, previous: float) -> float:
    if previous == 0:
        return 1.0 if current > 0 else 0.0
    return (current - previous) / abs(previous)


class MomentumEngine:
    """Computes and persists technology momentum scores."""

    def __init__(self, db: Session) -> None:
        self.db = db

    # ── Data loading ──────────────────────────────────────────────

    def _load_raw_signals(self) -> pd.DataFrame:
        """Gather raw signal values per technology from source tables."""
        records: list[dict] = []

        # Latest 2 repo snapshots per tech for growth calc
        repo_rows = (
            self.db.query(Repository)
            .order_by(Repository.technology, Repository.collected_at.desc())
            .all()
        )
        repo_map: dict[str, list[Repository]] = {}
        for r in repo_rows:
            repo_map.setdefault(r.technology, []).append(r)

        # Latest 2 SO snapshots
        so_rows = (
            self.db.query(StackOverflowStats)
            .order_by(StackOverflowStats.technology, StackOverflowStats.collected_at.desc())
            .all()
        )
        so_map: dict[str, list[StackOverflowStats]] = {}
        for s in so_rows:
            so_map.setdefault(s.technology, []).append(s)

        # Latest HN mentions
        hn_rows = (
            self.db.query(TechMention)
            .filter(TechMention.source == "hackernews")
            .order_by(TechMention.technology, TechMention.collected_at.desc())
            .all()
        )
        hn_map: dict[str, list[TechMention]] = {}
        for h in hn_rows:
            hn_map.setdefault(h.technology, []).append(h)

        all_techs = set(repo_map) | set(so_map) | set(hn_map)

        for tech in all_techs:
            repos = repo_map.get(tech, [])
            sos = so_map.get(tech, [])
            hns = hn_map.get(tech, [])

            # Stars growth
            if len(repos) >= 2:
                stars_growth = _safe_growth(repos[0].stars, repos[1].stars)
                contrib_growth = _safe_growth(repos[0].contributors, repos[1].contributors)
            elif repos:
                stars_growth = repos[0].stars / max(repos[0].stars, 1)
                contrib_growth = repos[0].contributors / max(repos[0].contributors, 1)
            else:
                stars_growth = 0.0
                contrib_growth = 0.0

            # Commit frequency (raw weekly value)
            commit_freq = repos[0].commit_frequency_weekly if repos else 0.0

            # SO growth
            if len(sos) >= 2:
                so_growth = _safe_growth(sos[0].question_count, sos[1].question_count)
            elif sos:
                so_growth = sos[0].new_questions_last_30_days / max(sos[0].question_count, 1)
            else:
                so_growth = 0.0

            # HN mentions count
            hn_count = hns[0].mention_count if hns else 0

            records.append({
                "technology": tech,
                "stars_growth_raw": stars_growth,
                "contributors_growth_raw": contrib_growth,
                "stackoverflow_growth_raw": so_growth,
                "hn_mentions_raw": float(hn_count),
                "commit_activity_raw": commit_freq,
            })

        return pd.DataFrame(records) if records else pd.DataFrame()

    # ── Compute ───────────────────────────────────────────────────

    def compute(self) -> pd.DataFrame:
        """Compute normalized momentum scores for all technologies."""
        df = self._load_raw_signals()
        if df.empty:
            logger.warning("No raw signals — nothing to compute.")
            return pd.DataFrame()

        # Normalize each signal to [0, 1]
        df["stars_growth"] = _normalize(df["stars_growth_raw"])
        df["contributors_growth"] = _normalize(df["contributors_growth_raw"])
        df["stackoverflow_growth"] = _normalize(df["stackoverflow_growth_raw"])
        df["hn_mentions"] = _normalize(df["hn_mentions_raw"])
        df["commit_activity"] = _normalize(df["commit_activity_raw"])

        # Weighted momentum score
        df["momentum_score"] = (
            WEIGHTS["stars_growth"] * df["stars_growth"]
            + WEIGHTS["contributors_growth"] * df["contributors_growth"]
            + WEIGHTS["stackoverflow_growth"] * df["stackoverflow_growth"]
            + WEIGHTS["hn_mentions"] * df["hn_mentions"]
            + WEIGHTS["commit_activity"] * df["commit_activity"]
        )

        logger.info("Momentum scores computed for %d technologies.", len(df))
        return df

    # ── Persist ───────────────────────────────────────────────────

    def run(self) -> list[TechnologyMomentum]:
        """Compute momentum scores and persist them to the database."""
        df = self.compute()
        if df.empty:
            return []

        now = datetime.now(timezone.utc)
        rows: list[TechnologyMomentum] = []

        for _, r in df.iterrows():
            record = TechnologyMomentum(
                technology_name=r["technology"],
                momentum_score=round(float(r["momentum_score"]), 4),
                stars_growth=round(float(r["stars_growth"]), 4),
                contributors_growth=round(float(r["contributors_growth"]), 4),
                stackoverflow_growth=round(float(r["stackoverflow_growth"]), 4),
                hn_mentions=round(float(r["hn_mentions"]), 4),
                commit_activity=round(float(r["commit_activity"]), 4),
                timestamp=now,
            )
            self.db.add(record)
            rows.append(record)

        self.db.commit()
        for row in rows:
            self.db.refresh(row)

        logger.info("Persisted %d momentum records.", len(rows))
        return rows
