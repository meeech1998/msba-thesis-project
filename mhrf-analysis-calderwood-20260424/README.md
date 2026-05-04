# MHRF Analysis

**Mental Health Referral Form (MHRF) Data Analysis**
**Missoula Police Department | MSBA Capstone | Michelle Calderwood**

---

## Overview

This analysis examines crisis call data collected through the Missoula Police Department's **Mental Health Referral Form (MHRF)** to surface patterns in crisis response, identify high-severity incident predictors, characterize repeat encounters, and cluster individuals by behavioral health profile. The findings are intended to support officer training, resource allocation, and program evaluation for MPD's co-response and Crisis Intervention Team (CIT) programs.

All data was provided under CJIS compliance protocols and fully de-identified prior to analysis.

---

## Repository Structure

```
mhrf-analysis-calderwood-20260424/
├── data/
│   ├── mhrf_analysis_ready.csv     ← cleaned input for all analysis scripts
│   └── mhrf_data_raw.xlsx          ← raw export (source file)
│
├── scripts/
│   ├── regen_figures.py            ← regenerates 12 of 17 thesis figures (CB-safe)
│   ├── recolor_figures.py          ← pixel-recolors 5 figures from originals
│   ├── full_analysis.py            ← generates all 5 thesis tables + CB-safe figures
│   ├── data_preparation.py         ← data cleaning & feature engineering helper
│   ├── a00_utils.py                ← ML utility functions (logistic, ROC, k-modes)
│   ├── a01_data_preparation.py     ← symlink to data_preparation.py (legacy name)
│   ├── complete_paper.py           ← generates thesis Word document
│   ├── 01_data_audit.py            ← [alt pipeline] data audit / pre-clean checks
│   ├── 02_data_cleaning.py         ← [alt pipeline] cleaned analytic CSV
│   ├── 03_data_quality_checks.py   ← [alt pipeline] QA tables
│   ├── 04_feature_engineering.py   ← [alt pipeline] engineered feature CSV
│   ├── 05_descriptive_analysis.py  ← [alt pipeline] descriptive figures + tables
│   ├── 06_severity_construction.py ← [alt pipeline] severity composite
│   ├── 07_severity_model.py        ← [alt pipeline] severity odds ratios
│   ├── 09_repeat_encounter_model.py← [alt pipeline] repeat encounter odds ratios
│   ├── 11_indicator_frequency_vs_impact.py ← frequency vs impact figure
│   ├── 11_time_patterns_analysis.py← trend figures
│   └── 12_mapping_analysis.py      ← folium choropleth maps
│
└── outputs/
    ├── figures/
    │   ├── original/               ← 17 thesis figures, original colors
    │   └── cb_safe/                ← 17 thesis figures, color-blind-safe palette
    └── tables/
        ├── summary_statistics.csv
        ├── table_severity_coefficients.csv
        ├── table_repeat_coefficients.csv
        ├── table_agency_comparison.csv
        └── table_cluster_profiles.csv
```

---

## Data

| File | Description |
|---|---|
| `mhrf_analysis_ready.csv` | Cleaned, analysis-ready dataset — primary input for all scripts |
| `mhrf_data_raw.xlsx` | Raw MHRF export from MPD |

The dataset captures mental health-related crisis calls responded to by MPD, MST (Mobile Support Team), and co-response units. Each record represents a single MHRF encounter and includes demographic, behavioral, housing, call type, triage, and disposition fields.

> **Note:** Raw data contains sensitive law enforcement information governed by CJIS security policy. Only de-identified data is stored in this repository.

---

## Methods & Analysis

### Descriptive Analysis
- Age distribution of individuals in crisis
- Behavioral health indicator prevalence (substance use, housing instability, prior contacts, etc.)
- Housing status breakdown
- Call type distribution
- Temporal dynamics (call volume by time of day, day of week, month)
- Spatial distribution of incidents across Missoula neighborhoods

### Response Model & Triage
- Agency response model: MPD-only, co-response (MPD + MST), MST-only
- Triage patterns within call type

### Severity Modeling
- Binary logistic regression predicting high-severity incidents
- Coefficient plot with odds ratios and confidence intervals
- ROC curve and AUC evaluation
- Model comparison across specifications

### Repeat Encounter Analysis
- Logistic regression predicting repeat MHRF encounters
- Kaplan-Meier survival curves for time to repeat contact
- Cox proportional hazards model with hazard ratios

### Behavioral Health Clustering
- Principal Component Analysis (PCA) for dimensionality reduction
- K-Modes clustering on categorical behavioral health indicators
- Four-cluster solution: **Minimal**, **Substance**, **Depressive**, and **Acute**
- Cluster outcome profiles and frequency vs. impact matrix

---

## Thesis Figures (17 Total)

| Figure | Title |
|---|---|
| figure_02 | Temporal Dynamics |
| figure_03 | Age Distribution |
| figure_04 | Behavioral Indicators |
| figure_05 | Housing Status |
| figure_06 | Call Type Distribution |
| figure_07 | Spatial Distribution |
| figure_08 | Response Model |
| figure_09 | Triage Within Call Type |
| figure_10 | Severity Coefficients |
| figure_11 | PCA Scree Plot |
| figure_12 | Model Comparison |
| figure_13 | ROC Curves |
| figure_14 | Kaplan-Meier Curves |
| figure_15 | Cox Hazard Ratios |
| figure_16 | Cluster Profiles |
| figure_17 | Cluster Outcomes |
| figure_18 | Frequency vs. Impact |

