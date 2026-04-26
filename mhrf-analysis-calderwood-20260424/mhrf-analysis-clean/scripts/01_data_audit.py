"""
MHRF Crisis Encounter Analysis
Author: Michelle Calderwood
File: 01_data_audit.py

Purpose:
Perform an initial audit of the raw MHRF dataset.
This script checks structure, missingness, key identity fields,
and duplicate incident date columns before cleaning.
"""

# Import Libraries

from pathlib import Path
import pandas as pd


# File Paths

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "raw" / "mhrf_data_2.xlsx"


# Load Dataset

print("\nLoading dataset...\n")
df = pd.read_excel(DATA_PATH)


# Basic Dataset Overview

print("Dataset Shape:")
print(df.shape)

print("\nFirst 5 Rows:")
print(df.head())


# Column Names

print("\nColumn Names:\n")
for col in df.columns:
    print(col)


# Data Types

print("\nData Types:\n")
print(df.dtypes)


# Missing Data Summary

print("\nMissing Values by Column:\n")
missing_summary = df.isna().sum().sort_values(ascending=False)
print(missing_summary)


# Identity Field Audit

identity_fields = [
    "Subject or Client Initials",
    "Subject or Client Birth Year",
    "person_id",
    "age_group",
    "Date at Incident",
    "Date at Incident.1",
    "record_id",
]

print("\nIdentity Field Audit:\n")
for col in identity_fields:
    if col in df.columns:
        print(f"{col}: present | missing = {df[col].isna().sum()}")
    else:
        print(f"{col}: NOT FOUND")


# Duplicate Date Column Check

if "Date at Incident" in df.columns and "Date at Incident.1" in df.columns:
    date_1 = pd.to_datetime(df["Date at Incident"], errors="coerce")
    date_2 = pd.to_datetime(df["Date at Incident.1"], errors="coerce")
    same_dates = date_1.equals(date_2)

    print("\nDuplicate Date Check:")
    print(f"Date at Incident matches Date at Incident.1: {same_dates}")
else:
    print("\nDuplicate Date Check:")
    print("One or both date columns not found.")


# Unique Values for Key Fields

key_fields = [
    "Call Type",
    "Status of Subject or Client at Time of Hand-off to Facility. Select one.",
    "Responding Agencies. Select all agencies involved in the incident response.",
    "Receiving Facility. Select one.",
    "Subject or Client's Housing Status at Time of Incident. Select one.",
    "Agency Affiliation of Professional Completing this Form. Select one.",
    "Subject or Client Initials",
    "Subject or Client Birth Year",
    "age_group",
]

print("\nUnique Value Preview for Key Fields:\n")
for col in key_fields:
    if col in df.columns:
        print(f"\nColumn: {col}")
        print(df[col].dropna().unique()[:10])


# Person ID Audit

if "person_id" in df.columns:
    print("\nPerson ID Audit:")
    print("Unique person_id count:", df["person_id"].nunique(dropna=True))
    print("Missing person_id count:", df["person_id"].isna().sum())
    print("Sample person_id values:")
    print(df["person_id"].dropna().unique()[:10])


# Birth Year Summary

if "Subject or Client Birth Year" in df.columns:
    birth_year = pd.to_numeric(df["Subject or Client Birth Year"], errors="coerce")

    print("\nBirth Year Summary:")
    print("Min birth year:", birth_year.min())
    print("Max birth year:", birth_year.max())
    print("Missing birth year:", birth_year.isna().sum())


# End of Audit

print("\nData audit complete.\n")