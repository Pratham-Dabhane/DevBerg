"""Analytics engine — converts raw metrics into human-readable insights."""

import logging
from datetime import datetime, timezone
from dataclasses import dataclass, field

import pandas as pd
from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from app.models.models import (
    Repository,
    TechnologyMetrics,
    TechnologyPrediction,
    StackOverflowStats,
    TechMention,
)

logger = logging.getLogger(__name__)


# ── Data classes ──────────────────────────────────────────────────

@dataclass
class HealthReport:
    technology: str
    health_score: int  # 0-100
    risk_level: str  # Low / Medium / High / Critical
    maintainer_activity: float
    release_frequency: float
    issue_resolution_speed: float
    contributor_diversity: float
    insights: list[str] = field(default_factory=list)


@dataclass
class EmergingTech:
    rank: int
    technology: str
    momentum_score: float
    predicted_growth: float
    trend_direction: str
    signals: list[str] = field(default_factory=list)


@dataclass
class TrendInsight:
    technology: str
    category: str  # growth / decline / anomaly / milestone
    message: str
    severity: str  # info / warning / critical
    data: dict = field(default_factory=dict)


class InsightsEngine:
    """Generates human-readable insights from ecosystem data."""

    def __init__(self, db: Session) -> None:
        self.db = db

    # ── Health Score ──────────────────────────────────────────────

    def compute_health_scores(self) -> list[HealthReport]:
        """
        Compute a Repo Health Score (0-100) per technology.

        health_score =
            maintainer_activity (25pts)   — commit frequency
            + release_frequency (25pts)   — commit consistency proxy
            + issue_resolution_speed (25pts) — open issue ratio
            + contributor_diversity (25pts)  — contributor count & growth
        """
        repos = self._latest_repos()
        metrics = self._latest_metrics()

        if not repos:
            return []

        reports: list[HealthReport] = []

        # Collect raw values per tech for relative scoring
        raw: list[dict] = []
        for tech, repo in repos.items():
            metric = metrics.get(tech)
            raw.append({
                "technology": tech,
                "commit_freq": repo.commit_frequency_weekly,
                "contributors": repo.contributors,
                "stars": repo.stars,
                "open_issues": repo.open_issues,
                "issue_resolution_rate": metric.issue_resolution_rate if metric else 0.0,
                "contributors_growth": metric.contributors_growth_rate if metric else 0.0,
                "commit_activity": metric.commit_activity_score if metric else 0.0,
            })

        df = pd.DataFrame(raw)
        if df.empty:
            return []

        # --- Maintainer activity (0-25): based on commit frequency ---
        max_commit = df["commit_freq"].max()
        df["maintainer_activity"] = (
            (df["commit_freq"] / max(max_commit, 1)) * 25
        ).clip(0, 25)

        # --- Release frequency (0-25): commit consistency proxy ---
        # Higher commit_activity_score = more consistent releases
        max_activity = df["commit_activity"].max()
        df["release_frequency"] = (
            (df["commit_activity"] / max(max_activity, 1)) * 25
        ).clip(0, 25)

        # --- Issue resolution speed (0-25) ---
        df["issue_resolution_speed"] = (df["issue_resolution_rate"] * 25).clip(0, 25)

        # --- Contributor diversity (0-25) ---
        max_contributors = df["contributors"].max()
        contrib_score = (df["contributors"] / max(max_contributors, 1)) * 15
        growth_bonus = (df["contributors_growth"].clip(0, 1)) * 10
        df["contributor_diversity"] = (contrib_score + growth_bonus).clip(0, 25)

        # --- Total health score ---
        df["health_score"] = (
            df["maintainer_activity"]
            + df["release_frequency"]
            + df["issue_resolution_speed"]
            + df["contributor_diversity"]
        ).round().astype(int).clip(0, 100)

        for _, row in df.iterrows():
            score = int(row["health_score"])
            risk = self._risk_level(score)
            insights = self._health_insights(row, repos[row["technology"]])

            reports.append(HealthReport(
                technology=row["technology"],
                health_score=score,
                risk_level=risk,
                maintainer_activity=round(float(row["maintainer_activity"]), 1),
                release_frequency=round(float(row["release_frequency"]), 1),
                issue_resolution_speed=round(float(row["issue_resolution_speed"]), 1),
                contributor_diversity=round(float(row["contributor_diversity"]), 1),
                insights=insights,
            ))

        reports.sort(key=lambda r: r.health_score, reverse=True)
        logger.info("Health scores computed for %d technologies", len(reports))
        return reports

    # ── Emerging Tech Radar ──────────────────────────────────────

    def detect_emerging_radar(self, top_n: int = 10) -> list[EmergingTech]:
        """
        Return the top N emerging technologies ranked by a composite
        of momentum score and predicted growth.
        """
        predictions = self._latest_predictions()
        metrics = self._latest_metrics()

        if not predictions:
            return []

        scored: list[dict] = []
        for tech, pred in predictions.items():
            metric = metrics.get(tech)
            # Composite ranking: momentum contributes 60%, predicted growth 40%
            composite = (pred.momentum_score * 0.6) + (pred.predicted_growth * 0.4)

            signals: list[str] = []
            if pred.is_emerging:
                signals.append("Flagged as emerging by anomaly detection")
            if pred.trend_direction == "up":
                signals.append("Upward growth trend predicted")
            if metric:
                if metric.stars_growth_rate > 0.1:
                    pct = round(metric.stars_growth_rate * 100, 1)
                    signals.append(f"GitHub stars growing {pct}%")
                if metric.stackoverflow_growth > 0.05:
                    pct = round(metric.stackoverflow_growth * 100, 1)
                    signals.append(f"StackOverflow activity up {pct}%")
                if metric.hn_mentions_growth > 0.1:
                    pct = round(metric.hn_mentions_growth * 100, 1)
                    signals.append(f"HackerNews mentions up {pct}%")

            scored.append({
                "technology": tech,
                "composite": composite,
                "momentum_score": pred.momentum_score,
                "predicted_growth": pred.predicted_growth,
                "trend_direction": pred.trend_direction,
                "signals": signals,
            })

        scored.sort(key=lambda x: x["composite"], reverse=True)
        top = scored[:top_n]

        result = [
            EmergingTech(
                rank=i + 1,
                technology=item["technology"],
                momentum_score=round(item["momentum_score"], 4),
                predicted_growth=round(item["predicted_growth"], 4),
                trend_direction=item["trend_direction"],
                signals=item["signals"],
            )
            for i, item in enumerate(top)
        ]

        logger.info("Emerging tech radar: top %d technologies identified", len(result))
        return result

    # ── Trend Insights ───────────────────────────────────────────

    def generate_trend_insights(self) -> list[TrendInsight]:
        """
        Generate human-readable trend insights across all technologies.
        Produces messages like:
          'LangChain contributions increased 230% in the last 6 months.'
          'Rust backend frameworks are gaining adoption.'
        """
        metrics = self._latest_metrics()
        predictions = self._latest_predictions()
        repos = self._latest_repos()

        insights: list[TrendInsight] = []

        for tech, metric in metrics.items():
            pred = predictions.get(tech)
            repo = repos.get(tech)

            # ── Growth insights ──
            if metric.stars_growth_rate > 0.1:
                pct = round(metric.stars_growth_rate * 100, 1)
                insights.append(TrendInsight(
                    technology=tech,
                    category="growth",
                    message=f"{tech} GitHub stars increased {pct}% since last collection.",
                    severity="info",
                    data={"metric": "stars_growth_rate", "value": metric.stars_growth_rate},
                ))

            if metric.contributors_growth_rate > 0.15:
                pct = round(metric.contributors_growth_rate * 100, 1)
                insights.append(TrendInsight(
                    technology=tech,
                    category="growth",
                    message=f"{tech} contributions increased {pct}% — growing contributor base.",
                    severity="info",
                    data={"metric": "contributors_growth_rate", "value": metric.contributors_growth_rate},
                ))

            if metric.stackoverflow_growth > 0.1:
                pct = round(metric.stackoverflow_growth * 100, 1)
                insights.append(TrendInsight(
                    technology=tech,
                    category="growth",
                    message=f"{tech} StackOverflow questions grew {pct}% — rising developer interest.",
                    severity="info",
                    data={"metric": "stackoverflow_growth", "value": metric.stackoverflow_growth},
                ))

            # ── Decline / risk insights ──
            if metric.stars_growth_rate < -0.05:
                pct = round(abs(metric.stars_growth_rate) * 100, 1)
                insights.append(TrendInsight(
                    technology=tech,
                    category="decline",
                    message=f"{tech} star growth declined {pct}% — possible waning interest.",
                    severity="warning",
                    data={"metric": "stars_growth_rate", "value": metric.stars_growth_rate},
                ))

            if metric.commit_activity_score < 5 and repo:
                insights.append(TrendInsight(
                    technology=tech,
                    category="decline",
                    message=f"{tech} has very low commit activity ({metric.commit_activity_score:.1f} commits/week) — may be stagnating.",
                    severity="warning",
                    data={"metric": "commit_activity_score", "value": metric.commit_activity_score},
                ))

            if metric.issue_resolution_rate < 0.3:
                pct = round(metric.issue_resolution_rate * 100, 1)
                insights.append(TrendInsight(
                    technology=tech,
                    category="decline",
                    message=f"{tech} issue resolution rate is low ({pct}%) — maintenance risk detected.",
                    severity="warning",
                    data={"metric": "issue_resolution_rate", "value": metric.issue_resolution_rate},
                ))

            # ── Prediction-based insights ──
            if pred:
                if pred.trend_direction == "up" and pred.confidence_score > 0.5:
                    insights.append(TrendInsight(
                        technology=tech,
                        category="growth",
                        message=f"{tech} is predicted to grow over the next {pred.forecast_horizon_months} months (confidence: {pred.confidence_score:.0%}).",
                        severity="info",
                        data={"predicted_growth": pred.predicted_growth, "confidence": pred.confidence_score},
                    ))
                elif pred.trend_direction == "down" and pred.confidence_score > 0.5:
                    insights.append(TrendInsight(
                        technology=tech,
                        category="decline",
                        message=f"{tech} is predicted to decline over the next {pred.forecast_horizon_months} months (confidence: {pred.confidence_score:.0%}).",
                        severity="warning",
                        data={"predicted_growth": pred.predicted_growth, "confidence": pred.confidence_score},
                    ))

                if pred.is_emerging:
                    insights.append(TrendInsight(
                        technology=tech,
                        category="anomaly",
                        message=f"{tech} shows anomalous growth signals — potential breakout technology.",
                        severity="info",
                        data={"momentum_score": pred.momentum_score, "is_emerging": True},
                    ))

            # ── Milestone insights ──
            if repo and repo.stars >= 50000:
                insights.append(TrendInsight(
                    technology=tech,
                    category="milestone",
                    message=f"{tech} has surpassed {repo.stars:,} GitHub stars — major open-source project.",
                    severity="info",
                    data={"stars": repo.stars},
                ))

            # ── Community engagement ──
            if metric.discussion_velocity > 1.5:
                insights.append(TrendInsight(
                    technology=tech,
                    category="growth",
                    message=f"{tech} has high community discussion velocity ({metric.discussion_velocity:.1f}x) — strong engagement.",
                    severity="info",
                    data={"discussion_velocity": metric.discussion_velocity},
                ))

        # Sort: warnings first, then by technology
        severity_order = {"critical": 0, "warning": 1, "info": 2}
        insights.sort(key=lambda i: (severity_order.get(i.severity, 3), i.technology))

        logger.info("Generated %d trend insights", len(insights))
        return insights

    # ── Risk Detection ───────────────────────────────────────────

    def detect_risks(self) -> list[TrendInsight]:
        """
        Detect abandoned or declining repositories.
        Returns only warning/critical insights for at-risk technologies.
        """
        all_insights = self.generate_trend_insights()
        return [i for i in all_insights if i.severity in ("warning", "critical")]

    # ── Private helpers ──────────────────────────────────────────

    def _latest_repos(self) -> dict[str, Repository]:
        """Return latest Repository snapshot per technology."""
        subq = (
            self.db.query(
                Repository.technology,
                func.max(Repository.collected_at).label("max_at"),
            )
            .group_by(Repository.technology)
            .subquery()
        )
        rows = (
            self.db.query(Repository)
            .join(
                subq,
                (Repository.technology == subq.c.technology)
                & (Repository.collected_at == subq.c.max_at),
            )
            .all()
        )
        return {r.technology: r for r in rows}

    def _latest_metrics(self) -> dict[str, TechnologyMetrics]:
        """Return latest TechnologyMetrics per technology."""
        subq = (
            self.db.query(
                TechnologyMetrics.technology,
                func.max(TechnologyMetrics.last_updated).label("max_updated"),
            )
            .group_by(TechnologyMetrics.technology)
            .subquery()
        )
        rows = (
            self.db.query(TechnologyMetrics)
            .join(
                subq,
                (TechnologyMetrics.technology == subq.c.technology)
                & (TechnologyMetrics.last_updated == subq.c.max_updated),
            )
            .all()
        )
        return {r.technology: r for r in rows}

    def _latest_predictions(self) -> dict[str, TechnologyPrediction]:
        """Return latest TechnologyPrediction per technology."""
        subq = (
            self.db.query(
                TechnologyPrediction.technology,
                func.max(TechnologyPrediction.created_at).label("max_created"),
            )
            .group_by(TechnologyPrediction.technology)
            .subquery()
        )
        rows = (
            self.db.query(TechnologyPrediction)
            .join(
                subq,
                (TechnologyPrediction.technology == subq.c.technology)
                & (TechnologyPrediction.created_at == subq.c.max_created),
            )
            .all()
        )
        return {r.technology: r for r in rows}

    @staticmethod
    def _risk_level(score: int) -> str:
        if score >= 75:
            return "Low"
        if score >= 50:
            return "Medium"
        if score >= 25:
            return "High"
        return "Critical"

    @staticmethod
    def _health_insights(row: pd.Series, repo: Repository) -> list[str]:
        """Generate per-technology health insight strings."""
        insights: list[str] = []
        if row["maintainer_activity"] >= 20:
            insights.append("Active maintainers with consistent commits")
        elif row["maintainer_activity"] < 10:
            insights.append("Low maintainer activity — potential abandonment risk")

        if row["issue_resolution_speed"] >= 20:
            insights.append("Strong issue resolution pipeline")
        elif row["issue_resolution_speed"] < 8:
            insights.append("Issue backlog growing — slow resolution")

        if row["contributor_diversity"] >= 18:
            insights.append("Healthy contributor diversity")
        elif row["contributor_diversity"] < 8:
            insights.append("Limited contributor base — bus factor risk")

        if repo.stars > 10000:
            insights.append(f"Popular project with {repo.stars:,} stars")

        return insights
