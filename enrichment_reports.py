"""
Step 6 (part 2) - Enrichment Transformations T9-T13 and Step 7 - Generate Reports
Owner: Member 4
Kerala Rainfall ETL Mini Project
"""

import pandas as pd
import numpy as np

# --------------------------------------------------------------------------
# Paths and constants (pure string paths)
# --------------------------------------------------------------------------
INPUT_FILE = "input/cleaned_stage1.csv"
REPORTS_DIR = "reports/"

# IMD rainfall classes using numpy infinity
RAIN_BINS = [0, 2.5, 15.6, 64.5, 115.6, 204.5, np.inf]
RAIN_LABELS = ["Very Light", "Light", "Moderate", "Heavy", "Very Heavy", "Extremely Heavy"]

SEASONS = {
    1: "Winter", 2: "Winter",
    3: "Pre-Monsoon", 4: "Pre-Monsoon", 5: "Pre-Monsoon",
    6: "Southwest Monsoon", 7: "Southwest Monsoon",
    8: "Southwest Monsoon", 9: "Southwest Monsoon",
    10: "Post-Monsoon", 11: "Post-Monsoon", 12: "Post-Monsoon",
}


def _log(log, step, reason, before, after):
    """Record what each transformation did and why it was needed."""
    log.append({"step": step, "reason": reason, "rows_before": before, "rows_after": after})
    print(f"  [{step}] rows: {before} -> {after}")


# --------------------------------------------------------------------------
# TRANSFORM - Enrichment (Step 6, Part 2)
# --------------------------------------------------------------------------
def t9_add_date_parts(df, log):
    """Split date into year, month, month name, and day of week."""
    before = len(df)
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["month_name"] = df["date"].dt.month_name()
    df["day_of_week"] = df["date"].dt.day_name()
    _log(log, "T9 Split date into parts", "Year/month/weekday columns make monthly and trend analysis easy", before, len(df))
    return df


def t10_add_season(df, log):
    """Map meteorological monsoon seasons for Kerala."""
    before = len(df)
    df["season"] = df["month"].map(SEASONS)
    _log(log, "T10 Create season column", "Kerala rainfall is driven by monsoon seasons, so season is a key category", before, len(df))
    return df


def t11_add_rainfall_category(df, log):
    """Classify daily rainfall into standard IMD intensity categories."""
    before = len(df)
    df["rainfall_category"] = pd.cut(df["rainfall_mm"], bins=RAIN_BINS, labels=RAIN_LABELS, right=False).astype("string")
    _log(log, "T11 Create rainfall category", "IMD intensity classes (Very Light ... Extremely Heavy) for each reading", before, len(df))
    return df


def t12_add_station_totals_and_rank(df, log):
    """Calculate cumulative station rainfall and rank stations (1 = wettest)."""
    before = len(df)
    df["station_total_rainfall_mm"] = df.groupby("station")["rainfall_mm"].transform("sum").round(2)
    station_totals = df.groupby("station")["rainfall_mm"].sum()
    rank = station_totals.rank(ascending=False, method="min").astype(int)
    df["station_rank"] = df["station"].map(rank)
    _log(log, "T12 Aggregation + ranking", "Station total rainfall and rank (1 = wettest) added to each row", before, len(df))
    return df


def t13_sort_records(df, log):
    """Sort data chronologically and by station."""
    before = len(df)
    df = df.sort_values(["station", "date"]).reset_index(drop=True)
    _log(log, "T13 Sort records", "Ordered by station then date for time-series use", before, len(df))
    return df


