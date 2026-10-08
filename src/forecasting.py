"""
Time-Series Forecasting Engine for Marketing Performance
Provides 3-month forecasting for Revenue and Marketing Spend using:
- statsmodels Holt's Exponential Smoothing (with additive trend and damping)
- Robust fallback to linear/exponential moving growth if sample size is small (< 4 months)
- Parametric prediction intervals (80% and 95% confidence bands)
"""

from typing import Any

import numpy as np
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing

from src.metrics import group_metrics, safe_divide


def generate_monthly_forecast(
    df: pd.DataFrame,
    horizon: int = 3,
    confidence_level: float = 0.95,
) -> dict[str, Any]:
    """
    Generate a statistical forecast of Revenue Generated and Marketing Spend
    for the next `horizon` months with confidence intervals.

    Returns:
        dict containing:
        - 'historical_months': list of month strings (e.g. ['Jan 2025', ...])
        - 'historical_dates': list of pd.Timestamp
        - 'historical_revenue': list of floats
        - 'historical_spend': list of floats
        - 'forecast_months': list of month strings (e.g. ['Sep 2026', ...])
        - 'forecast_dates': list of pd.Timestamp
        - 'forecast_revenue': list of floats
        - 'forecast_revenue_lower': list of floats (confidence interval)
        - 'forecast_revenue_upper': list of floats (confidence interval)
        - 'forecast_spend': list of floats
        - 'forecast_roi_pct': list of floats
        - 'model_type': string description of method used
    """
    if df is None or len(df) == 0:
        return {}

    # Aggregate monthly metrics chronologically
    monthly = group_metrics(df, by="Month", sort_by="Marketing Spend")
    monthly["_dt"] = pd.to_datetime(monthly["Month"], format="%b %Y")
    monthly = monthly.sort_values(by="_dt").reset_index(drop=True)

    n_points = len(monthly)
    if n_points == 0:
        return {}

    hist_months = monthly["Month"].tolist()
    hist_dates = monthly["_dt"].tolist()
    hist_rev = monthly["Revenue Generated"].astype(float).tolist()
    hist_spend = monthly["Marketing Spend"].astype(float).tolist()

    # Generate future dates
    last_date = hist_dates[-1]
    future_dates = [last_date + pd.DateOffset(months=i) for i in range(1, horizon + 1)]
    future_months = [d.strftime("%b %Y") for d in future_dates]

    # Z-multiplier for confidence interval (1.96 for 95%, 1.28 for 80%)
    z_score = 1.96 if confidence_level >= 0.90 else 1.28

    model_type = "Holt's Damped Trend Exponential Smoothing"

    # Forecasting Revenue
    rev_forecast, rev_lower, rev_upper = _fit_and_forecast_series(
        series=np.array(hist_rev),
        horizon=horizon,
        z_score=z_score,
    )

    # Forecasting Spend
    spend_forecast, _, _ = _fit_and_forecast_series(
        series=np.array(hist_spend),
        horizon=horizon,
        z_score=z_score,
    )

    # Derived Projected ROI % for each forecast month
    forecast_roi = []
    for r, s in zip(rev_forecast, spend_forecast):
        roi = round(safe_divide(r - s, s) * 100, 2)
        forecast_roi.append(roi)

    return {
        "historical_months": hist_months,
        "historical_dates": hist_dates,
        "historical_revenue": hist_rev,
        "historical_spend": hist_spend,
        "forecast_months": future_months,
        "forecast_dates": future_dates,
        "forecast_revenue": rev_forecast.tolist(),
        "forecast_revenue_lower": rev_lower.tolist(),
        "forecast_revenue_upper": rev_upper.tolist(),
        "forecast_spend": spend_forecast.tolist(),
        "forecast_roi_pct": forecast_roi,
        "model_type": model_type,
    }


def _fit_and_forecast_series(
    series: np.ndarray,
    horizon: int = 3,
    z_score: float = 1.96,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Fits Exponential Smoothing if sufficient data points exist (>= 4),
    otherwise applies linear regression slope with floor guard.
    """
    n = len(series)

    if n >= 4:
        try:
            # Holt's Linear Exponential Smoothing with damped trend
            model = ExponentialSmoothing(
                series,
                trend="add",
                damped_trend=True,
                seasonal=None,
                initialization_method="estimated",
            ).fit(damping_slope=0.88, optimized=True)

            forecast = np.maximum(0, model.forecast(horizon))
            residuals = model.fittedvalues - series
            sigma = float(np.std(residuals)) if len(residuals) > 0 else float(np.std(series) * 0.2)
        except Exception:
            # Fallback to linear regression
            forecast, sigma = _linear_trend_fallback(series, horizon)
    else:
        forecast, sigma = _linear_trend_fallback(series, horizon)

    # Expand confidence intervals over the forecast horizon (expanding variance sqrt(h))
    step_scales = np.sqrt(np.arange(1, horizon + 1))
    lower = np.maximum(0, forecast - z_score * sigma * step_scales)
    upper = forecast + z_score * sigma * step_scales

    return forecast, lower, upper


def _linear_trend_fallback(series: np.ndarray, horizon: int) -> tuple[np.ndarray, float]:
    """Fallback linear trend estimation when time series is short or non-convergent."""
    n = len(series)
    if n <= 1:
        base_val = series[0] if n == 1 else 100000.0
        return np.array([base_val] * horizon), base_val * 0.15

    x = np.arange(n)
    slope, intercept = np.polyfit(x, series, 1)

    future_x = np.arange(n, n + horizon)
    forecast = np.maximum(0, slope * future_x + intercept)

    # In case slope is aggressively negative, ensure reasonable floor
    last_val = series[-1]
    forecast = np.maximum(last_val * 0.5, forecast)

    residuals = series - (slope * x + intercept)
    sigma = float(np.std(residuals)) if len(residuals) > 0 else float(np.std(series) * 0.2)

    return forecast, sigma
