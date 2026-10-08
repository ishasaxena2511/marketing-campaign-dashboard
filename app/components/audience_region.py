"""
Audience Cohorts & Regional Analytics Component Suite
Renders the bottom section of the executive dashboard:
1. Audience Segment Analysis: Conversion Rate & ROI by segment (dual-axis bars + small table), highlighting top performer
2. Regional Campaign Performance Map: India Scattergeo with revenue-scaled bubbles, ROI colorscale, dark map styling
3. CTR & Conversion Trend: Monthly trajectory of CTR% and Conversion Rate% (computed from summed values) with gold area fill
4. ROI Gauge: Executive gauge comparing overall portfolio ROI vs user-defined target ROI
5. Campaign Details Table: Sortable dark-styled dataframe with ROI conditional formatting + CSV download button
"""

from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app.components.card import render_card_header
from app.theme import (
    ACCENT_GOLD,
    ACCENT_GOLD_LIGHT,
    STATUS_SUCCESS,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    get_plotly_layout,
    render_html,
)
from src.metrics import (
    calculate_kpis,
    format_indian_currency,
    group_metrics,
)

# Geographic Centroids for India Regions
REGION_COORDINATES = {
    "North": {"lat": 28.6139, "lon": 77.2090},  # New Delhi / Northern belt
    "South": {"lat": 12.9716, "lon": 77.5946},  # Bengaluru / Southern hub
    "West": {"lat": 19.0760, "lon": 72.8777},  # Mumbai / Western corridor
    "East": {"lat": 22.5726, "lon": 88.3639},  # Kolkata / Eastern delta
    "Central": {"lat": 23.2599, "lon": 77.4126},  # Bhopal / Central plains
    "North-East": {"lat": 26.1445, "lon": 91.7362},  # Guwahati / NE corridor
}


