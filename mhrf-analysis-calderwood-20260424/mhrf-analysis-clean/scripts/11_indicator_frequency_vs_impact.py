"""
MHRF Crisis Encounter Analysis
Author: Michelle Calderwood
File: 11_indicator_frequency_vs_impact.py

Purpose:
Compare indicator frequency vs. severity impact using the same
indicator construction logic used in 08_indicator_severity_model.py.

This figure includes only statistically significant indicators
from the severity model (p < 0.05).
"""

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# Paths

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_PATH = PROJECT_ROOT / "data" / "processed" / "mhrf_with_severity.csv"
MODEL_PATH = PROJECT_ROOT / "outputs" / "table_indicator_severity_odds_ratios.csv"
OUTPUT_PATH = PROJECT_ROOT / "outputs" / "fig_frequency_vs_impact.png"

# Load data

model_df = pd.read_csv(MODEL_PATH)
print("Loaded odds ratio table:", model_df.shape)

usecols = [
    "drug_or_alcohol_involvement",
    "behaviors_evident_at_time_of_incident_check_all_that_apply",
    "if_delusions_or_hallucinations_were_observed_during_the_encounter_please_describe_them_below",
]

df = pd.read_csv(
    DATA_PATH,
    usecols=usecols,
    low_memory=False,
    on_bad_lines="skip"
)
print("Loaded main dataset:", df.shape)

# Helper functions


def yes_flag(value):
    """Convert yes/no style fields into binary flags."""
    if pd.isna(value):
        return 0

    value = str(value).strip().lower()

    if value == "":
        return 0

    if "yes" in value:
        return 1

    if "no" in value:
        return 0

    return 0


def keyword_flag(series, pattern):
    """Return 1 if keyword pattern appears in text field, else 0."""
    return (
        series.astype(str)
        .str.contains(pattern, case=False, na=False, regex=True)
        .astype(int)
    )

# Build indicator flags from source columns

behavior_col = "behaviors_evident_at_time_of_incident_check_all_that_apply"
psychosis_text_col = (
    "if_delusions_or_hallucinations_were_observed_during_the_ENCOUNTER_please_describe_them_below"
)

# fallback in case capitalization differs
if psychosis_text_col not in df.columns:
    psychosis_text_col = (
        "if_delusions_or_hallucinations_were_observed_during_the_encounter_please_describe_them_below"
    )

df["substance_involvement_flag"] = df["drug_or_alcohol_involvement"].apply(yes_flag)
df["depressed_flag"] = keyword_flag(df[behavior_col], r"depress")
df["confusion_flag"] = keyword_flag(df[behavior_col], r"disorient|confus")
df["disorganized_speech_flag"] = keyword_flag(df[behavior_col], r"disorganized speech")
df["angry_uncooperative_flag"] = keyword_flag(df[behavior_col], r"angry|uncooperative")
df["scared_frightened_flag"] = keyword_flag(df[behavior_col], r"scared|frightened")
df["manic_flag"] = keyword_flag(df[behavior_col], r"manic")
df["delusions_flag"] = keyword_flag(df[psychosis_text_col], r"delusion")
df["hallucinations_flag"] = keyword_flag(df[psychosis_text_col], r"hallucin")

# Indicators used in model

indicators = [
    "angry_uncooperative_flag",
    "manic_flag",
    "confusion_flag",
    "delusions_flag",
    "substance_involvement_flag",
    "depressed_flag",
    "disorganized_speech_flag",
    "scared_frightened_flag",
    "hallucinations_flag",
]

# Calculate frequency (% of encounters)

freq_df = (df[indicators].mean() * 100).reset_index()
freq_df.columns = ["Variable", "Frequency"]

# Merge with model output

plot_df = pd.merge(freq_df, model_df, on="Variable", how="inner")
plot_df = plot_df[plot_df["Variable"] != "const"].copy()

# keep only statistically significant indicators
plot_df = plot_df[plot_df["P_Value"] < 0.05].copy()

# Clean labels

label_map = {
    "angry_uncooperative_flag": "Angry / Uncooperative",
    "manic_flag": "Manic",
    "confusion_flag": "Confusion",
    "delusions_flag": "Delusions",
    "substance_involvement_flag": "Substance",
    "depressed_flag": "Depression",
    "disorganized_speech_flag": "Disorganized Speech",
    "scared_frightened_flag": "Scared / Frightened",
    "hallucinations_flag": "Hallucinations",
}

plot_df["Label"] = plot_df["Variable"].map(label_map)
plot_df = plot_df.sort_values("Frequency").copy()

print("\nFinal statistically significant dataset for Figure 11:\n")
print(plot_df[["Label", "Frequency", "Coefficient", "P_Value"]])

# Plot

fig, ax = plt.subplots(figsize=(11, 7.5))

ax.scatter(
    plot_df["Frequency"],
    plot_df["Coefficient"],
    s=95
)

# custom label placement
for _, row in plot_df.iterrows():
    x = row["Frequency"]
    y = row["Coefficient"]
    label = row["Label"]

    if label == "Hallucinations":
        x_offset = 0.45
        y_offset = -0.06
    elif label == "Angry / Uncooperative":
        x_offset = 0.55
        y_offset = 0.05
    else:
        x_offset = 0.35
        y_offset = 0.02

    ax.text(
        x + x_offset,
        y + y_offset,
        label,
        fontsize=10
    )

# thresholds
x_split = plot_df["Frequency"].median()
y_split = 0

# reference lines
ax.axhline(y_split, color="black", linewidth=0.9)
ax.axvline(x_split, color="gray", linestyle="--", linewidth=1)

# quadrant labels
ax.text(
    8.0, 1.36,
    "Less Common\nHigher Impact",
    fontsize=11,
    ha="left",
    va="top"
)
ax.text(
    23.5, 1.36,
    "More Common\nHigher Impact",
    fontsize=11,
    ha="left",
    va="top"
)
ax.text(
    8.0, -1.38,
    "Less Common\nLower Impact",
    fontsize=11,
    ha="left",
    va="bottom"
)
ax.text(
    23.5, -1.38,
    "More Common\nLower Impact",
    fontsize=11,
    ha="left",
    va="bottom"
)

# title and labels
ax.set_title(
    "Frequency vs. Severity Impact for Significant Indicators",
    fontsize=13,
    pad=14,
    fontweight="bold",
    loc="left",
    x=0.0
)
ax.set_xlabel("Indicator Frequency (% of Encounters)")
ax.set_ylabel("Severity Impact (Logistic Regression Coefficient)")

# axis limits
ax.set_xlim(-1, 34)
ax.set_ylim(-1.45, 1.42)

# clean style
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

plt.tight_layout()
plt.savefig(OUTPUT_PATH, dpi=300)
plt.close()

print("\nSaved figure to:")
print(OUTPUT_PATH)