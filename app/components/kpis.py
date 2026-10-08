"""
KPI Scorecard Component Engine
Builds the 2-tier executive KPI scorecards:
- Top Tier (Primary Growth KPIs): Total Marketing Spend, Total Revenue, ROI %, CTR %, Conversion Rate %
- Bottom Tier (Unit Cost & Funnel Efficiency): CAC, CPC, CPM, Total Leads, Lead Conversion Rate
Features:
- Delta calculation vs. previous equivalent chronological period
- Inverted delta semantics for cost metrics (CAC/CPC/CPM decreasing is good/green)
- Indian currency shorthand (Lakh/Crore) and 1-decimal percentage formatting
- Graceful empty filter handling without crashing
"""

from datetime import timedelta
from typing import Any

import numpy as np
import pandas as pd
import streamlit as st

from app.theme import render_html
from src.metrics import calculate_kpis, format_indian_currency, safe_divide


def get_previous_period_df(
    df_all: pd.DataFrame,
    start_date: pd.Timestamp,
    end_date: pd.Timestamp,
    selected_platforms: list | None = None,
    selected_regions: list | None = None,
    selected_segments: list | None = None,
    selected_types: list | None = None,
    exclude_outliers: bool = False,
) -> pd.DataFrame:
    """
    Filters the master dataset for the previous equivalent chronological period
    with the exact same categorical and outlier filters applied.
    """
    duration_days = (end_date - start_date).days + 1
    prev_end = start_date - timedelta(days=1)
    prev_start = prev_end - timedelta(days=duration_days - 1)

    df_prev = df_all.copy()

    # Filter date on previous period
    df_prev = df_prev[(df_prev["Campaign Start Date"] >= prev_start) & (df_prev["Campaign Start Date"] <= prev_end)]

    # Apply identical categorical filters
    if selected_platforms:
        df_prev = df_prev[df_prev["Platform"].isin(selected_platforms)]
    if selected_regions:
        df_prev = df_prev[df_prev["Region"].isin(selected_regions)]
    if selected_segments:
        df_prev = df_prev[df_prev["Audience Segment"].isin(selected_segments)]
    if selected_types:
        df_prev = df_prev[df_prev["Campaign Type"].isin(selected_types)]

    if exclude_outliers:
        df_prev = df_prev[~df_prev["is_outlier"]]

    return df_prev


def compute_kpi_delta(
    curr_val: float,
    prev_val: float | None,
    is_cost_metric: bool = False,
    is_pct_metric: bool = False,
) -> tuple[str, str]:
    """
    Computes delta vs previous equivalent period with directional arrows and inverted
    cost semantics (for CAC, CPC, CPM, reduction is marked as positive green).

    Returns:
        (delta_string, pill_class) where pill_class is 'positive', 'negative', or 'neutral'.
    """
    if prev_val is None or prev_val == 0.0 or pd.isna(prev_val) or np.isclose(prev_val, 0.0):
        return ("— vs prior", "neutral")

    diff = curr_val - prev_val
    pct_change = safe_divide(diff, prev_val) * 100

    if np.isclose(pct_change, 0.0, atol=0.05):
        return ("0.0% vs prior", "neutral")

    is_increase = pct_change > 0
    arrow = "&uarr;" if is_increase else "&darr;"

    # Invert semantics for cost metrics (CAC, CPC, CPM, Spend)
    if is_cost_metric:
        pill_class = "negative" if is_increase else "positive"
    else:
        pill_class = "positive" if is_increase else "negative"

    sign = "+" if is_increase else ""
    return (f"{arrow} {sign}{pct_change:.1f}%", pill_class)


