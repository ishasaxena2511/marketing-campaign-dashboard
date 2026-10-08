"""
Unit and Integration Tests for Marketing Metrics Engine
Validates all KPI formulas, edge case handling, safe division,
funnel drop-offs, budget reallocation rules, and the Critical Ratio Aggregation Rule.
"""

import os

import numpy as np
import pandas as pd
import pytest

from src.metrics import (
    budget_opportunities,
    calculate_kpis,
    format_indian_currency,
    funnel_data,
    get_bottom_campaigns,
    get_top_campaigns,
    group_metrics,
    safe_divide,
)


@pytest.fixture
def mock_campaign_df():
    """
    Standard test dataset with known, mathematically verifiable totals.
    """
    data = {
        "Campaign ID": ["CMP-001", "CMP-002", "CMP-003", "CMP-004"],
        "Campaign Name": ["C1", "C2", "C3", "C4"],
        "Platform": ["Google", "Google", "Facebook", "Facebook"],
        "Region": ["North", "South", "North", "West"],
        "Audience Segment": ["Students", "Young Professionals", "Students", "Working Parents"],
        "Campaign Type": ["Lead Generation", "Brand Awareness", "Seasonal Sale", "Retargeting"],
        "Impressions": [10000, 20000, 30000, 40000],  # Total: 100,000
        "Clicks": [500, 1000, 900, 1600],  # Total: 4,000
        "Leads Generated": [100, 200, 180, 320],  # Total: 800
        "Conversions": [25, 50, 45, 80],  # Total: 200
        "Marketing Spend": [50000.0, 100000.0, 60000.0, 90000.0],  # Total: 300,000.0
        "Revenue Generated": [120000.0, 180000.0, 90000.0, 210000.0],  # Total: 600,000.0
        "ROI %": [140.0, 80.0, 50.0, 133.33],
        "ROAS": [2.4, 1.8, 1.5, 2.33],
        "CTR %": [5.0, 5.0, 3.0, 4.0],
        "Conversion Rate %": [5.0, 5.0, 5.0, 5.0],
        "Lead Conversion Rate %": [25.0, 25.0, 25.0, 25.0],
        "CPC": [100.0, 100.0, 66.67, 56.25],
        "CPM": [5000.0, 5000.0, 2000.0, 2250.0],
        "CAC": [2000.0, 2000.0, 1333.33, 1125.0],
        "CPL": [500.0, 500.0, 333.33, 281.25],
    }
    return pd.DataFrame(data)


def test_safe_divide():
    """Verify safe division prevents zero division and NaN/infinite crashes."""
    assert safe_divide(100, 20) == 5.0
    assert safe_divide(100, 0) == 0.0
    assert safe_divide(100, 0, default=-1.0) == -1.0
    assert safe_divide(np.nan, 20) == 0.0
    assert safe_divide(100, np.nan) == 0.0
    assert safe_divide(None, 20) == 0.0


def test_calculate_kpis_exact_math(mock_campaign_df):
    """
    Verify calculate_kpis matches exact sums and derived ratios:
    Total Spend = 300,000
    Total Revenue = 600,000
    Net Profit = 300,000
    ROI% = (600,000 - 300,000) / 300,000 * 100 = 100.0%
    ROAS = 600,000 / 300,000 = 2.0x
    Total Impressions = 100,000
    Total Clicks = 4,000 -> CTR% = 4,000 / 100,000 * 100 = 4.0%
    Total Leads = 800 -> Lead Conv% = 200 / 800 * 100 = 25.0%
    Total Conversions = 200 -> Conv Rate% = 200 / 4,000 * 100 = 5.0%
    CPC = 300,000 / 4,000 = 75.0
    CPM = 300,000 / 100,000 * 1000 = 3000.0
    CAC = 300,000 / 200 = 1500.0
    CPL = 300,000 / 800 = 375.0
    """
    kpis = calculate_kpis(mock_campaign_df)

    assert kpis["campaign_count"] == 4
    assert kpis["total_spend"] == 300000.0
    assert kpis["total_revenue"] == 600000.0
    assert kpis["net_profit"] == 300000.0
    assert kpis["roi_pct"] == 100.0
    assert kpis["roas"] == 2.0
    assert kpis["total_impressions"] == 100000
    assert kpis["total_clicks"] == 4000
    assert kpis["ctr_pct"] == 4.0
    assert kpis["total_leads"] == 800
    assert kpis["total_conversions"] == 200
    assert kpis["conversion_rate_pct"] == 5.0
    assert kpis["lead_conversion_rate_pct"] == 25.0
    assert kpis["cpc"] == 75.0
    assert kpis["cpm"] == 3000.0
    assert kpis["cac"] == 1500.0
    assert kpis["cpl"] == 375.0


