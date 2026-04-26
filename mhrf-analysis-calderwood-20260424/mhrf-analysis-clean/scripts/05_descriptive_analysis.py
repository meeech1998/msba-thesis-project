"""
MHRF Crisis Encounter Analysis
Author: Michelle Calderwood
File: 05_descriptive_analysis.py

Purpose:
Create descriptive analysis outputs for the thesis using the
modeling-ready MHRF dataset.
"""

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates as mdates


# File Paths

PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_PATH = PROJECT_ROOT / "data" / "processed" / "mhrf_with_severity.csv"
OUTPUT_DIR = PROJECT_ROOT / "outputs"

MONTHLY_TREND_PATH = OUTPUT_DIR / "fig_monthly_trend.png"
SEVERITY_TREND_PATH = OUTPUT_DIR / "fig_severity_trend.png"
REPEAT_TREND_PATH = OUTPUT_DIR / "fig_repeat_trend.png"


# Helper Functions


def style_bar_chart(
    categories,
    values,
    title,
    xlabel,
    output_path,
    highlight_labels=None,
    rotation=0,
    figsize=(10, 5)
):
    highlight_labels = highlight_labels or []

    categories = list(categories)
    values = list(values)

    colors = [
        "#2f6ea6" if cat in highlight_labels else "#c7c7c7"
        for cat in categories
    ]

    plt.figure(figsize=figsize)
    bars = plt.bar(categories, values, color=colors)

    plt.title(title, loc="left", fontsize=13)
    plt.xlabel(xlabel)
    plt.ylabel("")

    plt.yticks([])

    ax = plt.gca()
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_alpha(0.4)

    max_val = max(values) if len(values) > 0 else 0
    label_offset = max(max_val * 0.015, 1)

    for bar, val in zip(bars, values):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + label_offset,
            f"{int(val)}",
            ha="center",
            va="bottom",
            fontsize=10
        )

    plt.xticks(rotation=rotation, ha="right" if rotation else "center")
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()


def style_volume_line_chart(
    dates,
    values,
    title,
    output_path,
    ylabel="Number of Encounters",
    figsize=(12, 6)
):
    plt.figure(figsize=figsize)
    plt.plot(dates, values, linewidth=2)

    plt.title(title, loc="left", fontsize=13, pad=16)
    plt.xlabel("Month")
    plt.ylabel(ylabel)

    ax = plt.gca()
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    plt.xticks(rotation=35, ha="right")

    series = pd.DataFrame({"date": pd.to_datetime(dates), "value": values}).dropna()
    if not series.empty:
        peak_idx = series["value"].idxmax()
        peak_date = series.loc[peak_idx, "date"]
        peak_val = series.loc[peak_idx, "value"]

        plt.scatter(peak_date, peak_val, color="#2f6ea6", s=35, zorder=3)
        plt.annotate(
            f"{peak_date.strftime('%b %Y')}: {int(peak_val)}",
            xy=(peak_date, peak_val),
            xytext=(peak_date, peak_val + max(values) * 0.015),
            arrowprops=dict(arrowstyle="->"),
            fontsize=9,
            ha="center",
            va="bottom"
        )

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()


def style_percent_line_chart(
    dates,
    values,
    title,
    output_path,
    ylabel,
    note_text,
    figsize=(12, 6)
):
    plt.figure(figsize=figsize)
    plt.plot(dates, values, linewidth=1.8, marker="o", markersize=3.5)

    plt.title(title, loc="left", fontsize=13, pad=16)
    plt.xlabel("Month")
    plt.ylabel(ylabel)

    ax = plt.gca()
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1.0))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    plt.xticks(rotation=35, ha="right")

    series = pd.DataFrame({"date": pd.to_datetime(dates), "value": values}).dropna()
    if not series.empty:
        peak_idx = series["value"].idxmax()
        peak_date = series.loc[peak_idx, "date"]
        peak_val = series.loc[peak_idx, "value"]

        plt.scatter(peak_date, peak_val, color="#2f6ea6", s=35, zorder=3)
        plt.annotate(
            f"{peak_date.strftime('%b %Y')}: {peak_val:.0%}",
            xy=(peak_date, peak_val),
            xytext=(peak_date, peak_val + 0.03),
            arrowprops=dict(arrowstyle="->"),
            fontsize=9,
            ha="center",
            va="bottom"
        )

    plt.figtext(
        0.01,
        -0.03,
        note_text,
        ha="left",
        fontsize=8
    )

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()


# Load Data

print("\nLoading modeling-ready dataset...\n")
df = pd.read_csv(INPUT_PATH, low_memory=False)

