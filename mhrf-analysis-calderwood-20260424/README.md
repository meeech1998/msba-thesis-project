# MHRF Analysis — Capstone (Calderwood, 2026)

Quantitative analysis of 861 crisis encounters documented via the Missoula Police Department's Mental Health Referral Form (March 2024 – May 2025). Companion code and data for the written report in `report/`.

## Structure

```
.
├── report/
│   └── peer_cit_mhrf_analysis_calderwood_20260404.docx
├── data/
│   ├── mhrf_data_raw.xlsx           # raw MHRF export
│   └── mhrf_analysis_ready.csv      # cleaned, de-identified, feature-engineered
├── scripts/
│   ├── utils.py                     # shared helpers
│   ├── data_preparation.py          # raw → analysis-ready
│   ├── full_analysis.py             # descriptive analysis
│   ├── regen_figures.py             # figure regeneration
│   └── complete_paper.py            # main modeling and final figures
└── outputs/
    ├── figures/                     # figures 01–18 (1:1 with report)
    └── tables/                      # CSVs referenced by the report
```

## Pipeline

```
utils.py → data_preparation.py → full_analysis.py → regen_figures.py → complete_paper.py
```

## Figures (1:1 with report)

| # | File | Report caption |
|---|------|----------------|
| 01 | `figure_01_crisis_system_diagram.png` | Components of an Integrated Crisis Response System (Bruno, 2016) |
| 02 | `figure_02_temporal_dynamics.png` | Temporal dynamics: monthly volume, severity rate, repeat rate |
| 03 | `figure_03_age_distribution.png` | Encounter distribution by age group |
| 04 | `figure_04_behavioral_indicators.png` | Prevalence of behavioral indicators |
| 05 | `figure_05_housing_status.png` | Housing: volume + severity |
| 06 | `figure_06_call_type_distribution.png` | Call type distribution with severity rates |
| 07 | `figure_07_spatial_distribution.png` | Spatial distribution of encounters |
| 08 | `figure_08_response_model.png` | Response type counts + severity |
| 09 | `figure_09_triage_within_call_type.png` | Severity by response model within the same call type |
| 10 | `figure_10_severity_coefficients.png` | Logistic regression coefficients for severity model |
| 11 | `figure_11_pca_scree.png` | PCA scree plot |
| 12 | `figure_12_model_comparison.png` | Side-by-side model comparison |
| 13 | `figure_13_roc_curves.png` | ROC curves |
| 14 | `figure_14_kaplan_meier.png` | Kaplan–Meier survival curves |
| 15 | `figure_15_cox_hazard_ratios.png` | Cox proportional hazards |
| 16 | `figure_16_cluster_profiles.png` | Behavioral profile across typologies |
| 17 | `figure_17_cluster_outcomes.png` | Severity, repeat rate, and repeat volume by cluster |
| 18 | `figure_18_frequency_vs_impact.png` | Behavioral indicators by prevalence vs severity impact |

## Reproducing the analysis

```bash
python -m venv .venv
source .venv/bin/activate
pip install pandas numpy scipy scikit-learn statsmodels lifelines matplotlib seaborn python-docx openpyxl
python scripts/complete_paper.py
```
