# Marketing Campaign Performance Dashboard

## 1. Project Goal
The **Marketing Campaign Performance Dashboard** is an industry-grade, interactive analytics platform designed to evaluate multi-channel marketing campaign performance, ROI, conversion funnel efficiency, and budget allocation. It empowers growth marketers, CMOs, and agency leadership to make data-driven decisions across key paid and organic channels: Google Ads, Facebook Ads, Instagram Ads, LinkedIn Ads, Email Marketing, and YouTube Ads.

---

## 2. Target Audience
- **Chief Marketing Officers (CMOs) & Agency Executives**: High-level ROI, ROAS, total revenue vs. spend, channel comparison, executive KPI summaries.
- **Growth & Performance Marketing Managers**: Channel-level deep dives, campaign-level efficiency (CPC, CAC, CPM, CPL), conversion funnel diagnostics, and budget reallocation simulations.
- **Analytics & BI Engineers**: Data pipeline integrity, statistical forecasting, cross-channel attribution modeling, and clean aggregation standards.

---

## 3. Technology Stack
- **Language**: Python 3.10+ (Current runtime: Python 3.12)
- **Data Manipulation & Analysis**: `pandas`, `numpy`
- **Interactive Visualizations**: `plotly`
- **Web Dashboard Application**: `streamlit`
- **Predictive Analytics & Forecasting**: `scikit-learn`, `statsmodels`
- **Unit & Integration Testing**: `pytest`
- **File Handling**: `openpyxl`

---

## 4. Folder Structure
```text
marketing-campaign-dashboard/
│
├── .gitignore                     # Git ignore file for Python, virtualenv, and OS artifacts
├── requirements.txt               # Locked and verified project dependencies
├── README.md                      # Project introduction and quickstart guide
│
├── data/
│   ├── raw/                       # Immutable raw campaign datasets (CSV/JSON/Excel)
│   └── processed/                 # Cleaned, validated, and transformed analysis-ready datasets
│
├── notebooks/                     # Exploratory Data Analysis (EDA) and prototyping notebooks
│
├── src/                           # Reusable core analytical modules, data loaders, & calculation engines
│   └── __init__.py
│
├── app/                           # Streamlit dashboard application files
│   ├── __init__.py
│   ├── app.py                     # Streamlit entry point
│   └── components/                # Modular UI widgets, filter bars, charts, and KPI cards
│       └── __init__.py
│
├── tests/                         # Unit tests for metric calculations, aggregations, and data schemas
│   └── __init__.py
│
├── docs/                          # Project specifications, context, and documentation
│   └── PROJECT_CONTEXT.md         # Source of truth for definitions, business rules, and progress
│
├── screenshots/                   # Dashboard previews, screenshots, and visual assets
│
└── reports/                       # Generated analytical reports, exported summaries, and audits
```

---

## 5. Metric Definitions & Aggregation Rules

All analytical models, dashboard components, SQL/Pandas transformations, and tests must adhere strictly to these standardized business definitions.

### Metric Formulas
| Metric | Formula | Unit / Formatting |
| :--- | :--- | :--- |
| **Click-Through Rate (CTR%)** | $\frac{\text{Clicks}}{\text{Impressions}} \times 100$ | Percentage (`0.00%`) |
| **Conversion Rate (Conv. Rate %)** | $\frac{\text{Conversions}}{\text{Clicks}} \times 100$ | Percentage (`0.00%`) |
| **Lead Conversion Rate (Lead Conv. %)**| $\frac{\text{Conversions}}{\text{Leads}} \times 100$ | Percentage (`0.00%`) |
| **Return on Investment (ROI%)** | $\frac{\text{Revenue} - \text{Spend}}{\text{Spend}} \times 100$ | Percentage (`0.00%`) |
| **Return on Ad Spend (ROAS)** | $\frac{\text{Revenue}}{\text{Spend}}$ | Multiplier / Ratio (`0.00x`) |
| **Cost Per Click (CPC)** | $\frac{\text{Spend}}{\text{Clicks}}$ | Currency (`₹0.00`) |
| **Cost Per Mille / Thousand (CPM)** | $\frac{\text{Spend}}{\text{Impressions}} \times 1000$ | Currency (`₹0.00`) |
| **Customer Acquisition Cost (CAC)** | $\frac{\text{Spend}}{\text{Conversions}}$ | Currency (`₹0.00`) |
| **Cost Per Lead (CPL)** | $\frac{\text{Spend}}{\text{Leads}}$ | Currency (`₹0.00`) |

---

