"""Technology Investment Predictor.

Multi-horizon growth forecasting (3 / 6 / 12 months) using an ensemble of:
    - Prophet  (when ≥5 data points)
    - ARIMA    (statsmodels, when ≥8 data points)
    - XGBoost regression (feature-based, always available)
    - Linear regression fallback

The final predicted_growth_pct is the confidence-weighted average of whichever
models produced a result.  Results are persisted in ``technology_forecasts``.
"""

import logging
from datetime import datetime, timezone
from typing import NamedTuple

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.models import Repository, StackOverflowStats, TechMention, TechnologyForecast

logger = logging.getLogger(__name__)

HORIZONS = [3, 6, 12]  # months


class _SingleForecast(NamedTuple):
    predicted_growth_pct: float
    confidence: float
    model_name: str


# ── Individual model helpers ──────────────────────────────────────

def _forecast_prophet(ts: pd.DataFrame, horizon_days: int) -> _SingleForecast | None:
    try:
        from prophet import Prophet
    except ImportError:
        return None
    if len(ts) < 5:
        return None
    try:
        m = Prophet(yearly_seasonality=False, weekly_seasonality=False,
                    daily_seasonality=False, changepoint_prior_scale=0.5)
        m.fit(ts[["ds", "y"]])
        future = m.make_future_dataframe(periods=horizon_days, freq="D")
        fc = m.predict(future)
        predicted = float(fc["yhat"].iloc[-1])
        current = float(ts["y"].iloc[-1])
        growth_pct = ((predicted - current) / max(abs(current), 1e-9)) * 100
        interval = float(fc["yhat_upper"].iloc[-1] - fc["yhat_lower"].iloc[-1])
        conf = max(0.0, min(1.0, 1.0 - interval / (abs(predicted) + 1)))
        return _SingleForecast(round(growth_pct, 2), round(conf, 4), "prophet")
    except Exception as e:
        logger.debug("Prophet failed: %s", e)
        return None


def _forecast_arima(ts: pd.DataFrame, horizon_days: int) -> _SingleForecast | None:
    try:
        from statsmodels.tsa.arima.model import ARIMA
    except ImportError:
        return None
    if len(ts) < 8:
        return None
    try:
        y = ts.set_index("ds")["y"].asfreq("D", method="ffill")
        model = ARIMA(y, order=(1, 1, 1))
        fit = model.fit()
        fc = fit.forecast(steps=horizon_days)
        predicted = float(fc.iloc[-1])
        current = float(y.iloc[-1])
        growth_pct = ((predicted - current) / max(abs(current), 1e-9)) * 100
        aic = fit.aic
        conf = max(0.0, min(1.0, 1.0 / (1.0 + abs(aic) / 1000)))
        return _SingleForecast(round(growth_pct, 2), round(conf, 4), "arima")
    except Exception as e:
        logger.debug("ARIMA failed: %s", e)
        return None


