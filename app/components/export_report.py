"""
Executive Summary Report Export Generator
Produces a high-fidelity, self-contained executive report in HTML
(with dark/gold dashboard aesthetics and print-optimized PDF styling)
containing current KPIs, channel metrics, and strategic recommendations.
"""

from datetime import datetime

import pandas as pd
import streamlit as st

from src.metrics import (
    calculate_kpis,
    format_indian_currency,
    group_metrics,
)


def generate_executive_report_html(df: pd.DataFrame, target_roi: float = 300.0) -> str:
    """
    Generates a standalone, beautifully styled HTML executive report
    documenting active portfolio performance, channel matrices, and insights.
    """
    kpis = calculate_kpis(df)
    plat_df = group_metrics(df, by="Platform", sort_by="Marketing Spend")

    # Channel table rows
    table_rows = []
    for _, r in plat_df.iterrows():
        roi_color = "#34D399" if r["ROI %"] >= 60 else ("#E9A94B" if r["ROI %"] >= 25 else "#E05353")
        table_rows.append(f"""
        <tr>
            <td style="font-weight: 600;">{r["Platform"]}</td>
            <td>{format_indian_currency(r["Marketing Spend"])}</td>
            <td>{format_indian_currency(r["Revenue Generated"])}</td>
            <td style="font-weight: 700; color: {roi_color};">{r["ROI %"]:+.1f}%</td>
            <td>{r["ROAS"]:.2f}x</td>
            <td>{r["CTR %"]:.2f}%</td>
            <td>{r["Conversion Rate %"]:.1f}%</td>
            <td>₹{r["CAC"]:,.0f}</td>
        </tr>
        """)

    # Strategic insights summary
    best_plat = plat_df.iloc[0]["Platform"] if len(plat_df) > 0 else "N/A"
    best_roi = plat_df.iloc[0]["ROI %"] if len(plat_df) > 0 else 0.0

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Executive Marketing Campaign Audit Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background-color: #0E0E10;
            color: #F5F5F7;
            margin: 0;
            padding: 2.5rem;
            line-height: 1.5;
        }}
        .report-header {{
            border-bottom: 2px solid #E9A94B;
            padding-bottom: 1.2rem;
            margin-bottom: 2rem;
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
        }}
        .brand-title {{
            font-size: 1.6rem;
            font-weight: 800;
            letter-spacing: -0.02em;
            color: #F5F5F7;
        }}
        .brand-gold {{
            color: #E9A94B;
        }}
        .meta-text {{
            font-size: 0.8rem;
            color: #8E8F96;
            margin-top: 0.2rem;
        }}
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 1rem;
            margin-bottom: 2rem;
        }}
        .kpi-card {{
            background: #1A1B1F;
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 10px;
            padding: 1rem;
            text-align: center;
        }}
        .kpi-label {{
            font-size: 0.7rem;
            color: #8E8F96;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 0.3rem;
        }}
        .kpi-val {{
            font-size: 1.5rem;
            font-weight: 800;
            color: #F3C477;
        }}
        .kpi-sub {{
            font-size: 0.72rem;
            color: #34D399;
            margin-top: 0.25rem;
        }}
        .section-title {{
            font-size: 1rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            color: #E9A94B;
            margin: 1.8rem 0 0.8rem 0;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background: #1A1B1F;
            border-radius: 8px;
            overflow: hidden;
            font-size: 0.82rem;
            margin-bottom: 2rem;
        }}
        th {{
            background: rgba(255, 255, 255, 0.05);
            color: #8E8F96;
            text-transform: uppercase;
            font-size: 0.72rem;
            letter-spacing: 0.05em;
            padding: 0.65rem 0.8rem;
            text-align: left;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }}
        td {{
            padding: 0.65rem 0.8rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.04);
            color: #D1D2D8;
        }}
        .insights-box {{
            background: rgba(233, 169, 75, 0.08);
            border-left: 4px solid #E9A94B;
            border-radius: 4px;
            padding: 1rem 1.25rem;
            font-size: 0.84rem;
            line-height: 1.6;
        }}
        @media print {{
            body {{
                background-color: #FFFFFF !important;
                color: #111111 !important;
                padding: 1rem !important;
            }}
            .kpi-card, table {{
                background: #F9F9FB !important;
                border: 1px solid #E5E7EB !important;
            }}
            .kpi-val, .brand-gold, .section-title {{
                color: #B45309 !important;
            }}
            th {{
                background: #E5E7EB !important;
                color: #374151 !important;
            }}
            td {{
                color: #1F2937 !important;
            }}
            .insights-box {{
                background: #FFFBEB !important;
                border-left-color: #D97706 !important;
                color: #1F2937 !important;
            }}
        }}
    </style>
