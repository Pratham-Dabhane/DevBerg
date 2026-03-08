"""Anomaly detection for identifying emerging technologies."""

import logging

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)


def detect_emerging_technologies(
    metrics_df: pd.DataFrame,
    contamination: float = 0.15,
) -> pd.DataFrame:
    """
    Detect technologies that are statistical outliers (emerging) based
    on their growth signals using Isolation Forest.

    Input columns expected:
        technology, stars_growth_rate, contributors_growth_rate,
        commit_activity_score, stackoverflow_growth, hn_mentions_growth,
        discussion_velocity, last_updated

    Returns DataFrame with columns:
        technology, is_emerging, anomaly_score
    """
    if metrics_df.empty:
        return pd.DataFrame(columns=["technology", "is_emerging", "anomaly_score"])

    df = metrics_df.copy()

    # Use latest snapshot per technology
    df = df.sort_values("last_updated", ascending=False).drop_duplicates(
        subset=["technology"], keep="first"
    )

    feature_cols = [
        "stars_growth_rate",
        "contributors_growth_rate",
        "commit_activity_score",
        "stackoverflow_growth",
        "hn_mentions_growth",
        "discussion_velocity",
    ]

    X = df[feature_cols].values

    # Need at least 3 samples for meaningful anomaly detection
    if len(X) < 3:
        logger.warning(
            "Only %d technologies — marking all with highest growth as emerging", len(X)
        )
        df["anomaly_score"] = df[feature_cols].mean(axis=1)
        threshold = df["anomaly_score"].quantile(0.7)
        df["is_emerging"] = df["anomaly_score"] > threshold
        return df[["technology", "is_emerging", "anomaly_score"]].reset_index(drop=True)

    # Standardize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Fit Isolation Forest
    clf = IsolationForest(
        contamination=contamination,
        random_state=42,
        n_estimators=100,
    )
    clf.fit(X_scaled)

    # Anomaly scores: more negative = more anomalous
    raw_scores = clf.decision_function(X_scaled)
    predictions = clf.predict(X_scaled)

    # Invert score: higher = more anomalous / emerging
    df["anomaly_score"] = -raw_scores

    # Only flag as emerging if it's an outlier AND has positive growth signals
    growth_signal = df[feature_cols].mean(axis=1)
    df["is_emerging"] = (predictions == -1) & (growth_signal > growth_signal.median())

    result = df[["technology", "is_emerging", "anomaly_score"]].reset_index(drop=True)

    emerging = result[result["is_emerging"]]["technology"].tolist()
    logger.info(
        "Anomaly detection complete: %d emerging technologies detected: %s",
        len(emerging),
        emerging,
    )
    return result
