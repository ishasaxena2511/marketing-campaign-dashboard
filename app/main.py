"""
Marketing Campaign Performance Dashboard - Executive Analytics UI
Streamlit Entrypoint featuring:
- Executive dark-gold theme (inspired by docs/theme-reference.png)
- Left sidebar filter controls with single filtered DataFrame
- 5 Top KPI Cards (strictly summed numerators and denominators)
- Middle Row: Campaign Performance (Gradient Area), Platform Benchmark (Capsule Bars), Funnel Gauge
- Bottom Row: Audience Persona Insights, Geographic Regional Performance
"""

import os
import sys

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# Ensure project root is accessible
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.components.audience_region import render_audience_region_section
from app.components.budget_optimizer import render_budget_optimizer
from app.components.channel_insights import render_channel_insights
from app.components.drilldown import render_campaign_drilldown
from app.components.export_report import render_export_button
from app.components.insights_panel import render_insights_panel
from app.components.kpis import render_kpi_scorecards
from app.components.performance import render_performance_section
from app.theme import (
    inject_custom_css,
    render_html,
)
from src.metrics import (
    calculate_kpis,
)

# -----------------------------------------------------------------------------
# Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Marketing Campaign Intelligence | Executive Suite",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject Custom Design System
inject_custom_css()

# Guarantee Sidebar is opened and open/close arrows are synced
components.html(
    """
    <script>
    (function() {
        function syncSidebar() {
            try {
                const doc = window.parent.document;

                // Track user clicking collapse button
                const collapseBtn = doc.querySelector('[data-testid="stSidebarCollapseButton"] button, button[aria-label="Collapse sidebar"]');
                if (collapseBtn && !collapseBtn.dataset.synced) {
                    collapseBtn.dataset.synced = "true";
                    collapseBtn.addEventListener("click", function() {
                        window.parent.sessionStorage.setItem("user_closed_sidebar", "true");
                    });
                }

                // Track user clicking expand button
                const expandBtn = doc.querySelector('[data-testid="stExpandSidebarButton"] button, [data-testid="collapsedControl"] button, button[aria-label="Expand sidebar"]');
                if (expandBtn && !expandBtn.dataset.synced) {
                    expandBtn.dataset.synced = "true";
                    expandBtn.addEventListener("click", function() {
                        window.parent.sessionStorage.removeItem("user_closed_sidebar");
                    });
                }

                // If sidebar was collapsed without explicit user click in this session, auto-expand it!
                if (!window.parent.sessionStorage.getItem("user_closed_sidebar")) {
                    if (expandBtn) {
                        expandBtn.click();
                    }
                }
            } catch (err) {
                // Ignore cross-origin in sandboxed environments
            }
        }
        syncSidebar();
        setTimeout(syncSidebar, 150);
        setTimeout(syncSidebar, 500);
        setTimeout(syncSidebar, 1000);
    })();
    </script>
    """,
    height=0,
    width=0,
)


# -----------------------------------------------------------------------------
# Data Loader with Caching
# -----------------------------------------------------------------------------
@st.cache_data
def load_campaign_data(filepath: str = "data/processed/marketing_campaigns_clean.csv") -> pd.DataFrame:
    df = pd.read_csv(filepath)
    df["Campaign Start Date"] = pd.to_datetime(df["Campaign Start Date"])
    df["Campaign End Date"] = pd.to_datetime(df["Campaign End Date"])
    return df


df_raw = load_campaign_data()

# -----------------------------------------------------------------------------
# Sidebar Navigation & Filters
# -----------------------------------------------------------------------------
with st.sidebar:
    render_html("""
    <div style="padding: 0.1rem 0 0.5rem 0;">
        <div style="font-family: 'Outfit', sans-serif; font-size: 1.15rem; font-weight: 700; color: #F5F5F7;">
            ⚡ NEXUS <span style="color: #E9A94B;">ANALYTICS</span>
        </div>
        <div style="font-size: 0.70rem; color: #8E8F96; text-transform: uppercase; letter-spacing: 0.08em;">
            Executive Attribution Suite
        </div>
    </div>
    """)

    render_html("<p style='font-weight: 600; color: #F5F5F7; margin: 0.5rem 0 0.4rem 0;'>CAMPAIGN FILTERS</p>")

    # Date bounds
    min_date = df_raw["Campaign Start Date"].min().date()
    max_date = df_raw["Campaign End Date"].max().date()

    if "date_filter" not in st.session_state:
        st.session_state["date_filter"] = (min_date, max_date)

    selected_dates = st.date_input(
        "Date Range",
        value=st.session_state["date_filter"],
        min_value=min_date,
        max_value=max_date,
    )

    # Multi-select options
    all_platforms = sorted(df_raw["Platform"].unique().tolist())
    all_regions = sorted(df_raw["Region"].unique().tolist())
    all_segments = sorted(df_raw["Audience Segment"].unique().tolist())
    all_types = sorted(df_raw["Campaign Type"].unique().tolist())

    if "platforms_filter" not in st.session_state:
        st.session_state["platforms_filter"] = all_platforms
    if "regions_filter" not in st.session_state:
        st.session_state["regions_filter"] = all_regions
    if "segments_filter" not in st.session_state:
        st.session_state["segments_filter"] = all_segments
    if "types_filter" not in st.session_state:
        st.session_state["types_filter"] = all_types
    if "exclude_outliers" not in st.session_state:
        st.session_state["exclude_outliers"] = False

    selected_platforms = st.multiselect("Platform", options=all_platforms, default=st.session_state["platforms_filter"])
    selected_regions = st.multiselect("Region", options=all_regions, default=st.session_state["regions_filter"])
    selected_segments = st.multiselect(
        "Audience Segment", options=all_segments, default=st.session_state["segments_filter"]
    )
    selected_types = st.multiselect("Campaign Type", options=all_types, default=st.session_state["types_filter"])

    exclude_outliers = st.toggle(
        "Exclude Spend Outliers",
        value=st.session_state["exclude_outliers"],
        help="Excludes the 3 extreme budget entry outliers (> ₹18.5L) identified via platform IQR.",
    )

    render_html("<p style='font-weight: 600; color: #F5F5F7; margin: 0.6rem 0 0.2rem 0;'>PERFORMANCE BENCHMARK</p>")
    target_roi = st.slider(
        "Target Portfolio ROI %",
        min_value=50,
        max_value=600,
        value=300,
        step=25,
        help="Benchmark target for portfolio ROI gauge pacing (default: 300%)",
    )

    # Reset button
    if st.button("Reset All Filters"):
        st.session_state["date_filter"] = (min_date, max_date)
        st.session_state["platforms_filter"] = all_platforms
        st.session_state["regions_filter"] = all_regions
        st.session_state["segments_filter"] = all_segments
        st.session_state["types_filter"] = all_types
        st.session_state["exclude_outliers"] = False
        st.rerun()

    st.markdown("---")
    render_html("""
    <div style="font-size: 0.72rem; color: #5C5D65; line-height: 1.5;">
        <b>Reporting Standard:</b> All portfolio ratios computed strictly from summed numerators & denominators.<br>
        <b>Currency:</b> INR (₹) with Lakh/Crore shorthand.
    </div>
    """)


