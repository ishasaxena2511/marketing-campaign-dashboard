"""
Performance Analytics Component Suite
Renders the 5 middle-tier charts with Plotly using the dark-gold executive theme:
1. Campaign ROI Analysis: Horizontal capsule bars for Top 10 / Bottom 10 with minimum spend qualification
2. Revenue by Campaign: Bar chart of top 10 revenue drivers
3. Platform Performance Comparison: Grouped Spend vs. Revenue bars + Multi-channel efficiency heatmap matrix
4. Conversion Funnel: 4-stage funnel with exact stage-to-stage transition & drop-off % labels
5. Marketing Spend vs Revenue: Dual-axis monthly trajectory (Spend bars + Gold revenue area line with ROI hover)
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app.components.card import render_card_header
from app.theme import (
    ACCENT_GOLD,
    ACCENT_GOLD_LIGHT,
    STATUS_SUCCESS,
    TEXT_PRIMARY,
    get_plotly_layout,
    render_html,
)
from src.metrics import (
    format_indian_currency,
    funnel_data,
    get_bottom_campaigns,
    get_top_campaigns,
    group_metrics,
)


def render_campaign_roi_analysis(df: pd.DataFrame):
    """
    1. Campaign ROI Analysis: Horizontal capsule bars of Top 10 or Bottom 10
    campaigns by ROI with minimum spend filter and rich hover tooltips.
    """
    render_card_header("CAMPAIGN ROI ANALYSIS", badge="LEADERBOARD")

    col_toggle, col_min_spend = st.columns([1.2, 1.0])
    with col_toggle:
        roi_view = st.radio(
            "ROI Direction",
            options=["Top 10 Performers", "Bottom 10 Performers"],
            horizontal=True,
            label_visibility="collapsed",
            key="roi_rank_toggle",
        )
    with col_min_spend:
        min_spend_thresh = st.select_slider(
            "Min Spend Qualification",
            options=[0, 10000, 25000, 50000, 100000],
            value=25000,
            format_func=lambda x: f"Min ₹{x / 1000:.0f}k" if x > 0 else "All Spends",
            label_visibility="collapsed",
            key="roi_min_spend_slider",
        )

    is_top = roi_view == "Top 10 Performers"
    if is_top:
        ranked_df = get_top_campaigns(df, metric="ROI %", n=10, min_spend=float(min_spend_thresh))
        bar_color = ACCENT_GOLD
        border_color = ACCENT_GOLD_LIGHT
    else:
        ranked_df = get_bottom_campaigns(df, metric="ROI %", n=10, min_spend=float(min_spend_thresh))
        bar_color = "#D65C5C"
        border_color = "#E07A7A"

    if len(ranked_df) == 0:
        st.info("No campaigns qualify under the current minimum spend threshold.")
        return

    # Sort ascending for horizontal bar chart display so #1 is at the top
    ranked_display = ranked_df.sort_values(by="ROI %", ascending=True).copy()

    # Create label: Name or ID
    ranked_display["Display_Label"] = ranked_display.apply(
        lambda r: f"{r['Campaign ID']} ({r['Platform'][:4]})", axis=1
    )

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            y=ranked_display["Display_Label"],
            x=ranked_display["ROI %"],
            orientation="h",
            marker=dict(
                color=bar_color,
                line=dict(color=border_color, width=1),
            ),
            text=[f"{val:+.1f}%" for val in ranked_display["ROI %"]],
            textposition="inside" if is_top else "outside",
            insidetextanchor="end",
            textfont=dict(color="#0E0E10" if is_top else TEXT_PRIMARY, family="Outfit", size=10, weight="bold"),
            customdata=ranked_display[
                ["Campaign ID", "Campaign Name", "Platform", "Marketing Spend", "Revenue Generated", "ROAS", "CAC"]
            ].values,
            hovertemplate=(
                "<b>%{customdata[0]}</b> - %{customdata[1]}<br>"
                "Platform: <b>%{customdata[2]}</b><br>"
                "ROI: <b>%{x:+.2f}%</b> (ROAS: %{customdata[5]:.2f}x)<br>"
                "Spend: ₹%{customdata[3]:,.0f} | Revenue: ₹%{customdata[4]:,.0f}<br>"
                "Acquisition CAC: ₹%{customdata[6]:,.2f}<extra></extra>"
            ),
        )
    )

    layout = get_plotly_layout(height=340, show_legend=False)
    layout["xaxis"]["ticksuffix"] = "%"
    layout["xaxis"]["title"] = "Return on Investment (ROI %)"
    layout["margin"] = dict(l=10, r=16, t=10, b=24)
    fig.update_layout(layout)

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def render_revenue_by_campaign(df: pd.DataFrame):
    """
    2. Revenue by Campaign: Bar chart of top 10 revenue drivers.
    """
    render_card_header("TOP 10 REVENUE DRIVERS", badge="SCALE LEADERS")

    if len(df) == 0:
        st.info("No campaign records.")
        return

    top_rev = get_top_campaigns(df, metric="Revenue Generated", n=10, min_spend=0.0)
    if len(top_rev) == 0:
        st.info("No campaign records.")
        return
    top_rev = top_rev.sort_values(by="Revenue Generated", ascending=True).copy()
    top_rev["Display_Label"] = top_rev.apply(lambda r: f"{r['Campaign ID']} ({r['Platform'][:3]})", axis=1)

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            y=top_rev["Display_Label"],
            x=top_rev["Revenue Generated"],
            orientation="h",
            marker=dict(
                color=ACCENT_GOLD_LIGHT,
                line=dict(color=ACCENT_GOLD, width=1),
            ),
            text=[
                f"₹{val / 100000:.1f}L" if val >= 100000 else f"₹{val / 1000:.0f}k"
                for val in top_rev["Revenue Generated"]
            ],
            textposition="inside",
            insidetextanchor="end",
            textfont=dict(color="#0E0E10", family="Outfit", size=10, weight="bold"),
            customdata=top_rev[
                ["Campaign ID", "Campaign Name", "Platform", "Marketing Spend", "ROI %", "Conversions"]
            ].values,
            hovertemplate=(
                "<b>%{customdata[0]}</b> - %{customdata[1]}<br>"
                "Platform: <b>%{customdata[2]}</b><br>"
                "Gross Revenue: <b>₹%{x:,.0f}</b><br>"
                "Spend: ₹%{customdata[3]:,.0f} | ROI: %{customdata[4]:+.1f}%<br>"
                "Conversions: %{customdata[5]:,}<extra></extra>"
            ),
        )
    )

    layout = get_plotly_layout(height=340, show_legend=False)
    layout["xaxis"]["tickprefix"] = "₹"
    layout["xaxis"]["title"] = "Gross Revenue Generated"
    layout["margin"] = dict(l=10, r=16, t=10, b=24)
    fig.update_layout(layout)

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def render_platform_performance(df: pd.DataFrame):
    """
    3. Platform Performance Comparison: Grouped bars for spend vs revenue by platform,
    plus a small table/heatmap row showing ROI, CTR, conversion rate, CAC per platform.
    """
    render_card_header("PLATFORM PERFORMANCE COMPARISON", badge="CROSS-CHANNEL")

    if len(df) == 0:
        st.info("No records matching current filters.")
        return

    plat_df = group_metrics(df, by="Platform", sort_by="Marketing Spend", ascending=False)

    fig = go.Figure()
    # Spend Bars (Muted Charcoal with Subtle Border)
    fig.add_trace(
        go.Bar(
            name="Media Spend",
            x=plat_df["Platform"],
            y=plat_df["Marketing Spend"],
            marker=dict(
                color="#3D3E46",
                line=dict(color="rgba(255, 255, 255, 0.15)", width=1),
            ),
            customdata=plat_df[["ROI %", "ROAS", "CPC"]].values,
            hovertemplate=(
                "<b>%{x}</b> - Media Spend<br>Spend: <b>₹%{y:,.0f}</b><br>CPC: ₹%{customdata[2]:.2f}<extra></extra>"
            ),
        )
    )

    # Revenue Bars (Vibrant Gold)
    fig.add_trace(
        go.Bar(
            name="Gross Revenue",
            x=plat_df["Platform"],
            y=plat_df["Revenue Generated"],
            marker=dict(
                color=ACCENT_GOLD,
                line=dict(color=ACCENT_GOLD_LIGHT, width=1),
            ),
            customdata=plat_df[["ROI %", "ROAS", "CAC"]].values,
            hovertemplate=(
                "<b>%{x}</b> - Gross Revenue<br>"
                "Revenue: <b>₹%{y:,.0f}</b><br>"
                "ROI: <b>%{customdata[0]:+.1f}%</b> (ROAS: %{customdata[1]:.2f}x)<br>"
                "CAC: ₹%{customdata[2]:,.1f}<extra></extra>"
            ),
        )
    )

    layout = get_plotly_layout(height=265, show_legend=True)
    layout["yaxis"]["tickprefix"] = "₹"
    layout["barmode"] = "group"
    layout["margin"] = dict(l=10, r=10, t=16, b=10)
    fig.update_layout(layout)

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # Small Matrix Table Row showing ROI, CTR, Conv Rate, CAC per platform
    render_html("""
    <div style="font-family: 'Outfit', sans-serif; font-size: 0.72rem; color: #8E8F96;
                text-transform: uppercase; letter-spacing: 0.08em; margin: 0.6rem 0 0.35rem 0;">
        Channel Efficiency Matrix
    </div>
    """)

    table_rows = []
    for _, r in plat_df.iterrows():
        roi_color = STATUS_SUCCESS if r["ROI %"] >= 60 else (ACCENT_GOLD if r["ROI %"] >= 25 else "#E05353")
        table_rows.append(f"""
        <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.05); font-size: 0.76rem;">
            <td style="padding: 0.35rem 0.4rem; font-weight: 600; color: #F5F5F7;">{r["Platform"]}</td>
            <td style="padding: 0.35rem 0.4rem; color: #8E8F96;">{format_indian_currency(r["Marketing Spend"])}</td>
            <td style="padding: 0.35rem 0.4rem; color: #F5F5F7;">{format_indian_currency(r["Revenue Generated"])}</td>
            <td style="padding: 0.35rem 0.4rem; font-weight: 700; color: {roi_color};">{r["ROI %"]:+.1f}%</td>
            <td style="padding: 0.35rem 0.4rem; color: #E9A94B;">{r["CTR %"]:.2f}%</td>
            <td style="padding: 0.35rem 0.4rem; color: #8E8F96;">{r["Conversion Rate %"]:.1f}%</td>
            <td style="padding: 0.35rem 0.4rem; color: #F5F5F7; font-weight: 600;">₹{r["CAC"]:,.0f}</td>
        </tr>
        """)

    matrix_html = f"""
    <div style="overflow-x: auto; background: rgba(0, 0, 0, 0.20); border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.05); padding: 0.4rem 0.6rem;">
        <table style="width: 100%; text-align: left; border-collapse: collapse;">
            <thead>
                <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.08); font-size: 0.68rem; color: #8E8F96; text-transform: uppercase;">
                    <th style="padding: 0.3rem 0.4rem;">Channel</th>
                    <th style="padding: 0.3rem 0.4rem;">Spend</th>
                    <th style="padding: 0.3rem 0.4rem;">Revenue</th>
                    <th style="padding: 0.3rem 0.4rem;">ROI %</th>
                    <th style="padding: 0.3rem 0.4rem;">CTR %</th>
                    <th style="padding: 0.3rem 0.4rem;">Conv %</th>
                    <th style="padding: 0.3rem 0.4rem;">CAC</th>
                </tr>
            </thead>
            <tbody>
                {"".join(table_rows)}
            </tbody>
        </table>
    </div>
    """
    render_html(matrix_html)


def render_conversion_funnel(df: pd.DataFrame):
    """
    4. Conversion Funnel: Impressions to Clicks to Leads to Conversions funnel chart
    with drop-off % labels and throughput analytics.
    """
    render_card_header("CONVERSION FUNNEL EFFICIENCY", badge="DROP-OFF")

    if len(df) == 0:
        st.info("No funnel records.")
        return

    f_data = funnel_data(df)
    stages = f_data["Stage"].tolist()
    counts = f_data["Count"].tolist()

    # Calculate drop-off strings for annotation
    ctr_drop = f_data.loc[f_data["Stage"] == "Clicks", "Drop_Off_Pct"].values[0] if len(f_data) > 1 else 0
    lead_drop = f_data.loc[f_data["Stage"] == "Leads", "Drop_Off_Pct"].values[0] if len(f_data) > 2 else 0
    conv_drop = f_data.loc[f_data["Stage"] == "Conversions", "Drop_Off_Pct"].values[0] if len(f_data) > 3 else 0

    fig = go.Figure(
        go.Funnel(
            y=stages,
            x=counts,
            texttemplate="<b>%{value:,.0f}</b><br>(%{percentPrevious:.1%})",
            textposition="inside",
            textfont=dict(family="Outfit", size=11, color="#0E0E10"),
            marker=dict(
                color=[ACCENT_GOLD_LIGHT, ACCENT_GOLD, "#C88B35", "#8E6527"],
                line=dict(color="rgba(255, 255, 255, 0.15)", width=1),
            ),
            connector=dict(line=dict(color="rgba(233, 169, 75, 0.25)", width=1)),
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Volume: <b>%{x:,.0f}</b><br>"
                "Conversion from Prior: <b>%{percentPrevious:.1%}</b><br>"
                "Throughput from Initial: <b>%{percentInitial:.3%}</b><extra></extra>"
            ),
        )
    )

    layout = get_plotly_layout(height=280, show_legend=False)
    layout["margin"] = dict(l=10, r=10, t=10, b=10)
    fig.update_layout(layout)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # Drop-off badges
    render_html(f"""
    <div style="display: flex; justify-content: space-between; gap: 0.4rem; padding-top: 0.35rem; font-size: 0.72rem;">
        <div style="background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 8px; padding: 0.35rem 0.5rem; flex: 1; text-align: center;">
            <div style="color: #8E8F96;">CTR Leakage</div>
            <div style="color: #E05353; font-weight: 700;">-{ctr_drop:.1f}%</div>
        </div>
        <div style="background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 8px; padding: 0.35rem 0.5rem; flex: 1; text-align: center;">
            <div style="color: #8E8F96;">Lead Bounce</div>
            <div style="color: #E05353; font-weight: 700;">-{lead_drop:.1f}%</div>
        </div>
        <div style="background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 8px; padding: 0.35rem 0.5rem; flex: 1; text-align: center;">
            <div style="color: #8E8F96;">Cart Abandon</div>
            <div style="color: #E05353; font-weight: 700;">-{conv_drop:.1f}%</div>
        </div>
    </div>
    """)


def render_spend_vs_revenue_trajectory(df: pd.DataFrame):
    """
    5. Marketing Spend vs Revenue: Dual-axis monthly chart
    (Spend as bars, Revenue as gold area line) with ROI% in hover tooltips.
    """
    render_card_header("MARKETING SPEND VS GROSS REVENUE", badge="DUAL-AXIS")

    if len(df) == 0:
        st.info("No records matching current filters.")
        return

    monthly = group_metrics(df, by="Month", sort_by="Marketing Spend")
    monthly["_dt"] = pd.to_datetime(monthly["Month"], format="%b %Y")
    monthly = monthly.sort_values(by="_dt").reset_index(drop=True)

    fig = go.Figure()

    # Trace 1: Media Spend (Bars)
    fig.add_trace(
        go.Bar(
            x=monthly["Month"],
            y=monthly["Marketing Spend"],
            name="Media Spend",
            marker=dict(
                color="rgba(255, 255, 255, 0.16)",
                line=dict(color="rgba(255, 255, 255, 0.28)", width=1),
            ),
            hovertemplate=(
                "<b>%{x}</b> - Media Spend<br>"
                "Spend: <b>₹%{y:,.0f}</b><br>"
                "Net Profit: ₹%{customdata[0]:,.0f}<extra></extra>"
            ),
            customdata=monthly[["Net Profit"]].values,
        )
    )

    # Trace 2: Gross Revenue (Gold Area Line)
    fig.add_trace(
        go.Scatter(
            x=monthly["Month"],
            y=monthly["Revenue Generated"],
            name="Gross Revenue",
            mode="lines+markers",
            line=dict(color=ACCENT_GOLD_LIGHT, width=2.8),
            marker=dict(size=6, color=ACCENT_GOLD, line=dict(color="#0E0E10", width=1)),
            fill="tozeroy",
            fillcolor="rgba(233, 169, 75, 0.14)",
            customdata=monthly[["ROI %", "ROAS", "Net Profit"]].values,
            hovertemplate=(
                "<b>%{x}</b> - Gross Revenue<br>"
                "Revenue: <b>₹%{y:,.0f}</b><br>"
                "Aggregate ROI: <b>%{customdata[0]:+.1f}%</b><br>"
                "ROAS: <b>%{customdata[1]:.2f}x</b> | Profit: ₹%{customdata[2]:,.0f}<extra></extra>"
            ),
        )
    )

    layout = get_plotly_layout(height=280, show_legend=True)
    layout["yaxis"]["tickprefix"] = "₹"
    layout["yaxis"]["title"] = "Capital / Revenue (₹)"
    layout["barmode"] = "overlay"
    layout["margin"] = dict(l=10, r=10, t=16, b=10)
    fig.update_layout(layout)

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def render_performance_section(df_filtered: pd.DataFrame):
    """
    Orchestrates the entire middle performance section:
    - Row 1: Dual-Axis Spend vs Revenue Trajectory (Left) + Conversion Funnel Diagnostics (Right)
    - Row 2: Platform Benchmark & Matrix (Left) + Campaign ROI Extremes (Right)
    - Row 3: Revenue by Campaign (Full Width or Side-by-Side)
    """
    if df_filtered is None or len(df_filtered) == 0:
        return

    # Row 1: Macro Trajectory + Conversion Funnel
    r1_col1, r1_col2 = st.columns([1.35, 1.0])
    with r1_col1, st.container(border=True):
        render_spend_vs_revenue_trajectory(df_filtered)
    with r1_col2, st.container(border=True):
        render_conversion_funnel(df_filtered)

    # Row 2: Platform Performance Comparison + Campaign ROI Extremes
    r2_col1, r2_col2 = st.columns([1.15, 1.15])
    with r2_col1, st.container(border=True):
        render_platform_performance(df_filtered)
    with r2_col2, st.container(border=True):
        render_campaign_roi_analysis(df_filtered)

    # Row 3: Top 10 Revenue by Campaign (Dedicated View)
    with st.container(border=True):
        render_revenue_by_campaign(df_filtered)
