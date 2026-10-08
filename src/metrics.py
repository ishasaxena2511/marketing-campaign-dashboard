"""
Marketing Campaign Performance Analytics Engine
Single Source of Truth for all KPI Calculations, Funnel Analytics,
Grouped Aggregations, and Budget Optimization Recommendations.
"""

from typing import Any

import numpy as np
import pandas as pd


def safe_divide(numerator: Any, denominator: Any, default: float = 0.0) -> float:
    """
    Safely divide two numbers, returning a default value if the denominator
    is zero, null, NaN, or non-finite.
    """
    try:
        if pd.isna(numerator) or pd.isna(denominator):
            return default
        num = float(numerator)
        denom = float(denominator)
        if np.isclose(denom, 0.0) or denom == 0.0:
            return default
        res = num / denom
        if np.isnan(res) or np.isinf(res):
            return default
        return float(res)
    except (ZeroDivisionError, ValueError, TypeError):
        return default


def format_indian_currency(value: float, shorthand: bool = True) -> str:
    """
    Format monetary values in Indian Rupees (₹) using Indian numbering standards
    (Lakh 'L' and Crore 'Cr' shorthand for executive KPI cards).

    Examples:
        12500000.0 -> '₹1.25Cr'
        1240000.0  -> '₹12.40L'
        45200.5    -> '₹45,200.50'
    """
    if pd.isna(value):
        return "₹0.00"

    val = float(value)
    sign = "-" if val < 0 else ""
    abs_val = abs(val)

    if shorthand:
        if abs_val >= 10000000:  # >= 1 Crore
            return f"{sign}₹{abs_val / 10000000:.2f}Cr"
        elif abs_val >= 100000:  # >= 1 Lakh
            return f"{sign}₹{abs_val / 100000:.2f}L"
        else:
            return f"{sign}₹{abs_val:,.2f}"
    else:
        # Full precision with standard formatting
        return f"{sign}₹{abs_val:,.2f}"


def calculate_kpis(df: pd.DataFrame) -> dict[str, Any]:
    """
    Calculate executive portfolio-level KPIs from SUMMED numerators and denominators.
    Never averages row-level ratios.

    Returns:
        total spend, total revenue, net profit, ROI%, ROAS, CTR%, conversion rate%,
        lead conversion rate%, CPC, CPM, CAC, CPL, total leads, total conversions,
        total impressions, total clicks, and campaign count.
    """
    if df is None or len(df) == 0:
        return {
            "campaign_count": 0,
            "total_spend": 0.0,
            "total_revenue": 0.0,
            "net_profit": 0.0,
            "roi_pct": 0.0,
            "roas": 0.0,
            "ctr_pct": 0.0,
            "conversion_rate_pct": 0.0,
            "lead_conversion_rate_pct": 0.0,
            "cpc": 0.0,
            "cpm": 0.0,
            "cac": 0.0,
            "cpl": 0.0,
            "total_impressions": 0,
            "total_clicks": 0,
            "total_leads": 0,
            "total_conversions": 0,
        }

    # Summed base totals
    total_spend = float(df["Marketing Spend"].sum())
    total_revenue = float(df["Revenue Generated"].sum())
    total_impressions = int(df["Impressions"].sum())
    total_clicks = int(df["Clicks"].sum())
    total_leads = int(df["Leads Generated"].sum())
    total_conversions = int(df["Conversions"].sum())
    campaign_count = len(df)

    net_profit = round(total_revenue - total_spend, 2)

    # Core derived metrics computed from summed totals
    roi_pct = round(safe_divide(total_revenue - total_spend, total_spend) * 100, 2)
    roas = round(safe_divide(total_revenue, total_spend), 2)
    ctr_pct = round(safe_divide(total_clicks, total_impressions) * 100, 2)
    conversion_rate_pct = round(safe_divide(total_conversions, total_clicks) * 100, 2)
    lead_conversion_rate_pct = round(safe_divide(total_conversions, total_leads) * 100, 2)
    cpc = round(safe_divide(total_spend, total_clicks), 2)
    cpm = round(safe_divide(total_spend, total_impressions) * 1000, 2)
    cac = round(safe_divide(total_spend, total_conversions), 2)
    cpl = round(safe_divide(total_spend, total_leads), 2)

    return {
        "campaign_count": campaign_count,
        "total_spend": round(total_spend, 2),
        "total_revenue": round(total_revenue, 2),
        "net_profit": net_profit,
        "roi_pct": roi_pct,
        "roas": roas,
        "ctr_pct": ctr_pct,
        "conversion_rate_pct": conversion_rate_pct,
        "lead_conversion_rate_pct": lead_conversion_rate_pct,
        "cpc": cpc,
        "cpm": cpm,
        "cac": cac,
        "cpl": cpl,
        "total_impressions": total_impressions,
        "total_clicks": total_clicks,
        "total_leads": total_leads,
        "total_conversions": total_conversions,
    }