# --------------------------------------------------------------------------
# STEP 7: GENERATE REPORTS (Member 4)
# --------------------------------------------------------------------------
def generate_reports(df, log):
    """Build all report tables; returns dictionary of DataFrames."""
    print("\n--- Generating Reports (Step 7) ---")
    reports = {}

    # 1. Cleaned Data
    reports["cleaned_data.csv"] = df

    # 2. Summary Statistics
    summary = df["rainfall_mm"].describe().round(2).rename_axis("statistic").reset_index()
    summary.columns = ["statistic", "rainfall_mm"]
    extra_stats = pd.DataFrame({
        "statistic": ["stations", "districts", "first_date", "last_date"],
        "rainfall_mm": [
            df["station"].nunique(),
            df["district"].nunique(),
            df["date"].min().date(),
            df["date"].max().date()
        ],
    })
    reports["summary_statistics.csv"] = pd.concat([summary, extra_stats], ignore_index=True)

    # 3. District-Wise Report
    district = (df.groupby("district")
                .agg(stations=("station", "nunique"),
                     records=("rainfall_mm", "size"),
                     total_rainfall_mm=("rainfall_mm", "sum"),
                     avg_daily_rainfall_mm=("rainfall_mm", "mean"),
                     max_daily_rainfall_mm=("rainfall_mm", "max"))
                .round(2).sort_values("avg_daily_rainfall_mm", ascending=False).reset_index())
    district["rank_by_avg_daily_rainfall"] = range(1, len(district) + 1)
    reports["district_wise_report.csv"] = district

    # 4. Monthly Report
    monthly = (df.groupby(["month", "month_name"])
               .agg(records=("rainfall_mm", "size"),
                    total_rainfall_mm=("rainfall_mm", "sum"),
                    avg_daily_rainfall_mm=("rainfall_mm", "mean"),
                    max_daily_rainfall_mm=("rainfall_mm", "max"))
               .round(2).reset_index())
    reports["monthly_report.csv"] = monthly

    # 5. Seasonal Report
    seasonal = (df.groupby("season")
                .agg(records=("rainfall_mm", "size"),
                     avg_daily_rainfall_mm=("rainfall_mm", "mean"),
                     max_daily_rainfall_mm=("rainfall_mm", "max"))
                .round(2).sort_values("avg_daily_rainfall_mm", ascending=False).reset_index())
    reports["seasonal_report.csv"] = seasonal

    # 6. Rainfall Category Report
    category_counts = df["rainfall_category"].value_counts().reindex(RAIN_LABELS).fillna(0).astype(int)
    cat_df = category_counts.rename_axis("rainfall_category").reset_index(name="records")
    cat_df["percentage"] = (cat_df["records"] / cat_df["records"].sum() * 100).round(2)
    reports["rainfall_category_report.csv"] = cat_df

    # 7. Top 10 Rainiest Days
    cols = ["station", "district", "date", "rainfall_mm", "rainfall_category"]
    reports["top10_rainiest_days.csv"] = df.nlargest(10, "rainfall_mm")[cols].reset_index(drop=True)

    # 8. Top & Bottom 10 Stations
    station = (df.groupby(["station", "district"])
               .agg(records=("rainfall_mm", "size"),
                    total_rainfall_mm=("rainfall_mm", "sum"),
                    avg_daily_rainfall_mm=("rainfall_mm", "mean"))
               .round(2).reset_index())
    reports["top10_stations_by_avg_rainfall.csv"] = station.nlargest(10, "avg_daily_rainfall_mm").reset_index(drop=True)
    reports["bottom10_stations_by_avg_rainfall.csv"] = station.nsmallest(10, "avg_daily_rainfall_mm").reset_index(drop=True)

    # 9. Highest and Lowest Values
    hi = df.loc[df["rainfall_mm"].idxmax()]
    lo = df.loc[df["rainfall_mm"].idxmin()]
    reports["highest_lowest_values.csv"] = pd.DataFrame([
        {"type": "Highest", **{c: hi[c] for c in cols}},
        {"type": "Lowest", **{c: lo[c] for c in cols}},
    ])

    # 10. Transformation Log
    reports["transformation_log.csv"] = pd.DataFrame(log)

    for name, table in reports.items():
        print(f"  • {name}: {len(table)} rows")
    return reports


def run_enrichment_and_reports():
    """Load Member 3's cleaned stage 1 CSV, enrich it, and generate reports."""
    try:
        df = pd.read_csv(INPUT_FILE, parse_dates=["date_time", "date"])
    except FileNotFoundError:
        df = pd.read_csv("cleaned_stage1.csv", parse_dates=["date_time", "date"])

    log = []
    print("\n--- Enrichment Transformations (Member 4) ---")
    steps = (
        t9_add_date_parts,
        t10_add_season,
        t11_add_rainfall_category,
        t12_add_station_totals_and_rank,
        t13_sort_records,
    )
    for step in steps:
        df = step(df, log)

    reports = generate_reports(df, log)
    for name, table in reports.items():
        table.to_csv(f"reports/{name}", index=False)
    print(f"\n[OK] Reports saved in reports/ (Hand these to Member 5)")
    return reports


if __name__ == "__main__":
    run_enrichment_and_reports()