print("Input shape:", df.shape)


# Prepare Date Fields

df["date_at_incident"] = pd.to_datetime(df["date_at_incident"], errors="coerce")
df["incident_year"] = pd.to_numeric(df["incident_year"], errors="coerce")
df["incident_month"] = pd.to_numeric(df["incident_month"], errors="coerce")

month_map = {
    1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr",
    5: "May", 6: "Jun", 7: "Jul", 8: "Aug",
    9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"
}
df["incident_month_label"] = df["incident_month"].map(month_map)

print("Date fields prepared.")


# 1. Monthly Encounter Volume Trend (ALL DATES)

monthly_volume = (
    df.groupby(df["date_at_incident"].dt.to_period("M"))
    .size()
    .reset_index(name="encounter_count")
)

monthly_volume["date_at_incident"] = monthly_volume["date_at_incident"].dt.to_timestamp()

monthly_volume.to_csv(
    OUTPUT_DIR / "table_monthly_trend.csv",
    index=False
)

style_volume_line_chart(
    dates=monthly_volume["date_at_incident"],
    values=monthly_volume["encounter_count"],
    title="Monthly crisis encounter peaked December 2024",
    output_path=MONTHLY_TREND_PATH
)

print("Saved monthly trend output.")


# 2. Monthly Severity Rate Trend (ALL DATES)

severity_monthly = (
    df.groupby(df["date_at_incident"].dt.to_period("M"))
    .agg(
        encounter_count=("severe_flag", "size"),
        severity_rate=("severe_flag", "mean")
    )
    .reset_index()
)

severity_monthly["date_at_incident"] = severity_monthly["date_at_incident"].dt.to_timestamp()

severity_monthly = severity_monthly[severity_monthly["encounter_count"] >= 10].copy()

severity_monthly.to_csv(
    OUTPUT_DIR / "table_severity_trend.csv",
    index=False
)

style_percent_line_chart(
    dates=severity_monthly["date_at_incident"],
    values=severity_monthly["severity_rate"],
    title="Severity rates remained relatively stable over time after excluding low-volume months",
    output_path=SEVERITY_TREND_PATH,
    ylabel="Percent Severe",
    note_text="Note: Months with fewer than 10 encounters were excluded to avoid inflated severity rates."
)

print("Saved severity trend output.")


# 3. Monthly Repeat Rate Trend (ALL DATES)

repeat_monthly = (
    df.groupby(df["date_at_incident"].dt.to_period("M"))
    .agg(
        encounter_count=("repeat_contact_flag", "size"),
        repeat_rate=("repeat_contact_flag", "mean")
    )
    .reset_index()
)

repeat_monthly["date_at_incident"] = repeat_monthly["date_at_incident"].dt.to_timestamp()

repeat_monthly = repeat_monthly[repeat_monthly["encounter_count"] >= 10].copy()

repeat_monthly.to_csv(
    OUTPUT_DIR / "table_repeat_trend.csv",
    index=False
)

style_percent_line_chart(
    dates=repeat_monthly["date_at_incident"],
    values=repeat_monthly["repeat_rate"],
    title="Repeat encounter rates increased slightly in late 2025 but were otherwise consistent over time",
    output_path=REPEAT_TREND_PATH,
    ylabel="Percent Repeat",
    note_text="Note: Low-volume months were excluded to prevent distortion in repeat encounter rates."
)

print("Saved repeat trend output.")


# 4. Encounters by Year

incidents_by_year = (
    df["incident_year"]
    .value_counts(dropna=False)
    .sort_index()
    .reset_index()
)
incidents_by_year.columns = ["incident_year", "encounter_count"]

incidents_by_year.to_csv(
    OUTPUT_DIR / "table_incidents_by_year.csv",
    index=False
)

plot_year = incidents_by_year[incidents_by_year["incident_year"].notna()].copy()
plot_year["incident_year"] = plot_year["incident_year"].astype(int).astype(str)

style_bar_chart(
    categories=plot_year["incident_year"],
    values=plot_year["encounter_count"],
    title="Most Recorded Crisis Encounters Occurred in 2024 and 2025",
    xlabel="Year",
    output_path=OUTPUT_DIR / "fig_incidents_by_year.png",
    highlight_labels=["2025"],
    rotation=0,
    figsize=(8, 5)
)

print("Saved incidents by year outputs.")


# 5. Encounters by Month

month_order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

incidents_by_month = (
    df["incident_month_label"]
    .value_counts()
    .reindex(month_order)
    .reset_index()
)
incidents_by_month.columns = ["incident_month", "encounter_count"]

