"""
Auto-Generated Strategic Insights Panel Component
Computes reactive text insights from the active filtered dataset:
- Best performing platform
- Worst performing campaign / capital drag
- Biggest scale-up budget opportunity
- Funnel bottleneck & retention leakage
Zero hardcoded numbers; all figures computed directly from active filters.
"""

import pandas as pd
import streamlit as st

from app.components.card import render_card_header
from app.theme import (
    render_html,
)
from src.metrics import (
    budget_opportunities,
    format_indian_currency,
    funnel_data,
    get_bottom_campaigns,
    group_metrics,
)


def render_insights_panel(df: pd.DataFrame):
    """
    Renders the auto-generated executive intelligence panel summarizing
    best platform, worst campaign, scale-up opportunities, and funnel leaks.
    """
    with st.container(border=True):
        render_card_header("EXECUTIVE STRATEGIC INTELLIGENCE", badge="AUTO-GENERATED INSIGHTS")

        if df is None or len(df) == 0:
            st.info("No campaign records match the current filter criteria to synthesize insights.")
            return

        # 1. Best Platform by ROI
        plat_df = group_metrics(df, by="Platform", sort_by="ROI %", ascending=False)
        if len(plat_df) > 0:
            best_plat_row = plat_df.iloc[0]
            best_plat_name = best_plat_row["Platform"]
            best_plat_roi = best_plat_row["ROI %"]
            best_plat_spend = best_plat_row["Marketing Spend"]
            best_plat_rev = best_plat_row["Revenue Generated"]
            best_plat_cac = best_plat_row["CAC"]
        else:
            best_plat_name = "N/A"
            best_plat_roi = 0.0

        # 2. Worst Campaign (Capital Drag)
        bottom_camps = get_bottom_campaigns(df, metric="ROI %", n=1, min_spend=10000.0)
        has_worst = len(bottom_camps) > 0
        if has_worst:
            worst_camp = bottom_camps.iloc[0]
            worst_name = worst_camp["Campaign Name"]
            worst_plat = worst_camp["Platform"]
            worst_roi = worst_camp["ROI %"]
            worst_spend = worst_camp["Marketing Spend"]
            worst_cac = worst_camp["CAC"]
        else:
            worst_name = "N/A"

        # 3. Scale-Up Opportunity
        opps_df = budget_opportunities(df, dimension="Platform")
        scale_opps = (
            opps_df[opps_df["Action_Recommendation"].str.contains("Scale Up", na=False)]
            if len(opps_df) > 0
            else pd.DataFrame()
        )
        if len(scale_opps) > 0:
            top_opp = scale_opps.iloc[0]
            opp_segment = f"{top_opp['Platform']} (Channel)"
            opp_roi = top_opp["ROI %"]
            opp_share = top_opp["Spend_Share_Pct"]
        else:
            # Fallback to top platform
            opp_segment = f"{best_plat_name} (Channel)"
            opp_roi = best_plat_roi
            total_m_spend = df["Marketing Spend"].sum()
            opp_share = (best_plat_spend / total_m_spend * 100) if total_m_spend > 0 else 0.0

        # 4. Funnel Leakage Diagnostic
        f_data = funnel_data(df)
        ctr_drop = f_data.loc[f_data["Stage"] == "Clicks", "Drop_Off_Pct"].values[0] if len(f_data) > 1 else 0
        lead_drop = f_data.loc[f_data["Stage"] == "Leads", "Drop_Off_Pct"].values[0] if len(f_data) > 2 else 0
        conv_drop = f_data.loc[f_data["Stage"] == "Conversions", "Drop_Off_Pct"].values[0] if len(f_data) > 3 else 0

        # Determine largest leakage point
        if conv_drop >= 65:
            leak_msg = f"Final checkout abandon rate is elevated (-{conv_drop:.1f}% lead-to-conversion bounce). Audit friction in checkout flows."
        elif lead_drop >= 75:
            leak_msg = f"Click-to-lead qualification drop-off is severe (-{lead_drop:.1f}%). Optimize landing page copy and lead magnets."
        else:
            leak_msg = f"Top-of-funnel CTR leakage is -{ctr_drop:.1f}%. Refresh ad hooks and visual creatives to boost engagement."

        # Layout into 3 columns
        c1, c2, c3 = st.columns(3)

        with c1:
            render_html(f"""
            <div style="background: rgba(0, 0, 0, 0.25); border: 1px solid rgba(233, 169, 75, 0.25);
                        border-radius: 12px; padding: 0.85rem 1rem; height: 100%;">
                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.4rem;">
                    <span style="font-size: 1.15rem;">🏆</span>
                    <span style="font-size: 0.72rem; color: #8E8F96; text-transform: uppercase; letter-spacing: 0.08em; font-weight: 700;">Top Efficiency Channel</span>
                </div>
                <div style="font-size: 1.1rem; font-weight: 700; color: #F3C477; font-family: 'Outfit', sans-serif;">
                    {best_plat_name}
                </div>
                <div style="font-size: 0.82rem; color: #34D399; font-weight: 700; margin: 0.2rem 0;">
                    {best_plat_roi:+.1f}% ROI &bull; CAC: ₹{best_plat_cac:,.0f}
                </div>
                <div style="font-size: 0.75rem; color: #B0B1B9; line-height: 1.45;">
                    Generated <b>{format_indian_currency(best_plat_rev)}</b> revenue on <b>{format_indian_currency(best_plat_spend)}</b> spend. Prioritize this channel for primary baseline allocations.
                </div>
            </div>
            """)

        with c2:
            if has_worst:
                worst_content = f"""
                <div style="font-size: 1.1rem; font-weight: 700; color: #F87171; font-family: 'Outfit', sans-serif;">
                    {worst_name[:24]}
                </div>
                <div style="font-size: 0.82rem; color: #F87171; font-weight: 700; margin: 0.2rem 0;">
                    {worst_roi:+.1f}% ROI &bull; {worst_plat}
                </div>
                <div style="font-size: 0.75rem; color: #B0B1B9; line-height: 1.45;">
                    Absorbed <b>{format_indian_currency(worst_spend)}</b> spend with high acquisition cost (CAC: <b>₹{worst_cac:,.0f}</b>). Recommend pausing or reallocating to top performers.
                </div>
                """
            else:
                worst_content = """
                <div style="font-size: 0.85rem; color: #34D399; padding-top: 0.5rem;">
                    No severe budget drags qualifying under the ₹10k minimum spend threshold.
                </div>
                """

            render_html(f"""
            <div style="background: rgba(0, 0, 0, 0.25); border: 1px solid rgba(224, 83, 83, 0.25);
                        border-radius: 12px; padding: 0.85rem 1rem; height: 100%;">
                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.4rem;">
                    <span style="font-size: 1.15rem;">🛑</span>
                    <span style="font-size: 0.72rem; color: #8E8F96; text-transform: uppercase; letter-spacing: 0.08em; font-weight: 700;">Primary Capital Drag</span>
                </div>
                {worst_content}
            </div>
            """)

        with c3:
            render_html(f"""
            <div style="background: rgba(0, 0, 0, 0.25); border: 1px solid rgba(52, 211, 153, 0.25);
                        border-radius: 12px; padding: 0.85rem 1rem; height: 100%;">
                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.4rem;">
                    <span style="font-size: 1.15rem;">🚀</span>
                    <span style="font-size: 0.72rem; color: #8E8F96; text-transform: uppercase; letter-spacing: 0.08em; font-weight: 700;">Scale-Up Opportunity</span>
                </div>
                <div style="font-size: 1.1rem; font-weight: 700; color: #34D399; font-family: 'Outfit', sans-serif;">
                    {opp_segment}
                </div>
                <div style="font-size: 0.82rem; color: #F3C477; font-weight: 700; margin: 0.2rem 0;">
                    {opp_roi:+.1f}% ROI on {opp_share:.1f}% Spend Share
                </div>
                <div style="font-size: 0.75rem; color: #B0B1B9; line-height: 1.45;">
                    {leak_msg}
                </div>
            </div>
            """)