</head>
<body>
    <div class="report-header">
        <div>
            <div class="brand-title">⚡ NEXUS <span class="brand-gold">ANALYTICS</span></div>
            <div class="meta-text">Executive Marketing Performance & Attribution Audit</div>
        </div>
        <div style="text-align: right;">
            <div class="meta-text">Generated: <b>{datetime.now().strftime("%d %b %Y, %H:%M IST")}</b></div>
            <div class="meta-text">Active Filter Sample: <b>{kpis["campaign_count"]} Campaigns</b></div>
        </div>
    </div>

    <div class="kpi-grid">
        <div class="kpi-card">
            <div class="kpi-label">Total Media Spend</div>
            <div class="kpi-val" style="color: #F5F5F7;">{format_indian_currency(kpis["total_spend"])}</div>
            <div class="kpi-sub" style="color: #8E8F96;">Across {len(plat_df)} Channels</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Gross Revenue</div>
            <div class="kpi-val">{format_indian_currency(kpis["total_revenue"])}</div>
            <div class="kpi-sub">Net: {format_indian_currency(kpis["net_profit"])}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Portfolio ROI</div>
            <div class="kpi-val">{kpis["roi_pct"]:+.1f}%</div>
            <div class="kpi-sub">ROAS: {kpis["roas"]:.2f}x</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Customer Acquisition CAC</div>
            <div class="kpi-val" style="color: #F5F5F7;">₹{kpis["cac"]:,.0f}</div>
            <div class="kpi-sub">{kpis["total_conversions"]:,} Conversions</div>
        </div>
    </div>

    <div class="section-title">Channel Performance & Efficiency Matrix</div>
    <table>
        <thead>
            <tr>
                <th>Channel</th>
                <th>Spend</th>
                <th>Revenue</th>
                <th>ROI %</th>
                <th>ROAS</th>
                <th>CTR %</th>
                <th>Conv %</th>
                <th>CAC</th>
            </tr>
        </thead>
        <tbody>
            {"".join(table_rows)}
        </tbody>
    </table>

    <div class="section-title">Executive Strategic Findings & Prescriptions</div>
    <div class="insights-box">
        <p style="margin: 0 0 0.5rem 0;">
            <b>1. Primary Capital Efficiency Leader:</b> <b>{best_plat}</b> delivers the highest return across active channels at <b>{best_roi:+.1f}% ROI</b>. Recommend protecting baseline budget allocations and exploring creative scaling.
        </p>
        <p style="margin: 0 0 0.5rem 0;">
            <b>2. Funnel Conversion Leakage:</b> Total audience engagement produced <b>{kpis["total_clicks"]:,} clicks</b> converting to <b>{kpis["total_conversions"]:,} customer purchases</b> ({kpis["conversion_rate_pct"]:.1f}% conversion rate). Focus CRO investments on checkout funnel friction.
        </p>
        <p style="margin: 0;">
            <b>3. Target Pacing:</b> Portfolio ROI is currently pacing at <b>{kpis["roi_pct"]:+.1f}%</b> relative to the executive benchmark target of <b>{target_roi:.0f}%</b>.
        </p>
    </div>

    <div style="margin-top: 2.5rem; border-top: 1px solid rgba(255, 255, 255, 0.08); padding-top: 0.8rem; font-size: 0.7rem; color: #5C5E6B; display: flex; justify-content: space-between;">
        <div>Nexus Marketing Analytics Engine &bull; Portfolio Audit Standards</div>
        <div>To export as PDF: Open in browser and press <b>Ctrl + P</b> (Save as PDF)</div>
    </div>
</body>
</html>
"""
    return html


def render_export_button(df: pd.DataFrame, target_roi: float = 300.0):
    """
    Renders the executive summary download button.
    """
    html_content = generate_executive_report_html(df, target_roi=target_roi)
    st.download_button(
        label="📄 Download Executive Summary (HTML / Print to PDF)",
        data=html_content.encode("utf-8"),
        file_name=f"executive_marketing_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
        mime="text/html",
        key="btn_download_exec_summary",
        use_container_width=True,
    )
