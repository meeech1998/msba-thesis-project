# Scripts → Output mapping

All scripts that generate figures or tables in this project. Run from the project
root: `python3 scripts/<script>.py`.

## Directory layout

```
mhrf-analysis-calderwood-20260424/
├── data/
│   ├── mhrf_analysis_ready.csv      ← input for all analysis scripts
│   └── mhrf_data_raw.xlsx           ← raw export
├── scripts/                          ← all generators (this folder)
└── outputs/
    ├── figures/
    │   ├── original/                ← figure_02_*.png … figure_18_*.png  (original colors)
    │   └── cb_safe/                 ← figure_02_*.png … figure_18_*.png  (Tableau CB-safe)
    └── tables/                      ← summary_statistics.csv + 4 thesis tables
```

## Color-blind-safe palette

Applied across every figure that gets regenerated. See [memory feedback](#) for full spec.

| Hex | Color | Semantic role |
|---|---|---|
| `#4E79A7` | Blue | volume / repeat / Minimal cluster |
| `#F28E2B` | Orange | severity / warning / LE / Substance cluster |
| `#59A89E` | Teal | MST / behavioral health / Depressive cluster |
| `#7F77DD` | Purple | Co-Response / Acute cluster / high severity |
| `#888780` | Gray | neutral / baselines / unknown / gridlines |

## Run order to reproduce all outputs

```bash
python3 scripts/regen_figures.py     # 12 of 17 thesis figures (CB-safe), into outputs/figures/cb_safe/
python3 scripts/recolor_figures.py   # pixel-recolors the remaining 5 from outputs/figures/original/
python3 scripts/full_analysis.py     # 5 thesis tables into outputs/tables/  (also produces alt figures)
```

## Script → artifact map

### Primary thesis output

| Script | Produces |
|---|---|
| `regen_figures.py` | 12 of the 17 thesis figures, with the CB-safe palette. Skips fig01/06/10/13/16 (not part of the thesis figure set). Output → `outputs/figures/cb_safe/` |
| `recolor_figures.py` | Pixel-recolors any PNG in `outputs/figures/original/` to the CB-safe palette. Output → `outputs/figures/cb_safe/`. Used for the 5 figures whose source code isn't here: 07 spatial, 11 PCA, 12 model comparison, 14 KM, 15 Cox. |
| `full_analysis.py` | The 5 tables in `outputs/tables/`: `summary_statistics.csv`, `table_severity_coefficients.csv`, `table_repeat_coefficients.csv`, `table_agency_comparison.csv`, `table_cluster_profiles.csv`. Also writes its own figures to `outputs/figures/cb_safe/`. |
| `data_preparation.py` | Helper imported by `full_analysis.py` (`load_and_prepare`). Cleans the raw CSV → analysis-ready DataFrame. |
| `a00_utils.py` | Pure-Python ML helpers (logistic regression, ROC, k-modes, chi-square) — imported by `regen_figures.py` and `full_analysis.py`. |
| `a01_data_preparation.py` | Symlink → `data_preparation.py` (legacy import name). |
| `complete_paper.py` | Generates the thesis Word doc. References every figure by `figXX_*.png` name. Not needed to regenerate figures/tables. |

### Figure-by-figure mapping (thesis figure → script + section)

| Thesis figure | Script | Internal name | Status |
|---|---|---|---|
| figure_02_temporal_dynamics       | `regen_figures.py` §FIG14 | fig14_time_series        | source-regenerated ✓ |
| figure_03_age_distribution        | `regen_figures.py` §FIG00 | fig00_age_distribution   | source-regenerated ✓ |
| figure_04_behavioral_indicators   | `regen_figures.py` §FIG03 | fig03_behavioral_prevalence | source-regenerated ✓ |
| figure_05_housing_status          | `regen_figures.py` §FIG04 | fig04_housing            | source-regenerated ✓ |
| figure_06_call_type_distribution  | `regen_figures.py` §FIG05 | fig05_call_types         | source-regenerated ✓ |
| figure_07_spatial_distribution    | (no source available)     | —                        | pixel-recolored only |
| figure_08_response_model          | `regen_figures.py` §FIG02 | fig02_response_model     | source-regenerated ✓ |
| figure_09_triage_within_call_type | `regen_figures.py` §FIG07 | fig07_agency_within_calltype | source-regenerated ✓ |
| figure_10_severity_coefficients   | `regen_figures.py` §FIG08 | fig08_severity_coefficients  | source-regenerated ✓ |
| figure_11_pca_scree               | (no source available)     | —                        | pixel-recolored only |
| figure_12_model_comparison        | (no source available)     | —                        | pixel-recolored only |
| figure_13_roc_curves              | `regen_figures.py` §FIG09 | fig09_severity_roc       | source-regenerated ✓ |
| figure_14_kaplan_meier            | (no source available)     | —                        | pixel-recolored only |
| figure_15_cox_hazard_ratios       | (no source available)     | —                        | pixel-recolored only |
| figure_16_cluster_profiles        | `regen_figures.py` §FIG11 | fig11_cluster_profiles   | source-regenerated ✓ |
| figure_17_cluster_outcomes        | `regen_figures.py` §FIG12 | fig12_cluster_outcomes   | source-regenerated ✓ |
| figure_18_frequency_vs_impact     | `regen_figures.py` §FIG15 | fig15_frequency_vs_impact | source-regenerated ✓ |

### Table → script

| Table | Script |
|---|---|
| `summary_statistics.csv`         | `full_analysis.py` |
| `table_severity_coefficients.csv` | `full_analysis.py` |
| `table_repeat_coefficients.csv`  | `full_analysis.py` |
| `table_agency_comparison.csv`    | `full_analysis.py` |
| `table_cluster_profiles.csv`     | `full_analysis.py` |

### Alternative numbered pipeline (01–12)

These scripts (`01_data_audit.py` … `12_mapping_analysis.py`) implement an
alternative analysis pipeline with its own output naming (`fig_*.png`, `table_*.csv`).
They were originally rooted at `~/Desktop/mhrf-analysis-clean/`. They are kept here
as reference; they expect processed CSVs that aren't in `data/`.

| Script | Produces |
|---|---|
| `01_data_audit.py`                    | data audit / pre-clean checks |
| `02_data_cleaning.py`                 | cleaned analytic CSV |
| `03_data_quality_checks.py`           | QA tables (`qa_*.csv`) |
| `04_feature_engineering.py`           | engineered feature CSV |
| `05_descriptive_analysis.py`          | descriptive figures + frequency tables |
| `06_severity_construction.py`         | severity composite |
| `07_severity_model.py`                | `table_severity_model_odds_ratios.csv` |
| `09_repeat_encounter_model.py`        | `table_repeat_model_odds_ratios.csv` |
| `11_indicator_frequency_vs_impact.py` | `fig_frequency_vs_impact.png` |
| `11_time_patterns_analysis.py`        | trend figures |
| `12_mapping_analysis.py`              | `map_*.html` folium maps |

## Why two figure folders?

- `outputs/figures/original/` — the 17 figures as they appeared in the original thesis. **Do not modify.**
- `outputs/figures/cb_safe/` — the same 17 figures with the CB-safe palette. 12 are regenerated from source code (highest fidelity, exact spec); 5 are pixel-recolored from the originals (no source available).

To replace the originals with CB-safe: `cp outputs/figures/cb_safe/*.png outputs/figures/original/` (only do this once you're confident).
