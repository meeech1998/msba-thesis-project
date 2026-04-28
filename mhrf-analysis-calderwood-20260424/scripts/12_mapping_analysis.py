"""
MHRF Crisis Encounter Analysis
Author: Michelle Calderwood
File: 12_mapping_analysis.py

Purpose:
Geocode incident addresses from the MHRF and create:
- all encounter heatmap
- severity heatmap
- repeat encounter heatmap

This version:
- geocodes unique addresses only
- caches results so reruns resume
- uses longer timeout/retries
- cleans raw address strings before lookup
"""

from pathlib import Path
import re
import time

import folium
import pandas as pd
from folium.plugins import HeatMap
from geopy.extra.rate_limiter import RateLimiter
from geopy.geocoders import Nominatim


# Paths

PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = PROJECT_ROOT / "data" / "processed" / "mhrf_with_clusters.csv"
OUTPUT_FOLDER = PROJECT_ROOT / "outputs"

CACHE_PATH = PROJECT_ROOT / "data" / "processed" / "geocode_cache.csv"
GEOCODED_OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "mhrf_geocoded.csv"


# Load Data

df = pd.read_csv(INPUT_PATH)

ADDRESS_COL = "incident_address_street_or_intersection_is_sufficient"

df = df[[ADDRESS_COL, "severe_flag", "repeat_contact_flag"]].copy()
df = df.dropna(subset=[ADDRESS_COL]).copy()
df[ADDRESS_COL] = df[ADDRESS_COL].astype(str).str.strip()

print("\nLoaded rows:", len(df))


# Clean Address Text


def clean_address(value: str) -> str:
    text = str(value).strip()

    # normalize whitespace
    text = re.sub(r"\s+", " ", text)

    # convert slash intersections to "and"
    text = text.replace("/", " and ")
    text = text.replace("&", " and ")

    # common cleanup
    text = text.replace(" PD Station", "")
    text = text.replace("Ryman PD Station", "Ryman St")
    text = text.replace("Front/Owen", "Front St and Owen St")
    text = text.replace("Front and Owen", "Front St and Owen St")

    # remove trailing punctuation
    text = re.sub(r"[,\.;:]+$", "", text)

    return text


df["address_clean"] = df[ADDRESS_COL].apply(clean_address)


# Load Existing Cache

if CACHE_PATH.exists():
    cache_df = pd.read_csv(CACHE_PATH)
    print("Loaded existing cache:", len(cache_df))
else:
    cache_df = pd.DataFrame(columns=["address_clean", "lat", "lon"])
    print("No existing cache found. Starting fresh.")


cached_addresses = set(cache_df["address_clean"].astype(str).tolist())

unique_addresses = sorted(set(df["address_clean"].tolist()))
to_geocode = [a for a in unique_addresses if a not in cached_addresses]

print("Unique cleaned addresses:", len(unique_addresses))
print("Still need geocoding:", len(to_geocode))


# Geocoder Setup

geolocator = Nominatim(user_agent="missoula_cit_mapping", timeout=10)
geocode = RateLimiter(
    geolocator.geocode,
    min_delay_seconds=1.2,
    max_retries=3,
    error_wait_seconds=3.0,
    swallow_exceptions=True
)


def geocode_address(address: str):
    query = f"{address}, Missoula, Montana"
    location = geocode(query)
    if location:
        return location.latitude, location.longitude
    return None, None


# Geocode Missing Addresses Only

new_rows = []

for i, address in enumerate(to_geocode, start=1):
    lat, lon = geocode_address(address)
    new_rows.append({
        "address_clean": address,
        "lat": lat,
        "lon": lon
    })

    if i % 25 == 0:
        print(f"Geocoded {i} / {len(to_geocode)} new unique addresses...")

# append + save cache
if new_rows:
    new_cache = pd.DataFrame(new_rows)
    cache_df = pd.concat([cache_df, new_cache], ignore_index=True)
    cache_df = cache_df.drop_duplicates(subset=["address_clean"], keep="last")
    cache_df.to_csv(CACHE_PATH, index=False)
    print("Updated cache saved:", CACHE_PATH)
else:
    print("No new addresses needed geocoding.")


# Merge Coordinates Back

df = df.merge(cache_df, on="address_clean", how="left")
df.to_csv(GEOCODED_OUTPUT_PATH, index=False)

print("Merged geocoded file saved:", GEOCODED_OUTPUT_PATH)

mapped_df = df.dropna(subset=["lat", "lon"]).copy()
print("Rows with usable coordinates:", len(mapped_df))


# Base Map Centered on Missoula

MISSOULA_CENTER = [46.8721, -113.9940]


# Map 1: All Encounters

all_map = folium.Map(location=MISSOULA_CENTER, zoom_start=13)
HeatMap(mapped_df[["lat", "lon"]].values.tolist(), radius=10, blur=14).add_to(all_map)
all_map.save(OUTPUT_FOLDER / "map_heat_all.html")


# Map 2: Severe Encounters

severity_df = mapped_df[mapped_df["severe_flag"] == 1].copy()

severity_map = folium.Map(location=MISSOULA_CENTER, zoom_start=13)
HeatMap(severity_df[["lat", "lon"]].values.tolist(), radius=10, blur=14).add_to(severity_map)
severity_map.save(OUTPUT_FOLDER / "map_heat_severity.html")


# Map 3: Repeat Encounters

repeat_df = mapped_df[mapped_df["repeat_contact_flag"] == 1].copy()

repeat_map = folium.Map(location=MISSOULA_CENTER, zoom_start=13)
HeatMap(repeat_df[["lat", "lon"]].values.tolist(), radius=10, blur=14).add_to(repeat_map)
repeat_map.save(OUTPUT_FOLDER / "map_heat_repeat.html")


print("\nMapping complete.")
print("Outputs:")
print("- map_heat_all.html")
print("- map_heat_severity.html")
print("- map_heat_repeat.html")
print("- geocode_cache.csv")
print("- mhrf_geocoded.csv")