"""
MHRF Crisis Encounter Analysis
Author: Michelle Calderwood
File: 11_time_patterns_analysis.py

Purpose:
Create clean time-based visuals for:
1. Monthly encounter volume
2. Seasonal encounter volume
3. Monthly severity rate
4. Monthly repeat encounter rate

Design choices:
- left-aligned titles
- cleaner x-axis labels
- highlight key peaks
- annotate only meaningful points
- suppress misleading severity/repeat rates for very low-volume months
- add clean data notes below charts where needed
"""

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick


# Paths

PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_PATH = PROJECT_ROOT / "data" / "processed" / "mhrf_with_clusters.csv"
OUTPUT_FOLDER = PROJECT_ROOT / "outputs"


# Load Data

print("\nLoading dataset...\n")
df = pd.read_csv(INPUT_PATH)

print("Shape:", df.shape)


# Date Prep

df["date_at_incident"] = pd.to_datetime(df["date_at_incident"], errors="coerce")
df = df.dropna(subset=["date_at_incident"]).copy()

df["year_month"] = df["date_at_incident"].dt.to_period("M").astype(str)
df["month_start"] = df["date_at_incident"].dt.to_period("M").dt.to_timestamp()

print("Date fields prepared.")


# Style Helpers

HIGHLIGHT_COLOR = "#2f6ea6"
NEUTRAL_COLOR = "#c7c7c7"


def clean_axes(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(False)


def add_data_note(fig, text):
    fig.text(
        0.01,
        0.01,
        text,
        ha="left",
        va="bottom",
        fontsize=9,
        color="gray"
    )


def annotate_peak(
    ax,
    x,
    y,
    label,
    x_offset_days=0,
    y_offset=0,
    horizontal_alignment="center"
):
    ax.annotate(
        label,
        xy=(x, y),
        xytext=(x + pd.Timedelta(days=x_offset_days), y + y_offset),
        textcoords="data",
        arrowprops=dict(arrowstyle="->", lw=1),
        fontsize=9,
        ha=horizontal_alignment
    )


# 1. Monthly Encounter Volume

monthly_counts = (
    df.groupby("month_start")
    .size()
    .reset_index(name="encounters")
    .sort_values("month_start")
)

fig, ax = plt.subplots(figsize=(11, 6))
ax.plot(
    monthly_counts["month_start"],
    monthly_counts["encounters"],
    marker="o",
    linewidth=2
)

top_months = monthly_counts.nlargest(2, "encounters").sort_values("month_start")
ax.scatter(top_months["month_start"], top_months["encounters"], s=60, zorder=3)

for _, row in top_months.iterrows():
    annotate_peak(
        ax,
        row["month_start"],
        row["encounters"],
        f"{row['month_start'].strftime('%b %Y')}: {int(row['encounters'])}",
        y_offset=4
    )

ax.set_title(
    "Crisis encounter volume increased through mid-2024 and peaked in late 2024 and fall 2025",
    loc="left",
    fontsize=14,
    pad=18
)
ax.set_xlabel("Month")
ax.set_ylabel("Number of Encounters")
ax.set_xticks(monthly_counts["month_start"][::2])
ax.set_xticklabels(
    [d.strftime("%b %Y") for d in monthly_counts["month_start"][::2]],
    rotation=45,
    ha="right"
)
clean_axes(ax)
plt.tight_layout(rect=[0, 0.05, 1, 1])
plt.savefig(OUTPUT_FOLDER / "fig_monthly_trend.png", dpi=300, bbox_inches="tight")
plt.close()

print("Saved: fig_monthly_trend.png")


# 2. Seasonality

season_order = ["Spring", "Summer", "Fall", "Winter"]

season_counts = (
    df.groupby("incident_season")
    .size()
    .reindex(season_order)
    .reset_index(name="encounters")
)

peak_season = season_counts.loc[season_counts["encounters"].idxmax(), "incident_season"]

colors = [
    HIGHLIGHT_COLOR if season == peak_season else NEUTRAL_COLOR
    for season in season_counts["incident_season"]
]

fig, ax = plt.subplots(figsize=(9, 6))
bars = ax.bar(
    season_counts["incident_season"],
    season_counts["encounters"],
    color=colors
)

for bar, value in zip(bars, season_counts["encounters"]):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 4,
        str(int(value)),
        ha="center",
        fontsize=10
    )

ax.set_title(
    "Encounter volume appears higher in summer and fall, though early 2024 underreporting may influence this pattern",
    loc="left",
    fontsize=14,
    pad=18
)
ax.set_xlabel("Season")
ax.set_ylabel("Number of Encounters")
clean_axes(ax)
add_data_note(
    fig,
    "Note: Lower encounter counts in early 2024 may reflect incomplete form adoption "
    "rather than true seasonal variation."
)
plt.tight_layout(rect=[0, 0.05, 1, 1])
plt.savefig(OUTPUT_FOLDER / "fig_seasonality.png", dpi=300, bbox_inches="tight")
plt.close()

