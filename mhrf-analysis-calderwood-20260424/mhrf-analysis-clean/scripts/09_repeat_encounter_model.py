"""
MHRF Crisis Encounter Analysis
Author: Michelle Calderwood
File: 09_repeat_encounter_model.py

Purpose:
Run logistic regression to identify drivers of repeat crisis encounters.
"""

from pathlib import Path
import pandas as pd
import numpy as np
import statsmodels.api as sm


# Paths

PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_PATH = PROJECT_ROOT / "data" / "processed" / "mhrf_with_severity.csv"
OUTPUT_PATH = PROJECT_ROOT / "outputs" / "table_repeat_model_odds_ratios.csv"


# Load Data

print("\nLoading dataset...\n")
df = pd.read_csv(INPUT_PATH)

print("Shape:", df.shape)


# Collapse Rare Categories

main_facilities = {"Providence ED", "Riverwalk", "Community ED"}
df["receiving_facility_model"] = np.where(
    df["receiving_facility_clean"].isin(main_facilities),
    df["receiving_facility_clean"],
    "Other Facility"
)

main_call_types = {
    "Suicidal / Self-Harm",
    "Person Needs Assistance",
    "Welfare Check",
    "Disturbance",
    "Emergency Evaluation",
}
df["call_type_group_model"] = np.where(
    df["call_type_group"].isin(main_call_types),
    df["call_type_group"],
    "Other / Low Count"
)

print("Collapsed rare categories for modeling.")


# Select Variables

model_df = df[
    [
        "repeat_contact_flag",
        "severe_flag",
        "housing_status_clean",
        "call_type_group_model",
        "receiving_facility_model",
    ]
].copy()

model_df = model_df.dropna()

print("\nAfter dropna:", model_df.shape)


# Convert Variables

categorical_cols = [
    "housing_status_clean",
    "call_type_group_model",
    "receiving_facility_model",
]

model_df = pd.get_dummies(
    model_df,
    columns=categorical_cols,
    drop_first=True,
    dtype=int,
)

model_df["repeat_contact_flag"] = pd.to_numeric(
    model_df["repeat_contact_flag"], errors="coerce"
)
model_df["severe_flag"] = pd.to_numeric(
    model_df["severe_flag"], errors="coerce"
)

model_df = model_df.dropna()

print("\nAfter numeric conversion:", model_df.shape)


# Define X and y

X = model_df.drop(columns=["repeat_contact_flag"]).copy()
y = model_df["repeat_contact_flag"].astype(int).copy()

X = X.apply(pd.to_numeric, errors="coerce").astype(float)

valid_mask = X.notna().all(axis=1) & y.notna()
X = X.loc[valid_mask]
y = y.loc[valid_mask]

X = sm.add_constant(X, has_constant="add")

# Drop Riverwalk if it causes quasi-separation later
X = X.drop(columns=["receiving_facility_model_Riverwalk"], errors="ignore")

print("\nX columns:")
print(X.columns.tolist())

print("\nFinal modeling shape:")
print("X:", X.shape)
print("y:", y.shape)


# Fit Logistic Model

print("\nFitting logistic regression...\n")

model = sm.Logit(y, X)
result = model.fit(disp=True, maxiter=200)

print("\n--- MODEL SUMMARY ---\n")
print(result.summary())


# Odds Ratios

odds_ratios = pd.DataFrame(
    {
        "Variable": result.params.index,
        "Odds_Ratio": np.exp(result.params).round(3),
        "P_Value": result.pvalues.round(4),
        "Coefficient": result.params.round(4),
    }
)

odds_ratios = odds_ratios.sort_values(by="Odds_Ratio", ascending=False)
odds_ratios.to_csv(OUTPUT_PATH, index=False)

print("\n--- ODDS RATIOS ---\n")
print(odds_ratios)

print("\nOdds ratios saved to:")
print(OUTPUT_PATH)