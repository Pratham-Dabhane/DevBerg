"""Weighted momentum scoring for technology trend signals."""

import logging

import pandas as pd

logger = logging.getLogger(__name__)

# Configurable weights for the momentum formula
WEIGHTS = {
    "github_growth": 0.4,
    "contributor_growth": 0.3,
    "community_discussions": 0.2,
    "issue_activity": 0.1,
}


def _normalize_series(series: pd.Series) -> pd.Series:
    """Min-max normalize to [0, 1]."""
    min_val = series.min()
    max_val = series.max()
    if max_val == min_val:
        return pd.Series(0.5, index=series.index)
    return (series - min_val) / (max_val - min_val)


def compute_momentum_scores(metrics_df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute a weighted momentum score per technology from metrics history.

    Input columns expected:
        technology, stars_growth_rate, contributors_growth_rate,
        stackoverflow_growth, hn_mentions_growth, discussion_velocity,
        commit_activity_score, issue_resolution_rate, last_updated

    Returns DataFrame with columns:
        technology, momentum_score, github_growth_n, contributor_growth_n,
        community_discussions_n, issue_activity_n
    """
    if metrics_df.empty:
        return pd.DataFrame(
            columns=[
                "technology",
                "momentum_score",
                "github_growth_n",
                "contributor_growth_n",
                "community_discussions_n",
                "issue_activity_n",
            ]
        )

    df = metrics_df.copy()

    # Use the latest record per technology
    df = df.sort_values("last_updated", ascending=False).drop_duplicates(
        subset=["technology"], keep="first"
    )

    # Build raw feature columns
    # github_growth: stars growth + commit activity (blended)
    df["github_growth_raw"] = (
        df["stars_growth_rate"] * 0.6 + df["commit_activity_score"] * 0.4
    )
    # contributor_growth: direct
    df["contributor_growth_raw"] = df["contributors_growth_rate"]
    # community_discussions: SO + HN signals combined
    df["community_discussions_raw"] = (
        df["stackoverflow_growth"] * 0.4
        + df["hn_mentions_growth"] * 0.3
        + df["discussion_velocity"] * 0.3
    )
    # issue_activity: resolution rate as proxy
    df["issue_activity_raw"] = df["issue_resolution_rate"]

    # Normalize each feature across technologies
    df["github_growth_n"] = _normalize_series(df["github_growth_raw"])
    df["contributor_growth_n"] = _normalize_series(df["contributor_growth_raw"])
    df["community_discussions_n"] = _normalize_series(df["community_discussions_raw"])
    df["issue_activity_n"] = _normalize_series(df["issue_activity_raw"])

    # Weighted momentum score
    df["momentum_score"] = (
        WEIGHTS["github_growth"] * df["github_growth_n"]
        + WEIGHTS["contributor_growth"] * df["contributor_growth_n"]
        + WEIGHTS["community_discussions"] * df["community_discussions_n"]
        + WEIGHTS["issue_activity"] * df["issue_activity_n"]
    )

    result = df[
        [
            "technology",
            "momentum_score",
            "github_growth_n",
            "contributor_growth_n",
            "community_discussions_n",
            "issue_activity_n",
        ]
    ].reset_index(drop=True)

    logger.info("Momentum scores computed for %d technologies", len(result))
    return result