def render_audience_segment_analysis(df: pd.DataFrame):
    """
    1. Audience Segment Analysis: Conversion rate and ROI by segment (bar + small table),
    highlighting the best segment with dedicated callouts.
    """
    render_card_header("AUDIENCE PERSONA EFFICIENCY", badge="COHORTS")

    if len(df) == 0:
        st.info("No cohort records matching current filters.")
        return

    seg_df = group_metrics(df, by="Audience Segment", sort_by="ROI %", ascending=False)
    best_row = seg_df.iloc[0]

    # Best Segment Executive Badge
    render_html(f"""
    <div style="display: flex; align-items: center; justify-content: space-between;
                background: linear-gradient(90deg, rgba(233, 169, 75, 0.16) 0%, rgba(233, 169, 75, 0.04) 100%);
                border: 1px solid rgba(233, 169, 75, 0.35); border-radius: 10px;
                padding: 0.45rem 0.75rem; margin-bottom: 0.75rem;">
        <div style="display: flex; align-items: center; gap: 0.5rem;">
            <span style="font-size: 1.1rem;">⭐</span>
            <div>
                <div style="font-size: 0.68rem; color: #8E8F96; text-transform: uppercase; letter-spacing: 0.06em;">Highest Capital Efficiency</div>
                <div style="font-size: 0.88rem; font-weight: 700; color: #F3C477; font-family: 'Outfit', sans-serif;">{best_row["Audience Segment"]}</div>
            </div>
        </div>
        <div style="text-align: right;">
            <div style="font-size: 0.95rem; font-weight: 800; color: #34D399; font-family: 'Outfit', sans-serif;">{best_row["ROI %"]:+.1f}% ROI</div>
            <div style="font-size: 0.70rem; color: #8E8F96;">Conv: {best_row["Conversion Rate %"]:.1f}% | CAC: ₹{best_row["CAC"]:,.0f}</div>
        </div>
    </div>
    """)

    # Bar chart: Dual-axis showing ROI % (Gold Bars) and Conversion Rate % (Markers/Line)
    fig = go.Figure()

    # ROI % Bars
    bar_colors = [ACCENT_GOLD_LIGHT if idx == 0 else ACCENT_GOLD for idx in range(len(seg_df))]
    fig.add_trace(
        go.Bar(
            name="ROI %",
            x=seg_df["Audience Segment"],
            y=seg_df["ROI %"],
            marker=dict(
                color=bar_colors,
                line=dict(color="rgba(255, 255, 255, 0.12)", width=1),
            ),
            text=[f"{val:+.1f}%" for val in seg_df["ROI %"]],
            textposition="outside",
            textfont=dict(color=TEXT_PRIMARY, size=10, family="Outfit"),
            customdata=seg_df[["Marketing Spend", "Revenue Generated", "Conversions", "CAC"]].values,
            hovertemplate=(
                "<b>%{x}</b><br>"
                "ROI: <b>%{y:+.1f}%</b><br>"
                "Spend: ₹%{customdata[0]:,.0f} | Revenue: ₹%{customdata[1]:,.0f}<br>"
                "Acquisitions: %{customdata[2]:,} | CAC: ₹%{customdata[3]:,.1f}<extra></extra>"
            ),
            yaxis="y1",
        )
    )

    # Conversion Rate % Scatter Line (Secondary Axis)
    fig.add_trace(
        go.Scatter(
            name="Conv Rate %",
            x=seg_df["Audience Segment"],
            y=seg_df["Conversion Rate %"],
            mode="lines+markers",
            line=dict(color="#FFFFFF", width=2.2),
            marker=dict(size=7, color="#FFFFFF", line=dict(color="#0E0E10", width=1.5)),
            customdata=seg_df[["CTR %", "Leads Generated"]].values,
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Conversion Rate: <b>%{y:.2f}%</b><br>"
                "CTR: %{customdata[0]:.2f}% | Leads: %{customdata[1]:,}<extra></extra>"
            ),
            yaxis="y2",
        )
    )

    layout = get_plotly_layout(height=260, show_legend=True)
    layout["yaxis"] = dict(
        title="Return on Investment (ROI %)",
        ticksuffix="%",
        gridcolor="rgba(255, 255, 255, 0.05)",
        tickfont=dict(color=TEXT_SECONDARY, size=9),
    )
    layout["yaxis2"] = dict(
        title="Conversion Rate %",
        ticksuffix="%",
        overlaying="y",
        side="right",
        showgrid=False,
        tickfont=dict(color=TEXT_SECONDARY, size=9),
    )
    layout["xaxis"]["tickangle"] = -16
    layout["margin"] = dict(l=10, r=10, t=14, b=10)
    fig.update_layout(layout)

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # Small matrix table underneath
    table_rows = []
    for _, r in seg_df.iterrows():
        is_best = r["Audience Segment"] == best_row["Audience Segment"]
        row_bg = "background: rgba(233, 169, 75, 0.08);" if is_best else ""
        roi_color = STATUS_SUCCESS if r["ROI %"] >= 60 else (ACCENT_GOLD if r["ROI %"] >= 25 else "#E05353")
        table_rows.append(f"""
        <tr style="{row_bg} border-bottom: 1px solid rgba(255, 255, 255, 0.04); font-size: 0.74rem;">
            <td style="padding: 0.35rem 0.4rem; font-weight: 600; color: #F5F5F7;">{r["Audience Segment"]}</td>
            <td style="padding: 0.35rem 0.4rem; color: #8E8F96;">{format_indian_currency(r["Marketing Spend"])}</td>
            <td style="padding: 0.35rem 0.4rem; color: #F5F5F7;">{format_indian_currency(r["Revenue Generated"])}</td>
            <td style="padding: 0.35rem 0.4rem; font-weight: 700; color: {roi_color};">{r["ROI %"]:+.1f}%</td>
            <td style="padding: 0.35rem 0.4rem; color: #E9A94B;">{r["Conversion Rate %"]:.1f}%</td>
            <td style="padding: 0.35rem 0.4rem; color: #8E8F96;">₹{r["CAC"]:,.0f}</td>
        </tr>
        """)

    matrix_html = f"""
    <div style="overflow-x: auto; background: rgba(0, 0, 0, 0.22); border-radius: 10px; border: 1px solid rgba(255, 255, 255, 0.05); padding: 0.3rem 0.5rem; margin-top: 0.4rem;">
        <table style="width: 100%; text-align: left; border-collapse: collapse;">
            <thead>
                <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.08); font-size: 0.67rem; color: #8E8F96; text-transform: uppercase;">
                    <th style="padding: 0.3rem 0.4rem;">Segment</th>
                    <th style="padding: 0.3rem 0.4rem;">Spend</th>
                    <th style="padding: 0.3rem 0.4rem;">Revenue</th>
                    <th style="padding: 0.3rem 0.4rem;">ROI %</th>
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


def render_regional_performance_map(df: pd.DataFrame):
    """
    2. Regional Campaign Performance Map: India Scattergeo with bubbles at approximate
    centroids for North, South, East, West, Central, North-East; bubble size = revenue,
    colour = ROI, dark map styling matching the executive theme.
    """
    render_card_header("REGIONAL PERFORMANCE MAP (INDIA)", badge="GEOGRAPHY")

    if len(df) == 0:
        st.info("No geographic records matching current filters.")
        return

    reg_df = group_metrics(df, by="Region")

    lats, lons, texts, sizes, rois = [], [], [], [], []
    custom_rows = []

    max_rev = reg_df["Revenue Generated"].max()
    min_rev = reg_df["Revenue Generated"].min()

    for _, r in reg_df.iterrows():
        reg = r["Region"]
        if reg in REGION_COORDINATES:
            lats.append(REGION_COORDINATES[reg]["lat"])
            lons.append(REGION_COORDINATES[reg]["lon"])
            texts.append(reg)
            rois.append(r["ROI %"])

            # Proportional bubble sizing: 16px to 38px
            if max_rev == min_rev:
                sz = 26
            else:
                sz = 16 + 22 * ((r["Revenue Generated"] - min_rev) / (max_rev - min_rev + 1e-6))
            sizes.append(sz)

            custom_rows.append(
                [
                    reg,
                    r["Marketing Spend"],
                    r["Revenue Generated"],
                    r["ROI %"],
                    r["ROAS"],
                    r["CAC"],
                    r["Conversions"],
                ]
            )

    fig = go.Figure()

    fig.add_trace(
        go.Scattergeo(
            lon=lons,
            lat=lats,
            text=texts,
            mode="markers+text",
            textposition="top center",
            textfont=dict(family="Outfit", size=11, color="#F5F5F7", weight="bold"),
            marker=dict(
                size=sizes,
                color=rois,
                colorscale=[
                    [0.0, "#4E3615"],
                    [0.35, "#8E6527"],
                    [0.70, "#E9A94B"],
                    [1.0, "#F3C477"],
                ],
                colorbar=dict(
                    title=dict(text="ROI %", font=dict(color="#8E8F96", size=10, family="Outfit")),
                    ticksuffix="%",
                    tickfont=dict(color="#8E8F96", size=9, family="Outfit"),
                    len=0.75,
                    thickness=12,
                    outlinewidth=0,
                    x=0.98,
                ),
                line=dict(color="rgba(255, 255, 255, 0.4)", width=1.5),
            ),
            customdata=custom_rows,
            hovertemplate=(
                "<b>%{customdata[0]} Region</b><br>"
                "Gross Revenue: <b>₹%{customdata[2]:,.0f}</b><br>"
                "Media Spend: <b>₹%{customdata[1]:,.0f}</b><br>"
                "Regional ROI: <b>%{customdata[3]:+.1f}%</b> (ROAS: %{customdata[4]:.2f}x)<br>"
                "Customer Acquisition CAC: <b>₹%{customdata[5]:,.1f}</b><br>"
                "Total Conversions: %{customdata[6]:,}<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        geo=dict(
            scope="asia",
            center=dict(lat=22.0, lon=82.0),
            projection_scale=3.8,
            showland=True,
            landcolor="#18191E",
            showocean=True,
            oceancolor="#0E0E10",
            showlakes=False,
            showcountries=True,
            countrycolor="rgba(255, 255, 255, 0.22)",
            showcoastlines=True,
            coastlinecolor="rgba(255, 255, 255, 0.25)",
            showsubunits=True,
            subunitcolor="rgba(255, 255, 255, 0.10)",
            showrivers=False,
            bgcolor="rgba(0,0,0,0)",
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=330,
        margin=dict(l=0, r=0, t=10, b=10),
    )

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # Summary strip underneath map
    top_region = reg_df.sort_values(by="Revenue Generated", ascending=False).iloc[0]
    render_html(f"""
    <div style="display: flex; justify-content: space-between; gap: 0.5rem; font-size: 0.72rem; color: #8E8F96; padding-top: 0.2rem;">
        <div>Top Scale Region: <b style="color: #F3C477;">{top_region["Region"]}</b> ({format_indian_currency(top_region["Revenue Generated"])})</div>
        <div>Bubble Size = Gross Revenue &bull; Bubble Color = ROI %</div>
    </div>
    """)


def render_ctr_conversion_trend(df: pd.DataFrame):
    """
    3. CTR & Conversion Trend: Monthly line chart of CTR% and Conversion Rate%
    (computed from summed values), gold gradient area style.
    """
    render_card_header("CTR & CONVERSION EFFICIENCY TRAJECTORY", badge="MOMENTUM")

    if len(df) == 0:
        st.info("No records matching current filters.")
        return

    monthly = group_metrics(df, by="Month", sort_by="Marketing Spend")
    monthly["_dt"] = pd.to_datetime(monthly["Month"], format="%b %Y")
    monthly = monthly.sort_values(by="_dt").reset_index(drop=True)

    fig = go.Figure()

    # Trace 1: Conversion Rate % (Gold Fill Area Line on Right Axis)
    fig.add_trace(
        go.Scatter(
            name="Conversion Rate %",
            x=monthly["Month"],
            y=monthly["Conversion Rate %"],
            mode="lines+markers",
            line=dict(color=ACCENT_GOLD, width=2.8, shape="spline"),
            marker=dict(size=6, color=ACCENT_GOLD, line=dict(color="#0E0E10", width=1)),
            fill="tozeroy",
            fillcolor="rgba(233, 169, 75, 0.16)",
            customdata=monthly[["Conversions", "Leads Generated"]].values,
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Conversion Rate: <b>%{y:.2f}%</b><br>"
                "Conversions: %{customdata[0]:,} | Leads: %{customdata[1]:,}<extra></extra>"
            ),
            yaxis="y2",
        )
    )

    # Trace 2: Click-Through Rate (CTR %) (Lighter Gold Line on Left Axis)
    fig.add_trace(
        go.Scatter(
            name="CTR %",
            x=monthly["Month"],
            y=monthly["CTR %"],
            mode="lines+markers",
            line=dict(color=ACCENT_GOLD_LIGHT, width=2.2, shape="spline"),
            marker=dict(size=5, color=ACCENT_GOLD_LIGHT),
            customdata=monthly[["Clicks", "Impressions"]].values,
            hovertemplate=(
                "<b>%{x}</b><br>"
                "CTR: <b>%{y:.2f}%</b><br>"
                "Clicks: %{customdata[0]:,} | Impressions: %{customdata[1]:,}<extra></extra>"
            ),
            yaxis="y1",
        )
    )

    layout = get_plotly_layout(height=280, show_legend=True)
    layout["yaxis"] = dict(
        title="CTR (%)",
        ticksuffix="%",
        gridcolor="rgba(255, 255, 255, 0.05)",
        tickfont=dict(color=TEXT_SECONDARY, size=9),
    )
    layout["yaxis2"] = dict(
        title="Conversion Rate (%)",
        ticksuffix="%",
        overlaying="y",
        side="right",
        showgrid=False,
        tickfont=dict(color=TEXT_SECONDARY, size=9),
    )
    layout["margin"] = dict(l=10, r=10, t=16, b=10)
    fig.update_layout(layout)

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def render_roi_gauge(df: pd.DataFrame, target_roi: float = 300.0):
    """
    4. ROI Gauge: A donut/gauge for overall ROI vs target (let user set target in sidebar, default 300%).
    """
    render_card_header("PORTFOLIO ROI VS TARGET", badge="BENCHMARK")

    if len(df) == 0:
        st.info("No records to evaluate ROI.")
        return

    kpis = calculate_kpis(df)
    current_roi = kpis["roi_pct"]
    delta_roi = current_roi - target_roi
    is_on_track = delta_roi >= 0

    max_gauge = max(target_roi * 1.5, current_roi * 1.25, 400.0)

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number+delta",
            value=current_roi,
            delta={
                "reference": target_roi,
                "valueformat": "+.1f%",
                "increasing": {"color": STATUS_SUCCESS},
                "decreasing": {"color": "#E05353"},
            },
            gauge={
                "axis": {
                    "range": [0, max_gauge],
                    "ticksuffix": "%",
                    "tickcolor": TEXT_SECONDARY,
                    "tickfont": {"color": TEXT_SECONDARY, "size": 9},
                },
                "bar": {"color": ACCENT_GOLD, "thickness": 0.28},
                "bgcolor": "rgba(255, 255, 255, 0.04)",
                "borderwidth": 0,
                "threshold": {
                    "line": {"color": ACCENT_GOLD_LIGHT, "width": 3.5},
                    "thickness": 0.75,
                    "value": target_roi,
                },
                "steps": [
                    {"range": [0, target_roi * 0.5], "color": "rgba(255, 255, 255, 0.03)"},
                    {"range": [target_roi * 0.5, target_roi], "color": "rgba(233, 169, 75, 0.10)"},
                    {"range": [target_roi, max_gauge], "color": "rgba(233, 169, 75, 0.24)"},
                ],
            },
            number={"suffix": "%", "font": {"color": ACCENT_GOLD, "size": 34, "family": "Outfit"}},
        )
    )

    layout = get_plotly_layout(height=220, show_legend=False)
    layout["margin"] = dict(l=20, r=20, t=10, b=0)
    fig.update_layout(layout)

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # Executive Pacing Status Box
    status_color = STATUS_SUCCESS if is_on_track else "#E05353"
    status_icon = "🎯" if is_on_track else "⚠️"
    status_label = "Pacing Ahead of Target" if is_on_track else "Trailing Target Benchmark"

    render_html(f"""
    <div style="background: rgba(0, 0, 0, 0.22); border: 1px solid rgba(255, 255, 255, 0.06);
                border-radius: 10px; padding: 0.55rem 0.75rem; text-align: center; margin-top: 0.3rem;">
        <div style="font-size: 0.72rem; color: #8E8F96; text-transform: uppercase; letter-spacing: 0.06em;">
            Target: <b style="color: #F5F5F7;">{target_roi:.0f}%</b> &bull; Status: <b style="color: {status_color};">{status_label}</b>
        </div>
        <div style="font-size: 0.88rem; font-weight: 700; color: {status_color}; margin-top: 0.15rem; font-family: 'Outfit', sans-serif;">
            {status_icon} {delta_roi:+.1f}% vs Target ({kpis["roas"]:.2f}x ROAS)
        </div>
        <div style="font-size: 0.70rem; color: #8E8F96; margin-top: 0.2rem;">
            Net Profit: <b style="color: #F5F5F7;">{format_indian_currency(kpis["net_profit"])}</b> on Spend: <b style="color: #F5F5F7;">{format_indian_currency(kpis["total_spend"])}</b>
        </div>
    </div>
    """)


def render_campaign_details_table(df: pd.DataFrame):
    """
    5. Campaign Details Table: A sortable dark-styled dataframe (Campaign Name, Platform,
    Spend, Revenue, ROI%, Conversions, CAC) with conditional colouring on ROI,
    plus a 'Download filtered data (CSV)' button.
    """
    render_card_header("CAMPAIGN AUDIT & EXPORT DIRECTORY", badge="RECORDS")

    if len(df) == 0:
        st.info("No records matching current filters.")
        return

    # Prepare display dataframe
    cols = [
        "Campaign ID",
        "Campaign Name",
        "Platform",
        "Campaign Type",
        "Marketing Spend",
        "Revenue Generated",
        "ROI %",
        "Conversions",
        "CAC",
    ]
    table_df = df[cols].copy()

    # Conditional ROI formatting logic
    def color_roi(val):
        if val >= 60:
            return "color: #34D399; font-weight: bold;"
        elif val >= 25:
            return "color: #F3C477; font-weight: bold;"
        else:
            return "color: #F87171; font-weight: bold;"

    styled_df = table_df.style.map(color_roi, subset=["ROI %"]).format(
        {
            "Marketing Spend": "₹{:,.0f}",
            "Revenue Generated": "₹{:,.0f}",
            "ROI %": "{:+.1f}%",
            "Conversions": "{:,.0f}",
            "CAC": "₹{:,.1f}",
        }
    )

    # Top action bar with record count and download button
    col_info, col_download = st.columns([1.5, 1.0])
    with col_info:
        render_html(f"""
        <div style="font-size: 0.78rem; color: #8E8F96; padding-top: 0.4rem;">
            Displaying <b style="color: #F5F5F7;">{len(table_df)}</b> filtered campaigns &bull; Sortable by clicking column headers
        </div>
        """)

    with col_download:
        csv_bytes = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download filtered data (CSV)",
            data=csv_bytes,
            file_name=f"marketing_campaigns_filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True,
            key="btn_download_filtered_csv",
        )

    st.dataframe(
        styled_df,
        use_container_width=True,
        height=380,
    )


def render_audience_region_section(df_filtered: pd.DataFrame, target_roi: float = 300.0):
    """
    Orchestrates the entire bottom section:
    - Row 1: Regional Campaign Performance Map (Left) + Audience Segment Analysis (Right)
    - Row 2: CTR & Conversion Trajectory (Left) + ROI Gauge vs Target (Right)
    - Row 3: Full-width Campaign Details Table with search, sorting, and CSV download
    """
    if df_filtered is None or len(df_filtered) == 0:
        return

    # Row 1: Regional Map + Audience Cohorts
    r1_col1, r1_col2 = st.columns([1.15, 1.15])
    with r1_col1, st.container(border=True):
        render_regional_performance_map(df_filtered)
    with r1_col2, st.container(border=True):
        render_audience_segment_analysis(df_filtered)

    # Row 2: Momentum Trajectory + Portfolio Target Gauge
    r2_col1, r2_col2 = st.columns([1.35, 1.0])
    with r2_col1, st.container(border=True):
        render_ctr_conversion_trend(df_filtered)
    with r2_col2, st.container(border=True):
        render_roi_gauge(df_filtered, target_roi=target_roi)

    # Row 3: Interactive Audit Directory & CSV Export
    with st.container(border=True):
        render_campaign_details_table(df_filtered)
