"""
What-If Budget Reallocation & Diminishing Returns Simulator Component
Allows growth marketers and agency leadership to simulate multi-channel budget shifts:
- Platform-level budget adjustment sliders (-100% to +150%)
- Diminishing-returns response modeling via power-law elasticity (beta = 0.85)
- Clear on-screen statement of the diminishing-returns assumption
- Side-by-side Before vs. After KPI Scorecards (Spend, Revenue, ROI, Net Profit)
- Grouped cross-channel comparative visualization
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
    format_indian_currency,
    group_metrics,
    safe_divide,
)


def render_budget_optimizer(df: pd.DataFrame):
    """
    Renders the interactive what-if budget optimizer with diminishing returns.
    """
    render_card_header("STRATEGIC BUDGET OPTIMISER & WHAT-IF SIMULATOR", badge="SCENARIO MODELING")

    if df is None or len(df) == 0:
        st.info("No campaign records available to simulate budget reallocation.")
        return

    plat_df = group_metrics(df, by="Platform", sort_by="Marketing Spend", ascending=False)
    if len(plat_df) == 0:
        st.info("No platform records.")
        return

    # Diminishing Returns Assumption Banner
    render_html("""
    <div style="background: rgba(233, 169, 75, 0.08); border: 1px solid rgba(233, 169, 75, 0.30);
                border-radius: 10px; padding: 0.65rem 0.95rem; margin: 0.6rem 0 1rem 0;">
        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.25rem;">
            <span style="font-size: 1rem;">📐</span>
            <span style="font-size: 0.75rem; font-weight: 700; color: #F3C477; text-transform: uppercase; letter-spacing: 0.06em;">
                Econometric Modeling Assumption: Diminishing Marginal Returns
            </span>
        </div>
        <div style="font-size: 0.74rem; color: #D1D2D8; line-height: 1.45;">
            Media response is modeled using power-law elasticity:
            <code style="background: rgba(0,0,0,0.3); padding: 0.1rem 0.3rem; border-radius: 4px; color: #E9A94B;">
                R_proj = R_base &times; (Spend_new / Spend_base)<sup>&beta;</sup>
            </code>,
            where response elasticity <b>&beta; = 0.85</b>.
            Scaling spend encounters audience saturation and creative fatigue (marginal ROAS decays).
            Conversely, trimming budget retains high-intent core converters.
        </div>
    </div>
    """)

    # Channel Reallocation Sliders
    render_html("""
    <div style="font-size: 0.72rem; color: #8E8F96; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.5rem;">
        Adjust Capital Allocation by Channel (% Shift vs. Historical Baseline)
    </div>
    """)

    platforms = plat_df["Platform"].tolist()
    shifts = {}

    # Render sliders in a responsive 3-column grid
    cols_per_row = 3
    slider_cols = st.columns(cols_per_row)

    for i, plat in enumerate(platforms):
        with slider_cols[i % cols_per_row]:
            plat_spend = plat_df.loc[plat_df["Platform"] == plat, "Marketing Spend"].values[0]
            plat_roi = plat_df.loc[plat_df["Platform"] == plat, "ROI %"].values[0]

            shifts[plat] = st.slider(
                f"{plat} (Base: {format_indian_currency(plat_spend)}, {plat_roi:+.0f}% ROI)",
                min_value=-100,
                max_value=150,
                value=0,
                step=5,
                format="%+d%%",
                key=f"shift_slider_{plat}",
            )

    # Reset button for simulator
    if st.button("Reset Simulator to 100% Baseline", key="btn_reset_optimizer"):
        for plat in platforms:
            st.session_state[f"shift_slider_{plat}"] = 0
        st.rerun()

    # Compute Projected Outcomes with diminishing returns
    beta = 0.85
    sim_data = []

    for _, r in plat_df.iterrows():
        plat = r["Platform"]
        base_s = float(r["Marketing Spend"])
        base_r = float(r["Revenue Generated"])
        pct_shift = shifts.get(plat, 0)

        # New spend
        new_s = max(0.0, base_s * (1.0 + pct_shift / 100.0))

        # Projected revenue via power-law elasticity
        if base_s > 0:
            scale_ratio = max(0.0, (new_s + 1.0) / (base_s + 1.0))
            new_r = base_r * (scale_ratio**beta)
        else:
            new_r = 0.0

        new_roi = safe_divide(new_r - new_s, new_s) * 100 if new_s > 0 else 0.0

        sim_data.append(
            {
                "Platform": plat,
                "Base Spend": base_s,
                "Base Revenue": base_r,
                "Base ROI %": r["ROI %"],
                "Shift %": pct_shift,
                "Projected Spend": new_s,
                "Projected Revenue": new_r,
                "Projected ROI %": new_roi,
            }
        )

    sim_df = pd.DataFrame(sim_data)

    # Portfolio Totals: Before vs. After
    tot_base_spend = sim_df["Base Spend"].sum()
    tot_base_rev = sim_df["Base Revenue"].sum()
    tot_base_profit = tot_base_rev - tot_base_spend
    tot_base_roi = safe_divide(tot_base_profit, tot_base_spend) * 100

    tot_proj_spend = sim_df["Projected Spend"].sum()
    tot_proj_rev = sim_df["Projected Revenue"].sum()
    tot_proj_profit = tot_proj_rev - tot_proj_spend
    tot_proj_roi = safe_divide(tot_proj_profit, tot_proj_spend) * 100

    delta_spend = tot_proj_spend - tot_base_spend
    delta_rev = tot_proj_rev - tot_base_rev
    delta_profit = tot_proj_profit - tot_base_profit
    delta_roi = tot_proj_roi - tot_base_roi

    # 4 Scorecards: Before vs. After
    st.markdown("---")
    sc1, sc2, sc3, sc4 = st.columns(4)

    with sc1:
        s_color = TEXT_PRIMARY if abs(delta_spend) < 1000 else (STATUS_SUCCESS if delta_spend < 0 else ACCENT_GOLD)
        render_html(f"""
        <div style="background: rgba(0, 0, 0, 0.25); border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 10px; padding: 0.65rem 0.8rem; text-align: center;">
            <div style="font-size: 0.67rem; color: #8E8F96; text-transform: uppercase;">Total Media Spend</div>
            <div style="font-size: 1.15rem; font-weight: 700; color: #F5F5F7; font-family: 'Outfit', sans-serif;">{format_indian_currency(tot_proj_spend)}</div>
            <div style="font-size: 0.72rem; color: {s_color}; margin-top: 0.2rem;">
                Delta: {format_indian_currency(delta_spend)} ({safe_divide(delta_spend, tot_base_spend) * 100:+.1f}%)
            </div>
        </div>
        """)

    with sc2:
        r_color = STATUS_SUCCESS if delta_rev >= 0 else STATUS_DANGER
        render_html(f"""
        <div style="background: rgba(0, 0, 0, 0.25); border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 10px; padding: 0.65rem 0.8rem; text-align: center;">
            <div style="font-size: 0.67rem; color: #8E8F96; text-transform: uppercase;">Projected Gross Revenue</div>
            <div style="font-size: 1.15rem; font-weight: 700; color: #F3C477; font-family: 'Outfit', sans-serif;">{format_indian_currency(tot_proj_rev)}</div>
            <div style="font-size: 0.72rem; color: {r_color}; margin-top: 0.2rem;">
                Delta: {format_indian_currency(delta_rev)} ({safe_divide(delta_rev, tot_base_rev) * 100:+.1f}%)
            </div>
        </div>
        """)

    with sc3:
        roi_color = STATUS_SUCCESS if delta_roi >= 0 else STATUS_DANGER
        render_html(f"""
        <div style="background: rgba(0, 0, 0, 0.25); border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 10px; padding: 0.65rem 0.8rem; text-align: center;">
            <div style="font-size: 0.67rem; color: #8E8F96; text-transform: uppercase;">Projected Portfolio ROI</div>
            <div style="font-size: 1.15rem; font-weight: 700; color: {STATUS_SUCCESS if tot_proj_roi >= 50 else ACCENT_GOLD}; font-family: 'Outfit', sans-serif;">{tot_proj_roi:+.1f}%</div>
            <div style="font-size: 0.72rem; color: {roi_color}; margin-top: 0.2rem;">
                Delta: {delta_roi:+.1f}% vs. Baseline ({tot_base_roi:+.1f}%)
            </div>
        </div>
        """)

    with sc4:
        p_color = STATUS_SUCCESS if delta_profit >= 0 else STATUS_DANGER
        render_html(f"""
        <div style="background: rgba(0, 0, 0, 0.25); border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 10px; padding: 0.65rem 0.8rem; text-align: center;">
            <div style="font-size: 0.67rem; color: #8E8F96; text-transform: uppercase;">Projected Net Profit</div>
            <div style="font-size: 1.15rem; font-weight: 700; color: #34D399; font-family: 'Outfit', sans-serif;">{format_indian_currency(tot_proj_profit)}</div>
            <div style="font-size: 0.72rem; color: {p_color}; margin-top: 0.2rem;">
                Net Gain: {format_indian_currency(delta_profit)}
            </div>
        </div>
        """)

    # Plotly Grouped Bar Chart: Before vs. After across Channels
    render_html("""
    <div style="font-size: 0.72rem; color: #8E8F96; text-transform: uppercase; letter-spacing: 0.08em; margin: 1rem 0 0.4rem 0;">
        Channel Impact Matrix: Baseline vs. Optimized Capital Allocation
    </div>
    """)

    fig = go.Figure()

    # Historical Revenue
    fig.add_trace(
        go.Bar(
            name="Historical Revenue",
            x=sim_df["Platform"],
            y=sim_df["Base Revenue"],
            marker=dict(color="#3D3E46", line=dict(color="rgba(255, 255, 255, 0.15)", width=1)),
            hovertemplate="<b>%{x}</b> - Historical Revenue: ₹%{y:,.0f}<extra></extra>",
        )
    )

    # Projected Revenue
    fig.add_trace(
        go.Bar(
            name="Projected Revenue",
            x=sim_df["Platform"],
            y=sim_df["Projected Revenue"],
            marker=dict(color=ACCENT_GOLD, line=dict(color=ACCENT_GOLD_LIGHT, width=1)),
            customdata=sim_df[["Shift %", "Projected ROI %"]].values,
            hovertemplate=(
                "<b>%{x}</b> - Projected Revenue<br>"
                "Revenue: <b>₹%{y:,.0f}</b><br>"
                "Budget Shift: <b>%{customdata[0]:+d}%</b><br>"
                "Projected ROI: <b>%{customdata[1]:+.1f}%</b><extra></extra>"
            ),
        )
    )

    layout = get_plotly_layout(height=280, show_legend=True)
    layout["yaxis"]["tickprefix"] = "₹"
    layout["barmode"] = "group"
    layout["margin"] = dict(l=10, r=10, t=10, b=10)
    fig.update_layout(layout)

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