### CRITICAL AGGREGATION RULE
> [!IMPORTANT]
> **NEVER average row-level ratios across groups.**
> For any aggregated view (by platform, region, campaign, monthly/weekly roll-ups, global filter selections, or dataset totals):
> - Always compute ratios from the **SUM of numerators** divided by the **SUM of denominators**.
> - Example: $\text{Aggregated CTR} = \frac{\sum \text{Clicks}}{\sum \text{Impressions}} \times 100$, NOT $\text{mean}(\text{CTR}_i)$.
> - Example: $\text{Aggregated ROAS} = \frac{\sum \text{Revenue}}{\sum \text{Spend}}$, NOT $\text{mean}(\text{ROAS}_i)$.

---

### Currency & Number Formatting Rules
- **Currency**: Indian Rupees (**₹**).
- **Number System**: Indian Numbering System using **Lakh (L)** and **Crore (Cr)** abbreviations in KPI cards and high-level summaries:
  - Values $\ge 1,00,00,000$ ($\ge 1\text{ Cr}$): formatted as `₹X.XXCr` (e.g., `₹1.25Cr`).
  - Values $\ge 1,00,000$ ($\ge 1\text{ Lakh}$): formatted as `₹X.XXL` (e.g., `₹12.40L`).
  - Values $< 1,00,000$: formatted with comma separators as `₹XX,XXX.XX` (e.g., `₹45,200.50`).
- Tooltips or detailed tabular views should preserve full precision with Indian grouping commas (e.g., `₹1,25,00,000`).

---

## 6. Progress Log

