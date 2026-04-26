"""
MHRF Crisis Encounter Analysis
Author: Michelle Calderwood
File: 02_data_cleaning.py

Purpose:
Clean and standardize the raw MHRF dataset, rebuild analytical identity
variables from initials and birth year, and export both a restricted file
and a de-identified analytic file.

Major tasks:
1. Standardize column names
2. Remove duplicate incident date column
3. Clean initials and convert names/notes to 2-letter initials
4. Clean birth year
5. Drop previously created derived identity/history fields
6. Rebuild anonymous person_id
7. Recalculate age_group
8. Rebuild encounter history variables
9. Drop sensitive columns from final analytic dataset
"""

from pathlib import Path
import re
import pandas as pd
import numpy as np


# File Paths

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_PATH = PROJECT_ROOT / "data" / "raw" / "mhrf_data_2.xlsx"
RESTRICTED_OUTPUT_PATH = (
    PROJECT_ROOT / "data" / "processed" / "mhrf_cleaned_restricted.csv"
)
ANALYTIC_OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "mhrf_cleaned_analytic.csv"


# Helper Functions


def standardize_column_names(columns: pd.Index) -> pd.Index:
    """Convert raw column names into Python-friendly snake_case."""
    return (
        columns.str.strip()
        .str.lower()
        .str.replace(r"[^\w\s]", "", regex=True)
        .str.replace(r"\s+", "_", regex=True)
    )


def clean_text_value(value):
    """Strip whitespace and preserve missing values."""
    if pd.isna(value):
        return pd.NA
    value = str(value).strip()
    return value if value != "" else pd.NA


def extract_or_build_initials(value):
    """
    Convert raw initials/name field into standardized 2-letter initials.

    Rules:
    - Keep initials, but reduce 3+ letters to first + last
    - Convert full names to first initial + last initial
    - Extract initials from notes like: John Doe (possibly "DB"?)
    - Set unknown/error/unusable values to missing
    """
    if pd.isna(value):
        return pd.NA

    raw = str(value).strip()

    if raw == "":
        return pd.NA

    raw_lower = raw.lower()

    invalid_terms = ["unknown", "error", "date of incident provided", "n/a", "na"]
    if any(term in raw_lower for term in invalid_terms):
        return pd.NA

    quoted_match = re.search(r'"([A-Za-z]{2,5})"', raw)
    if quoted_match:
        extracted = quoted_match.group(1).upper()
        return extracted[0] + extracted[-1]

    cleaned = re.sub(r"[^A-Za-z\s']", " ", raw)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    if cleaned == "":
        return pd.NA

    tokens = cleaned.split()

    if len(tokens) == 1:
        letters_only = re.sub(r"[^A-Za-z]", "", tokens[0]).upper()

        if letters_only == "":
            return pd.NA

        if len(letters_only) >= 2:
            return letters_only[0] + letters_only[-1]

        return pd.NA

    first_token = re.sub(r"[^A-Za-z]", "", tokens[0])
    last_token = re.sub(r"[^A-Za-z]", "", tokens[-1])

    if first_token and last_token:
        return (first_token[0] + last_token[0]).upper()

    return pd.NA


def clean_birth_year(value, incident_year=None):
    """
    Clean birth year and keep only plausible values.
    Valid range: 1900 through incident year.
    """
    if pd.isna(value):
        return pd.NA

    value_str = str(value).strip()

    if value_str == "":
        return pd.NA

    match = re.search(r"\b(19\d{2}|20\d{2})\b", value_str)
    if not match:
        return pd.NA

    year = int(match.group(1))

    max_year = incident_year if incident_year is not None else pd.Timestamp.today().year

    if 1900 <= year <= max_year:
        return year

    return pd.NA


# Load Raw Data

print("\nLoading raw dataset...\n")
df = pd.read_excel(DATA_PATH)

print("Raw dataset shape:", df.shape)


# Standardize Column Names

df.columns = standardize_column_names(df.columns)

print("\nColumn names standardized.")


# Remove Duplicate Incident Date Column

df = df.drop(columns=["date_at_incident1"], errors="ignore")

df["date_at_incident"] = pd.to_datetime(df["date_at_incident"], errors="coerce")

print("\nDuplicate incident date column handled.")


# Basic Text Cleaning

text_columns = df.select_dtypes(include=["object", "string"]).columns

for col in text_columns:
    df[col] = df[col].apply(clean_text_value)

print("\nBasic text cleaning complete.")


# Drop Previously Created Derived Fields

old_derived_columns = [
    "person_id",
    "record_id",
    "age_group",
    "occurance_number",
    "prior_contact_flag",
    "total_contact",
    "age",
]

df = df.drop(columns=old_derived_columns, errors="ignore")

print("\nOld derived identity/history fields dropped.")


# Clean Initials

df["clean_initials"] = df["subject_or_client_initials"].apply(extract_or_build_initials)