def render_kpi_card_html(
    label: str,
    value: str,
    delta_text: str,
    pill_class: str,
    sublabel: str | None = None,
    is_secondary: bool = False,
):
    """
    Renders styled KPI card with gold typography and delta pill.
    Secondary cards feature slightly more compact padding for the 2nd row.
    """
    card_padding = "0.95rem 1.05rem" if is_secondary else "1.15rem 1.25rem"
    val_size = "1.55rem" if is_secondary else "1.90rem"
    label_size = "0.68rem" if is_secondary else "0.72rem"

    pill_html = ""
    if delta_text:
        pill_html = f'<span class="kpi-pill {pill_class}">{delta_text}</span>'

    subtext_html = ""
    if sublabel or delta_text:
        subtext_html = f"""
        <div class="kpi-subtext" style="margin-top: 0.35rem;">
            {pill_html}
            <span style="font-size: 0.72rem; color: #8E8F96;">{sublabel or ""}</span>
        </div>
        """

    card_html = f"""
    <div class="kpi-card" style="padding: {card_padding};">
        <div class="kpi-label" style="font-size: {label_size};">{label}</div>
        <div class="kpi-value" style="font-size: {val_size};">{value}</div>
        {subtext_html}
    </div>
    """
    render_html(card_html)


def render_kpi_scorecards(
    df_filtered: pd.DataFrame,
    df_all: pd.DataFrame,
    selected_dates: tuple[Any, Any],
    selected_platforms: list | None = None,
    selected_regions: list | None = None,
    selected_segments: list | None = None,
    selected_types: list | None = None,
    exclude_outliers: bool = False,
):
    """
    Main entry point for rendering the dual-tier KPI scorecard layout.
    Gracefully handles empty filter results.
    """
    # -------------------------------------------------------------------------
    # Guard: Empty filter results
    # -------------------------------------------------------------------------
    if df_filtered is None or len(df_filtered) == 0:
        render_html("""
        <div style="background: rgba(233, 169, 75, 0.08); border: 1px solid rgba(233, 169, 75, 0.28);
                    border-radius: 16px; padding: 1.5rem; text-align: center; margin-bottom: 1.2rem;">
            <div style="font-family: 'Outfit', sans-serif; font-size: 1.1rem; font-weight: 600; color: #F3C477; margin-bottom: 0.3rem;">
                ⚠️ No data for these filters
            </div>
            <div style="font-size: 0.82rem; color: #8E8F96;">
                No campaign records matched the selected combination of dates, channels, regions, or audience segments.<br>
                Please adjust your filter parameters or click <b>Reset All Filters</b> in the left sidebar.
            </div>
        </div>
        """)
        return

    # -------------------------------------------------------------------------
    # 1. Compute Current Period KPIs
    # -------------------------------------------------------------------------
    curr = calculate_kpis(df_filtered)

    # -------------------------------------------------------------------------
    # 2. Compute Previous Equivalent Period KPIs
    # -------------------------------------------------------------------------
    prev = None
    if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
        start_d = pd.to_datetime(selected_dates[0])
        end_d = pd.to_datetime(selected_dates[1])
        df_prev = get_previous_period_df(
            df_all=df_all,
            start_date=start_d,
            end_date=end_d,
            selected_platforms=selected_platforms,
            selected_regions=selected_regions,
            selected_segments=selected_segments,
            selected_types=selected_types,
            exclude_outliers=exclude_outliers,
        )
        if len(df_prev) > 0:
            prev = calculate_kpis(df_prev)

    # -------------------------------------------------------------------------
    # 3. ROW 1: Primary Executive KPIs (5 Cards)
    # -------------------------------------------------------------------------
    # Total Marketing Spend
    spend_val = format_indian_currency(curr["total_spend"])
    spend_prev = prev["total_spend"] if prev else None
    spend_delta, spend_pill = compute_kpi_delta(curr["total_spend"], spend_prev, is_cost_metric=True)

    # Total Revenue
    rev_val = format_indian_currency(curr["total_revenue"])
    rev_prev = prev["total_revenue"] if prev else None
    rev_delta, rev_pill = compute_kpi_delta(curr["total_revenue"], rev_prev, is_cost_metric=False)

    # ROI %
    roi_val = f"{curr['roi_pct']:.1f}%"
    roi_prev = prev["roi_pct"] if prev else None
    roi_delta, roi_pill = compute_kpi_delta(curr["roi_pct"], roi_prev, is_cost_metric=False)

    # CTR %
    ctr_val = f"{curr['ctr_pct']:.1f}%"
    ctr_prev = prev["ctr_pct"] if prev else None
    ctr_delta, ctr_pill = compute_kpi_delta(curr["ctr_pct"], ctr_prev, is_cost_metric=False)

    # Conversion Rate %
    cr_val = f"{curr['conversion_rate_pct']:.1f}%"
    cr_prev = prev["conversion_rate_pct"] if prev else None
    cr_delta, cr_pill = compute_kpi_delta(curr["conversion_rate_pct"], cr_prev, is_cost_metric=False)

    r1_c1, r1_c2, r1_c3, r1_c4, r1_c5 = st.columns(5)
    with r1_c1:
        render_kpi_card_html(
            "Total Marketing Spend", spend_val, spend_delta, spend_pill, f"{curr['campaign_count']} campaigns"
        )
    with r1_c2:
        render_kpi_card_html(
            "Total Revenue", rev_val, rev_delta, rev_pill, f"Net {format_indian_currency(curr['net_profit'])}"
        )
    with r1_c3:
        render_kpi_card_html("ROI %", roi_val, roi_delta, roi_pill, f"ROAS {curr['roas']:.2f}x")
    with r1_c4:
        render_kpi_card_html("CTR %", ctr_val, ctr_delta, ctr_pill, f"{curr['total_clicks']:,} clicks")
    with r1_c5:
        render_kpi_card_html("Conversion Rate %", cr_val, cr_delta, cr_pill, f"{curr['total_conversions']:,} purchases")

    render_html("<div style='height: 0.55rem;'></div>")

    # -------------------------------------------------------------------------
    # 4. ROW 2: Secondary Efficiency & Funnel KPIs (5 Cards, Smaller Height)
    # -------------------------------------------------------------------------
    # CAC (Cost Per Acquisition) - Cost metric (inverted)
    cac_val = format_indian_currency(curr["cac"]) if curr["cac"] >= 100000 else f"₹{curr['cac']:,.0f}"
    cac_prev = prev["cac"] if prev else None
    cac_delta, cac_pill = compute_kpi_delta(curr["cac"], cac_prev, is_cost_metric=True)

    # CPC (Cost Per Click) - Cost metric (inverted)
    cpc_val = f"₹{curr['cpc']:.1f}"
    cpc_prev = prev["cpc"] if prev else None
    cpc_delta, cpc_pill = compute_kpi_delta(curr["cpc"], cpc_prev, is_cost_metric=True)

    # CPM (Cost Per Mille) - Cost metric (inverted)
    cpm_val = f"₹{curr['cpm']:,.0f}"
    cpm_prev = prev["cpm"] if prev else None
    cpm_delta, cpm_pill = compute_kpi_delta(curr["cpm"], cpm_prev, is_cost_metric=True)

    # Total Leads - Volume metric (higher is better)
    leads_val = f"{curr['total_leads'] / 100000:.2f}L" if curr["total_leads"] >= 100000 else f"{curr['total_leads']:,}"
    leads_prev = prev["total_leads"] if prev else None
    leads_delta, leads_pill = compute_kpi_delta(curr["total_leads"], leads_prev, is_cost_metric=False)

    # Lead Conversion Rate % - Efficiency metric (higher is better)
    lcr_val = f"{curr['lead_conversion_rate_pct']:.1f}%"
    lcr_prev = prev["lead_conversion_rate_pct"] if prev else None
    lcr_delta, lcr_pill = compute_kpi_delta(curr["lead_conversion_rate_pct"], lcr_prev, is_cost_metric=False)

    r2_c1, r2_c2, r2_c3, r2_c4, r2_c5 = st.columns(5)
    with r2_c1:
        render_kpi_card_html("CAC (Cost Per Acq)", cac_val, cac_delta, cac_pill, "Unit Cost", is_secondary=True)
    with r2_c2:
        render_kpi_card_html("CPC (Cost Per Click)", cpc_val, cpc_delta, cpc_pill, "Traffic Cost", is_secondary=True)
    with r2_c3:
        render_kpi_card_html("CPM (Cost Per Mille)", cpm_val, cpm_delta, cpm_pill, "Impression Cost", is_secondary=True)
    with r2_c4:
        render_kpi_card_html("Total Leads", leads_val, leads_delta, leads_pill, "Mid-funnel", is_secondary=True)
    with r2_c5:
        render_kpi_card_html("Lead Conversion Rate", lcr_val, lcr_delta, lcr_pill, "Lead → Customer", is_secondary=True)

    render_html("<div style='height: 0.85rem;'></div>")
