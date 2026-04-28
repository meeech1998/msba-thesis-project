"""
MHRF Crisis Encounter Analysis
Author: Michelle Calderwood
File: 04_feature_engineering.py

Purpose:
Create additional modeling and analysis variables from the cleaned
analytic MHRF dataset.

Variables created:
1. repeat_contact_flag
2. high_frequency_flag
3. super_user_flag
4. call_type_clean
5. call_type_group
6. receiving_facility_clean
7. housing_status_clean
8. status_at_handoff_clean
9. commitment_criteria_count
10. incident_year
11. incident_month
12. incident_season
"""

from pathlib import Path
import re
import pandas as pd
import numpy as np


# File Paths

PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_PATH = PROJECT_ROOT / "data" / "processed" / "mhrf_cleaned_analytic.csv"
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "mhrf_modeling_ready.csv"
CALL_TYPE_REVIEW_PATH = PROJECT_ROOT / "outputs" / "qa_call_type_review.csv"


# Helper Functions


def standardize_column_names(columns: pd.Index) -> pd.Index:
    """Convert column names to predictable snake_case."""
    return (
        columns.str.strip()
        .str.lower()
        .str.replace(r"[^\w\s]", "", regex=True)
        .str.replace(r"\s+", "_", regex=True)
    )


def normalize_call_type(value):
    """Clean raw call type text into a normalized text value."""
    if pd.isna(value):
        return pd.NA

    value = str(value).strip().lower()

    if value == "":
        return pd.NA

    value = value.replace("&", " and ")
    value = value.replace("/", " / ")
    value = value.replace("-", " ")
    value = value.replace(";", " ")
    value = re.sub(r"[^a-z0-9\s/]", " ", value)
    value = re.sub(r"\s+", " ", value).strip()

    replacements = {
        "pna": "person needs assistance",
        "p n a": "person needs assistance",
        "person need assis": "person needs assistance",
        "person need assistance": "person needs assistance",
        "person needs assistatance": "person needs assistance",
        "persons needs assistance": "person needs assistance",
        "person that needs assistance": "person needs assistance",
        "person needs assessment": "person needs assistance",
        "mhe": "mental health evaluation",
        "mh 1": "mental health",
        "mh1": "mental health",
        "emergency eval": "emergency evaluation",
        "energency eval": "emergency evaluation",
        "medical stanby bls": "medical standby bls",
        "medical stand by bls": "medical standby bls",
        "disturbanc": "disturbance",
        "tresspassing": "trespassing",
        "incorrigable": "incorrigible juvenile",
        "incorrigalbe juvenile": "incorrigible juvenile",
        "suicide person": "suicidal person",
        "suicidal caller": "suicidal person",
        "suicidal claller": "suicidal person",
        "suicidal ideations": "suicidal ideation",
        "runway / suicidal person": "runaway / suicidal person",
        "person needs assistance / suicidal person": "person needs assistance / suicidal person",
        "person to be removed / welfare check": "person to be removed / welfare check",
    }

    if value in replacements:
        value = replacements[value]

    return value


def group_call_type(value):
    """Map normalized call type into broader analytic categories."""
    if pd.isna(value):
        return "Missing"

    v = str(value)

    if any(term in v for term in [
        "assault", "sexual assault", "partner family member assault",
        "intimidation", "harassment", "shots fired", "sex offense"
    ]):
        return "Assault / Violence"

    if any(term in v for term in [
        "suicidal", "suicide", "self harm", "selfharm", "attempted suicide"
    ]):
        return "Suicidal / Self-Harm"

    if "person needs assistance" in v:
        return "Person Needs Assistance"

    if "welfare check" in v:
        return "Welfare Check"

    if "disturbance" in v or "domestic disturbance" in v:
        return "Disturbance"

    if (
        "emergency evaluation" in v
        or "evaluation" in v
        or "mental health evaluation" in v
    ):
        return "Emergency Evaluation"

    if any(term in v for term in [
        "medical", "overdose", "medical transfer", "medical emergency",
        "medical assistance", "medical call", "medical standby"
    ]):
        return "Medical"

    if "person to be removed" in v or "removed" in v:
        return "Person to be Removed"

    if "suspicious activity" in v or "privacy in communications" in v:
        return "Suspicious Activity"

    if any(term in v for term in [
        "juvenile", "runaway", "ungovernable"
    ]):
        return "Juvenile / Runaway"

    if any(term in v for term in [
        "trespass", "trespassing", "disorderly conduct", "criminal mischief", "burglary"
    ]):
        return "Trespass / Disorderly Conduct"

    if any(term in v for term in [
        "mental health", "involuntary", "invol", "order of apprehension", "officer initiated"
    ]):
        return "Mental Health Other"

    if any(term in v for term in [
        "assist fire", "fire assist", "assist law enforcement", "assist outside agency",
        "agency request", "client request", "client requested", "officer request",
        "not applicable", "not provided", "not recorded", "transport",
        "hazard", "hazards", "missing person", "probation", "traffic hazard",
        "fire vehicle", "follow up", "doc", "pfma", "eval"
    ]):
        return "Other / Administrative / Unknown"

    return "Other / Administrative / Unknown"


def clean_receiving_facility(value):
    """Standardize receiving facility values."""
    if pd.isna(value):
        return "Unknown"

    value = str(value).strip().lower()

    if value == "":
        return "Unknown"
    if "providence" in value:
        return "Providence ED"
    if "riverwalk" in value:
        return "Riverwalk"
    if "community" in value:
        return "Community ED"
    if "dakota" in value:
        return "Dakota Place"
    if "pat" in value:
        return "St. Pat's"
    if "informational report" in value:
        return "Unknown"
    if "box checked" in value:
        return "Unknown"
    if "not listed" in value:
        return "Unknown"
    if value == "other":
        return "Other"

    return "Unknown"