incidents_by_month.to_csv(
    OUTPUT_DIR / "table_incidents_by_month.csv",
    index=False
)

style_bar_chart(
    categories=incidents_by_month["incident_month"],
    values=incidents_by_month["encounter_count"],
    title="Crisis Encounters Peaked in Late Summer and Early Fall",
    xlabel="Month",
    output_path=OUTPUT_DIR / "fig_incidents_by_month.png",
    highlight_labels=["Aug", "Sep", "Oct"],
    rotation=0,
    figsize=(10, 5)
)

print("Saved incidents by month outputs.")


# 6. Encounters by Season

season_order = ["Winter", "Spring", "Summer", "Fall"]

incidents_by_season = (
    df["incident_season"]
    .value_counts(dropna=False)
    .reindex(season_order + [pd.NA], fill_value=0)
    .reset_index()
)
incidents_by_season.columns = ["incident_season", "encounter_count"]

incidents_by_season.to_csv(
    OUTPUT_DIR / "table_incidents_by_season.csv",
    index=False
)

plot_season = incidents_by_season[incidents_by_season["incident_season"].notna()].copy()

style_bar_chart(
    categories=plot_season["incident_season"],
    values=plot_season["encounter_count"],
    title="Crisis Encounters Were Highest in Summer and Fall",
    xlabel="Season",
    output_path=OUTPUT_DIR / "fig_incidents_by_season.png",
    highlight_labels=["Summer", "Fall"],
    rotation=0,
    figsize=(8, 5)
)

print("Saved incidents by season outputs.")


# 7. Age Group Distribution

age_order = [
    "UNDER 18", "18-29", "30-39", "40-49",
    "50-59", "60-69", "70-79", "80-89", "90-100"
]

age_group_dist = (
    df["age_group"]
    .value_counts(dropna=False)
    .reindex(age_order + [pd.NA], fill_value=0)
    .reset_index()
)
age_group_dist.columns = ["age_group", "encounter_count"]

age_group_dist.to_csv(
    OUTPUT_DIR / "table_age_group_distribution.csv",
    index=False
)

plot_age = age_group_dist[age_group_dist["age_group"].notna()].copy()

style_bar_chart(
    categories=plot_age["age_group"],
    values=plot_age["encounter_count"],
    title="Young Adults Ages 18–39 Accounted for the Largest Share of Crisis Encounters",
    xlabel="Age Group",
    output_path=OUTPUT_DIR / "fig_age_distribution.png",
    highlight_labels=["18-29", "30-39"],
    rotation=0,
    figsize=(10, 5)
)

print("Saved age group outputs.")


# 8. Call Type Group Distribution

call_type_dist = (
    df["call_type_group"]
    .value_counts(dropna=False)
    .reset_index()
)
call_type_dist.columns = ["call_type_group", "encounter_count"]

call_type_dist.to_csv(
    OUTPUT_DIR / "table_call_type_group_distribution.csv",
    index=False
)

style_bar_chart(
    categories=call_type_dist["call_type_group"],
    values=call_type_dist["encounter_count"],
    title="Most Crisis Encounters Began as Suicidal/Self-Harm, Person Needs Assistance, or Welfare Check Calls",
    xlabel="Call Type Group",
    output_path=OUTPUT_DIR / "fig_call_type_distribution.png",
    highlight_labels=["Suicidal / Self-Harm", "Person Needs Assistance", "Welfare Check"],
    rotation=35,
    figsize=(12, 6)
)

print("Saved call type group outputs.")


# 9. Receiving Facility Distribution

facility_dist = (
    df["receiving_facility_clean"]
    .value_counts(dropna=False)
    .reset_index()
)
facility_dist.columns = ["receiving_facility_clean", "encounter_count"]

facility_dist.to_csv(
    OUTPUT_DIR / "table_receiving_facility_distribution.csv",
    index=False
)

style_bar_chart(
    categories=facility_dist["receiving_facility_clean"],
    values=facility_dist["encounter_count"],
    title="Providence ED Received the Largest Share of Mental Health Crisis Encounters",
    xlabel="Receiving Facility",
    output_path=OUTPUT_DIR / "fig_receiving_facility.png",
    highlight_labels=["Providence ED"],
    rotation=0,
    figsize=(10, 5)
)

print("Saved receiving facility outputs.")


# 10. Housing Status Distribution

housing_order = ["Housed", "Unhoused", "Facility", "Unknown"]