### Color-Blind-Safe Palette

| Hex | Color | Semantic Role |
|---|---|---|
| `#4E79A7` | Blue | Volume / repeat encounters / Minimal cluster |
| `#F28E2B` | Orange | Severity / warning / LE response / Substance cluster |
| `#59A89E` | Teal | MST / behavioral health / Depressive cluster |
| `#7F77DD` | Purple | Co-Response / Acute cluster / high severity |
| `#888780` | Gray | Neutral / baselines / unknown / gridlines |

---

## Thesis Tables (5 Total)

| File | Contents |
|---|---|
| `summary_statistics.csv` | Descriptive summary of all key variables |
| `table_severity_coefficients.csv` | Logistic regression odds ratios — severity model |
| `table_repeat_coefficients.csv` | Logistic regression odds ratios — repeat encounter model |
| `table_agency_comparison.csv` | Comparison of outcomes across response agency types |
| `table_cluster_profiles.csv` | Behavioral health cluster profiles (K-Modes) |

All tables are in `outputs/tables/`.

---

## Running the Analysis

### Prerequisites

- Python 3.8+
- pip

### Install Dependencies

```bash
pip install pandas numpy scipy matplotlib scikit-learn lifelines folium openpyxl
```

### Recommended: Virtual Environment

```bash
python -m venv venv
source venv/bin/activate    # Mac/Linux
# venv\Scripts\activate    # Windows
pip install pandas numpy scipy matplotlib scikit-learn lifelines folium openpyxl
```

### Reproduce All Outputs

Run from the `mhrf-analysis-calderwood-20260424/` directory:

```bash
python3 scripts/regen_figures.py    # 12 thesis figures into outputs/figures/cb_safe/
python3 scripts/recolor_figures.py  # 5 pixel-recolored figures into outputs/figures/cb_safe/
python3 scripts/full_analysis.py    # 5 thesis tables into outputs/tables/
```

---

## Script Reference

### Primary Thesis Scripts

| Script | Purpose |
|---|---|
| `regen_figures.py` | Regenerates 12 thesis figures from source with the CB-safe palette. Skips figures 07, 11, 12, 14, 15 (no source available). |
| `recolor_figures.py` | Pixel-recolors PNGs in `outputs/figures/original/` to the CB-safe palette. Used for the 5 figures with no source code. |
| `full_analysis.py` | Generates all 5 thesis tables and additional CB-safe figures. |
| `data_preparation.py` | Cleans the raw CSV into an analysis-ready DataFrame. Imported by `full_analysis.py`. |
| `a00_utils.py` | Pure-Python utilities: logistic regression, ROC, K-Modes, chi-square. Imported by `regen_figures.py` and `full_analysis.py`. |
| `complete_paper.py` | Assembles the thesis Word document. Not needed to regenerate figures or tables. |

### Alternative Numbered Pipeline (reference only)

These scripts implement an earlier analysis pipeline and are kept for reference. They expect intermediate CSVs not present in `data/` and are not part of the primary reproducible workflow.

| Script | Purpose |
|---|---|
| `01_data_audit.py` | Data audit and pre-clean checks |
| `02_data_cleaning.py` | Outputs cleaned analytic CSV |
| `03_data_quality_checks.py` | QA tables |
| `04_feature_engineering.py` | Engineered feature CSV |
| `05_descriptive_analysis.py` | Descriptive figures and frequency tables |
| `06_severity_construction.py` | Severity composite variable |
| `07_severity_model.py` | Severity model odds ratios |
| `09_repeat_encounter_model.py` | Repeat encounter odds ratios |
| `11_indicator_frequency_vs_impact.py` | Frequency vs. impact figure |
| `11_time_patterns_analysis.py` | Trend figures |
| `12_mapping_analysis.py` | Folium choropleth maps |

---

## Reproducibility Notes

- All outputs are generated programmatically from `mhrf_analysis_ready.csv`
- Original thesis figures are preserved in `outputs/figures/original/` — do not overwrite
- CB-safe versions in `outputs/figures/cb_safe/` can be regenerated at any time
- To swap originals with CB-safe versions: `cp outputs/figures/cb_safe/*.png outputs/figures/original/` (only do this once you are confident in the result)

---

## Limitations

- Dataset reflects MPD MHRF encounters only; undocumented contacts are excluded
- Behavioral health indicators are officer-reported and subject to observation bias
- Spatial analysis is limited by geocoding completeness
- Survival analysis assumes independence of repeat encounters
- Cluster labels are interpretive; K-Modes does not guarantee meaningful separation

---

## Author

**Michelle Calderwood**
MSBA Capstone — University of Montana
michelle.calderwood@umontana.edu

---

*Data used in this analysis is subject to CJIS security policies and has been de-identified for research purposes. Raw data files are not publicly distributed.*