def test_aggregated_roi_differs_from_mean_row_level_roi():
    """
    CRITICAL AGGREGATION RULE PROOF:
    Demonstrates mathematically why row-level averaging of ratios is fundamentally flawed
    and proves that calculate_kpis strictly uses summed numerators and denominators.

    Scenario:
    - Campaign A: Tiny spend ₹1,000, revenue ₹10,000 -> ROI = 900%
    - Campaign B: Large spend ₹100,000, revenue ₹50,000 -> ROI = -50%

    Row-level mean ROI: (900% + -50%) / 2 = +425% (Falsely suggests massive profitability!)
    True Aggregate ROI: Total Rev ₹60,000 - Total Spend ₹101,000 = -₹41,000 (Actual Net Loss!)
    True ROI% = (-41,000 / 101,000) * 100 = -40.59%
    """
    df_imbalanced = pd.DataFrame(
        {
            "Campaign ID": ["CMP-A", "CMP-B"],
            "Marketing Spend": [1000.0, 100000.0],
            "Revenue Generated": [10000.0, 50000.0],
            "Impressions": [1000, 100000],
            "Clicks": [100, 2000],
            "Leads Generated": [20, 200],
            "Conversions": [5, 50],
            "ROI %": [900.0, -50.0],
        }
    )

    mean_row_roi = df_imbalanced["ROI %"].mean()
    kpis = calculate_kpis(df_imbalanced)
    aggregated_roi = kpis["roi_pct"]

    # Verify that the two values differ radically
    assert mean_row_roi == 425.0
    assert aggregated_roi == -40.59
    assert abs(mean_row_roi - aggregated_roi) > 400.0

    # Ensure calculate_kpis uses the true aggregated ROI, not the average of rows
    assert kpis["roi_pct"] == -40.59
    assert kpis["roas"] == 0.59


def test_group_metrics_preserves_aggregation_rule(mock_campaign_df):
    """
    Verify that group_metrics calculates group-level KPIs from summed numerators
    and denominators per group, not row averages.
    """
    grouped_platform = group_metrics(mock_campaign_df, by="Platform", sort_by="Marketing Spend", ascending=False)

    assert len(grouped_platform) == 2
    assert "Google" in grouped_platform["Platform"].values
    assert "Facebook" in grouped_platform["Platform"].values

    # Check Google group:
    # Spend = 50k + 100k = 150k
    # Revenue = 120k + 180k = 300k
    # ROI% = (300k - 150k) / 150k * 100 = 100.0%
    google_row = grouped_platform[grouped_platform["Platform"] == "Google"].iloc[0]
    assert google_row["Marketing Spend"] == 150000.0
    assert google_row["Revenue Generated"] == 300000.0
    assert google_row["ROI %"] == 100.0
    assert google_row["ROAS"] == 2.0
    assert google_row["Campaigns"] == 2

    # Check Facebook group:
    # Spend = 60k + 90k = 150k
    # Revenue = 90k + 210k = 300k
    # ROI% = (300k - 150k) / 150k * 100 = 100.0%
    fb_row = grouped_platform[grouped_platform["Platform"] == "Facebook"].iloc[0]
    assert fb_row["Marketing Spend"] == 150000.0
    assert fb_row["Revenue Generated"] == 300000.0
    assert fb_row["ROI %"] == 100.0


def test_funnel_data(mock_campaign_df):
    """Verify funnel analysis stage drop-offs and overall throughput percentages."""
    funnel = funnel_data(mock_campaign_df)

    assert len(funnel) == 4
    stages = funnel["Stage"].tolist()
    assert stages == ["Impressions", "Clicks", "Leads", "Conversions"]

    impr_row = funnel[funnel["Stage"] == "Impressions"].iloc[0]
    assert impr_row["Count"] == 100000
    assert impr_row["Stage_Conv_Pct"] == 100.0

    clicks_row = funnel[funnel["Stage"] == "Clicks"].iloc[0]
    assert clicks_row["Count"] == 4000
    assert clicks_row["Stage_Conv_Pct"] == 4.0
    assert clicks_row["Drop_Off_Pct"] == 96.0

    leads_row = funnel[funnel["Stage"] == "Leads"].iloc[0]
    assert leads_row["Count"] == 800
    assert leads_row["Stage_Conv_Pct"] == 20.0  # 800 / 4000
    assert leads_row["Drop_Off_Pct"] == 80.0

    conv_row = funnel[funnel["Stage"] == "Conversions"].iloc[0]
    assert conv_row["Count"] == 200
    assert conv_row["Stage_Conv_Pct"] == 25.0  # 200 / 800
    assert conv_row["Drop_Off_Pct"] == 75.0