housing_dist = (
    df["housing_status_clean"]
    .value_counts(dropna=False)
    .reindex(housing_order, fill_value=0)
    .reset_index()
)
housing_dist.columns = ["housing_status_clean", "encounter_count"]

housing_dist.to_csv(
    OUTPUT_DIR / "table_housing_status_distribution.csv",
    index=False
)

style_bar_chart(
    categories=housing_dist["housing_status_clean"],
    values=housing_dist["encounter_count"],
    title="Most Encountered Individuals Were Housed, Though Unhoused Individuals Represented a Large Share",
    xlabel="Housing Status",
    output_path=OUTPUT_DIR / "fig_housing_distribution.png",
    highlight_labels=["Housed", "Unhoused"],
    rotation=0,
    figsize=(8, 5)
)

print("Saved housing status outputs.")


# 11. Status at Handoff Distribution

handoff_order = ["Voluntary", "Involuntary", "Involuntary & Under Arrest", "Unknown"]

handoff_dist = (
    df["status_at_handoff_clean"]
    .value_counts(dropna=False)
    .reindex(handoff_order, fill_value=0)
    .reset_index()
)
handoff_dist.columns = ["status_at_handoff_clean", "encounter_count"]

handoff_dist.to_csv(
    OUTPUT_DIR / "table_status_at_handoff_distribution.csv",
    index=False
)

style_bar_chart(
    categories=handoff_dist["status_at_handoff_clean"],
    values=handoff_dist["encounter_count"],
    title="Voluntary and Involuntary Handoffs Both Appeared Frequently in Crisis Encounters",
    xlabel="Status at Handoff",
    output_path=OUTPUT_DIR / "fig_status_at_handoff.png",
    highlight_labels=["Voluntary", "Involuntary"],
    rotation=0,
    figsize=(9, 5)
)

print("Saved status at handoff outputs.")


# 12. Commitment Criteria Count Distribution

criteria_dist = (
    df["commitment_criteria_count"]
    .value_counts(dropna=False)
    .sort_index()
    .reset_index()
)
criteria_dist.columns = ["commitment_criteria_count", "encounter_count"]

criteria_dist["commitment_criteria_label"] = criteria_dist["commitment_criteria_count"].map({
    1.0: "1 Criterion",
    2.0: "2 Criteria",
    3.0: "3 Criteria"
})

criteria_dist.to_csv(
    OUTPUT_DIR / "table_commitment_criteria_distribution.csv",
    index=False
)

plot_criteria = criteria_dist[criteria_dist["commitment_criteria_label"].notna()].copy()

style_bar_chart(
    categories=plot_criteria["commitment_criteria_label"],
    values=plot_criteria["encounter_count"],
    title="Most Crisis Encounters Documented All Three Major Commitment Criteria Categories",
    xlabel="Commitment Criteria Count",
    output_path=OUTPUT_DIR / "fig_commitment_criteria.png",
    highlight_labels=["3 Criteria"],
    rotation=0,
    figsize=(8, 5)
)

print("Saved commitment criteria outputs.")


# 13. Repeat vs One-Time Distribution

repeat_dist = (
    df["repeat_contact_flag"]
    .value_counts(dropna=False)
    .sort_index()
    .reset_index()
)
repeat_dist.columns = ["repeat_contact_flag", "encounter_count"]

repeat_dist["repeat_contact_label"] = repeat_dist["repeat_contact_flag"].map({
    0.0: "One-Time Encounter",
    1.0: "Repeat Encounter"
})

repeat_dist.to_csv(
    OUTPUT_DIR / "table_repeat_contact_distribution.csv",
    index=False
)

plot_repeat = repeat_dist[repeat_dist["repeat_contact_label"].notna()].copy()

repeat_total = plot_repeat["encounter_count"].sum()
repeat_count = plot_repeat.loc[
    plot_repeat["repeat_contact_label"] == "Repeat Encounter",
    "encounter_count"
].iloc[0]
repeat_pct = round((repeat_count / repeat_total) * 100)

repeat_title = f"About {repeat_pct}% of Crisis Encounters Were Repeat Contacts"

style_bar_chart(
    categories=plot_repeat["repeat_contact_label"],
    values=plot_repeat["encounter_count"],
    title=repeat_title,
    xlabel="Encounter Type",
    output_path=OUTPUT_DIR / "fig_repeat_contact.png",
    highlight_labels=["Repeat Encounter"],
    rotation=0,
    figsize=(7, 5)
)

print("Saved repeat contact outputs.")


# Final Summary

print("\nDescriptive analysis complete.")
print("Key output files saved to:")
print(OUTPUT_DIR)