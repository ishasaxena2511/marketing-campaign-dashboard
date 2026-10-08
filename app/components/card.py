"""
Reusable Executive Card & Container Components
Provides HTML/CSS building blocks for rendering styled cards and KPI scorecards
matching the reference dark executive theme.
"""

from app.theme import render_html


def render_kpi_card(
    label: str,
    value: str,
    subtext: str | None = None,
    pill_text: str | None = None,
    pill_type: str = "neutral",  # 'positive', 'neutral', 'negative'
    highlight: bool = True,
):
    """
    Renders an executive scorecard KPI card with uppercase label,
    prominent formatted metric value, and optional status indicator pill.
    """
    val_class = "kpi-value" if highlight else "kpi-value white"

    pill_html = ""
    if pill_text:
        pill_class = f"kpi-pill {pill_type}"
        pill_html = f'<span class="{pill_class}">{pill_text}</span>'

    subtext_html = ""
    if subtext or pill_text:
        subtext_html = f"""
        <div class="kpi-subtext">
            {pill_html}
            <span>{subtext or ""}</span>
        </div>
        """

    card_html = f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="{val_class}">{value}</div>
        {subtext_html}
    </div>
    """
    render_html(card_html)


def render_card_header(title: str, badge: str | None = None):
    """
    Renders standard section/card header with uppercase title and gold capsule badge.
    """
    badge_html = f'<span class="exec-card-badge">{badge}</span>' if badge else ""
    header_html = f"""
    <div class="exec-card-header">
        <div class="exec-card-title">{title}</div>
        {badge_html}
    </div>
    """
    render_html(header_html)