def test_top_and_bottom_campaigns(mock_campaign_df):
    """Verify top/bottom ranking, min_spend qualification, and CAC logic."""
    # Top 2 by ROI with min spend 55k should filter out CMP-001 (spend 50k)
    top_roi = get_top_campaigns(mock_campaign_df, metric="ROI %", n=2, min_spend=55000.0)
    assert len(top_roi) == 2
    assert "CMP-001" not in top_roi["Campaign ID"].values
    assert top_roi.iloc[0]["Campaign ID"] == "CMP-004"  # ROI 133.33%

    # Bottom 1 by Revenue
    bot_rev = get_bottom_campaigns(mock_campaign_df, metric="Revenue Generated", n=1)
    assert len(bot_rev) == 1
    assert bot_rev.iloc[0]["Campaign ID"] == "CMP-003"  # Revenue 90k

    # Top by CAC: For CAC, lower is better!
    # CMP-004 CAC is 1125, CMP-003 is 1333, CMP-001/002 is 2000
    top_cac = get_top_campaigns(mock_campaign_df, metric="CAC", n=1)
    assert top_cac.iloc[0]["Campaign ID"] == "CMP-004"  # Lowest CAC

    # Bottom by CAC: Highest CAC
    bot_cac = get_bottom_campaigns(mock_campaign_df, metric="CAC", n=2)
    assert bot_cac.iloc[0]["CAC"] == 2000.0


def test_budget_opportunities():
    """Verify allocation opportunity flagging (Scale Up vs Reduce/Optimise)."""
    df_budget = pd.DataFrame(
        {
            "Campaign ID": ["C1", "C2", "C3"],
            "Platform": ["Email", "Google", "Facebook"],
            "Marketing Spend": [10000.0, 60000.0, 30000.0],  # Total 100k (Email share = 10%)
            "Revenue Generated": [50000.0, 80000.0, 25000.0],  # Total 155k (Email ROI = 400%)
        }
    )
    # Overall ROI: (155k - 100k) / 100k = 55%
    # Avg Spend Share: 100% / 3 = 33.33%

    opps = budget_opportunities(df_budget, dimension="Platform")

    # Email has 400% ROI (> 55%) and 10% spend share (< 33.33%) -> Scale Up!
    email_opp = opps[opps["Platform"] == "Email"].iloc[0]
    assert "Scale Up" in email_opp["Action_Recommendation"]

    # Facebook has -16.67% ROI (< 55%) and 30% spend share (< 33.33%) -> Monitor/Test
    # Google has 33.33% ROI (< 55%) and 60% spend share (> 33.33%) -> Reduce/Optimise
    google_opp = opps[opps["Platform"] == "Google"].iloc[0]
    assert "Reduce / Optimise" in google_opp["Action_Recommendation"]


def test_format_indian_currency():
    """Verify Indian currency abbreviation formatting in Lakhs and Crores."""
    assert format_indian_currency(12500000) == "₹1.25Cr"
    assert format_indian_currency(1240000) == "₹12.40L"
    assert format_indian_currency(45200.5) == "₹45,200.50"
    assert format_indian_currency(-250000) == "-₹2.50L"
    assert format_indian_currency(0) == "₹0.00"
    assert format_indian_currency(np.nan) == "₹0.00"


def test_empty_dataframe_handling():
    """Verify all metric functions handle empty DataFrames safely without crashing."""
    df_empty = pd.DataFrame()
    kpis = calculate_kpis(df_empty)
    assert kpis["campaign_count"] == 0
    assert kpis["total_spend"] == 0.0

    grouped = group_metrics(df_empty, by="Platform")
    assert len(grouped) == 0

    funnel = funnel_data(df_empty)
    assert len(funnel) == 0

    top = get_top_campaigns(df_empty)
    assert len(top) == 0

    opps = budget_opportunities(df_empty)
    assert len(opps) == 0


def test_real_clean_dataset_kpis():
    """Integration test against actual processed dataset."""
    clean_path = "data/processed/marketing_campaigns_clean.csv"
    if os.path.exists(clean_path):
        df_clean = pd.read_csv(clean_path)
        kpis = calculate_kpis(df_clean)
        assert kpis["campaign_count"] == 214
        assert kpis["total_spend"] > 0
        assert kpis["total_revenue"] > 0
        assert kpis["total_conversions"] > 0
        assert kpis["roas"] > 0