print("Saved: fig_seasonality.png")


# 3. Severity Trend

severity_monthly = (
    df.groupby("month_start")
    .agg(
        severe_rate=("severe_flag", "mean"),
        encounters=("severe_flag", "size")
    )
    .reset_index()
    .sort_values("month_start")
)

severity_plot = severity_monthly.copy()
severity_plot.loc[severity_plot["encounters"] < 10, "severe_rate"] = pd.NA

fig, ax = plt.subplots(figsize=(11, 6))
ax.plot(
    severity_plot["month_start"],
    severity_plot["severe_rate"],
    marker="o",
    linewidth=2
)

valid_severity = severity_plot.dropna(subset=["severe_rate"]).copy()
peak_severity = valid_severity.loc[valid_severity["severe_rate"].idxmax()]

ax.scatter([peak_severity["month_start"]], [peak_severity["severe_rate"]], s=60, zorder=3)
annotate_peak(
    ax,
    peak_severity["month_start"],
    peak_severity["severe_rate"],
    f"{peak_severity['month_start'].strftime('%b %Y')}: {peak_severity['severe_rate']:.0%}",
    y_offset=0.06
)

ax.set_ylim(0, valid_severity["severe_rate"].max() + 0.12)

ax.set_title(
    "Severity rates remained relatively stable over time after excluding low-volume months",
    loc="left",
    fontsize=14,
    pad=18
)
ax.set_xlabel("Month")
ax.set_ylabel("Percent Severe")
ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
ax.set_xticks(severity_plot["month_start"][::2])
ax.set_xticklabels(
    [d.strftime("%b %Y") for d in severity_plot["month_start"][::2]],
    rotation=45,
    ha="right"
)
clean_axes(ax)
add_data_note(
    fig,
    "Note: Months with fewer than 10 encounters were excluded to avoid inflated severity rates."
)
plt.tight_layout(rect=[0, 0.05, 1, 1])
plt.savefig(OUTPUT_FOLDER / "fig_severity_trend.png", dpi=300, bbox_inches="tight")
plt.close()

print("Saved: fig_severity_trend.png")


# 4. Repeat Trend

repeat_monthly = (
    df.groupby("month_start")
    .agg(
        repeat_rate=("repeat_contact_flag", "mean"),
        encounters=("repeat_contact_flag", "size")
    )
    .reset_index()
    .sort_values("month_start")
)

repeat_plot = repeat_monthly.copy()
repeat_plot.loc[repeat_plot["encounters"] < 10, "repeat_rate"] = pd.NA

fig, ax = plt.subplots(figsize=(11, 6))
ax.plot(
    repeat_plot["month_start"],
    repeat_plot["repeat_rate"],
    marker="o",
    linewidth=2
)

valid_repeat = repeat_plot.dropna(subset=["repeat_rate"]).copy()
peak_repeat = valid_repeat.loc[valid_repeat["repeat_rate"].idxmax()]

ax.scatter([peak_repeat["month_start"]], [peak_repeat["repeat_rate"]], s=60, zorder=3)
annotate_peak(
    ax,
    peak_repeat["month_start"],
    peak_repeat["repeat_rate"],
    f"{peak_repeat['month_start'].strftime('%b %Y')}: {peak_repeat['repeat_rate']:.0%}",
    x_offset_days=-10,
    y_offset=-0.06,
    horizontal_alignment="right"
)

ax.set_ylim(0, valid_repeat["repeat_rate"].max() + 0.12)

ax.set_title(
    "Repeat encounter rates increased slightly in late 2025 but were otherwise consistent over time",
    loc="left",
    fontsize=14,
    pad=25
)
ax.set_xlabel("Month")
ax.set_ylabel("Percent Repeat")
ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
ax.set_xticks(repeat_plot["month_start"][::2])
ax.set_xticklabels(
    [d.strftime("%b %Y") for d in repeat_plot["month_start"][::2]],
    rotation=45,
    ha="right"
)
clean_axes(ax)
add_data_note(
    fig,
    "Note: Low-volume months were excluded to prevent distortion in repeat encounter rates."
)
plt.tight_layout(rect=[0, 0.05, 1, 1])
plt.savefig(OUTPUT_FOLDER / "fig_repeat_trend.png", dpi=300, bbox_inches="tight")
plt.close()

print("Saved: fig_repeat_trend.png")

print("\nTime pattern analysis complete.\n")