| Date | Phase / Task | Description | Status |
| :--- | :--- | :--- | :--- |
| 2026-10-08 | Project Initialization | Initialized directory architecture (`data/raw`, `data/processed`, `notebooks`, `src`, `app`, `app/components`, `tests`, `docs`, `screenshots`, `reports`). Created `.gitignore`, `requirements.txt`, and isolated virtual environment (`.venv`). Documented project context, core metrics, aggregation rules, and currency standards. | **COMPLETED** |
| 2026-10-08 | Raw Data Generation | Developed `src/generate_data.py` (seeded with NumPy seed 42) producing 220 campaigns saved to `data/raw/marketing_campaigns_raw.csv`. Injected domain realism, channel dynamics (Google, Facebook, Instagram, LinkedIn, Email, YouTube), festive/seasonal multipliers, 6 duplicate IDs, ~4% missing values, platform spelling variations, mixed date formats, 3 spend outliers, and 3 inverted date anomalies. | **COMPLETED** |
| 2026-10-08 | Data Cleaning & Audit | Implemented `src/clean_data.py` containing modular functions for deduplication (preserving most complete rows), ISO date parsing, chronological swapping of 3 inverted dates, platform/segment/region standardization, domain-principled imputation, platform-level IQR outlier detection (`is_outlier`), and recomputation of derived metrics (CTR%, Conv. Rate%, Lead Conv. Rate%, ROI%, ROAS, CPC, CPM, CAC, CPL, Duration Days, Month, Quarter, Year). Output saved to `data/processed/marketing_campaigns_clean.csv` (214 rows x 30 columns) and audited in `reports/data_quality_report.md`. All integrity assertions passed. | **COMPLETED** |
| 2026-10-08 | Metrics Engine & Pytest Suite | Built `src/metrics.py` as single source of truth for KPI calculations (`calculate_kpis`, `group_metrics`, `funnel_data`, `get_top_campaigns`, `get_bottom_campaigns`, `budget_opportunities`, `safe_divide`, `format_indian_currency`). Developed `tests/test_metrics.py` verifying all KPI formulas, edge cases, and proving mathematically that aggregated ROI differs from average row-level ROI. All 10 pytest tests passing. | **COMPLETED** |
| 2026-10-08 | Exploratory Data Analysis & Insights | Developed and executed `notebooks/01_eda_and_campaign_analysis.ipynb` containing 10 recruiter-focused analytical sections using `src/metrics.py`. Analyzed dataset distributions, 3 rogue spend outliers, top/bottom performers with ₹25k qualification filter, multi-channel benchmarks, cross-segment ROI slices, CAC trajectories, 4-stage funnel leakage, and Indian festive seasonality (+135.5% ROAS lift). Generated executive advisory report in `reports/key_insights.md` with concrete capital reallocation recommendations. | **COMPLETED** |
| 2026-10-08 | Executive UI & Dashboard Architecture | Recreated dark executive visual language from `docs/theme-reference.png` (#0D0E11 background, #1A1B1F card surfaces, warm gold #E9A94B/#F3C477 accents, 18px rounded cards, Inter/Outfit typography, soft inner glow). Created `app/theme.py`, reusable container helper in `app/components/card.py`, and primary dashboard in `app/main.py` with left sidebar filters (date range, platform, region, segment, campaign type, outlier toggle), top 5 executive KPI cards, middle row (revenue trajectory area, platform ROI capsule bars, donut throughput funnel), and bottom row (audience cohorts and regional split). Streamlit app running and verified at http://localhost:8501. | **COMPLETED** |
| 2026-10-08 | Dual-Tier KPI Cards & Period Deltas | Built `app/components/kpis.py` and wired into `app/main.py`. Implemented primary tier (Total Spend, Total Revenue, ROI %, CTR %, Conversion Rate %) and secondary tier (CAC, CPC, CPM, Total Leads, Lead Conversion Rate %). Configured dynamic period comparison against previous equivalent chronological window with directional arrows (green/red). Implemented inverted cost semantics (reduction in CAC/CPC/CPM marked positive). Handled empty filter results gracefully with informative user notice. | **COMPLETED** |
| 2026-10-08 | Performance Analytics Suite | Developed `app/components/performance.py` and integrated into the middle section of `app/main.py`. Built 5 Plotly visualizations with executive dark/gold styling: (1) Campaign ROI Leaderboard with Top/Bottom 10 toggle and minimum spend qualification slider, (2) Top 10 Revenue Drivers bar chart, (3) Cross-channel grouped bars (Spend vs. Revenue) with an interactive Channel Efficiency Matrix table, (4) 4-stage Conversion Funnel with stage-to-stage transition and drop-off leakage badges, and (5) Dual-axis monthly Spend vs. Gross Revenue trajectory (Spend bars + Gold area line) with ROI% hover metrics. All charts wired dynamically to sidebar filters. | **COMPLETED** |
| 2026-10-08 | Audience Cohorts, Regional Geo & Audit Suite | Developed `app/components/audience_region.py` and integrated into the bottom section of `app/main.py`. Implemented 5 key features: (1) Audience Segment Analysis with dual-axis ROI/Conversion bars, top-performer highlight badge, and cohort efficiency table; (2) India Regional Performance Map using Plotly `Scattergeo` (dark land/ocean, revenue-proportional bubbles, continuous ROI colorscale, North/South/East/West/Central/NE centroids); (3) CTR & Conversion Efficiency Trajectory (dual-axis monthly spline with gold area gradients); (4) Portfolio ROI Gauge with user-configurable target benchmark in sidebar (default 300%) and delta pacing indicator; (5) Sortable dark-styled Campaign Directory table with conditional color-coded ROI % and filtered CSV data export button. | **COMPLETED** |
| 2026-10-08 | Multi-Tab Navigation, Forecasting & Budget Optimiser | Upgraded architecture to a modular 4-tab executive suite in `app/main.py`: (1) Multi-page navigation ("Executive Overview", "Channel Insights", "Campaign Drill-down", "Budget Optimiser"); (2) Auto-generated strategic insights panel (`app/components/insights_panel.py`) dynamically identifying top platform, capital drags, and scale-up opportunities; (3) Campaign Drill-Down suite (`app/components/drilldown.py`) with campaign selector, dedicated 4-stage funnel, daily burn/run-rates, platform benchmark deltas, and dynamic plain-English verdict; (4) Predictive forecasting engine (`src/forecasting.py`, `app/components/channel_insights.py`) implementing statsmodels Holt's Exponential Smoothing with 95% confidence intervals and linear fallback; (5) What-if budget optimizer (`app/components/budget_optimizer.py`) with channel reallocation sliders, power-law diminishing returns response curve (beta=0.85), and side-by-side Before/After scorecards; (6) Executive Summary export generator (`app/components/export_report.py`) producing print-optimized HTML/PDF reports. | **COMPLETED** |
| 2026-10-08 | HTML Code Rendering Fix & Collapsible Navigation Panel | Fixed all instances where raw HTML tags/code snippets rendered as text due to markdown 4-space code block interpretation via native `st.html()`. Refactored side navigation panel to use streamlined open/close arrow buttons (`stSidebarCollapseButton` `<<` and `stExpandSidebarButton` `>>`) with gold executive styling and smooth transitions, removing redundant header/sidebar text buttons (`✕ Close` and `◀ Hide Nav Panel`). | **COMPLETED** |
| 2026-10-08 | QA Engineering, Edge-Case Hardening & Code Quality | Conducted full-suite QA and UI audit. Independently recomputed core KPIs in Pandas matching metrics engine with 100% mathematical parity. Stress-tested 24 filter combinations across 4 tabs with zero crashes. Resolved empty-slice ranking schema stripping (`KeyError`), protected single-campaign drilldown indexing, fixed unreachable budget optimizer modeling banners, and added `@st.cache_data` caching for predictive forecasting models. Formatted and linted codebase to 100% Ruff/PEP 8 compliance with comprehensive docstrings and comments. | **COMPLETED** |
| 2026-10-08 | Comprehensive Documentation & Portfolio Deliverables | Created production-grade `README.md` (badges, schema, formulas, insights, setup, roadmap), formal 2-page CMO briefing report (`reports/project_report.md`), recruiter resume impact lines (`docs/resume_lines.md`), 10 deep-dive interview preparation Q&As (`docs/interview_prep.md`), and GitHub repository metadata (name, description, topics). | **COMPLETED** |




