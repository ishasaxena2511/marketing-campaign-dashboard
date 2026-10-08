"""
Executive Analytics Design System & Styling Theme
Recreates the reference UI visual language:
- Near-black charcoal background (#0D0E11)
- Elevated card surfaces (#1A1B1F to #222328)
- Warm amber/gold accent palette (#E9A94B and #F3C477)
- Rounded cards (16-20px radius), subtle borders, soft inner glow
- Inter typography with bold KPI metrics and uppercase muted labels
- Transparent Plotly dark template
"""

import streamlit as st

# -----------------------------------------------------------------------------
# Color Tokens
# -----------------------------------------------------------------------------
BG_MAIN = "#0D0E11"
BG_SIDEBAR = "#121316"
BG_CARD = "#1A1B1F"
BG_CARD_ELEVATED = "#222328"
BG_CARD_HOVER = "#282930"

ACCENT_GOLD = "#E9A94B"
ACCENT_GOLD_LIGHT = "#F3C477"
ACCENT_GOLD_DARK = "#B87F32"
ACCENT_GOLD_MUTED = "rgba(233, 169, 75, 0.15)"
ACCENT_GOLD_GLOW = "rgba(233, 169, 75, 0.25)"

TEXT_PRIMARY = "#F5F5F7"
TEXT_SECONDARY = "#8E8F96"
TEXT_MUTED = "#5E5F66"

BORDER_CARD = "rgba(255, 255, 255, 0.07)"
BORDER_CARD_GOLD = "rgba(233, 169, 75, 0.28)"
BORDER_CARD_ACTIVE = "rgba(233, 169, 75, 0.50)"

STATUS_SUCCESS = "#4EBA6F"
STATUS_WARNING = "#F3C477"
STATUS_DANGER = "#E05353"

GOLD_COLORWAY = [
    "#E9A94B",  # Primary gold
    "#F3C477",  # Bright gold highlight
    "#C88B35",  # Deep amber
    "#986725",  # Muted bronze
    "#D9B464",  # Pale gold
    "#8E8F96",  # Neutral slate
]


# -----------------------------------------------------------------------------
# Shared Plotly Theme
# -----------------------------------------------------------------------------
def get_plotly_layout(height: int = 340, show_legend: bool = False) -> dict:
    """
    Returns layout dictionary matching the executive dark-gold UI aesthetic.
    """
    return dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=height,
        margin=dict(l=16, r=16, t=28, b=20),
        font=dict(
            family="Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
            color=TEXT_SECONDARY,
            size=12,
        ),
        colorway=GOLD_COLORWAY,
        showlegend=show_legend,
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color=TEXT_PRIMARY, size=11),
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor="rgba(255, 255, 255, 0.04)",
            zeroline=False,
            showline=True,
            linecolor="rgba(255, 255, 255, 0.08)",
            tickfont=dict(color=TEXT_SECONDARY, size=10),
            title_font=dict(color=TEXT_SECONDARY, size=11),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(255, 255, 255, 0.04)",
            zeroline=False,
            showline=False,
            tickfont=dict(color=TEXT_SECONDARY, size=10),
            title_font=dict(color=TEXT_SECONDARY, size=11),
        ),
        hoverlabel=dict(
            bgcolor=BG_CARD,
            bordercolor=ACCENT_GOLD,
            font=dict(
                family="Inter, sans-serif",
                color=TEXT_PRIMARY,
                size=12,
            ),
        ),
    )