def clean_housing_status(value):
    """Standardize housing status."""
    if pd.isna(value):
        return "Unknown"

    value = str(value).strip().lower()

    if value == "":
        return "Unknown"
    if "unhoused" in value:
        return "Unhoused"
    if "housed" in value and "facility" not in value:
        return "Housed"
    if "facility" in value:
        return "Facility"
    if "unknown" in value:
        return "Unknown"

    return "Unknown"


def clean_handoff_status(value):
    """Standardize status at handoff to facility."""
    if pd.isna(value):
        return "Unknown"

    value = str(value).strip().lower()

    if value == "":
        return "Unknown"
    if "involuntary" in value and "arrest" in value:
        return "Involuntary & Under Arrest"
    if "involuntary" in value:
        return "Involuntary"
    if "voluntary" in value:
        return "Voluntary"

    return "Unknown"


def assign_season(month):
    """Convert month number into season."""
    if pd.isna(month):
        return pd.NA
    month = int(month)

    if month in [12, 1, 2]:
        return "Winter"
    if month in [3, 4, 5]:
        return "Spring"
    if month in [6, 7, 8]:
        return "Summer"
    if month in [9, 10, 11]:
        return "Fall"

    return pd.NA


# Load Data

print("\nLoading analytic dataset...\n")
df = pd.read_csv(INPUT_PATH)

print("Input shape:", df.shape)

df.columns = standardize_column_names(df.columns)

print("\nColumn names standardized.")


# Create Repeat Contact Flag

df["repeat_contact_flag"] = np.where(df["occurance_number"] > 1, 1, 0)
df.loc[df["occurance_number"].isna(), "repeat_contact_flag"] = pd.NA

print("repeat_contact_flag created.")


# Create High Frequency Flag

df["high_frequency_flag"] = np.where(df["total_contact"] >= 3, 1, 0)
df.loc[df["total_contact"].isna(), "high_frequency_flag"] = pd.NA

print("high_frequency_flag created.")


# Create Super User Flag

df["super_user_flag"] = np.where(df["total_contact"] >= 10, 1, 0)
df.loc[df["total_contact"].isna(), "super_user_flag"] = pd.NA

print("super_user_flag created.")


# Clean and Group Call Type

df["call_type_clean"] = df["call_type"].apply(normalize_call_type)
df["call_type_group"] = df["call_type_clean"].apply(group_call_type)

print("call_type_clean created.")
print("call_type_group created.")


# Save Call Type Review Table

call_type_review = (
    df[["call_type", "call_type_clean", "call_type_group"]]
    .drop_duplicates()
    .sort_values(["call_type_group", "call_type_clean", "call_type"], na_position="last")
)

call_type_review.to_csv(CALL_TYPE_REVIEW_PATH, index=False)

print("Call type review file saved to:")
print(CALL_TYPE_REVIEW_PATH)


# Clean Receiving Facility

facility_col = "receiving_facility_select_one"
df["receiving_facility_clean"] = df[facility_col].apply(clean_receiving_facility)

print("\nreceiving_facility_clean created.")


# Clean Housing Status

housing_col = "subject_or_clients_housing_status_at_time_of_incident_select_one"
df["housing_status_clean"] = df[housing_col].apply(clean_housing_status)

print("housing_status_clean created.")


# Clean Status at Handoff

handoff_col = "status_of_subject_or_client_at_time_of_handoff_to_facility_select_one"
df["status_at_handoff_clean"] = df[handoff_col].apply(clean_handoff_status)

print("status_at_handoff_clean created.")


# Create Commitment Criteria Count

criteria_cols = [
    "criteria_for_commitment_imminent_danger_to_self_check_all_that_apply",
    "criteria_for_commitment_imminent_danger_to_others_check_all_that_apply",
    "criteria_for_commitment_unable_to_meet_basic_needs_check_all_that_apply",
]

df["commitment_criteria_count"] = df[criteria_cols].notna().sum(axis=1)

# set to missing if all three source fields are missing
all_missing_mask = df[criteria_cols].isna().all(axis=1)
df.loc[all_missing_mask, "commitment_criteria_count"] = pd.NA

print("commitment_criteria_count created.")


# Create Date-Based Fields

df["date_at_incident"] = pd.to_datetime(df["date_at_incident"], errors="coerce")
df["incident_year"] = df["date_at_incident"].dt.year
df["incident_month"] = df["date_at_incident"].dt.month
df["incident_season"] = df["incident_month"].apply(assign_season)

print("incident_year, incident_month, and incident_season created.")


# Save Modeling File

df.to_csv(OUTPUT_PATH, index=False)

print("\nModeling-ready dataset saved to:")
print(OUTPUT_PATH)

print("\nFinal shape:", df.shape)


# Quick Summaries

print("\nRepeat contact flag summary:")
print(df["repeat_contact_flag"].value_counts(dropna=False).sort_index())

print("\nHigh frequency flag summary:")
print(df["high_frequency_flag"].value_counts(dropna=False).sort_index())

print("\nSuper user flag summary:")
print(df["super_user_flag"].value_counts(dropna=False).sort_index())

print("\nCall type group summary:")
print(df["call_type_group"].value_counts(dropna=False))

print("\nReceiving facility clean summary:")
print(df["receiving_facility_clean"].value_counts(dropna=False))

print("\nHousing status clean summary:")
print(df["housing_status_clean"].value_counts(dropna=False))

print("\nStatus at handoff clean summary:")
print(df["status_at_handoff_clean"].value_counts(dropna=False))

print("\nCommitment criteria count summary:")
print(df["commitment_criteria_count"].value_counts(dropna=False).sort_index())

print("\nIncident season summary:")
print(df["incident_season"].value_counts(dropna=False))