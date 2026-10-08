import os
import sys

import numpy as np
import pandas as pd

# Ensure utf-8 stdout on Windows
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

# Add repo to sys.path
sys.path.append(os.path.abspath("."))

from src.metrics import (
    calculate_kpis,
)


def run_number_verification():
    print("=== NUMBER VERIFICATION (INDEPENDENT PANDAS VS METRICS ENGINE) ===")
    df = pd.read_csv("data/processed/marketing_campaigns_clean.csv")

    # Independent Pandas Recomputation
    spend_raw = df["Marketing Spend"].sum()
    revenue_raw = df["Revenue Generated"].sum()
    impressions_raw = df["Impressions"].sum()
    clicks_raw = df["Clicks"].sum()
    leads_raw = df["Leads Generated"].sum()
    conversions_raw = df["Conversions"].sum()

    indep_spend = spend_raw
    indep_rev = revenue_raw
    indep_roi = ((revenue_raw - spend_raw) / spend_raw) * 100
    indep_ctr = (clicks_raw / impressions_raw) * 100
    indep_conv_rate = (conversions_raw / clicks_raw) * 100
    indep_lead_conv_rate = (conversions_raw / leads_raw) * 100
    indep_cac = spend_raw / conversions_raw

    # Engine Computation
    engine_kpis = calculate_kpis(df)

    print(f"Total Spend: Independent = ₹{indep_spend:,.2f} | Engine = ₹{engine_kpis['total_spend']:,.2f}")
    assert np.isclose(indep_spend, engine_kpis["total_spend"], atol=0.05), "Spend mismatch!"

    print(f"Total Revenue: Independent = ₹{indep_rev:,.2f} | Engine = ₹{engine_kpis['total_revenue']:,.2f}")
    assert np.isclose(indep_rev, engine_kpis["total_revenue"], atol=0.05), "Revenue mismatch!"

    print(f"Overall ROI%: Independent = {indep_roi:.2f}% | Engine = {engine_kpis['roi_pct']:.2f}%")
    assert np.isclose(round(indep_roi, 2), engine_kpis["roi_pct"], atol=0.01), "ROI mismatch!"

    print(f"CTR%: Independent = {indep_ctr:.2f}% | Engine = {engine_kpis['ctr_pct']:.2f}%")
    assert np.isclose(round(indep_ctr, 2), engine_kpis["ctr_pct"], atol=0.01), "CTR mismatch!"

    print(f"Conv. Rate%: Independent = {indep_conv_rate:.2f}% | Engine = {engine_kpis['conversion_rate_pct']:.2f}%")
    assert np.isclose(round(indep_conv_rate, 2), engine_kpis["conversion_rate_pct"], atol=0.01), "Conv Rate mismatch!"

    print(
        f"Lead Conv. Rate%: Independent = {indep_lead_conv_rate:.2f}% | Engine = {engine_kpis['lead_conversion_rate_pct']:.2f}%"
    )
    assert np.isclose(round(indep_lead_conv_rate, 2), engine_kpis["lead_conversion_rate_pct"], atol=0.01), (
        "Lead Conv Rate mismatch!"
    )

    print(f"CAC: Independent = ₹{indep_cac:.2f} | Engine = ₹{engine_kpis['cac']:.2f}")
    assert np.isclose(round(indep_cac, 2), engine_kpis["cac"], atol=0.05), "CAC mismatch!"

    print(">>> 5 KPI INDEPENDENT VERIFICATION PASSED PERFECTLY!\n")


if __name__ == "__main__":
    run_number_verification()