# -----------------------------------------------------------------------------
# Global CSS Theme Injection
# -----------------------------------------------------------------------------
def inject_custom_css():
    """
    Injects custom CSS to transform Streamlit into the executive dark UI:
    - Imports Inter & Outfit Google fonts
    - Hides default Streamlit branding, header, footer
    - Styles cards with 18px border-radius, soft inner glows, and borders
    - Customizes inputs, buttons, and multiselects with gold accents
    """
    css = f"""
    <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Outfit:wght@400;500;600;700&display=swap');

        /* Root / Main App Background */
        html, body, [data-testid="stAppViewContainer"] {{
            background-color: {BG_MAIN} !important;
            color: {TEXT_PRIMARY} !important;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        }}

        /* Hide only Streamlit default chrome that should not be visible */
        #MainMenu,
        footer,
        [data-testid="stDecoration"],
        [data-testid="stStatusWidget"],
        [data-testid="stDeployButton"],
        [data-testid="stToolbarActions"],
        [data-testid="stToolbarMenuItems"] {{
            visibility: hidden !important;
            display: none !important;
            height: 0 !important;
            width: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
        }}

        /* Header is transparent, non-blocking, sits above content */
        header[data-testid="stHeader"] {{
            background: transparent !important;
            color: transparent !important;
            height: 3rem !important;
            z-index: 99999 !important;
        }}

        /* Keep Toolbar transparent and visible so the expand button is accessible */
        [data-testid="stToolbar"] {{
            background: transparent !important;
            visibility: visible !important;
            display: flex !important;
            height: auto !important;
            margin: 0 !important;
            padding: 0.25rem 0.5rem !important;
        }}

        /* Sidebar container styling - guaranteed visible */
        section[data-testid="stSidebar"] {{
            background-color: {BG_SIDEBAR} !important;
            border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
            visibility: visible !important;
        }}

        /* Make both Expand and Collapse buttons always 100% visible and interactive */
        [data-testid="stSidebarCollapseButton"],
        [data-testid="stExpandSidebarButton"],
        [data-testid="collapsedControl"] {{
            visibility: visible !important;
            display: inline-flex !important;
            opacity: 1 !important;
            cursor: pointer !important;
            z-index: 999999 !important;
        }}

        /* Floating expand arrow positioned cleanly at the top-left when collapsed */
        [data-testid="stExpandSidebarButton"],
        [data-testid="collapsedControl"] {{
            position: fixed !important;
            top: 0.65rem !important;
            left: 0.75rem !important;
            display: flex !important;
            visibility: visible !important;
            opacity: 1 !important;
        }}

        [data-testid="stSidebarCollapseButton"] button,
        [data-testid="stExpandSidebarButton"] button,
        [data-testid="collapsedControl"] button {{
            background: #1A1B20 !important;
            border: 1px solid rgba(233, 169, 75, 0.5) !important;
            border-radius: 9px !important;
            color: #E9A94B !important;
            width: 2.2rem !important;
            height: 2.2rem !important;
            min-width: 2.2rem !important;
            min-height: 2.2rem !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            cursor: pointer !important;
            transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
            box-shadow: 0 4px 14px rgba(0, 0, 0, 0.6) !important;
            opacity: 1 !important;
        }}

        [data-testid="stSidebarCollapseButton"] button:hover,
        [data-testid="stExpandSidebarButton"] button:hover,
        [data-testid="collapsedControl"] button:hover {{
            background: #25262E !important;
            border-color: #E9A94B !important;
            box-shadow: 0 0 18px rgba(233, 169, 75, 0.55) !important;
            transform: scale(1.08) !important;
        }}

        [data-testid="stSidebarCollapseButton"] svg,
        [data-testid="stExpandSidebarButton"] svg,
        [data-testid="collapsedControl"] svg,
        [data-testid="stSidebarCollapseButton"] span,
        [data-testid="stExpandSidebarButton"] span,
        [data-testid="collapsedControl"] span {{
            color: #E9A94B !important;
            fill: #E9A94B !important;
            font-size: 1.25rem !important;
        }}

        [data-testid="stSidebarHeader"] {{
            padding: 0.6rem 0.8rem 0.2rem 0.8rem !important;
            background: transparent !important;
        }}

        /* Content container */
        .block-container {{
            padding-top: 1.5rem !important;
            padding-bottom: 2.5rem !important;
            padding-left: 2.5rem !important;
            padding-right: 2rem !important;
            max-width: 98% !important;
        }}

        /* Sidebar Styling */
        [data-testid="stSidebar"] {{
            background-color: {BG_SIDEBAR} !important;
            border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
        }}

        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {{
            color: {TEXT_SECONDARY};
            font-size: 0.85rem;
        }}

        /* Sidebar headings */
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {{
            color: {TEXT_PRIMARY} !important;
            font-family: 'Outfit', sans-serif !important;
            font-weight: 600 !important;
            letter-spacing: -0.01em;
        }}

        /* Custom Card Containers */
        .exec-card,
        div[data-testid="stVerticalBlockBorderWrapper"] {{
            background: linear-gradient(145deg, {BG_CARD} 0%, {BG_CARD_ELEVATED} 100%) !important;
            border: 1px solid {BORDER_CARD} !important;
            border-radius: 18px !important;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.45), inset 0 1px 0 rgba(255, 255, 255, 0.05) !important;
            transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
        }}

        .exec-card:hover,
        div[data-testid="stVerticalBlockBorderWrapper"]:hover {{
            border-color: {BORDER_CARD_GOLD} !important;
            box-shadow: 0 12px 32px rgba(0, 0, 0, 0.55), 0 0 16px {ACCENT_GOLD_MUTED} !important;
        }}

        .exec-card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.8rem;
        }}

        .exec-card-title {{
            font-family: 'Outfit', sans-serif;
            font-size: 0.82rem;
            font-weight: 600;
            color: {TEXT_SECONDARY};
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin: 0;
        }}

        .exec-card-badge {{
            background: {ACCENT_GOLD_MUTED};
            color: {ACCENT_GOLD};
            border: 1px solid rgba(233, 169, 75, 0.35);
            padding: 0.18rem 0.55rem;
            border-radius: 999px;
            font-size: 0.70rem;
            font-weight: 600;
            letter-spacing: 0.03em;
        }}

        /* KPI Scorecard Container */
        .kpi-card {{
            background: linear-gradient(135deg, #1A1B20 0%, #202228 100%);
            border: 1px solid {BORDER_CARD};
            border-radius: 18px;
            padding: 1.15rem 1.25rem;
            position: relative;
            overflow: hidden;
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.40);
            transition: transform 0.2s ease, border-color 0.2s ease;
        }}

        .kpi-card:hover {{
            transform: translateY(-2px);
            border-color: {BORDER_CARD_GOLD};
        }}

        .kpi-label {{
            font-family: 'Inter', sans-serif;
            font-size: 0.72rem;
            font-weight: 600;
            color: {TEXT_SECONDARY};
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 0.35rem;
        }}

        .kpi-value {{
            font-family: 'Outfit', sans-serif;
            font-size: 1.85rem;
            font-weight: 700;
            color: {ACCENT_GOLD};
            line-height: 1.15;
            letter-spacing: -0.02em;
        }}

        .kpi-value.white {{
            color: {TEXT_PRIMARY};
        }}

        .kpi-subtext {{
            font-size: 0.75rem;
            color: {TEXT_SECONDARY};
            margin-top: 0.4rem;
            display: flex;
            align-items: center;
            gap: 0.35rem;
        }}

        .kpi-pill {{
            display: inline-block;
            font-size: 0.70rem;
            font-weight: 600;
            padding: 0.12rem 0.45rem;
            border-radius: 6px;
        }}

        .kpi-pill.positive {{
            background: rgba(78, 186, 111, 0.15);
            color: {STATUS_SUCCESS};
            border: 1px solid rgba(78, 186, 111, 0.3);
        }}

        .kpi-pill.neutral {{
            background: rgba(233, 169, 75, 0.12);
            color: {ACCENT_GOLD_LIGHT};
            border: 1px solid rgba(233, 169, 75, 0.25);
        }}

        /* Form elements (Multiselect, Selectbox, Inputs) */
        .stSelectbox, .stMultiSelect, .stDateInput, .stSlider {{
            margin-bottom: 0.9rem;
        }}

        div[data-baseweb="select"] > div {{
            background-color: {BG_CARD} !important;
            border-color: rgba(255, 255, 255, 0.10) !important;
            border-radius: 12px !important;
            color: {TEXT_PRIMARY} !important;
        }}

        div[data-baseweb="select"] > div:hover {{
            border-color: {ACCENT_GOLD} !important;
        }}

        /* Selected tag in multiselect */
        span[data-baseweb="tag"] {{
            background-color: {BG_CARD_ELEVATED} !important;
            border: 1px solid {BORDER_CARD_GOLD} !important;
            border-radius: 8px !important;
        }}

        span[data-baseweb="tag"] span {{
            color: {ACCENT_GOLD_LIGHT} !important;
            font-weight: 500 !important;
            font-size: 0.8rem !important;
        }}

        /* Buttons */
        .stButton > button {{
            background: linear-gradient(135deg, {ACCENT_GOLD} 0%, {ACCENT_GOLD_DARK} 100%) !important;
            color: #0E0E10 !important;
            font-weight: 700 !important;
            font-size: 0.85rem !important;
            border: none !important;
            border-radius: 12px !important;
            padding: 0.55rem 1.2rem !important;
            transition: all 0.2s ease !important;
            box-shadow: 0 4px 12px rgba(233, 169, 75, 0.25) !important;
            letter-spacing: 0.02em !important;
            width: 100% !important;
        }}

        .stButton > button:hover {{
            transform: translateY(-1px) !important;
            box-shadow: 0 6px 18px rgba(233, 169, 75, 0.40) !important;
        }}

        /* App Banner / Title Bar */
        .dash-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.5rem 0 1.2rem 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.06);
            margin-bottom: 1.4rem;
        }}

        .dash-title {{
            font-family: 'Outfit', sans-serif;
            font-size: 1.65rem;
            font-weight: 700;
            color: {TEXT_PRIMARY};
            letter-spacing: -0.02em;
            margin: 0;
        }}

        .dash-subtitle {{
            font-size: 0.82rem;
            color: {TEXT_SECONDARY};
            margin-top: 0.2rem;
        }}

        .dash-live-badge {{
            display: flex;
            align-items: center;
            gap: 0.4rem;
            background: rgba(233, 169, 75, 0.10);
            border: 1px solid rgba(233, 169, 75, 0.30);
            padding: 0.35rem 0.8rem;
            border-radius: 999px;
            font-size: 0.72rem;
            font-weight: 600;
            color: {ACCENT_GOLD_LIGHT};
            letter-spacing: 0.04em;
        }}

        .live-dot {{
            width: 7px;
            height: 7px;
            background: {ACCENT_GOLD};
            border-radius: 50%;
            box-shadow: 0 0 8px {ACCENT_GOLD};
            animation: pulse-dot 2s infinite ease-in-out;
        }}

        @keyframes pulse-dot {{
            0%, 100% {{ opacity: 1; transform: scale(1); }}
            50% {{ opacity: 0.4; transform: scale(0.85); }}
        }}

        /* Scrollbars */
        ::-webkit-scrollbar {{
            width: 6px;
            height: 6px;
        }}
        ::-webkit-scrollbar-track {{
            background: {BG_MAIN};
        }}
        ::-webkit-scrollbar-thumb {{
            background: #25262C;
            border-radius: 3px;
        }}
        ::-webkit-scrollbar-thumb:hover {{
            background: {ACCENT_GOLD_DARK};
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def render_html(html_str: str):
    """
    Safely renders raw HTML without markdown interpreting
    indented lines as code blocks. Strips all leading whitespace on every line.
    Uses native st.html (Streamlit 1.34+) to completely bypass CommonMark markdown parsing.
    """
    if not html_str:
        return
    import re

    cleaned = re.sub(r"^[ \t]+", "", html_str, flags=re.MULTILINE).strip()
    if not cleaned:
        return
    if hasattr(st, "html"):
        st.html(cleaned)
    else:
        st.markdown(cleaned, unsafe_allow_html=True)
