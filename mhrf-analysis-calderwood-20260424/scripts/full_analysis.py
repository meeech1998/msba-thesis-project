"""
full_analysis.py
Complete analysis pipeline: descriptive stats, agency analysis, severity model,
repeat model, encounter typology, time series. Generates all figures.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import PercentFormatter

from a00_utils import (train_test_split, logistic_regression_coefficients,
                       logistic_regression_fit, logistic_regression_predict_proba,
                       auc_score, roc_curve, chi_square_test, kmodes_fit)

# ── Config ────────────────────────────────────────────────────────────
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'outputs', 'figures', 'cb_safe')
TABLE_DIR = os.path.join(os.path.dirname(__file__), '..', 'outputs', 'tables')
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TABLE_DIR, exist_ok=True)

plt.rcParams.update({
    'figure.figsize': (10, 6),
    'font.size': 11,
    'axes.titlesize': 13,
    'axes.labelsize': 11,
    'figure.dpi': 150,
    'savefig.dpi': 150,
})
COLORS = {'LE': '#F28E2B', 'BH': '#4E79A7', 'Co': '#59A89E', 'neutral': '#7f8c8d'}

# ── Load Data ─────────────────────────────────────────────────────────
from a01_data_preparation import load_and_prepare
df = load_and_prepare()

# =====================================================================
# SECTION 1: DESCRIPTIVE ANALYSIS
# =====================================================================
print("\n" + "="*60)
print("SECTION 1: DESCRIPTIVE ANALYSIS")
print("="*60)

# Fig 1: Encounter volume by month
fig, ax = plt.subplots(figsize=(12, 5))
monthly = df.groupby('incident_yearmonth').size()
monthly.index = monthly.index.astype(str)
ax.bar(range(len(monthly)), monthly.values, color='#34495e', alpha=0.8)
ax.set_xticks(range(len(monthly)))
ax.set_xticklabels(monthly.index, rotation=45, ha='right', fontsize=9)
ax.set_ylabel('Number of Encounters')
ax.set_title('Monthly Crisis Encounter Volume (March 2024 – February 2026)')
ax.axvline(x=2.5, color='red', linestyle='--', alpha=0.5, label='Implementation ramp-up')
ax.legend()
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'fig01_monthly_volume.png'))
plt.close()

# Fig 2: Response Model Distribution
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
rt_counts = df['response_type'].value_counts()
colors_rt = {'Law Enforcement Only (MPD)': COLORS['LE'],
             'Behavioral Health Only (MST)': COLORS['BH'],
             'Co-Response (MPD+MST)': COLORS['Co'],
             'Law Enforcement Only (MCSO)': '#F28E2B',
             'Co-Response (MCSO+MST)': '#59A89E',
             'Other': COLORS['neutral'], 'Unknown': '#bdc3c7'}
bar_colors = [colors_rt.get(x, COLORS['neutral']) for x in rt_counts.index]
axes[0].barh(range(len(rt_counts)), rt_counts.values, color=bar_colors)
axes[0].set_yticks(range(len(rt_counts)))
axes[0].set_yticklabels(rt_counts.index, fontsize=10)
axes[0].set_xlabel('Number of Encounters')
axes[0].set_title('A. Encounters by Response Type')
axes[0].invert_yaxis()
for i, v in enumerate(rt_counts.values):
    axes[0].text(v + 3, i, str(v), va='center', fontsize=9)

# Severity by response model
rm_sev = df.groupby('response_model')['severe_flag'].agg(['mean','count'])
rm_sev = rm_sev.sort_values('mean', ascending=True)
bar_c = [COLORS.get({'Law Enforcement Only':'LE','Behavioral Health Only':'BH',
                      'Co-Response':'Co','Other':'neutral'}.get(x,'neutral'),'#95a5a6')
         for x in rm_sev.index]
axes[1].barh(range(len(rm_sev)), rm_sev['mean'].values * 100, color=bar_c)
axes[1].set_yticks(range(len(rm_sev)))
axes[1].set_yticklabels(rm_sev.index, fontsize=10)
axes[1].set_xlabel('Severity Rate (%)')
axes[1].set_title('B. Severity Rate by Response Model')
for i, (rate, n) in enumerate(zip(rm_sev['mean'], rm_sev['count'])):
    axes[1].text(rate * 100 + 1, i, f'{rate:.1%} (n={n})', va='center', fontsize=9)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'fig02_response_model.png'))
plt.close()

# Fig 3: Behavioral Indicator Prevalence
beh_cols = ['beh_depressed','beh_angry','beh_confusion','beh_disorganized_speech',
            'beh_delusions','beh_hallucinations','beh_scared','beh_manic']
beh_labels = ['Depression','Anger/Uncooperative','Confusion','Disorganized Speech',
              'Delusions','Hallucinations','Scared/Frightened','Manic']
beh_rates = [df[c].mean() for c in beh_cols]
fig, ax = plt.subplots(figsize=(10, 5))
sorted_idx = np.argsort(beh_rates)[::-1]
bars = ax.bar(range(len(beh_cols)), [beh_rates[i] for i in sorted_idx],
              color='#4E79A7', alpha=0.8)
ax.set_xticks(range(len(beh_cols)))
ax.set_xticklabels([beh_labels[i] for i in sorted_idx], rotation=30, ha='right')
ax.set_ylabel('Prevalence (proportion of encounters)')
ax.set_title('Behavioral Indicator Prevalence Across All Encounters')
ax.yaxis.set_major_formatter(PercentFormatter(1.0))
for i, idx in enumerate(sorted_idx):
    ax.text(i, beh_rates[idx] + 0.005, f'{beh_rates[idx]:.1%}', ha='center', fontsize=9)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'fig03_behavioral_prevalence.png'))
plt.close()

# Fig 4: Housing Status
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
housing_counts = df['housing_status_clean'].value_counts()
axes[0].bar(range(len(housing_counts)), housing_counts.values, color='#2c3e50', alpha=0.8)
axes[0].set_xticks(range(len(housing_counts)))
axes[0].set_xticklabels(housing_counts.index)
axes[0].set_ylabel('Number of Encounters')
axes[0].set_title('A. Encounters by Housing Status')

housing_sev = df.groupby('housing_status_clean').agg(
    severity=('severe_flag','mean'),
    repeat=('repeat_contact_flag', lambda x: x.dropna().mean())
).round(3)
x = np.arange(len(housing_sev))
w = 0.35
axes[1].bar(x - w/2, housing_sev['severity'] * 100, w, label='Severity Rate', color=COLORS['LE'], alpha=0.8)
axes[1].bar(x + w/2, housing_sev['repeat'] * 100, w, label='Repeat Rate', color=COLORS['BH'], alpha=0.8)
axes[1].set_xticks(x)
axes[1].set_xticklabels(housing_sev.index)
axes[1].set_ylabel('Rate (%)')
axes[1].set_title('B. Severity & Repeat Rates by Housing Status')
axes[1].legend()
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'fig04_housing.png'))
plt.close()

# Fig 5: Call Type Distribution with severity rates
fig, ax = plt.subplots(figsize=(12, 6))
ct_stats = df.groupby('call_type_group').agg(
    count=('severe_flag','count'),
    severity=('severe_flag','mean')
).sort_values('count', ascending=True)
y_pos = range(len(ct_stats))
bars = ax.barh(y_pos, ct_stats['count'], color='#34495e', alpha=0.7)
ax.set_yticks(y_pos)
ax.set_yticklabels(ct_stats.index, fontsize=9)
ax.set_xlabel('Number of Encounters')
ax.set_title('Call Type Distribution (with severity rates)')
for i, (cnt, sev) in enumerate(zip(ct_stats['count'], ct_stats['severity'])):
    ax.text(cnt + 3, i, f'n={cnt}, sev={sev:.0%}', va='center', fontsize=8)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'fig05_call_types.png'))
plt.close()

print("Descriptive figures saved.")

# =====================================================================
# SECTION 2: RESPONDING AGENCY ANALYSIS
# =====================================================================
print("\n" + "="*60)
print("SECTION 2: RESPONDING AGENCY ANALYSIS")
print("="*60)

# Fig 6: Severity components by response model
fig, axes = plt.subplots(1, 4, figsize=(16, 5), sharey=True)
components = [('involuntary_flag', 'Involuntary Determination'),
              ('force_flag', 'Force Used'),
              ('subject_injury_flag', 'Subject Injured'),
              ('others_injury_flag', 'Others Injured')]

for ax, (col, title) in zip(axes, components):
    rates = df.groupby('response_model')[col].mean().reindex(
        ['Law Enforcement Only','Co-Response','Behavioral Health Only','Other'])
    colors_bar = [COLORS['LE'], COLORS['Co'], COLORS['BH'], COLORS['neutral']]
    ax.bar(range(len(rates)), rates.values * 100, color=colors_bar[:len(rates)])
    ax.set_xticks(range(len(rates)))
    ax.set_xticklabels(['LE Only','Co-Resp','BH Only','Other'], rotation=30, ha='right', fontsize=8)
    ax.set_title(title, fontsize=10)
    ax.set_ylabel('Rate (%)' if ax == axes[0] else '')
    for i, v in enumerate(rates.values):
        ax.text(i, v * 100 + 1, f'{v:.1%}', ha='center', fontsize=8)

plt.suptitle('Severity Components by Response Model', fontsize=13, y=1.02)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'fig06_agency_severity_components.png'))
plt.close()

# Fig 7: Within-call-type comparison
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
for ax, ct_name in zip(axes, ['Suicidal / Self-Harm', 'Person Needs Assistance']):
    sub = df[df['call_type_group'] == ct_name]
    rm_rates = sub.groupby('response_model')['severe_flag'].agg(['mean','count'])
    rm_rates = rm_rates[rm_rates['count'] >= 5].sort_values('mean', ascending=True)
    colors_bar = [{'Law Enforcement Only':COLORS['LE'], 'Co-Response':COLORS['Co'],
                   'Behavioral Health Only':COLORS['BH']}.get(x, COLORS['neutral'])
                  for x in rm_rates.index]
    ax.barh(range(len(rm_rates)), rm_rates['mean'] * 100, color=colors_bar)
    ax.set_yticks(range(len(rm_rates)))
    ax.set_yticklabels(rm_rates.index, fontsize=9)
    ax.set_xlabel('Severity Rate (%)')
    ax.set_title(f'{ct_name} Calls')
    for i, (rate, n) in enumerate(zip(rm_rates['mean'], rm_rates['count'])):
        ax.text(rate * 100 + 1, i, f'{rate:.1%} (n={n})', va='center', fontsize=9)

plt.suptitle('Severity Rate by Response Model Within Same Call Types', fontsize=13)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'fig07_agency_within_calltype.png'))
plt.close()

# Statistical test: agency vs severity
from collections import Counter
ct_table = pd.crosstab(df['response_model'], df['severe_flag'])
chi2, p_val, dof = chi_square_test(ct_table.values)
print(f"\nChi-square test (response model x severity): χ²={chi2:.1f}, df={dof}, p<0.001")

# Print key stats
print("\nSeverity by Response Model:")
for rm in ['Law Enforcement Only', 'Co-Response', 'Behavioral Health Only']:
    sub = df[df['response_model'] == rm]
    print(f"  {rm:30s}  n={len(sub):3d}  severity={sub['severe_flag'].mean():.3f}"
          f"  force={sub['force_flag'].mean():.3f}"
          f"  involuntary={sub['involuntary_handoff'].mean():.3f}")

print("\nAgency analysis figures saved.")

# =====================================================================
# SECTION 3: SEVERITY MODEL
# =====================================================================
print("\n" + "="*60)
print("SECTION 3: SEVERITY MODEL")
print("="*60)

# Feature matrix for severity model
feature_cols = ['has_mst', 'has_mpd', 'beh_angry', 'beh_manic', 'beh_confusion',
                'beh_depressed', 'beh_disorganized_speech', 'beh_hallucinations',
                'beh_scared', 'substance_involved', 'is_unhoused', 'is_housed',
                'probable_cause']
feature_names = ['MST Responded', 'MPD Responded', 'Anger/Uncooperative', 'Manic',
                 'Confusion', 'Depression', 'Disorganized Speech', 'Hallucinations',
                 'Scared/Frightened', 'Substance Involved', 'Unhoused', 'Housed',
                 'Probable Cause']

# Drop rows with missing target
sev_df = df.dropna(subset=['severe_flag'] + feature_cols).copy()
X_sev = sev_df[feature_cols].values.astype(float)
y_sev = sev_df['severe_flag'].values.astype(float)

print(f"Severity model: n={len(y_sev)}, positive rate={y_sev.mean():.3f}")

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X_sev, y_sev, test_size=0.3)

# Fit on training data
results_sev, w_sev = logistic_regression_coefficients(
    X_train, y_train, feature_names, lr=0.005, max_iter=20000, l2=0.001)

# Predict on test set
y_pred_test = logistic_regression_predict_proba(X_test, w_sev)
y_pred_train = logistic_regression_predict_proba(X_train, w_sev)

auc_train = auc_score(y_train, y_pred_train)
auc_test = auc_score(y_test, y_pred_test)
print(f"Severity Model — Train AUC: {auc_train:.3f}, Test AUC: {auc_test:.3f}")
print(f"\nCoefficients:")
print(results_sev[['feature','coefficient','p_value','significant']].to_string(index=False))

# Fig 8: Severity model coefficients
fig, ax = plt.subplots(figsize=(10, 7))
res = results_sev.sort_values('coefficient')
colors_coef = ['#F28E2B' if c > 0 and s else '#4E79A7' if c < 0 and s else '#bdc3c7'
               for c, s in zip(res['coefficient'], res['significant'])]
ax.barh(range(len(res)), res['coefficient'], color=colors_coef)
ax.set_yticks(range(len(res)))
ax.set_yticklabels(res['feature'], fontsize=10)
ax.axvline(x=0, color='black', linewidth=0.5)
ax.set_xlabel('Coefficient (log-odds)')
ax.set_title(f'Severity Model: Logistic Regression Coefficients\nTest AUC = {auc_test:.3f}')
# Add significance markers
for i, (_, row) in enumerate(res.iterrows()):
    marker = '***' if row['p_value'] < 0.001 else '**' if row['p_value'] < 0.01 else '*' if row['p_value'] < 0.05 else ''
    if marker:
        x_pos = row['coefficient'] + (0.05 if row['coefficient'] >= 0 else -0.15)
        ax.text(x_pos, i, marker, va='center', fontsize=10, color='#2c3e50')
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'fig08_severity_coefficients.png'))
plt.close()

# Fig 9: ROC curve for severity
fig, ax = plt.subplots(figsize=(7, 7))
fpr, tpr, _ = roc_curve(y_test, y_pred_test)
ax.plot(fpr, tpr, color=COLORS['LE'], linewidth=2, label=f'Test AUC = {auc_test:.3f}')
fpr_tr, tpr_tr, _ = roc_curve(y_train, y_pred_train)
ax.plot(fpr_tr, tpr_tr, color=COLORS['BH'], linewidth=1.5, alpha=0.5, label=f'Train AUC = {auc_train:.3f}')
ax.plot([0,1],[0,1], 'k--', alpha=0.3, label='Random (AUC = 0.5)')
ax.set_xlabel('False Positive Rate')
ax.set_ylabel('True Positive Rate')
ax.set_title('ROC Curve: Severity Model')
ax.legend(loc='lower right')
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'fig09_severity_roc.png'))
plt.close()

print("Severity model figures saved.")

# =====================================================================
# SECTION 4: REPEAT ENCOUNTER MODEL
# =====================================================================
print("\n" + "="*60)
print("SECTION 4: REPEAT ENCOUNTER MODEL")
print("="*60)

rep_feature_cols = ['is_unhoused', 'is_housed', 'has_mst', 'has_mpd',
                    'substance_involved', 'beh_angry', 'beh_confusion',
                    'beh_depressed', 'beh_manic', 'severe_flag']
rep_feature_names = ['Unhoused', 'Housed', 'MST Responded', 'MPD Responded',
                     'Substance Involved', 'Anger/Uncooperative', 'Confusion',
                     'Depression', 'Manic', 'Severe Encounter']

rep_df = df.dropna(subset=['repeat_contact_flag'] + rep_feature_cols).copy()
X_rep = rep_df[rep_feature_cols].values.astype(float)
y_rep = rep_df['repeat_contact_flag'].values.astype(float)

print(f"Repeat model: n={len(y_rep)}, positive rate={y_rep.mean():.3f}")

X_train_r, X_test_r, y_train_r, y_test_r = train_test_split(X_rep, y_rep, test_size=0.3)

results_rep, w_rep = logistic_regression_coefficients(
    X_train_r, y_train_r, rep_feature_names, lr=0.005, max_iter=20000, l2=0.001)

y_pred_test_r = logistic_regression_predict_proba(X_test_r, w_rep)
y_pred_train_r = logistic_regression_predict_proba(X_train_r, w_rep)

auc_train_r = auc_score(y_train_r, y_pred_train_r)
auc_test_r = auc_score(y_test_r, y_pred_test_r)
print(f"Repeat Model — Train AUC: {auc_train_r:.3f}, Test AUC: {auc_test_r:.3f}")
print(f"\nCoefficients:")
print(results_rep[['feature','coefficient','p_value','significant']].to_string(index=False))

# Fig 10: Repeat model coefficients
fig, ax = plt.subplots(figsize=(10, 6))
res_r = results_rep.sort_values('coefficient')
colors_coef_r = ['#F28E2B' if c > 0 and s else '#4E79A7' if c < 0 and s else '#bdc3c7'
                 for c, s in zip(res_r['coefficient'], res_r['significant'])]
ax.barh(range(len(res_r)), res_r['coefficient'], color=colors_coef_r)
ax.set_yticks(range(len(res_r)))
ax.set_yticklabels(res_r['feature'], fontsize=10)
ax.axvline(x=0, color='black', linewidth=0.5)
ax.set_xlabel('Coefficient (log-odds)')
ax.set_title(f'Repeat Encounter Model: Logistic Regression Coefficients\nTest AUC = {auc_test_r:.3f}')
for i, (_, row) in enumerate(res_r.iterrows()):
    marker = '***' if row['p_value'] < 0.001 else '**' if row['p_value'] < 0.01 else '*' if row['p_value'] < 0.05 else ''
    if marker:
        x_pos = row['coefficient'] + (0.03 if row['coefficient'] >= 0 else -0.1)
        ax.text(x_pos, i, marker, va='center', fontsize=10, color='#2c3e50')
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'fig10_repeat_coefficients.png'))
plt.close()

print("Repeat model figures saved.")

# =====================================================================
# SECTION 5: ENCOUNTER TYPOLOGY (K-MODES)
# =====================================================================
print("\n" + "="*60)
print("SECTION 5: ENCOUNTER TYPOLOGY")
print("="*60)

cluster_cols = ['beh_angry', 'beh_manic', 'beh_confusion', 'beh_depressed',
                'beh_hallucinations', 'beh_scared', 'substance_involved',
                'is_unhoused', 'repeat_contact_flag', 'involuntary_handoff']
cluster_labels_short = ['Anger', 'Manic', 'Confusion', 'Depression',
                        'Hallucinations', 'Scared', 'Substance', 'Unhoused',
                        'Repeat', 'Involuntary']

clust_df = df.dropna(subset=cluster_cols).copy()
X_clust = clust_df[cluster_cols].values.astype(int)

# Run k-modes with k=3 (low/medium/high risk)
labels, centroids, cost = kmodes_fit(X_clust, k=3, max_iter=100, n_init=20, random_state=42)
clust_df['cluster'] = labels

# Calculate severity and repeat rates per cluster
print("\nCluster profiles:")
for c in range(3):
    mask = clust_df['cluster'] == c
    n = mask.sum()
    sev = clust_df.loc[mask, 'severe_flag'].mean()
    rep = clust_df.loc[mask, 'repeat_contact_flag'].mean()
    print(f"\n  Cluster {c}: n={n}, severity={sev:.3f}, repeat={rep:.3f}")
    for col, label in zip(cluster_cols, cluster_labels_short):
        print(f"    {label:20s}: {clust_df.loc[mask, col].mean():.3f}")

# Name clusters by severity rate
cluster_sev = clust_df.groupby('cluster')['severe_flag'].mean()
rank = cluster_sev.rank().astype(int)
risk_names = {1: 'Low Risk', 2: 'Moderate Risk', 3: 'High Risk'}
clust_df['risk_level'] = clust_df['cluster'].map(lambda x: risk_names[rank[x]])

# Fig 11: Cluster profiles heatmap
fig, ax = plt.subplots(figsize=(12, 5))
profile_data = []
for c in range(3):
    mask = clust_df['cluster'] == c
    name = risk_names[rank[c]]
    n = mask.sum()
    sev = clust_df.loc[mask, 'severe_flag'].mean()
    row_label = f'{name}\n(n={n}, sev={sev:.0%})'
    profile_data.append([clust_df.loc[mask, col].mean() for col in cluster_cols])

profile_df = pd.DataFrame(profile_data, columns=cluster_labels_short,
                          index=[f'{risk_names[rank[c]]}\n(n={sum(clust_df["cluster"]==c)}, sev={clust_df[clust_df["cluster"]==c]["severe_flag"].mean():.0%})'
                                 for c in range(3)])
# Sort by severity
order = cluster_sev.sort_values().index
profile_df = profile_df.iloc[[list(order).index(c) for c in range(3)]]

sns.heatmap(profile_df, annot=True, fmt='.2f', cmap='YlOrRd', vmin=0, vmax=1,
            linewidths=1, ax=ax, cbar_kws={'label': 'Proportion'})
ax.set_title('Encounter Typology: Cluster Profiles with Outcome Rates')
ax.set_xlabel('Indicator')
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'fig11_cluster_profiles.png'))
plt.close()

# Fig 12: Cluster outcome rates
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
cluster_outcomes = clust_df.groupby('risk_level').agg(
    severity=('severe_flag','mean'),
    repeat=('repeat_contact_flag','mean'),
    count=('severe_flag','count')
).reindex(['Low Risk','Moderate Risk','High Risk'])

risk_colors = ['#59A89E', '#F28E2B', '#F28E2B']
axes[0].bar(range(3), cluster_outcomes['severity'] * 100, color=risk_colors)
axes[0].set_xticks(range(3))
axes[0].set_xticklabels(cluster_outcomes.index)
axes[0].set_ylabel('Severity Rate (%)')
axes[0].set_title('A. Severity Rate by Encounter Type')
for i, v in enumerate(cluster_outcomes['severity']):
    axes[0].text(i, v*100+1, f'{v:.1%}', ha='center')

axes[1].bar(range(3), cluster_outcomes['repeat'] * 100, color=risk_colors)
axes[1].set_xticks(range(3))
axes[1].set_xticklabels(cluster_outcomes.index)
axes[1].set_ylabel('Repeat Encounter Rate (%)')
axes[1].set_title('B. Repeat Rate by Encounter Type')
for i, v in enumerate(cluster_outcomes['repeat']):
    axes[1].text(i, v*100+1, f'{v:.1%}', ha='center')

plt.suptitle('Encounter Typology Outcome Rates', fontsize=13)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'fig12_cluster_outcomes.png'))
plt.close()

# Fig 13: Cluster x Response Model
fig, ax = plt.subplots(figsize=(10, 6))
cluster_agency = pd.crosstab(clust_df['risk_level'], clust_df['response_model'], normalize='index')
cluster_agency = cluster_agency.reindex(['Low Risk','Moderate Risk','High Risk'])
agency_cols_ordered = ['Behavioral Health Only','Co-Response','Law Enforcement Only','Other']
cluster_agency = cluster_agency.reindex(columns=[c for c in agency_cols_ordered if c in cluster_agency.columns])
cluster_agency.plot(kind='bar', stacked=True, ax=ax,
                    color=[COLORS['BH'], COLORS['Co'], COLORS['LE'], COLORS['neutral']])
ax.set_ylabel('Proportion of Encounters')
ax.set_title('Response Model Distribution by Encounter Type')
ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
ax.legend(title='Response Model', bbox_to_anchor=(1.02, 1))
ax.yaxis.set_major_formatter(PercentFormatter(1.0))
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'fig13_cluster_agency.png'))
plt.close()

print("Cluster analysis figures saved.")

# =====================================================================
# SECTION 6: TIME SERIES ANALYSIS
# =====================================================================
print("\n" + "="*60)
print("SECTION 6: TIME SERIES ANALYSIS")
print("="*60)

# Exclude first 2 months (implementation ramp-up)
df_time = df[df['date_at_incident'] >= '2024-05-01'].copy()
monthly_ts = df_time.groupby('incident_yearmonth').agg(
    volume=('severe_flag','count'),
    severity=('severe_flag','mean'),
    repeat=('repeat_contact_flag', lambda x: x.dropna().mean())
)
monthly_ts.index = monthly_ts.index.astype(str)

# Fig 14: Time series with smoothing
fig, axes = plt.subplots(3, 1, figsize=(14, 12), sharex=True)

# Volume
axes[0].bar(range(len(monthly_ts)), monthly_ts['volume'], color='#34495e', alpha=0.7)
axes[0].set_ylabel('Encounters')
axes[0].set_title('A. Monthly Encounter Volume (May 2024 onward)')

# Severity with 3-month moving average
axes[1].plot(range(len(monthly_ts)), monthly_ts['severity'] * 100, 'o-',
             color=COLORS['LE'], alpha=0.4, markersize=4, label='Monthly')
ma3 = monthly_ts['severity'].rolling(3, center=True).mean() * 100
axes[1].plot(range(len(monthly_ts)), ma3, '-', color=COLORS['LE'],
             linewidth=2.5, label='3-Month Moving Avg')
axes[1].set_ylabel('Severity Rate (%)')
axes[1].set_title('B. Severity Rate Over Time (with 3-month smoothing)')
axes[1].legend()
axes[1].set_ylim(0, 80)

# Repeat with 3-month moving average
axes[2].plot(range(len(monthly_ts)), monthly_ts['repeat'] * 100, 'o-',
             color=COLORS['BH'], alpha=0.4, markersize=4, label='Monthly')
ma3_r = monthly_ts['repeat'].rolling(3, center=True).mean() * 100
axes[2].plot(range(len(monthly_ts)), ma3_r, '-', color=COLORS['BH'],
             linewidth=2.5, label='3-Month Moving Avg')
axes[2].set_ylabel('Repeat Rate (%)')
axes[2].set_title('C. Repeat Encounter Rate Over Time (with 3-month smoothing)')
axes[2].legend()

axes[2].set_xticks(range(len(monthly_ts)))
axes[2].set_xticklabels(monthly_ts.index, rotation=45, ha='right', fontsize=8)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'fig14_time_series.png'))
plt.close()

print("Time series figures saved.")

# =====================================================================
# SECTION 7: FREQUENCY VS IMPACT
# =====================================================================
print("\n" + "="*60)
print("SECTION 7: FREQUENCY VS IMPACT")
print("="*60)

# Fig 15: Frequency vs severity coefficient
fig, ax = plt.subplots(figsize=(10, 7))
beh_features_idx = [i for i, f in enumerate(feature_names) if f in
                    ['Anger/Uncooperative','Manic','Confusion','Depression',
                     'Disorganized Speech','Hallucinations','Scared/Frightened']]
for idx in beh_features_idx:
    fname = feature_names[idx]
    col = feature_cols[idx]
    freq = df[col].mean()
    coef = results_sev[results_sev['feature'] == fname]['coefficient'].values[0]
    sig = results_sev[results_sev['feature'] == fname]['significant'].values[0]
    color = COLORS['LE'] if sig and coef > 0 else COLORS['BH'] if sig and coef < 0 else COLORS['neutral']
    ax.scatter(freq, coef, s=150, color=color, edgecolors='black', linewidth=0.5, zorder=3)
    ax.annotate(fname, (freq, coef), fontsize=9, ha='left',
                xytext=(8, 4), textcoords='offset points')

ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
ax.set_xlabel('Prevalence (proportion of encounters)')
ax.set_ylabel('Severity Model Coefficient')
ax.set_title('Behavioral Indicator: Frequency vs. Impact on Severity')
ax.xaxis.set_major_formatter(PercentFormatter(1.0))
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'fig15_frequency_vs_impact.png'))
plt.close()

# =====================================================================
# SAVE SUMMARY STATISTICS
# =====================================================================
print("\n" + "="*60)
print("SAVING SUMMARY STATISTICS")
print("="*60)

# Save all key tables
results_sev.to_csv(os.path.join(TABLE_DIR, 'table_severity_coefficients.csv'), index=False)
results_rep.to_csv(os.path.join(TABLE_DIR, 'table_repeat_coefficients.csv'), index=False)

# Agency comparison table
agency_table = df.groupby('response_model').agg(
    n=('severe_flag','count'),
    severity_rate=('severe_flag','mean'),
    involuntary_rate=('involuntary_handoff','mean'),
    force_rate=('force_flag','mean'),
    injury_rate=('subject_injury_flag','mean'),
    repeat_rate=('repeat_contact_flag', lambda x: x.dropna().mean())
).round(3)
agency_table.to_csv(os.path.join(TABLE_DIR, 'table_agency_comparison.csv'))

# Cluster profiles
cluster_prof = clust_df.groupby('risk_level').agg(
    n=('severe_flag','count'),
    severity=('severe_flag','mean'),
    repeat=('repeat_contact_flag','mean'),
    **{label: (col, 'mean') for col, label in zip(cluster_cols, cluster_labels_short)}
).round(3)
cluster_prof.to_csv(os.path.join(TABLE_DIR, 'table_cluster_profiles.csv'))

# Summary stats
summary = {
    'total_encounters': len(df),
    'unique_persons': df['person_id'].nunique(),
    'severity_rate': df['severe_flag'].mean(),
    'repeat_rate': df['repeat_contact_flag'].dropna().mean(),
    'severity_auc_test': auc_test,
    'repeat_auc_test': auc_test_r,
    'le_only_severity': df[df['response_model']=='Law Enforcement Only']['severe_flag'].mean(),
    'bh_only_severity': df[df['response_model']=='Behavioral Health Only']['severe_flag'].mean(),
    'co_response_severity': df[df['response_model']=='Co-Response']['severe_flag'].mean(),
}
pd.Series(summary).to_csv(os.path.join(TABLE_DIR, 'summary_statistics.csv'))

print("\nAll outputs saved to:", OUTPUT_DIR)
print(f"\nFigures generated: {len([f for f in os.listdir(OUTPUT_DIR) if f.endswith('.png')])}")
print(f"Tables generated: {len([f for f in os.listdir(OUTPUT_DIR) if f.endswith('.csv')])}")
print("\n✓ ANALYSIS COMPLETE")