# -----------------------------------------------------------------------------
# Filter Engine (Single filtered DataFrame feeding the entire app)
# -----------------------------------------------------------------------------
df_filtered = df_raw.copy()

# Date filter
if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
    start_filter, end_filter = selected_dates
    df_filtered = df_filtered[
        (df_filtered["Campaign Start Date"].dt.date >= start_filter)
        & (df_filtered["Campaign Start Date"].dt.date <= end_filter)
    ]

# Categorical filters
if selected_platforms:
    df_filtered = df_filtered[df_filtered["Platform"].isin(selected_platforms)]
if selected_regions:
    df_filtered = df_filtered[df_filtered["Region"].isin(selected_regions)]
if selected_segments:
    df_filtered = df_filtered[df_filtered["Audience Segment"].isin(selected_segments)]
if selected_types:
    df_filtered = df_filtered[df_filtered["Campaign Type"].isin(selected_types)]

# Outlier filter
if exclude_outliers:
    df_filtered = df_filtered[~df_filtered["is_outlier"]]

# Compute master KPIs
kpis = calculate_kpis(df_filtered)


# -----------------------------------------------------------------------------
# Executive Header Banner & Export Action
# -----------------------------------------------------------------------------
header_col1, header_col2 = st.columns([3.0, 1.0])
with header_col1:
    render_html("""
    <div class="dash-header" style="margin-bottom: 0.5rem;">
        <div>
            <h1 class="dash-title">CAMPAIGN PERFORMANCE INTELLIGENCE</h1>
            <div class="dash-subtitle">Cross-Channel ROI, Funnel Attribution & Strategic Budget Reallocation</div>
        </div>
        <div class="dash-live-badge">
            <div class="live-dot"></div>
            <span>LIVE TELEMETRY</span>
        </div>
    </div>
    """)

with header_col2:
    render_html("<div style='padding-top: 0.65rem;'></div>")
    render_export_button(df_filtered, target_roi=float(target_roi))


# -----------------------------------------------------------------------------
# Dynamic Strategic Intelligence Panel (Reactive to Active Filters)
# -----------------------------------------------------------------------------
render_insights_panel(df_filtered)


# -----------------------------------------------------------------------------
# Multi-Page Executive Navigation (Tabs)
# -----------------------------------------------------------------------------
tab_overview, tab_channels, tab_drilldown, tab_optimizer = st.tabs(
    [
        "📊 Executive Overview",
        "📡 Channel Insights & Forecasting",
        "🎯 Campaign Drill-Down",
        "⚖️ Budget Optimiser",
    ]
)

with tab_overview:
    # 1. TOP SECTION: Dual-Tier Executive KPI Scorecards (10 Cards Total)
    render_kpi_scorecards(
        df_filtered=df_filtered,
        df_all=df_raw,
        selected_dates=selected_dates,
        selected_platforms=selected_platforms,
        selected_regions=selected_regions,
        selected_segments=selected_segments,
        selected_types=selected_types,
        exclude_outliers=exclude_outliers,
    )

    # 2. MIDDLE SECTION: Performance Analytics Suite (5 Plotly Visualizations)
    render_performance_section(df_filtered)

    # 3. BOTTOM SECTION: Audience Persona, Geographic Map, Momentum & Audit
    render_audience_region_section(df_filtered, target_roi=float(target_roi))

with tab_channels:
    render_channel_insights(df_filtered)

with tab_drilldown:
    render_campaign_drilldown(df_filtered)

with tab_optimizer:
    render_budget_optimizer(df_filtered)
