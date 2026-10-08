# Data Quality & Cleaning Audit Report

**Generated At:** 2026-10-08 13:53:11  
**Source Dataset:** `data/raw/marketing_campaigns_raw.csv`  
**Processed Target:** `data/processed/marketing_campaigns_clean.csv`  
**Pipeline Author:** Senior Analytics Engineering Team  

---

## 1. Executive Summary: Dataset Volume Before & After

| Metric | Raw Dataset | Processed Clean Dataset | Delta / Fixes Applied |
| :--- | :--- | :--- | :--- |
| **Total Rows** | 220 | 214 | -6 duplicate records removed |
| **Unique Campaign IDs** | 214 | 214 | 100% Unique Primary Key enforced |
| **Total Columns** | 20 | 30 | +10 analytical & audit columns added |
| **Missing Values (Nulls)** | 105 | 0 | 100% complete dataset after domain imputation |
| **Anomalous Inverted Dates** | 3 | 0 | Corrected via chronologic swap |
| **Outliers Flagged** | 0 | 3 | Flagged via platform IQR thresholds |

---

## 2. Category-by-Category Data Cleaning Summary

### A. Deduplication
- **Method:** Sorted records by `Campaign ID` and `completeness` (count of non-null attributes per row) in descending order, retaining the most complete instance.
- **Duplicate Records Removed:** 6 rows.
- **Affected Campaign IDs:** `CMP-2025-013, CMP-2025-046, CMP-2025-089, CMP-2026-121, CMP-2026-161, CMP-2026-201`

### B. Temporal Normalization & Chronological Integrity
- **Heterogeneous Date Formats Standardized:** `YYYY-MM-DD`, `DD/MM/YYYY`, and `DD Mon YYYY` parsed to unified ISO datetime format.
- **Inverted Dates Detected & Repaired:** 3 rows where `Campaign End Date < Campaign Start Date`.
- **Engineering Decision:** Rather than dropping campaigns and discarding telemetry, the start and end dates were chronologically swapped (`min()` and `max()`). This restored correct campaign duration while preserving performance data.
- **Repaired Campaign IDs:** `CMP-2025-020, CMP-2025-103, CMP-2026-178`
- **Duration Range:** 7 to 45 days.

### C. Categorical Standardization
- **Platform Normalization:** All raw casing and abbreviation variants (`fb`, `FB`, `google ads`, `Insta`, `linkedin `, `youtube`, etc.) mapped to 6 canonical platforms:
  `Email, Facebook, Google, Instagram, LinkedIn, YouTube`.
- **Audience Segment Normalization:** Cleaned whitespace and casing variants into 6 standardized segments:
  `Enterprise Decision Makers, Returning Customers, Small Business Owners, Students, Working Parents, Young Professionals`.
- **Region Normalization:** Cleaned 6 Indian geographic regions:
  `Central, East, North, North-East, South, West`.

### D. Missing Value Imputation Strategy
All missing values (~4% intentional injection) were resolved using domain-principled business rules:
1. **No Spend & No Revenue Check:** Rows with null/zero spend and revenue were audited (0 found).
2. **Missing Clicks:** Imputed using $Clicks = \text{round}(Impressions \times \text{Platform Median CTR})$.
3. **Missing Leads:** Imputed using $Leads = \text{round}(Clicks \times \text{Platform Median Lead Rate})$.
4. **Missing Conversions:** Imputed using $Conversions = \text{round}(Leads \times \text{Platform Median Conversion Rate})$.
5. **Missing Revenue:** Imputed using $Revenue = \text{round}(Spend \times \text{Platform Median ROAS})$.
6. **Missing Categoricals (Region, Audience Segment):** Imputed using the modal segment/region for that specific channel.
7. **Funnel Hierarchy Enforcement:** Enforced strict physical constraint $Impressions \ge Clicks \ge Leads \ge Conversions \ge 1$.

