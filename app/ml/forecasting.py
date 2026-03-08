"""Time-series forecasting for technology growth prediction.

Uses Prophet when sufficient data points exist (≥3 snapshots),
falls back to linear regression for sparse data.
"""

import logging
from typing import NamedTuple

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

logger = logging.getLogger(__name__)

FORECAST_MONTHS = 6


class ForecastResult(NamedTuple):
    technology: str
    predicted_growth: float  # predicted momentum 6 months ahead
    confidence_score: float  # 0-1 confidence in the prediction
    trend_direction: str     # "up" / "down" / "stable"


def _classify_trend(current: float, predicted: float, threshold: float = 0.05) -> str:
    """Classify trend direction based on predicted vs. current momentum."""
    delta = predicted - current
    if delta > threshold:
        return "up"
    elif delta < -threshold:
        return "down"
    return "stable"


def _forecast_with_prophet(
    ts_df: pd.DataFrame, technology: str
) -> ForecastResult | None:
    """Forecast using Prophet. Returns None if Prophet is unavailable or fails."""
    try:
        from prophet import Prophet
    except ImportError:
        logger.debug("Prophet not installed — skipping Prophet forecast for %s", technology)
        return None

    if len(ts_df) < 3:
        return None

    # Prophet requires columns 'ds' and 'y'
    prophet_df = ts_df.rename(columns={"ds": "ds", "y": "y"})[["ds", "y"]].copy()
    prophet_df["ds"] = pd.to_datetime(prophet_df["ds"])

    try:
        model = Prophet(
            yearly_seasonality=False,
            weekly_seasonality=False,
            daily_seasonality=False,
            changepoint_prior_scale=0.5,
        )
        model.fit(prophet_df)

        future = model.make_future_dataframe(periods=FORECAST_MONTHS * 30, freq="D")
        forecast = model.predict(future)

        # Get the predicted value at the forecast horizon
        predicted = forecast["yhat"].iloc[-1]
        lower = forecast["yhat_lower"].iloc[-1]
        upper = forecast["yhat_upper"].iloc[-1]

        # Confidence based on prediction interval width relative to predicted value
        interval_width = upper - lower
        if abs(predicted) > 0:
            confidence = max(0.0, min(1.0, 1.0 - (interval_width / (abs(predicted) + 1))))
        else:
            confidence = 0.3

        current = prophet_df["y"].iloc[-1]
        direction = _classify_trend(current, predicted)

        return ForecastResult(
            technology=technology,
            predicted_growth=round(float(predicted), 4),
            confidence_score=round(float(confidence), 4),
            trend_direction=direction,
        )
    except Exception as e:
        logger.warning("Prophet forecast failed for %s: %s", technology, e)
        return None


def _forecast_with_linear(ts_df: pd.DataFrame, technology: str) -> ForecastResult:
    """Fallback: linear regression forecast when data is sparse."""
    df = ts_df.copy().sort_values("ds")

    if len(df) < 2:
        # Single data point — no trend determinable
        current_val = df["y"].iloc[0] if not df.empty else 0.0
        return ForecastResult(
            technology=technology,
            predicted_growth=round(float(current_val), 4),
            confidence_score=0.2,
            trend_direction="stable",
        )

    # Convert dates to numeric (days since first observation)
    df["ds_numeric"] = (pd.to_datetime(df["ds"]) - pd.to_datetime(df["ds"]).min()).dt.days
    X = df["ds_numeric"].values.reshape(-1, 1)
    y = df["y"].values

    model = LinearRegression()
    model.fit(X, y)

    # Predict 6 months ahead
    last_day = df["ds_numeric"].max()
    future_day = last_day + FORECAST_MONTHS * 30
    predicted = float(model.predict([[future_day]])[0])

    # Confidence from R² score
    r2 = model.score(X, y)
    confidence = max(0.0, min(1.0, r2))

    current = float(y[-1])
    direction = _classify_trend(current, predicted)

    return ForecastResult(
        technology=technology,
        predicted_growth=round(predicted, 4),
        confidence_score=round(confidence, 4),
        trend_direction=direction,
    )


def forecast_technology_growth(
    metrics_df: pd.DataFrame,
) -> list[ForecastResult]:
    """
    Forecast growth for each technology using time-series data.

    Input columns expected:
        technology, momentum_score (or a y-value proxy), last_updated

    Tries Prophet first, falls back to linear regression.

    Returns list of ForecastResult.
    """
    if metrics_df.empty:
        return []

    df = metrics_df.copy()
    df["ds"] = pd.to_datetime(df["last_updated"])
    df["y"] = df["momentum_score"]

    results: list[ForecastResult] = []

    for technology, group in df.groupby("technology"):
        ts = group[["ds", "y"]].sort_values("ds").reset_index(drop=True)

        # Try Prophet first
        result = _forecast_with_prophet(ts, str(technology))

        # Fallback to linear
        if result is None:
            result = _forecast_with_linear(ts, str(technology))

        results.append(result)
        logger.info(
            "Forecast for %s: growth=%.4f, confidence=%.4f, trend=%s",
            result.technology,
            result.predicted_growth,
            result.confidence_score,
            result.trend_direction,
        )

    return results
