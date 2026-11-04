# Member 4 – Enrichment Transformations and Reports (Step 6 part 2, Step 7)

## Your tasks
1. Understand and test the 5 enrichment transformations in `enrichment_reports.py`:

| # | Function | What it does | Why |
|---|---|---|---|
| T9 | `t9_add_date_parts` | year, month, month name, weekday | Monthly/trend analysis |
| T10 | `t10_add_season` | Winter / Pre-Monsoon / Southwest Monsoon / Post-Monsoon | Kerala rainfall is monsoon-driven |
| T11 | `t11_add_rainfall_category` | IMD classes: Very Light … Extremely Heavy | Describes intensity |
| T12 | `t12_add_station_totals_and_rank` | Station total rainfall and rank | Aggregation + ranking |
| T13 | `t13_sort_records` | Sort by station and date | Time-series ready |

2. Understand `generate_reports()`, which builds these reports (requirement: at least 3):
   `cleaned_data`, `summary_statistics`, `district_wise_report`, `monthly_report`, `seasonal_report`, `rainfall_category_report`, `top10_rainiest_days`, `top10_stations_by_avg_rainfall`, `bottom10_stations_by_avg_rainfall`, `highest_lowest_values`, `transformation_log`.
3. Run: `pip install pandas` then `python enrichment_reports.py` – reports appear in `reports/`.
4. Open 2–3 reports and write one or two lines about what each shows (for example, which month is wettest, which district is highest).
5. Take screenshots of the terminal and of a few reports; save them in `screenshots/` here.

## Files in this folder
| File | Purpose |
|---|---|
| `enrichment_reports.py` | Your code |
| `input/cleaned_stage1.csv` | Member 3's cleaned data (input) |
| `reports/` | Output folder (empty until you run the script) |

## Hand over to
Member 5 – the `reports/` folder and your report descriptions.

## Be ready to explain in viva
- How the IMD rainfall classes were chosen
- Why station averages are used for top/bottom 10 (stations have different numbers of readings)
- The data has no zero-rain days, so averages reflect rainy-day readings
