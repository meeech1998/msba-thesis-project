"""
MHRF Crisis Encounter Analysis
Author: Michelle Calderwood
File: 06_severity_construction.py

Purpose:
Construct a unified severity outcome for thesis modeling.

This script creates:
1. involuntary_flag
2. high_criteria_flag
3. force_flag
4. subject_injury_flag
5. others_injury_flag
6. severity_score
7. severe_flag

Severity logic:
- Severe = 1 if:
    A) force used, OR
    B) subject injured, OR
    C) others injured, OR
    D) involuntary AND high criteria
"""

from pathlib import Path
import pandas as pd
import numpy as np


# Paths

PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_PATH = PROJECT_ROOT / "data" / "processed" / "mhrf_modeling_ready.csv"
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "mhrf_with_severity.csv"


# Load Data

print("\nLoading dataset...\n")
df = pd.read_csv(INPUT_PATH)

print("Shape:", df.shape)


# Helper Function


def yes_flag(value):
    """
    Convert yes/no/unsure style fields into binary flags.
    Returns:
        1 for yes
        0 for no
        0 for missing/unsure/unknown (for modeling consistency)
    """
    if pd.isna(value):
        return 0

    value = str(value).strip().lower()

    if value == "":
        return 0

    if "yes" in value:
        return 1

    if "no" in value:
        return 0

    if "unsure" in value or "unknown" in value:
        return 0

    return 0


# 1. Legal Severity

df["involuntary_flag"] = np.where(
    df["status_at_handoff_clean"].isin(["Involuntary", "Involuntary & Under Arrest"]),
    1,
    0
)

print("involuntary_flag created.")


# 2. Clinical Severity
# Use a stricter threshold:
# all 3 major commitment criteria categories documented

df["high_criteria_flag"] = np.where(
    df["commitment_criteria_count"] >= 3,
    1,
    0
)
df["high_criteria_flag"] = df["high_criteria_flag"].fillna(0)

print("high_criteria_flag created.")


# 3. Encounter Intensity

df["force_flag"] = df["was_force_utilized_during_the_encounter"].apply(yes_flag)
print("force_flag created.")

df["subject_injury_flag"] = df["was_the_subjectclient_injured"].apply(yes_flag)
print("subject_injury_flag created.")

df["others_injury_flag"] = df["did_the_subjectclient_injure_anyone"].apply(yes_flag)
print("others_injury_flag created.")


# 4. Severity Score

severity_components = [
    "involuntary_flag",
    "high_criteria_flag",
    "force_flag",
    "subject_injury_flag",
    "others_injury_flag"
]

df["severity_score"] = df[severity_components].sum(axis=1)

print("severity_score created.")


# 5. Final Severe Flag
# Severe if:
# - any high-intensity indicator is present
# OR
# - involuntary and high criteria are both present

df["severe_flag"] = np.where(
    (
        (df["force_flag"] == 1) |
        (df["subject_injury_flag"] == 1) |
        (df["others_injury_flag"] == 1)
    ) |
    (
        (df["involuntary_flag"] == 1) &
        (df["high_criteria_flag"] == 1)
    ),
    1,
    0
)

print("severe_flag created.")


# Save

df.to_csv(OUTPUT_PATH, index=False)

print("\nSaved to:")
print(OUTPUT_PATH)


# Summaries

print("\n--- Severity Score Distribution ---")
print(df["severity_score"].value_counts().sort_index())

print("\n--- Severe Flag Distribution ---")
print(df["severe_flag"].value_counts())

print("\n--- Component Breakdown ---")

for col in severity_components:
    print(f"\n{col}")
    print(df[col].value_counts())