def group_metrics(
    df: pd.DataFrame,
    by: str | list[str],
    sort_by: str = "Marketing Spend",
    ascending: bool = False,
) -> pd.DataFrame:
    """
    Compute grouped performance metrics by one or more dimensions (e.g. Platform, Region,
    Audience Segment, Campaign Type, Month, Campaign ID).

    CRITICAL RULE: Ratios are computed from SUMMED numerators and denominators within each group.
    """
    if df is None or len(df) == 0:
        cols = [by] if isinstance(by, str) else by
        return pd.DataFrame(
            columns=cols
            + [
                "Campaigns",
                "Marketing Spend",
                "Revenue Generated",
                "Net Profit",
                "ROI %",
                "ROAS",
                "Impressions",
                "Clicks",
                "CTR %",
                "Leads Generated",
                "Conversions",
                "Conversion Rate %",
                "Lead Conversion Rate %",
                "CPC",
                "CPM",
                "CAC",
                "CPL",
            ]
        )

    group_cols = [by] if isinstance(by, str) else by

    # Group and aggregate base totals
    agg_dict = {
        "Impressions": "sum",
        "Clicks": "sum",
        "Leads Generated": "sum",
        "Conversions": "sum",
        "Marketing Spend": "sum",
        "Revenue Generated": "sum",
    }
    if "Campaign ID" in df.columns:
        agg_dict["Campaign ID"] = "count"

    grouped = df.groupby(group_cols, as_index=False).agg(agg_dict)
    if "Campaign ID" in grouped.columns:
        grouped = grouped.rename(columns={"Campaign ID": "Campaigns"})
    else:
        grouped["Campaigns"] = df.groupby(group_cols, as_index=False).size()["size"]

    # Calculate net profit
    grouped["Net Profit"] = np.round(grouped["Revenue Generated"] - grouped["Marketing Spend"], 2)

    # Compute derived ratios from summed totals
    grouped["ROI %"] = np.round(
        grouped.apply(
            lambda r: safe_divide(r["Revenue Generated"] - r["Marketing Spend"], r["Marketing Spend"]) * 100,
            axis=1,
        ),
        2,
    )
    grouped["ROAS"] = np.round(
        grouped.apply(lambda r: safe_divide(r["Revenue Generated"], r["Marketing Spend"]), axis=1),
        2,
    )
    grouped["CTR %"] = np.round(
        grouped.apply(lambda r: safe_divide(r["Clicks"], r["Impressions"]) * 100, axis=1),
        2,
    )
    grouped["Conversion Rate %"] = np.round(
        grouped.apply(lambda r: safe_divide(r["Conversions"], r["Clicks"]) * 100, axis=1),
        2,
    )
    grouped["Lead Conversion Rate %"] = np.round(
        grouped.apply(lambda r: safe_divide(r["Conversions"], r["Leads Generated"]) * 100, axis=1),
        2,
    )
    grouped["CPC"] = np.round(
        grouped.apply(lambda r: safe_divide(r["Marketing Spend"], r["Clicks"]), axis=1),
        2,
    )
    grouped["CPM"] = np.round(
        grouped.apply(lambda r: safe_divide(r["Marketing Spend"], r["Impressions"]) * 1000, axis=1),
        2,
    )
    grouped["CAC"] = np.round(
        grouped.apply(lambda r: safe_divide(r["Marketing Spend"], r["Conversions"]), axis=1),
        2,
    )
    grouped["CPL"] = np.round(
        grouped.apply(lambda r: safe_divide(r["Marketing Spend"], r["Leads Generated"]), axis=1),
        2,
    )

    # Round base financial columns
    grouped["Marketing Spend"] = np.round(grouped["Marketing Spend"], 2)
    grouped["Revenue Generated"] = np.round(grouped["Revenue Generated"], 2)

    # Sort
    if sort_by in grouped.columns:
        grouped = grouped.sort_values(by=sort_by, ascending=ascending).reset_index(drop=True)

    return grouped