**Imputations Applied Per Field:**
- **Region:** 9 records imputed
- **Audience Segment:** 9 records imputed
- **Clicks:** 9 records imputed
- **Leads Generated:** 8 records imputed
- **Conversions:** 9 records imputed
- **Revenue Generated:** 8 records imputed

### E. Outlier Detection (Interquartile Range - IQR)
- **Method:** Platform-segmented IQR on `Marketing Spend` ($Upper = Q3 + 1.5 \times IQR$).
- **Engineering Decision:** To maintain audit transparency and prevent silent data loss, outliers are **flagged** via `is_outlier = True` with human-readable rationale in `outlier_reason`, allowing leadership to toggle an "Exclude Outliers" filter in the Streamlit app.
- **Total Flagged Outliers:** 3 campaigns.

**Platform Threshold Breakdown:**
| Platform | Q1 (₹) | Q3 (₹) | IQR (₹) | Upper Threshold (₹) | Outliers Flagged |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Email** | ₹5,999.06 | ₹12,465.46 | ₹6,466.40 | ₹22,165.07 | 0 |
| **Facebook** | ₹55,255.56 | ₹91,343.48 | ₹36,087.92 | ₹145,475.35 | 1 |
| **Google** | ₹75,169.52 | ₹140,944.15 | ₹65,774.63 | ₹239,606.11 | 2 |
| **Instagram** | ₹58,387.34 | ₹121,748.23 | ₹63,360.89 | ₹216,789.57 | 0 |
| **LinkedIn** | ₹81,180.94 | ₹188,859.02 | ₹107,678.08 | ₹350,376.15 | 0 |
| **YouTube** | ₹81,767.28 | ₹181,133.07 | ₹99,365.79 | ₹330,181.76 | 0 |

### F. Recomputation of Derived Metrics
Rather than trusting raw derived values, all analytical KPIs were recomputed from clean base numerators and denominators following **docs/PROJECT_CONTEXT.md**:
- **CTR%:** $\frac{Clicks}{Impressions} \times 100$
- **Conversion Rate%:** $\frac{Conversions}{Clicks} \times 100$
- **Lead Conversion Rate%:** $\frac{Conversions}{Leads} \times 100$
- **ROI%:** $\frac{Revenue - Spend}{Spend} \times 100$
- **ROAS:** $\frac{Revenue}{Spend}$
- **CPC:** $\frac{Spend}{Clicks}$
- **CPM:** $\frac{Spend}{Impressions} \times 1000$
- **CAC:** $\frac{Spend}{Conversions}$
- **CPL:** $\frac{Spend}{Leads}$
- **Temporal Dimensions Added:** `Duration Days`, `Year`, `Quarter`, `Month`.

---

## 3. Data Integrity & Validation Checks

| Validation Rule | Target Assertion | Status |
| :--- | :--- | :--- |
| **Funnel Integrity** | $Impressions \ge Clicks \ge Leads \ge Conversions \ge 1$ | **PASSED (Impressions >= Clicks >= Leads >= Conversions)** |
| **Non-Negativity** | Spend, Revenue, Duration $\ge 0$ | **PASSED (Spend >= 0, Revenue >= 0, Duration >= 0)** |
| **Completeness** | 0 nulls across all essential analytical attributes | **PASSED (0 null values across all critical columns)** |
| **Primary Key** | `Campaign ID` is unique across all rows | **PASSED (100% unique Campaign IDs)** |

---

## 4. Key Engineering Assumptions & Notes for Modeling
1. **Ratio Aggregation Rule:** As specified in `PROJECT_CONTEXT.md`, row-level ratios must never be averaged across platforms or time windows. All Streamlit KPI cards and Plotly aggregations must sum base numerators and denominators.
2. **Outlier Treatment:** The 3 flagged spend outliers (> ₹18.5L) represent rogue media buyer inputs. The dashboard should default to showing all data with an interactive toggle: `[ ] Exclude Flagged Outliers`.
3. **Currency Display:** All monetary KPIs must format values using Indian numbering shorthand (e.g. ₹12.4L, ₹1.2Cr).