def _forecast_xgboost(ts: pd.DataFrame, horizon_days: int) -> _SingleForecast | None:
    try:
        from xgboost import XGBRegressor
    except ImportError:
        return None
    if len(ts) < 3:
        return None
    try:
        df = ts.copy().sort_values("ds")
        df["day_num"] = (df["ds"] - df["ds"].min()).dt.days.astype(float)
        df["lag1"] = df["y"].shift(1).fillna(method="bfill")
        df["rolling_mean"] = df["y"].rolling(min(3, len(df)), min_periods=1).mean()

        features = ["day_num", "lag1", "rolling_mean"]
        X = df[features].values
        y = df["y"].values

        model = XGBRegressor(n_estimators=50, max_depth=3, verbosity=0)
        model.fit(X, y)

        last_day = float(df["day_num"].iloc[-1])
        future_day = last_day + horizon_days
        last_y = float(y[-1])
        last_rm = float(df["rolling_mean"].iloc[-1])
        pred = float(model.predict(np.array([[future_day, last_y, last_rm]]))[0])

        growth_pct = ((pred - last_y) / max(abs(last_y), 1e-9)) * 100
        # Confidence from train R²
        train_pred = model.predict(X)
        ss_res = np.sum((y - train_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r2 = 1 - ss_res / max(ss_tot, 1e-9)
        conf = max(0.0, min(1.0, r2))
        return _SingleForecast(round(growth_pct, 2), round(conf, 4), "xgboost")
    except Exception as e:
        logger.debug("XGBoost failed: %s", e)
        return None


def _forecast_linear(ts: pd.DataFrame, horizon_days: int) -> _SingleForecast:
    df = ts.copy().sort_values("ds")
    if len(df) < 2:
        return _SingleForecast(0.0, 0.1, "linear")
    df["day_num"] = (df["ds"] - df["ds"].min()).dt.days.astype(float)
    X = df["day_num"].values.reshape(-1, 1)
    y = df["y"].values
    model = LinearRegression().fit(X, y)
    last_day = float(X[-1][0])
    pred = float(model.predict([[last_day + horizon_days]])[0])
    current = float(y[-1])
    growth_pct = ((pred - current) / max(abs(current), 1e-9)) * 100
    r2 = max(0.0, min(1.0, model.score(X, y)))
    return _SingleForecast(round(growth_pct, 2), round(r2, 4), "linear")


def _ensemble(forecasts: list[_SingleForecast]) -> tuple[float, float, str]:
    """Confidence-weighted average of individual forecasts."""
    if not forecasts:
        return 0.0, 0.0, "stable"
    total_conf = sum(f.confidence for f in forecasts)
    if total_conf == 0:
        avg = sum(f.predicted_growth_pct for f in forecasts) / len(forecasts)
        best_model = forecasts[0].model_name
    else:
        avg = sum(f.predicted_growth_pct * f.confidence for f in forecasts) / total_conf
        best_model = max(forecasts, key=lambda f: f.confidence).model_name
    avg_conf = total_conf / len(forecasts)
    direction = "up" if avg > 5 else ("down" if avg < -5 else "stable")
    return round(avg, 2), round(avg_conf, 4), best_model if direction != "stable" else best_model


# ── Main class ────────────────────────────────────────────────────

class InvestmentForecaster:
    """Predicts technology growth across multiple horizons."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def _build_time_series(self, technology: str) -> pd.DataFrame:
        """Build a time-series DataFrame (ds, y) from collected signals."""
        # Combine stars over time from Repository snapshots
        repos = (
            self.db.query(Repository)
            .filter(Repository.technology == technology)
            .order_by(Repository.collected_at)
            .all()
        )
        records: list[dict] = []
        for r in repos:
            records.append({"ds": r.collected_at, "y": float(r.stars)})

        if not records:
            return pd.DataFrame(columns=["ds", "y"])

        df = pd.DataFrame(records)
        df["ds"] = pd.to_datetime(df["ds"], utc=True).dt.tz_localize(None)
        return df.sort_values("ds").reset_index(drop=True)

    def forecast_technology(self, technology: str) -> list[dict]:
        """Forecast growth for a single technology across all horizons."""
        ts = self._build_time_series(technology)
        results: list[dict] = []

        for months in HORIZONS:
            horizon_days = months * 30

            forecasts: list[_SingleForecast] = []

            # Try each model
            prophet_fc = _forecast_prophet(ts, horizon_days)
            if prophet_fc:
                forecasts.append(prophet_fc)

            arima_fc = _forecast_arima(ts, horizon_days)
            if arima_fc:
                forecasts.append(arima_fc)

            xgb_fc = _forecast_xgboost(ts, horizon_days)
            if xgb_fc:
                forecasts.append(xgb_fc)

            linear_fc = _forecast_linear(ts, horizon_days)
            forecasts.append(linear_fc)

            growth_pct, confidence, model_used = _ensemble(forecasts)
            direction = "up" if growth_pct > 5 else ("down" if growth_pct < -5 else "stable")

            results.append(
                {
                    "technology": technology,
                    "horizon_months": months,
                    "predicted_growth_pct": growth_pct,
                    "model_used": model_used,
                    "confidence_score": confidence,
                    "trend_direction": direction,
                }
            )
        return results

    def run(self) -> list[TechnologyForecast]:
        """Run forecasts for all tracked technologies and persist results."""
        from app.config import get_settings

        settings = get_settings()
        techs = [t["name"] for t in settings.tracked_technologies]

        now = datetime.now(timezone.utc)
        orm_objects: list[TechnologyForecast] = []

        for tech in techs:
            forecasts = self.forecast_technology(tech)
            for fc in forecasts:
                obj = TechnologyForecast(
                    technology=fc["technology"],
                    horizon_months=fc["horizon_months"],
                    predicted_growth_pct=fc["predicted_growth_pct"],
                    model_used=fc["model_used"],
                    confidence_score=fc["confidence_score"],
                    trend_direction=fc["trend_direction"],
                    created_at=now,
                )
                self.db.add(obj)
                orm_objects.append(obj)

        self.db.commit()
        for obj in orm_objects:
            self.db.refresh(obj)

        logger.info("Persisted %d forecasts across %d technologies.", len(orm_objects), len(techs))
        return orm_objects