def funnel_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build marketing conversion funnel summary with counts, stage-to-stage conversion rates,
    drop-off rates, and overall throughput from Impressions.
    """
    if df is None or len(df) == 0:
        return pd.DataFrame(columns=["Stage", "Count", "Stage_Conv_Pct", "Drop_Off_Pct", "Overall_Conv_Pct"])

    impressions = int(df["Impressions"].sum())
    clicks = int(df["Clicks"].sum())
    leads = int(df["Leads Generated"].sum())
    conversions = int(df["Conversions"].sum())

    stages = [
        {
            "Stage": "Impressions",
            "Count": impressions,
            "Stage_Conv_Pct": 100.0,
            "Drop_Off_Pct": 0.0,
            "Overall_Conv_Pct": 100.0,
        },
        {
            "Stage": "Clicks",
            "Count": clicks,
            "Stage_Conv_Pct": round(safe_divide(clicks, impressions) * 100, 2),
            "Drop_Off_Pct": round((1.0 - safe_divide(clicks, impressions)) * 100, 2),
            "Overall_Conv_Pct": round(safe_divide(clicks, impressions) * 100, 2),
        },
        {
            "Stage": "Leads",
            "Count": leads,
            "Stage_Conv_Pct": round(safe_divide(leads, clicks) * 100, 2),
            "Drop_Off_Pct": round((1.0 - safe_divide(leads, clicks)) * 100, 2),
            "Overall_Conv_Pct": round(safe_divide(leads, impressions) * 100, 2),
        },
        {
            "Stage": "Conversions",
            "Count": conversions,
            "Stage_Conv_Pct": round(safe_divide(conversions, leads) * 100, 2),
            "Drop_Off_Pct": round((1.0 - safe_divide(conversions, leads)) * 100, 2),
            "Overall_Conv_Pct": round(safe_divide(conversions, impressions) * 100, 2),
        },
    ]

    return pd.DataFrame(stages)


def get_top_campaigns(
    df: pd.DataFrame,
    metric: str = "ROI %",
    n: int = 5,
    min_spend: float = 0.0,
) -> pd.DataFrame:
    """
    Retrieve top N performing campaigns ranked by metric with minimum spend qualification.

    Note on CAC: For CAC, lower is better, so 'top' returns campaigns with the lowest CAC.
    For ROI % and Revenue Generated, 'top' returns highest values.
    """
    if df is None or len(df) == 0:
        return df.head(0).copy() if df is not None else pd.DataFrame()

    filtered = df[df["Marketing Spend"] >= min_spend].copy()
    if len(filtered) == 0:
        return df.head(0).copy()

    # For CAC, smaller is better (most cost-effective customer acquisition)
    ascending = metric in ["CAC", "Customer Acquisition Cost", "CPC", "CPL"]

    ranked = filtered.sort_values(by=metric, ascending=ascending).head(n).reset_index(drop=True)
    return ranked


def get_bottom_campaigns(
    df: pd.DataFrame,
    metric: str = "ROI %",
    n: int = 5,
    min_spend: float = 0.0,
) -> pd.DataFrame:
    """
    Retrieve bottom N performing campaigns ranked by metric with minimum spend qualification.

    Note on CAC: For CAC, higher is worse, so 'bottom' returns campaigns with the highest CAC.
    For ROI % and Revenue Generated, 'bottom' returns lowest values.
    """
    if df is None or len(df) == 0:
        return df.head(0).copy() if df is not None else pd.DataFrame()

    filtered = df[df["Marketing Spend"] >= min_spend].copy()
    if len(filtered) == 0:
        return df.head(0).copy()

    # For CAC, higher is worse (least cost-effective)
    ascending = metric not in ["CAC", "Customer Acquisition Cost", "CPC", "CPL"]

    ranked = filtered.sort_values(by=metric, ascending=ascending).head(n).reset_index(drop=True)
    return ranked


def budget_opportunities(
    df: pd.DataFrame,
    dimension: str = "Platform",
) -> pd.DataFrame:
    """
    Identify strategic budget reallocation opportunities:
    - Scale Up (Underinvested Winners): ROI above average AND spend share below average.
    - Reduce / Optimise (Overinvested Underperformers): ROI below average AND spend share above average.
    - Maintain / Core Drivers: ROI above average AND spend share above average.
    - Monitor / Low Impact: ROI below average AND spend share below average.
    """
    if df is None or len(df) == 0:
        return pd.DataFrame(
            columns=[
                dimension,
                "Spend",
                "Revenue",
                "ROI %",
                "ROAS",
                "Spend_Share_Pct",
                "Revenue_Share_Pct",
                "Action_Recommendation",
                "ROI_Delta_vs_Avg",
                "Spend_Share_Delta_vs_Avg",
            ]
        )

    grouped = (
        df.groupby(dimension, as_index=False)
        .agg(
            {
                "Marketing Spend": "sum",
                "Revenue Generated": "sum",
                "Campaign ID": "count" if "Campaign ID" in df.columns else "size",
            }
        )
        .rename(columns={"Campaign ID": "Campaigns"})
    )

    total_spend = float(grouped["Marketing Spend"].sum())
    total_revenue = float(grouped["Revenue Generated"].sum())
    num_segments = len(grouped)

    # Benchmark averages
    avg_roi_pct = safe_divide(total_revenue - total_spend, total_spend) * 100
    avg_spend_share_pct = 100.0 / num_segments if num_segments > 0 else 0.0

    grouped["ROI %"] = np.round(
        grouped.apply(
            lambda r: safe_divide(r["Revenue Generated"] - r["Marketing Spend"], r["Marketing Spend"]) * 100,
            axis=1,
        ),
        2,
    )
    grouped["ROAS"] = np.round(
        grouped.apply(lambda r: safe_divide(r["Revenue Generated"], r["Marketing Spend"]), axis=1),
        2,
    )
    grouped["Spend_Share_Pct"] = np.round(
        grouped.apply(lambda r: safe_divide(r["Marketing Spend"], total_spend) * 100, axis=1),
        2,
    )
    grouped["Revenue_Share_Pct"] = np.round(
        grouped.apply(lambda r: safe_divide(r["Revenue Generated"], total_revenue) * 100, axis=1),
        2,
    )

    grouped["ROI_Delta_vs_Avg"] = np.round(grouped["ROI %"] - avg_roi_pct, 2)
    grouped["Spend_Share_Delta_vs_Avg"] = np.round(grouped["Spend_Share_Pct"] - avg_spend_share_pct, 2)

    def assign_action(row):
        roi_above = row["ROI %"] >= avg_roi_pct
        spend_above = row["Spend_Share_Pct"] >= avg_spend_share_pct

        if roi_above and not spend_above:
            return "Scale Up (Underinvested High Performer)"
        elif not roi_above and spend_above:
            return "Reduce / Optimise (Overinvested Low Performer)"
        elif roi_above and spend_above:
            return "Maintain (Core Growth Driver)"
        else:
            return "Monitor / Test (Low Impact Channel)"

    grouped["Action_Recommendation"] = grouped.apply(assign_action, axis=1)

    grouped["Marketing Spend"] = np.round(grouped["Marketing Spend"], 2)
    grouped["Revenue Generated"] = np.round(grouped["Revenue Generated"], 2)

    return grouped.sort_values(by="ROI %", ascending=False).reset_index(drop=True)
