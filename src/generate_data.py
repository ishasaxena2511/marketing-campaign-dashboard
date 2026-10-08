"""
Data Generator for Marketing Campaign Performance Dashboard
Generates a realistic raw dataset of 220 marketing campaigns with seeded randomness,
business domain constraints, and intentionally injected data quality issues for EDA and cleaning.
"""

import os
import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd


def generate_marketing_data(output_path="data/raw/marketing_campaigns_raw.csv", seed=42):
    # Set seeds for reproducibility
    np.random.seed(seed)
    random.seed(seed)

    # Configuration
    base_n = 214  # We will duplicate 6 campaigns to reach exactly 220 rows
    duplicate_count = 6
    total_target = base_n + duplicate_count  # 220

    platforms = ["Google", "Facebook", "Instagram", "LinkedIn", "Email", "YouTube"]
    regions = ["North", "South", "East", "West", "Central", "North-East"]
    audience_segments = [
        "Students",
        "Young Professionals",
        "Working Parents",
        "Small Business Owners",
        "Enterprise Decision Makers",
        "Returning Customers",
    ]

    # Channel distribution weights
    platform_probs = [0.24, 0.20, 0.20, 0.14, 0.12, 0.10]

    # Start dates range from Jan 1, 2025 to Aug 15, 2026
    start_anchor = datetime(2025, 1, 1)
    end_anchor = datetime(2026, 8, 15)
    total_days = (end_anchor - start_anchor).days

    records = []

    for i in range(base_n):
        cmp_id = f"CMP-{2025 + (i // 110):04d}-{(i + 1):03d}"
        platform = np.random.choice(platforms, p=platform_probs)

        # Realistic campaign type distribution based on platform
        if platform == "Email":
            cmp_type = np.random.choice(
                ["Newsletter", "Retargeting", "Seasonal Sale", "Product Launch"], p=[0.40, 0.30, 0.20, 0.10]
            )
            segment = np.random.choice(["Returning Customers", "Young Professionals", "Small Business Owners"])
        elif platform == "LinkedIn":
            cmp_type = np.random.choice(["Lead Generation", "Brand Awareness", "Product Launch"], p=[0.60, 0.25, 0.15])
            segment = np.random.choice(["Enterprise Decision Makers", "Small Business Owners"], p=[0.65, 0.35])
        elif platform == "YouTube":
            cmp_type = np.random.choice(["Brand Awareness", "Product Launch", "Seasonal Sale"], p=[0.60, 0.25, 0.15])
            segment = np.random.choice(["Young Professionals", "Students", "Working Parents"])
        elif platform == "Google":
            cmp_type = np.random.choice(
                ["Lead Generation", "Seasonal Sale", "Retargeting", "Brand Awareness"], p=[0.45, 0.25, 0.20, 0.10]
            )
            segment = np.random.choice(audience_segments)
        else:  # Facebook & Instagram
            cmp_type = np.random.choice(
                ["Brand Awareness", "Seasonal Sale", "Retargeting", "Lead Generation"], p=[0.30, 0.35, 0.20, 0.15]
            )
            segment = np.random.choice(["Young Professionals", "Students", "Working Parents", "Returning Customers"])

        region = np.random.choice(regions, p=[0.28, 0.25, 0.18, 0.15, 0.08, 0.06])

        # Campaign Name generator
        cmp_name = f"{platform}_{cmp_type.replace(' ', '')}_{segment.replace(' ', '')}_{region[:2]}"

        # Dates and duration
        random_day_offset = random.randint(0, total_days)
        start_date = start_anchor + timedelta(days=random_day_offset)
        duration_days = random.randint(7, 45)
        end_date = start_date + timedelta(days=duration_days)

        # Festive and Sale Seasonality Multiplier (India)
        # Oct & Nov (Diwali, Dussehra), Jan (New Year/Republic Day Sale), Aug (Independence Day Sale)
        month = start_date.month
        is_festive = month in [10, 11]
        is_sale_period = month in [1, 8]
        if is_festive:
            season_mult = random.uniform(1.30, 1.65)
        elif is_sale_period:
            season_mult = random.uniform(1.15, 1.30)
        else:
            season_mult = random.uniform(0.92, 1.08)

        # Platform Specific Metrics & Funnel Dynamics
        if platform == "Email":
            # Tiny spend, high CTR (2-5%), superior ROI
            spend = round(random.uniform(3500, 16000), 2)
            impressions = int(random.uniform(25000, 140000))
            ctr_pct = random.uniform(2.2, 5.2)  # %
            clicks = max(10, int(round(impressions * (ctr_pct / 100))))
            leads = max(5, int(round(clicks * random.uniform(0.28, 0.45))))
            conversions = max(2, int(round(leads * random.uniform(0.35, 0.55))))
            # Baseline ROAS for email: 2.2x to 3.8x
            base_roas = random.uniform(2.2, 3.8)
            revenue = round(spend * base_roas * season_mult, 2)

        elif platform == "Google":
            # High intent, strong conversion, healthy ROI
            spend = round(random.uniform(35000, 160000), 2)
            impressions = int(random.uniform(50000, 280000))
            ctr_pct = random.uniform(2.4, 4.6)
            clicks = max(20, int(round(impressions * (ctr_pct / 100))))
            leads = max(10, int(round(clicks * random.uniform(0.18, 0.32))))
            conversions = max(4, int(round(leads * random.uniform(0.25, 0.48))))
            # Baseline ROAS for Google: 1.5x to 2.8x
            base_roas = random.uniform(1.5, 2.8)
            revenue = round(spend * base_roas * season_mult, 2)

        elif platform in ["Facebook", "Instagram"]:
            # High reach, lower CTR (0.6-1.5%), varied ROI
            spend = round(random.uniform(25000, 140000), 2)
            impressions = int(random.uniform(120000, 750000))
            ctr_pct = random.uniform(0.65, 1.50)
            clicks = max(20, int(round(impressions * (ctr_pct / 100))))
            leads = max(8, int(round(clicks * random.uniform(0.10, 0.22))))
            conversions = max(2, int(round(leads * random.uniform(0.18, 0.36))))
            # Baseline ROAS: 1.1x to 2.2x
            base_roas = random.uniform(1.1, 2.2)
            revenue = round(spend * base_roas * season_mult, 2)

        elif platform == "LinkedIn":
            # High CPC, low volume, B2B audience, high deal value
            spend = round(random.uniform(45000, 220000), 2)
            impressions = int(random.uniform(18000, 85000))
            ctr_pct = random.uniform(0.40, 1.05)
            clicks = max(15, int(round(impressions * (ctr_pct / 100))))
            leads = max(4, int(round(clicks * random.uniform(0.12, 0.28))))
            conversions = max(1, int(round(leads * random.uniform(0.15, 0.32))))
            # Baseline ROAS: 0.8x to 2.1x
            base_roas = random.uniform(0.80, 2.10)
            revenue = round(spend * base_roas * season_mult, 2)

        elif platform == "YouTube":
            # Huge impressions, low CTR, weak direct response ROI
            spend = round(random.uniform(55000, 240000), 2)
            impressions = int(random.uniform(450000, 2400000))
            ctr_pct = random.uniform(0.20, 0.65)
            clicks = max(25, int(round(impressions * (ctr_pct / 100))))
            leads = max(5, int(round(clicks * random.uniform(0.06, 0.15))))
            conversions = max(1, int(round(leads * random.uniform(0.08, 0.20))))
            # Weak direct response ROI (ROAS 0.35x - 0.95x)
            base_roas = random.uniform(0.35, 0.95)
            revenue = round(spend * base_roas * season_mult, 2)

        # Logical funnel sanity check: Impressions > Clicks >= Leads >= Conversions
        if clicks >= impressions:
            clicks = int(impressions * 0.02)
        if leads >= clicks:
            leads = max(1, int(clicks * 0.5))
        if conversions >= leads:
            conversions = max(1, int(leads * 0.5))

        records.append(
            {
                "Campaign ID": cmp_id,
                "Campaign Name": cmp_name,
                "Campaign Type": cmp_type,
                "Platform": platform,
                "Campaign Start Date": start_date,
                "Campaign End Date": end_date,
                "Region": region,
                "Audience Segment": segment,
                "Impressions": impressions,
                "Clicks": clicks,
                "Leads Generated": leads,
                "Conversions": conversions,
                "Marketing Spend": spend,
                "Revenue Generated": revenue,
            }
        )

    df = pd.DataFrame(records)

    # -------------------------------------------------------------------------
    # Intentional Story Elements: Clear Winners and Losers
    # -------------------------------------------------------------------------
    # Designate ~10 distinct campaigns as breakout mega-winners (ROI > 400%, i.e., ROAS > 5.0x)
    winner_indices = [15, 42, 68, 78, 105, 115, 148, 175, 192, 210]
    for idx in winner_indices:
        boost_mult = random.uniform(5.2, 7.8)  # ROI: 420% to 680%
        df.at[idx, "Revenue Generated"] = round(df.at[idx, "Marketing Spend"] * boost_mult, 2)

    # Designate ~18 distinct campaigns as clear losers (Negative ROI: -25% to -75%)
    loser_indices = [7, 23, 39, 54, 61, 82, 99, 122, 134, 141, 155, 168, 172, 183, 188, 197, 203, 205]
    for idx in loser_indices:
        loss_factor = random.uniform(0.25, 0.75)  # Revenue < Spend
        df.at[idx, "Revenue Generated"] = round(df.at[idx, "Marketing Spend"] * loss_factor, 2)

    # -------------------------------------------------------------------------
    # Intentional Data Quality Injection 1: 6 Duplicate Campaign IDs
    # -------------------------------------------------------------------------
    dup_source_indices = [12, 45, 88, 120, 160, 200]
    dup_rows = df.iloc[dup_source_indices].copy()
    df = pd.concat([df, dup_rows], ignore_index=True)
    assert len(df) == total_target, f"Expected {total_target} rows, got {len(df)}"

    # -------------------------------------------------------------------------
    # Intentional Data Quality Injection 2: Extreme Outliers in Spend
    # -------------------------------------------------------------------------
    # 3 campaigns with rogue budget entry (e.g. ₹22.5L, ₹31.8L, ₹18.5L)
    outlier_spends = [2250000.0, 3180000.0, 1850000.0]
    outlier_indices = [8, 85, 165]
    for idx, sp in zip(outlier_indices, outlier_spends):
        df.at[idx, "Marketing Spend"] = sp

    # -------------------------------------------------------------------------
    # Intentional Data Quality Injection 3: 2-3 Rows with End Date before Start Date
    # -------------------------------------------------------------------------
    swapped_date_indices = [19, 102, 177]
    for idx in swapped_date_indices:
        s_date = df.at[idx, "Campaign Start Date"]
        e_date = df.at[idx, "Campaign End Date"]
        df.at[idx, "Campaign Start Date"] = e_date
        df.at[idx, "Campaign End Date"] = s_date - timedelta(days=random.randint(3, 10))

    # -------------------------------------------------------------------------
    # Intentional Data Quality Injection 4: Mixed Date Formats
    # -------------------------------------------------------------------------
    # Formats: YYYY-MM-DD (~75%), DD/MM/YYYY (~15%), "DD Mon YYYY" (~10%)
    formatted_start = []
    formatted_end = []

    for i in range(len(df)):
        s_d = df.at[i, "Campaign Start Date"]
        e_d = df.at[i, "Campaign End Date"]
        fmt_rand = random.random()
        if fmt_rand < 0.15:
            # DD/MM/YYYY
            formatted_start.append(s_d.strftime("%d/%m/%Y"))
            formatted_end.append(e_d.strftime("%d/%m/%Y"))
        elif fmt_rand < 0.25:
            # "12 Mar 2025"
            formatted_start.append(s_d.strftime("%d %b %Y"))
            formatted_end.append(e_d.strftime("%d %b %Y"))
        else:
            # Standard ISO YYYY-MM-DD
            formatted_start.append(s_d.strftime("%Y-%m-%d"))
            formatted_end.append(e_d.strftime("%Y-%m-%d"))

    df["Campaign Start Date"] = formatted_start
    df["Campaign End Date"] = formatted_end

    # -------------------------------------------------------------------------
    # Intentional Data Quality Injection 5: Platform Spelling & Casing Variants
    # -------------------------------------------------------------------------
    platform_dirty_map = {
        "Facebook": ["fb", "FB", "Facebook", "Facebook"],
        "Google": ["google ads", "Google", "Google Ads", "Google"],
        "Instagram": ["Insta", "Instagram", "Insta", "Instagram"],
        "LinkedIn": ["linkedin ", "LinkedIn", "linkedin", "LinkedIn "],
        "YouTube": ["youtube", "YouTube", "youtube", "YouTube"],
        "Email": ["Email", "Email", "email", "Email"],
    }

    for i in range(len(df)):
        orig_p = df.at[i, "Platform"]
        if random.random() < 0.35:
            df.at[i, "Platform"] = random.choice(platform_dirty_map[orig_p])

    # -------------------------------------------------------------------------
    # Intentional Data Quality Injection 6: Audience Segment Casing & Spacing Variants
    # -------------------------------------------------------------------------
    for i in range(len(df)):
        if random.random() < 0.25:
            seg = df.at[i, "Audience Segment"]
            variant_choice = random.choice([1, 2, 3])
            if variant_choice == 1:
                df.at[i, "Audience Segment"] = f" {seg.lower()} "
            elif variant_choice == 2:
                df.at[i, "Audience Segment"] = seg.upper()
            else:
                df.at[i, "Audience Segment"] = f"{seg} "

    # -------------------------------------------------------------------------
    # Compute Raw Calculated Columns
    # -------------------------------------------------------------------------
    df["CTR %"] = np.round((df["Clicks"] / df["Impressions"]) * 100, 2)
    df["Conversion Rate %"] = np.round((df["Conversions"] / df["Clicks"]) * 100, 2)
    df["ROI %"] = np.round(((df["Revenue Generated"] - df["Marketing Spend"]) / df["Marketing Spend"]) * 100, 2)
    df["CPC"] = np.round(df["Marketing Spend"] / df["Clicks"], 2)
    df["CPM"] = np.round((df["Marketing Spend"] / df["Impressions"]) * 1000, 2)
    df["Customer Acquisition Cost"] = np.round(df["Marketing Spend"] / df["Conversions"], 2)

    # -------------------------------------------------------------------------
    # Intentional Data Quality Injection 7: ~4% Missing Values in Selected Columns
    # -------------------------------------------------------------------------
    # ~4% of 220 is ~9 missing values per designated column
    missing_cols = ["Clicks", "Leads Generated", "Conversions", "Revenue Generated", "Region", "Audience Segment"]
    for col in missing_cols:
        null_indices = np.random.choice(df.index, size=9, replace=False)
        df.loc[null_indices, col] = np.nan
        # If Clicks is null, dependent metrics become null
        if col == "Clicks":
            df.loc[null_indices, ["CTR %", "Conversion Rate %", "CPC"]] = np.nan
        elif col == "Conversions":
            df.loc[null_indices, ["Conversion Rate %", "Customer Acquisition Cost"]] = np.nan
        elif col == "Revenue Generated":
            df.loc[null_indices, "ROI %"] = np.nan

    # -------------------------------------------------------------------------
    # Reorder columns to match explicit specification exactly
    # -------------------------------------------------------------------------
    ordered_columns = [
        "Campaign ID",
        "Campaign Name",
        "Campaign Type",
        "Platform",
        "Campaign Start Date",
        "Campaign End Date",
        "Region",
        "Audience Segment",
        "Impressions",
        "Clicks",
        "CTR %",
        "Leads Generated",
        "Conversions",
        "Conversion Rate %",
        "Marketing Spend",
        "Revenue Generated",
        "ROI %",
        "CPC",
        "CPM",
        "Customer Acquisition Cost",
    ]
    df = df[ordered_columns]

    # Save to CSV
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"[SUCCESS] Generated raw marketing dataset at: {output_path}")
    return df


if __name__ == "__main__":
    df_raw = generate_marketing_data()

    print("\n" + "=" * 50)
    print("DATASET SUMMARY REPORT")
    print("=" * 50)
    print(f"Total Rows: {len(df_raw)}")
    print(f"Total Columns: {len(df_raw.columns)}")
    print(f"Duplicate Campaign IDs: {df_raw['Campaign ID'].duplicated().sum()}")

    print("\n--- Missing Values (Nulls) Per Column ---")
    null_counts = df_raw.isnull().sum()
    print(null_counts[null_counts > 0])

    print("\n--- Platform Raw Value Counts ---")
    print(df_raw["Platform"].value_counts())
    print("=" * 50)
