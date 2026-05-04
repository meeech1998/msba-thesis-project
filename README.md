# MSBA Thesis Project

**Michelle Calderwood | University of Montana | MSBA Capstone**

[![GitHub Pages](https://img.shields.io/badge/Portfolio-Live-green)](https://meeech1998.github.io/msba-thesis-project/)

---

## Overview

This repository contains the full capstone thesis project for the Master of Science in Business Analytics (MSBA) program at the University of Montana. The project is a partnership with the **Missoula Police Department (MPD)** focused on data-driven analysis of mental health crisis response. It encompasses two primary analyses, a digital portfolio, and weekly progress documentation.

The work aims to support the MPD's Crisis Intervention Team (CIT) and Mental Health Referral Form (MHRF) programs by providing actionable insights through statistical modeling, machine learning, and data visualization.

---

## Repository Structure

```
msba-thesis-project/
├── cit-ksa-analysis_calderwood_20260218/   # CIT Training Evaluation (KSA Analysis)
├── mhrf-analysis-calderwood-20260424/      # Mental Health Referral Form Analysis
├── portfolio/                              # GitHub Pages digital portfolio
│   ├── index.html
│   └── headshot.jpeg
├── .gitignore
└── three_ps_calderwood.txt                 # Weekly progress log (3 Ps)
```

---

## Project Components

### 1. CIT-KSA Analysis

Evaluation of the **Missoula CIT Academy #8** and its impact on Law Enforcement Knowledge, Skills, and Abilities (KSA). The analysis measures immediate and sustained effects of the 40-hour CIT training program across four time stages: Pre-training, Post-training, 3–6 months, and 12 months.

**Key findings:**
- All 8 KSA metrics improved from Pre to Post training
- 7 of 8 improvements were statistically significant (Welch's t-test, α = 0.05)
- All effect sizes were large (Cohen's d > 1.0)
- Composite KSA Index increased by ~1.00 point immediately post-training
- Gains were sustained at both 3–6 months and 12 months
- One-way ANOVA confirmed significant stage-level differences

**Methods:** Descriptive statistics, Welch's t-tests, Cohen's d, one-way ANOVA, composite KSA index, trajectory visualization

**Tech stack:** Python, pandas, numpy, scipy, matplotlib

**Pipeline:** 12 ordered scripts (01_load_and_profile.py through 12_small_multiples_ksa_trajectories.py)

---

### 2. MHRF Analysis

Comprehensive analysis of the Missoula Police Department's **Mental Health Referral Form (MHRF)** data. This analysis examines crisis call characteristics, triage patterns, severity predictors, repeat encounters, and behavioral health clustering to support officer training and program evaluation.

**Key deliverables:**
- 17 thesis figures (temporal dynamics, demographic distributions, behavioral indicators, response models, severity coefficients, ROC curves, Kaplan-Meier curves, cluster profiles, and more)
- 5 summary tables (summary statistics, severity/repeat encounter model coefficients, agency comparison, cluster profiles)
- Color-blind-safe (CB-safe) palette applied across all figures

**Methods:** Logistic regression, PCA, K-Modes clustering, Cox proportional hazards, Kaplan-Meier survival analysis, chi-square tests, ROC analysis

**Tech stack:** Python, pandas, numpy, scipy, matplotlib, scikit-learn, lifelines, folium

---

### 3. Digital Portfolio

A GitHub Pages-hosted digital portfolio showcasing the full thesis project.

Live at: **https://meeech1998.github.io/msba-thesis-project/**

---

### 4. Weekly Progress Log

A running weekly journal (January 2026 – May 2026) documenting project progress using the "3 Ps" framework: **Progress**, **Problems**, and **Plans** - located in three_ps_calderwood.txt.

---

## Client & Context

This project was conducted in partnership with the **Missoula Police Department (MPD)**, with subject matter expertise provided by the department's CIT coordinator and behavioral health liaisons. Data access was governed by CJIS compliance protocols. All data was de-identified prior to analysis.

**Primary stakeholders:** MPD CIT coordinators, hospital behavioral health units, upper management, co-response team (MST), CIT officers

---

## Getting Started

### Prerequisites

- Python 3.8+
- pip

### Setup

Clone the repository and create a virtual environment:

```bash
git clone https://github.com/meeech1998/msba-thesis-project.git
cd msba-thesis-project
python -m venv venv
source venv/bin/activate
pip install -r cit-ksa-analysis_calderwood_20260218/requirements.txt
```

### Run CIT-KSA Analysis

```bash
cd cit-ksa-analysis_calderwood_20260218
python scripts/01_load_and_profile.py
# ... continue through script 12
```

### Run MHRF Analysis

```bash
cd mhrf-analysis-calderwood-20260424
python3 scripts/regen_figures.py
python3 scripts/recolor_figures.py
python3 scripts/full_analysis.py
```

---

## Author

**Michelle Calderwood**
MSBA Capstone - University of Montana
michelle.calderwood@umontana.edu

---

*Data used in this project is subject to CJIS security policies and has been de-identified for research purposes.*