print("\nInitials cleaned and standardized.")
print("Missing cleaned initials:", df["clean_initials"].isna().sum())


# Clean Birth Year

incident_year_series = df["date_at_incident"].dt.year

df["clean_birth_year"] = [
    clean_birth_year(birth_val, incident_year=incident_year)
    for birth_val, incident_year in zip(
        df["subject_or_client_birth_year"], incident_year_series
    )
]

df["clean_birth_year"] = pd.Series(df["clean_birth_year"], dtype="Int64")

print("\nBirth year cleaned.")
print("Missing cleaned birth year:", df["clean_birth_year"].isna().sum())


# Rebuild Anonymous Person ID

df["temp_person_key"] = (
    df["clean_initials"].astype("string")
    + "_"
    + df["clean_birth_year"].astype("string")
)

missing_mask = df["clean_initials"].isna() | df["clean_birth_year"].isna()
df.loc[missing_mask, "temp_person_key"] = pd.NA

unique_keys = (
    df["temp_person_key"]
    .dropna()
    .drop_duplicates()
    .sort_values()
    .reset_index(drop=True)
)

person_lookup = {
    key: f"PID-{i + 1:04d}"
    for i, key in enumerate(unique_keys)
}

df["person_id"] = df["temp_person_key"].map(person_lookup)

print("\nAnonymous person_id rebuilt.")
print("Unique person IDs:", df["person_id"].nunique(dropna=True))
print("Missing person IDs:", df["person_id"].isna().sum())


# Rebuild Record ID

df = df.reset_index(drop=True)
df["record_id"] = "REC-" + (df.index + 1).astype(str).str.zfill(5)

print("\nRecord ID rebuilt.")


# Recalculate Age Group

df["age"] = df["date_at_incident"].dt.year - df["clean_birth_year"]

df.loc[(df["age"] < 0) | (df["age"] > 100), "age"] = pd.NA

age_bins = [0, 17, 29, 39, 49, 59, 69, 79, 89, 100]
age_labels = [
    "UNDER 18",
    "18-29",
    "30-39",
    "40-49",
    "50-59",
    "60-69",
    "70-79",
    "80-89",
    "90-100",
]

df["age_group"] = pd.cut(df["age"], bins=age_bins, labels=age_labels)

print("\nAge group rebuilt.")
print("Missing age_group:", df["age_group"].isna().sum())


# Rebuild Encounter History Variables

df = df.sort_values(
    ["person_id", "date_at_incident", "record_id"], na_position="last"
).reset_index(drop=True)

df["occurance_number"] = df.groupby("person_id").cumcount() + 1
df.loc[df["person_id"].isna(), "occurance_number"] = pd.NA

df["total_contact"] = df.groupby("person_id")["person_id"].transform("count")
df.loc[df["person_id"].isna(), "total_contact"] = pd.NA

df["prior_contact_flag"] = np.where(df["occurance_number"] > 1, 1, 0)
df.loc[df["occurance_number"].isna(), "prior_contact_flag"] = pd.NA

print("\nEncounter history variables rebuilt.")
print("Missing occurance_number:", df["occurance_number"].isna().sum())
print("Missing total_contact:", df["total_contact"].isna().sum())


# Drop Age from Final Datasets

restricted_df = df.drop(columns=["age"], errors="ignore").copy()

print("\nAge column removed from restricted output.")


# Save Restricted File

restricted_df.to_csv(RESTRICTED_OUTPUT_PATH, index=False)

print("\nRestricted file saved to:")
print(RESTRICTED_OUTPUT_PATH)


# Drop Sensitive / Temporary Fields for Analytic File

analytic_df = restricted_df.drop(
    columns=[
        "subject_or_client_initials",
        "subject_or_client_birth_year",
        "clean_initials",
        "clean_birth_year",
        "temp_person_key",
        "name_of_professional_completing_this_form",
        "email",
        "id",
        "incident_number",
        "explain_the_incident_in_detail_with_respect_to_the_specific"
        "_commitment_criteria_identified_above",
        "use_the_space_below_to_offer_additional_comments_relevant_to"
        "_the_incident_andor_continuity_of_subjectclient_care",
        "if_more_than_one_agency_responded_to_the_incident_as_reported"
        "_in_section_1_responding_agencies_please_list_names_andor"
        "_badge_numbers_of_other_responding_personnel_that_could"
        "_offer_additiona",
        "if_neededappropriate_use_the_space_below_to_offer_information"
        "_specific_to_this_mhrf_such_as_the_content_of_the_mhrf_andor"
        "_related_process_steps",
    ],
    errors="ignore",
)

analytic_df.to_csv(ANALYTIC_OUTPUT_PATH, index=False)

print("\nAnalytic file saved to:")
print(ANALYTIC_OUTPUT_PATH)


# Final Summary

print("\nCleaning complete.")
print("Restricted shape:", restricted_df.shape)
print("Analytic shape:", analytic_df.shape)