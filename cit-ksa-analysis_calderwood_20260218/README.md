# CIT-KSA-Analysis

Evaluation of the Missoula Crisis Intervention Team (CIT) Academy #8 impact on Law Enforcement Knowledge, Skills, and Abilities (KSA).

This project analyzes pre-training, post-training, and long-term follow-up survey data to assess immediate and sustained effects of the 40-hour CIT Academy.

---

## Executive Summary

The Missoula CIT Academy demonstrates:

- Large immediate improvements in officer knowledge and preparedness
- Statistically significant gains across 7 of 8 KSA domains
- Very large practical effect sizes (Cohen’s d > 1.0)
- Sustained improvements at both 3–6 months and 12 months
- Significant stage-level differences confirmed by ANOVA

Overall, the training produces strong and durable improvements in officer-reported crisis response readiness.

Primary analytic focus: Missoula Law Enforcement (MLE).

---

## Project Objective

To determine whether the CIT Academy produces:

1. Immediate improvements in officer knowledge and preparedness  
2. Sustained improvements at 3–6 months and 12 months  
3. Statistically significant and practically meaningful effects  

---

## Style Guide & Development Standards

This project follows:

- PEP 8 Python Style Guide  
- Google Python Style Guide  
- GitHub Markdown best practices  
- Reproducible research directory conventions  

All scripts:

- Use ordered numeric prefixes reflecting pipeline sequence  
- Use snake_case naming conventions  
- Avoid hard-coded system-specific paths  
- Generate deterministic outputs  
- Separate raw data, processed data, scripts, and outputs  

---

## Project Structure

cit-ksa-analysis/
│
├── data/                     # Raw Excel input files
│   ├── pre_post.xlsx
│   ├── m3_6.xlsx
│   └── m12.xlsx
│
├── output/                   # Generated datasets & statistical outputs
│   ├── combined_clean.csv
│   ├── combined_numeric.csv
│   ├── mle_pre_post_descriptives.csv
│   ├── mle_pre_post_inference.csv
│   ├── mle_long_term_trends.csv
│   ├── mle_stage_anova.csv
│   ├── figure_1_pre_vs_post_table.csv
│   ├── figure_2_overall_ksa_index_table.csv
│   ├── figure_3_stage_means_by_metric.csv
│   └── figures/
│       ├── figure_1_pre_vs_post_grouped_bar.png
│       ├── figure_2_overall_ksa_index_trajectory.png
│       ├── figure_3_small_multiples_ksa_trajectories.png
│       └── *.png
│
├── scripts/                  # Ordered analysis pipeline
│   ├── 01_load_and_profile.py
│   ├── 02_combine_and_clean.py
│   ├── 03_role_counts.py
│   ├── 04_map_likert_to_numeric.py
│   ├── 05_mle_pre_post_descriptives.py
│   ├── 06_mle_pre_post_inference.py
│   ├── 07_mle_long_term_trends.py
│   ├── 08_mle_stage_anova.py
│   ├── 09_mle_visualizations.py
│   ├── 10_pre_post_grouped_bar.py
│   ├── 11_overall_ksa_index_trajectory.py
│   └── 12_small_multiples_ksa_trajectories.py
│
├── requirements.txt
└── README.md

---

## Data Overview

The analysis uses three structured KSA survey datasets:

- pre_post.xlsx – Pre and Immediate Post training responses  
- m3_6.xlsx – 3–6 month follow-up responses  
- m12.xlsx – 12-month follow-up responses  

Total responses: 92  
Primary analytic group: Missoula Law Enforcement (MLE)

Because surveys are deidentified, analyses compare independent groups across timepoints rather than tracking individuals longitudinally.

---

## Statistical Methods

The following techniques were used:

- Descriptive mean comparisons  
- Welch’s independent samples t-tests (Pre vs Post)  
- Cohen’s d effect size estimation  
- One-way ANOVA across four stages  
- Composite KSA index construction (mean of 8 metrics)  
- Trajectory visualization  

Significance threshold: alpha = 0.05

---

## Composite KSA Index

An Overall KSA Index was constructed by averaging the eight numeric KSA metrics for each respondent.

This provides a single interpretable measure of total perceived preparedness and knowledge, enabling evaluation of overall training effect and long-term sustainability.

---

## Key Findings

- All 8 KSA metrics improved from Pre to Post  
- 7 of 8 improvements statistically significant  
- All effect sizes large (Cohen’s d > 1.0)  
- Composite KSA index increased by ~1.00 point immediately post-training  
- Gains sustained at both 3–6 months and 12 months  
- ANOVA confirms significant stage-level differences  

The CIT Academy produces statistically significant, practically meaningful, and durable improvements.

---

## Environment Setup

This project uses a requirements file to ensure reproducibility.

### Step 1 – Create a Virtual Environment (Recommended)

Mac/Linux:
python -m venv venv  
source venv/bin/activate  

Windows:
python -m venv venv  
venv\Scripts\activate  

### Step 2 – Install Dependencies

pip install -r requirements.txt

Dependencies include:

- pandas  
- numpy  
- scipy  
- matplotlib  
- openpyxl  

---

## Running the Full Analysis Pipeline

From the project root:

python scripts/01_load_and_profile.py  
python scripts/02_combine_and_clean.py  
python scripts/03_role_counts.py  
python scripts/04_map_likert_to_numeric.py  
python scripts/05_mle_pre_post_descriptives.py  
python scripts/06_mle_pre_post_inference.py  
python scripts/07_mle_long_term_trends.py  
python scripts/08_mle_stage_anova.py  
python scripts/09_mle_visualizations.py  
python scripts/10_pre_post_grouped_bar.py  
python scripts/11_overall_ksa_index_trajectory.py  
python scripts/12_small_multiples_ksa_trajectories.py  

All outputs are saved in the /output directory.

---

## Reproducibility

- No manual data manipulation required
- All outputs generated programmatically
- Figures saved automatically
- Deterministic results given input datasets

---

## Limitations

- Independent cross-sectional samples at each stage  
- Small 12-month sample (n = 4)  
- Self-reported measures  
- Potential non-response bias  

Results reflect group-level trends rather than individual-level longitudinal change.

---

## Author

Michelle Calderwood  
MSBA Capstone Project  
University of Montana