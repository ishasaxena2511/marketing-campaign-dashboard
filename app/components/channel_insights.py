"""
Channel Insights & 3-Month Predictive Forecasting Component
Features:
1. Cross-Channel Efficiency Quadrant (Spend vs. ROAS vs. Conversions)
2. Channel Distribution Breakdown (Revenue vs. Spend share)
3. 3-Month Time-Series Forecast of Revenue and Media Spend using Holt's Exponential Smoothing
   with 95% Parametric Confidence Bands and safe linear fallback
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app.components.card import render_card_header
from app.theme import (
    ACCENT_GOLD,
    ACCENT_GOLD_LIGHT,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    get_plotly_layout,
    render_html,
)
from src.forecasting import generate_monthly_forecast
from src.metrics import (
    format_indian_currency,
    group_metrics,
)


def render_channel_insights(df: pd.DataFrame):
    """
    Renders cross-channel deep-dives and 3-month time-series forecasting.
    """
    if df is None or len(df) == 0:
        st.info("No records matching current filters.")
        return

    # Section 1: 3-Month Forecasting (Holt's Exponential Smoothing)
    with st.container(border=True):
        _render_time_series_forecast(df)

    # Section 2: Channel Efficiency Quadrant & Distribution
    col1, col2 = st.columns([1.2, 1.0])
    with col1, st.container(border=True):
        _render_efficiency_quadrant(df)
    with col2, st.container(border=True):
        _render_channel_share_breakdown(df)


@st.cache_data
def get_cached_forecast(data: pd.DataFrame, horizon: int = 3, confidence_level: float = 0.95):
    return generate_monthly_forecast(data, horizon=horizon, confidence_level=confidence_level)


def _render_time_series_forecast(df: pd.DataFrame):
    """
    Renders 3-month forecast of Revenue and Media Spend with confidence bands.
    """
    render_card_header("3-MONTH STATISTICAL REVENUE & SPEND FORECAST", badge="PROJECTION")

    fc_data = get_cached_forecast(df, horizon=3, confidence_level=0.95)
    if not fc_data or len(fc_data.get("historical_months", [])) == 0:
        st.info("Insufficient monthly history to generate predictive forecast.")
        return

    hist_m = fc_data["historical_months"]
    hist_r = fc_data["historical_revenue"]
    hist_s = fc_data["historical_spend"]

    fut_m = fc_data["forecast_months"]
    fut_r = fc_data["forecast_revenue"]
    fut_r_low = fc_data["forecast_revenue_lower"]
    fut_r_up = fc_data["forecast_revenue_upper"]
    fut_s = fc_data["forecast_spend"]
    fut_roi = fc_data["forecast_roi_pct"]

    # Connect historical to future seamlessly
    connect_m = [hist_m[-1]] + fut_m
    connect_r = [hist_r[-1]] + fut_r
    connect_r_low = [hist_r[-1]] + fut_r_low
    connect_r_up = [hist_r[-1]] + fut_r_up
    connect_s = [hist_s[-1]] + fut_s

    fig = go.Figure()

    # 1. Historical Media Spend (Solid Dark Line)
    fig.add_trace(
        go.Scatter(
            name="Historical Spend",
            x=hist_m,
            y=hist_s,
            mode="lines+markers",
            line=dict(color="#5C5E6B", width=2),
            marker=dict(size=4, color="#5C5E6B"),
            hovertemplate="<b>%{x}</b><br>Historical Spend: ₹%{y:,.0f}<extra></extra>",
        )
    )

    # 2. Historical Gross Revenue (Solid Gold Line)
    fig.add_trace(
        go.Scatter(
            name="Historical Revenue",
            x=hist_m,
            y=hist_r,
            mode="lines+markers",
            line=dict(color=ACCENT_GOLD, width=2.8),
            marker=dict(size=5, color=ACCENT_GOLD),
            hovertemplate="<b>%{x}</b><br>Historical Revenue: ₹%{y:,.0f}<extra></extra>",
        )
    )

    # 3. Confidence Band: Upper Bound (Invisible Line)
    fig.add_trace(
        go.Scatter(
            name="95% CI Upper",
            x=connect_m,
            y=connect_r_up,
            mode="lines",
            line=dict(width=0),
            showlegend=False,
            hoverinfo="skip",
        )
    )

    # 4. Confidence Band: Lower Bound (Filled to Upper Bound)
    fig.add_trace(
        go.Scatter(
            name="95% Confidence Band",
            x=connect_m,
            y=connect_r_low,
            mode="lines",
            line=dict(width=0),
            fill="tonexty",
            fillcolor="rgba(233, 169, 75, 0.15)",
            hoverinfo="skip",
        )
    )

    # 5. Projected Spend (Dashed Slate Line)
    fig.add_trace(
        go.Scatter(
            name="Projected Spend",
            x=connect_m,
            y=connect_s,
            mode="lines+markers",
            line=dict(color="#8E8F96", width=2, dash="dash"),
            marker=dict(size=6, color="#8E8F96", symbol="diamond"),
            hovertemplate="<b>%{x} (Projected)</b><br>Planned Spend: ₹%{y:,.0f}<extra></extra>",
        )
    )

    # 6. Projected Revenue (Dashed Gold Line with Diamonds)
    fig.add_trace(
        go.Scatter(
            name="Projected Revenue",
            x=connect_m,
            y=connect_r,
            mode="lines+markers",
            line=dict(color=ACCENT_GOLD_LIGHT, width=3, dash="dot"),
            marker=dict(size=7, color=ACCENT_GOLD_LIGHT, symbol="diamond"),
            customdata=list(zip([0.0] + fut_roi, [hist_r[-1]] + fut_r_low, [hist_r[-1]] + fut_r_up)),
            hovertemplate=(
                "<b>%{x} (PROJECTION)</b><br>"
                "Expected Revenue: <b>₹%{y:,.0f}</b><br>"
                "Projected ROI: <b>%{customdata[0]:+.1f}%</b><br>"
                "95% Confidence Interval: [₹%{customdata[1]:,.0f} &ndash; ₹%{customdata[2]:,.0f}]<extra></extra>"
            ),
        )
    )

    layout = get_plotly_layout(height=320, show_legend=True)
    layout["yaxis"]["tickprefix"] = "₹"
    layout["yaxis"]["title"] = "Financial Trajectory (₹)"
    layout["margin"] = dict(l=10, r=10, t=10, b=10)
    fig.update_layout(layout)

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # Summary Callout Cards for the 3 Forecast Months
    c1, c2, c3 = st.columns(3)
    cols = [c1, c2, c3]
    for idx, col in enumerate(cols):
        with col:
            m_label = fut_m[idx]
            exp_rev = fut_r[idx]
            exp_spend = fut_s[idx]
            exp_roi = fut_roi[idx]
            exp_profit = exp_rev - exp_spend
            render_html(f"""
            <div style="background: rgba(0, 0, 0, 0.22); border: 1px solid rgba(255, 255, 255, 0.06);
                        border-radius: 8px; padding: 0.5rem 0.75rem; text-align: center;">
                <div style="font-size: 0.68rem; color: #8E8F96; text-transform: uppercase;">Projection &bull; {m_label}</div>
                <div style="font-size: 1.05rem; font-weight: 700; color: #F3C477; font-family: 'Outfit', sans-serif;">{format_indian_currency(exp_rev)}</div>
                <div style="font-size: 0.72rem; color: #34D399; font-weight: 600; margin-top: 0.15rem;">
                    {exp_roi:+.1f}% ROI &bull; Net: {format_indian_currency(exp_profit)}
                </div>
            </div>
            """)


def _render_efficiency_quadrant(df: pd.DataFrame):
    """
    Renders Scatter bubble chart: Spend (X) vs. ROAS (Y) vs. Conversions (Size).
    """
    render_card_header("CHANNEL EFFICIENCY QUADRANT", badge="ROAS VS SCALE")

    plat_df = group_metrics(df, by="Platform", sort_by="Marketing Spend")

    max_c = plat_df["Conversions"].max()
    min_c = plat_df["Conversions"].min()
    sizes = [16 + 26 * ((c - min_c) / (max_c - min_c + 1e-6)) for c in plat_df["Conversions"]]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=plat_df["Marketing Spend"],
            y=plat_df["ROAS"],
            text=plat_df["Platform"],
            mode="markers+text",
            textposition="top center",
            textfont=dict(family="Outfit", size=10, color=TEXT_PRIMARY, weight="bold"),
            marker=dict(
                size=sizes,
                color=plat_df["ROI %"],
                colorscale=[
                    [0.0, "#4E3615"],
                    [0.4, "#8E6527"],
                    [0.75, "#E9A94B"],
                    [1.0, "#F3C477"],
                ],
                colorbar=dict(
                    title=dict(text="ROI %", font=dict(color=TEXT_SECONDARY, size=9, family="Outfit")),
                    ticksuffix="%",
                    len=0.8,
                    thickness=10,
                    outlinewidth=0,
                ),
                line=dict(color="rgba(255, 255, 255, 0.3)", width=1.5),
            ),
            customdata=plat_df[["Revenue Generated", "CAC", "Conversions"]].values,
            hovertemplate=(
                "<b>%{text}</b><br>"
                "Spend: ₹%{x:,.0f} | Revenue: ₹%{customdata[0]:,.0f}<br>"
                "ROAS: <b>%{y:.2f}x</b> (ROI: %{marker.color:+.1f}%)<br>"
                "CAC: ₹%{customdata[1]:,.1f} | Acquisitions: %{customdata[2]:,}<extra></extra>"
            ),
        )
    )

    layout = get_plotly_layout(height=260, show_legend=False)
    layout["xaxis"]["tickprefix"] = "₹"
    layout["xaxis"]["title"] = "Media Spend (₹)"
    layout["yaxis"]["ticksuffix"] = "x"
    layout["yaxis"]["title"] = "Return on Ad Spend (ROAS)"
    layout["margin"] = dict(l=10, r=10, t=10, b=10)
    fig.update_layout(layout)

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def _render_channel_share_breakdown(df: pd.DataFrame):
    """
    Renders Donut chart comparing capital deployment share across platforms.
    """
    render_card_header("MEDIA BUDGET DISTRIBUTION", badge="SHARE OF WALLET")

    plat_df = group_metrics(df, by="Platform", sort_by="Marketing Spend")

    fig = go.Figure(
        go.Pie(
            labels=plat_df["Platform"],
            values=plat_df["Marketing Spend"],
            hole=0.55,
            marker=dict(
                colors=[ACCENT_GOLD_LIGHT, ACCENT_GOLD, "#C88B35", "#8E6527", "#4A3B22", "#2B2418"],
                line=dict(color="#0E0E10", width=2),
            ),
            textinfo="label+percent",
            textfont=dict(family="Outfit", size=10, color=TEXT_PRIMARY),
            hovertemplate="<b>%{label}</b><br>Spend: ₹%{value:,.0f} (%{percent})<extra></extra>",
        )
    )

    layout = get_plotly_layout(height=260, show_legend=False)
    layout["margin"] = dict(l=10, r=10, t=10, b=10)
    fig.update_layout(layout)

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
