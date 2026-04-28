"""
MHRF Crisis Encounter Analysis
Author: Michelle Calderwood
File: 03_data_quality_checks.py

Purpose:
Run quality checks on the cleaned MHRF dataset to identify issues
that still need to be fixed before feature engineering and modeling.

Checks included:
1. Dataset shape and columns
2. Duplicate date columns
3. Missing person_id and age_group
4. Frequency of age_group
5. Encounter history review
6. Rows needing manual review
7. Export QA review files
"""

from pathlib import Path
import pandas as pd


# File Paths

PROJECT_ROOT = Path(__file__).resolve().parents[1]

RESTRICTED_PATH = PROJECT_ROOT / "data" / "processed" / "mhrf_cleaned_restricted.csv"
ANALYTIC_PATH = PROJECT_ROOT / "data" / "processed" / "mhrf_cleaned_analytic.csv"

QA_MISSING_PERSON_PATH = PROJECT_ROOT / "outputs" / "qa_missing_person_id.csv"
QA_MISSING_AGE_PATH = PROJECT_ROOT / "outputs" / "qa_missing_age_group.csv"
QA_DUPLICATE_PERSON_PATH = PROJECT_ROOT / "outputs" / "qa_repeat_person_preview.csv"


# Load Data

print("\nLoading cleaned files...\n")

restricted_df = pd.read_csv(RESTRICTED_PATH)
analytic_df = pd.read_csv(ANALYTIC_PATH)

print("Restricted shape:", restricted_df.shape)
print("Analytic shape:", analytic_df.shape)


# Column Review

print("\nRestricted columns:\n")
for col in restricted_df.columns:
    print(col)

print("\nAnalytic columns:\n")
for col in analytic_df.columns:
    print(col)


# Duplicate Date Column Check

date_like_cols_restricted = [col for col in restricted_df.columns if "date_at_incident" in col]
date_like_cols_analytic = [col for col in analytic_df.columns if "date_at_incident" in col]

print("\nDate-like columns in restricted file:", date_like_cols_restricted)
print("Date-like columns in analytic file:", date_like_cols_analytic)


# Missingness Checks

print("\nMissing person_id in restricted file:", restricted_df["person_id"].isna().sum())
print("Missing person_id in analytic file:", analytic_df["person_id"].isna().sum())

print("\nMissing age_group in restricted file:", restricted_df["age_group"].isna().sum())
print("Missing age_group in analytic file:", analytic_df["age_group"].isna().sum())

if "age" in restricted_df.columns:
    print("\nMissing age in restricted file:", restricted_df["age"].isna().sum())

if "age" in analytic_df.columns:
    print("Missing age in analytic file:", analytic_df["age"].isna().sum())


# Age Group Distribution

print("\nAge group counts (restricted):\n")
print(restricted_df["age_group"].value_counts(dropna=False).sort_index())

print("\nAge group counts (analytic):\n")
print(analytic_df["age_group"].value_counts(dropna=False).sort_index())


# Encounter History Checks

print("\nOccurrence number summary:\n")
if "occurance_number" in restricted_df.columns:
    print(restricted_df["occurance_number"].value_counts(dropna=False).sort_index().head(20))

print("\nTotal contact summary:\n")
if "total_contact" in restricted_df.columns:
    print(restricted_df["total_contact"].value_counts(dropna=False).sort_index().head(20))

print("\nPrior contact flag summary:\n")
if "prior_contact_flag" in restricted_df.columns:
    print(restricted_df["prior_contact_flag"].value_counts(dropna=False).sort_index())


# Review Repeated Person IDs

repeat_preview = restricted_df.copy()

if "date_at_incident" in repeat_preview.columns:
    repeat_preview["date_at_incident"] = pd.to_datetime(
        repeat_preview["date_at_incident"], errors="coerce"
    )

repeat_preview = repeat_preview.sort_values(
    ["person_id", "date_at_incident"], na_position="last"
)

repeat_preview = repeat_preview[
    repeat_preview["total_contact"].fillna(0) > 1
][
    [
        "person_id",
        "record_id",
        "date_at_incident",
        "occurance_number",
        "total_contact",
        "age_group",
    ]
].head(50)

repeat_preview.to_csv(QA_DUPLICATE_PERSON_PATH, index=False)

print("\nRepeat-person preview saved to:")
print(QA_DUPLICATE_PERSON_PATH)


# Export Manual Review Files

_pii_cols = [
    "subject_or_client_initials", "subject_or_client_birth_year",
    "clean_initials", "clean_birth_year", "temp_person_key",
    "name_of_professional_completing_this_form", "email", "id",
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
]

missing_person_df = (
    restricted_df[restricted_df["person_id"].isna()]
    .drop(columns=_pii_cols, errors="ignore")
    .copy()
)
missing_person_df.to_csv(QA_MISSING_PERSON_PATH, index=False)

print("\nMissing person_id review file saved to:")
print(QA_MISSING_PERSON_PATH)

missing_age_df = (
    restricted_df[restricted_df["age_group"].isna()]
    .drop(columns=_pii_cols, errors="ignore")
    .copy()
)
missing_age_df.to_csv(QA_MISSING_AGE_PATH, index=False)

print("\nMissing age_group review file saved to:")
print(QA_MISSING_AGE_PATH)


# Final Notes

print("\nQuality check complete.")
print("Next step: review QA files and then revise 02_data_cleaning.py if needed.")

#  Revisions to 02_data_cleaning.py
#
# Based on these quality check findings, the next version of
# 02_data_cleaning.py should make the following changes:
#
# 1. Drop the duplicate incident date column:
#    - Remove date_at_incident1
#    - Keep only date_at_incident
#
# 2. Remove the age column from outputs:
#    - Keep age_group only
#    - This is cleaner for analysis and better for de-identification
#
# 3. Keep rebuilt fields created from scratch:
#    - person_id
#    - record_id
#    - occurance_number
#    - total_contact
#    - prior_contact_flag
#    - age_group
#
# 4. Continue dropping old derived fields before rebuilding:
#    - old person_id
#    - old record_id
#    - old age_group
#    - old occurance_number
#    - old total_contact
#    - old prior_contact_flag
#
# 5. Continue using:
#    - cleaned initials + cleaned birth year
#    - only as temporary matching logic
#    - never in final analytic file
#
# 6. Final analytic file will exclude:
#    - subject_or_client_initials
#    - subject_or_client_birth_year
#    - clean_initials
#    - clean_birth_year
#    - temp_person_key
#    - age
#    - date_at_incident1
#
# End of QA revision notes.