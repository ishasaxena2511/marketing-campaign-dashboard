"""
Campaign Drill-Down Component Suite
Renders deep single-campaign telemetry:
1. Interactive Campaign Selector with rich metadata
2. Daily-style Run-Rate Metrics (Daily Spend, Daily Revenue, Daily Conversions, Pace)
3. Single-Campaign 4-Stage Conversion Funnel with drop-off diagnostics
4. Side-by-Side Comparison vs. Platform Benchmark (ROI, CTR, Conv Rate, CAC)
5. Dynamic Plain-English Verdict & Strategic Prescription
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app.components.card import render_card_header
from app.theme import (
    ACCENT_GOLD,
    ACCENT_GOLD_LIGHT,
    STATUS_DANGER,
    STATUS_SUCCESS,
    TEXT_PRIMARY,
    get_plotly_layout,
    render_html,
)
from src.metrics import (
    calculate_kpis,
)


def render_campaign_drilldown(df: pd.DataFrame):
    """
    Renders deep-dive telemetry and plain-English evaluation for a selected campaign.
    """
    render_card_header("CAMPAIGN TELEMETRY & ATTRIBUTION DRILL-DOWN", badge="SINGLE CAMPAIGN")

    if df is None or len(df) == 0:
        st.info("No campaign records match the current filters.")
        return

    # Campaign selection dropdown
    df_sorted = df.sort_values(by="Marketing Spend", ascending=False).reset_index(drop=True)
    camp_options = [
        f"{row['Campaign ID']} | {row['Campaign Name']} ({row['Platform']})" for _, row in df_sorted.iterrows()
    ]

    selected_label = st.selectbox(
        "Select Campaign to Inspect",
        options=camp_options,
        index=0,
        help="Select any campaign from the filtered portfolio to view its funnel, run-rate, and channel benchmark comparison.",
    )

    selected_id = selected_label.split(" | ")[0].strip()
    matches = df[df["Campaign ID"] == selected_id]
    if len(matches) == 0:
        st.info("Selected campaign not found in filtered data.")
        return
    camp_row = matches.iloc[0]

    # Campaign Metadata Banner
    dur_days = max(1, int(camp_row["Duration Days"])) if "Duration Days" in camp_row else 30
    render_html(f"""
    <div style="background: rgba(0, 0, 0, 0.28); border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 12px; padding: 0.75rem 1rem; margin: 0.8rem 0 1rem 0;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 0.5rem;">
            <div>
                <div style="font-size: 0.70rem; color: #8E8F96; text-transform: uppercase; letter-spacing: 0.06em;">Campaign Name & Target</div>
                <div style="font-size: 1.15rem; font-weight: 700; color: #F5F5F7; font-family: 'Outfit', sans-serif;">{camp_row["Campaign Name"]}</div>
                <div style="font-size: 0.76rem; color: #E9A94B; margin-top: 0.15rem;">
                    <b>{camp_row["Platform"]}</b> &bull; {camp_row["Campaign Type"]} &bull; {camp_row["Audience Segment"]} &bull; {camp_row["Region"]}
                </div>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 0.70rem; color: #8E8F96; text-transform: uppercase;">Flight Duration</div>
                <div style="font-size: 0.95rem; font-weight: 700; color: #F5F5F7;">{dur_days} Days</div>
                <div style="font-size: 0.70rem; color: #8E8F96;">{str(camp_row["Campaign Start Date"])[:10]} to {str(camp_row["Campaign End Date"])[:10]}</div>
            </div>
        </div>
    </div>
    """)

    # 1. Daily Run-Rate Metrics Row
    d_spend = camp_row["Marketing Spend"] / dur_days
    d_rev = camp_row["Revenue Generated"] / dur_days
    d_conv = camp_row["Conversions"] / dur_days
    d_clicks = camp_row["Clicks"] / dur_days

    r1, r2, r3, r4 = st.columns(4)
    with r1:
        render_html(f"""
        <div style="background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 8px; padding: 0.5rem 0.7rem; text-align: center;">
            <div style="font-size: 0.65rem; color: #8E8F96; text-transform: uppercase;">Daily Burn Rate</div>
            <div style="font-size: 1.05rem; font-weight: 700; color: #F5F5F7; font-family: 'Outfit', sans-serif;">₹{d_spend:,.0f}<span style="font-size: 0.7rem; color: #8E8F96;">/day</span></div>
        </div>
        """)
    with r2:
        render_html(f"""
        <div style="background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 8px; padding: 0.5rem 0.7rem; text-align: center;">
            <div style="font-size: 0.65rem; color: #8E8F96; text-transform: uppercase;">Daily Revenue Run-Rate</div>
            <div style="font-size: 1.05rem; font-weight: 700; color: #F3C477; font-family: 'Outfit', sans-serif;">₹{d_rev:,.0f}<span style="font-size: 0.7rem; color: #8E8F96;">/day</span></div>
        </div>
        """)
    with r3:
        render_html(f"""
        <div style="background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 8px; padding: 0.5rem 0.7rem; text-align: center;">
            <div style="font-size: 0.65rem; color: #8E8F96; text-transform: uppercase;">Daily Conversions</div>
            <div style="font-size: 1.05rem; font-weight: 700; color: #34D399; font-family: 'Outfit', sans-serif;">{d_conv:.1f}<span style="font-size: 0.7rem; color: #8E8F96;">/day</span></div>
        </div>
        """)
    with r4:
        render_html(f"""
        <div style="background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 8px; padding: 0.5rem 0.7rem; text-align: center;">
            <div style="font-size: 0.65rem; color: #8E8F96; text-transform: uppercase;">Daily Click Cadence</div>
            <div style="font-size: 1.05rem; font-weight: 700; color: #F5F5F7; font-family: 'Outfit', sans-serif;">{d_clicks:,.0f}<span style="font-size: 0.7rem; color: #8E8F96;">/day</span></div>
        </div>
        """)

    # 2. Main Middle Section: Single-Campaign Funnel (Left) + Benchmark Comparison (Right)
    col_funnel, col_bench = st.columns([1.15, 1.25])

    with col_funnel:
        render_html("""
        <div style="font-size: 0.72rem; color: #8E8F96; text-transform: uppercase; letter-spacing: 0.08em; margin: 0.8rem 0 0.4rem 0;">
            Campaign Funnel Throughput
        </div>
        """)

        stages = ["Impressions", "Clicks", "Leads", "Conversions"]
        counts = [
            camp_row["Impressions"],
            camp_row["Clicks"],
            camp_row["Leads Generated"],
            camp_row["Conversions"],
        ]

        fig_cf = go.Figure(
            go.Funnel(
                y=stages,
                x=counts,
                texttemplate="<b>%{value:,.0f}</b><br>(%{percentPrevious:.1%})",
                textposition="inside",
                textfont=dict(family="Outfit", size=10, color="#0E0E10"),
                marker=dict(
                    color=[ACCENT_GOLD_LIGHT, ACCENT_GOLD, "#C88B35", "#8E6527"],
                    line=dict(color="rgba(255, 255, 255, 0.15)", width=1),
                ),
                connector=dict(line=dict(color="rgba(233, 169, 75, 0.25)", width=1)),
                hovertemplate=(
                    "<b>%{y}</b><br>Volume: <b>%{x:,.0f}</b><br>Throughput: <b>%{percentInitial:.3%}</b><extra></extra>"
                ),
            )
        )
        layout_cf = get_plotly_layout(height=260, show_legend=False)
        layout_cf["margin"] = dict(l=10, r=10, t=10, b=10)
        fig_cf.update_layout(layout_cf)
        st.plotly_chart(fig_cf, use_container_width=True, config={"displayModeBar": False})

    with col_bench:
        render_html(f"""
        <div style="font-size: 0.72rem; color: #8E8F96; text-transform: uppercase; letter-spacing: 0.08em; margin: 0.8rem 0 0.4rem 0;">
            Campaign vs. {camp_row["Platform"]} Benchmark
        </div>
        """)

        # Compute platform average from all platform campaigns
        df_plat = df[df["Platform"] == camp_row["Platform"]]
        plat_kpis = calculate_kpis(df_plat)

        c_roi = camp_row["ROI %"]
        p_roi = plat_kpis["roi_pct"]
        roi_delta = c_roi - p_roi

        c_ctr = camp_row["CTR %"]
        p_ctr = plat_kpis["ctr_pct"]
        ctr_delta = c_ctr - p_ctr

        c_conv = camp_row["Conversion Rate %"]
        p_conv = plat_kpis["conversion_rate_pct"]
        conv_delta = c_conv - p_conv

        c_cac = camp_row["CAC"]
        p_cac = plat_kpis["cac"]
        cac_delta = c_cac - p_cac  # negative is good for CAC

        def get_delta_badge(val, is_cost=False, is_pct=True, suffix="%"):
            good = (val < 0) if is_cost else (val > 0)
            color = STATUS_SUCCESS if good else STATUS_DANGER
            arrow = "▼" if val < 0 else "▲"
            val_str = f"{abs(val):.2f}{suffix}" if is_pct else f"₹{abs(val):,.1f}"
            return f'<span style="color: {color}; font-weight: 700; font-size: 0.74rem;">{arrow} {val_str}</span>'

        render_html(f"""
        <div style="background: rgba(0, 0, 0, 0.22); border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 10px; padding: 0.5rem 0.8rem;">
            <table style="width: 100%; border-collapse: collapse; font-size: 0.76rem;">
                <thead>
                    <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.08); color: #8E8F96; text-transform: uppercase; font-size: 0.67rem;">
                        <th style="padding: 0.35rem 0.2rem; text-align: left;">Metric</th>
                        <th style="padding: 0.35rem 0.2rem; text-align: right;">Campaign</th>
                        <th style="padding: 0.35rem 0.2rem; text-align: right;">Channel Avg</th>
                        <th style="padding: 0.35rem 0.2rem; text-align: right;">Delta</th>
                    </tr>
                </thead>
                <tbody>
                    <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.04);">
                        <td style="padding: 0.4rem 0.2rem; font-weight: 600; color: #F5F5F7;">ROI %</td>
                        <td style="padding: 0.4rem 0.2rem; text-align: right; font-weight: 700; color: #F3C477;">{c_roi:+.1f}%</td>
                        <td style="padding: 0.4rem 0.2rem; text-align: right; color: #8E8F96;">{p_roi:+.1f}%</td>
                        <td style="padding: 0.4rem 0.2rem; text-align: right;">{get_delta_badge(roi_delta)}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.04);">
                        <td style="padding: 0.4rem 0.2rem; font-weight: 600; color: #F5F5F7;">CTR %</td>
                        <td style="padding: 0.4rem 0.2rem; text-align: right; color: #F5F5F7;">{c_ctr:.2f}%</td>
                        <td style="padding: 0.4rem 0.2rem; text-align: right; color: #8E8F96;">{p_ctr:.2f}%</td>
                        <td style="padding: 0.4rem 0.2rem; text-align: right;">{get_delta_badge(ctr_delta)}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.04);">
                        <td style="padding: 0.4rem 0.2rem; font-weight: 600; color: #F5F5F7;">Conversion Rate %</td>
                        <td style="padding: 0.4rem 0.2rem; text-align: right; color: #F5F5F7;">{c_conv:.1f}%</td>
                        <td style="padding: 0.4rem 0.2rem; text-align: right; color: #8E8F96;">{p_conv:.1f}%</td>
                        <td style="padding: 0.4rem 0.2rem; text-align: right;">{get_delta_badge(conv_delta)}</td>
                    </tr>
                    <tr>
                        <td style="padding: 0.4rem 0.2rem; font-weight: 600; color: #F5F5F7;">CAC</td>
                        <td style="padding: 0.4rem 0.2rem; text-align: right; font-weight: 600; color: #F5F5F7;">₹{c_cac:,.0f}</td>
                        <td style="padding: 0.4rem 0.2rem; text-align: right; color: #8E8F96;">₹{p_cac:,.0f}</td>
                        <td style="padding: 0.4rem 0.2rem; text-align: right;">{get_delta_badge(cac_delta, is_cost=True, is_pct=False)}</td>
                    </tr>
                </tbody>
            </table>
        </div>
        """)

    # 3. Dynamic Plain-English Strategic Verdict
    if c_roi >= p_roi + 20 and c_cac <= p_cac:
        verdict_badge = "🌟 HIGH CONVERTING STAR (SCALE ALLOCATION)"
        verdict_color = STATUS_SUCCESS
        verdict_border = "rgba(52, 211, 153, 0.35)"
        verdict_bg = "rgba(52, 211, 153, 0.08)"
        verdict_text = (
            f"This campaign significantly outperforms the {camp_row['Platform']} baseline across both "
            f"capital returns (+{roi_delta:.1f}% ROI lift) and acquisition efficiency (-₹{abs(cac_delta):,.0f} CAC advantage). "
            f"<b>Actionable Prescription:</b> Increase daily budget allocation by 20% to 30% while monitoring CPC stability."
        )
    elif c_roi > 0 and c_cac > p_cac * 1.25:
        verdict_badge = "⚠️ PROFITABLE BUT COST-INEFFICIENT (OPTIMIZE FUNNEL)"
        verdict_color = ACCENT_GOLD
        verdict_border = "rgba(233, 169, 75, 0.35)"
        verdict_bg = "rgba(233, 169, 75, 0.08)"
        verdict_text = (
            f"Generating positive revenue (+{c_roi:.1f}% ROI), but customer acquisition cost is elevated "
            f"(₹{c_cac:,.0f} vs ₹{p_cac:,.0f} channel benchmark). "
            f"<b>Actionable Prescription:</b> Audit ad creative fatigue, refresh headline copy, and streamline checkout landing page friction to bring CAC into alignment."
        )
    elif c_roi < 0:
        verdict_badge = "🛑 UNDERPERFORMING CAPITAL DRAG (PAUSE / RESTRUCTURE)"
        verdict_color = STATUS_DANGER
        verdict_border = "rgba(224, 83, 83, 0.35)"
        verdict_bg = "rgba(224, 83, 83, 0.08)"
        verdict_text = (
            f"Campaign generates negative net returns ({c_roi:+.1f}% ROI) and lags the channel average by "
            f"{abs(roi_delta):.1f}%. Capital deployed here dilutes portfolio profitability. "
            f"<b>Actionable Prescription:</b> Immediately pause active ad sets and shift remaining flight budget to top-quartile campaigns."
        )
    elif c_ctr > p_ctr * 1.3 and c_conv < p_conv * 0.7:
        verdict_badge = "⚡ HIGH ENGAGEMENT BOUNCE (AUDIT LANDING PAGE)"
        verdict_color = "#60A5FA"
        verdict_border = "rgba(96, 165, 250, 0.35)"
        verdict_bg = "rgba(96, 165, 250, 0.08)"
        verdict_text = (
            f"Top-of-funnel audience engagement is exceptionally strong ({c_ctr:.2f}% CTR), but downstream conversion rate "
            f"experiences severe leakage ({c_conv:.1f}% vs {p_conv:.1f}% channel avg). "
            f"<b>Actionable Prescription:</b> Conduct landing page conversion rate optimization (CRO), verify page load speeds, and resolve checkout payment friction."
        )
    else:
        verdict_badge = "⚖️ STABLE CHANNEL CONTRIBUTOR (MAINTAIN PACING)"
        verdict_color = TEXT_PRIMARY
        verdict_border = "rgba(255, 255, 255, 0.12)"
        verdict_bg = "rgba(255, 255, 255, 0.03)"
        verdict_text = (
            f"Campaign performs in close alignment with standard {camp_row['Platform']} benchmarks. "
            f"Delivering predictable throughput ({c_roi:+.1f}% ROI, ₹{c_cac:,.0f} CAC). "
            f"<b>Actionable Prescription:</b> Maintain existing pacing schedule and monitor weekly frequency saturation."
        )

    render_html(f"""
    <div style="background: {verdict_bg}; border: 1px solid {verdict_border}; border-radius: 10px;
                padding: 0.75rem 1rem; margin-top: 0.9rem;">
        <div style="font-size: 0.70rem; color: #8E8F96; text-transform: uppercase; letter-spacing: 0.06em;">Executive Verdict</div>
        <div style="font-size: 0.95rem; font-weight: 700; color: {verdict_color}; margin: 0.2rem 0; font-family: 'Outfit', sans-serif;">
            {verdict_badge}
        </div>
        <div style="font-size: 0.78rem; color: #D1D2D8; line-height: 1.5;">
            {verdict_text}
        </div>
    </div>
    """)
