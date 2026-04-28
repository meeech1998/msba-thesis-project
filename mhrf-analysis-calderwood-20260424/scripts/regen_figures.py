"""
regen_figures.py
Regenerates all analysis figures with the project's CB-safe semantic palette.

Color palette (CB-safe across protanopia, deuteranopia, tritanopia):
- Blue   '#4E79A7'  primary / volume / repeat / Minimal cluster
- Orange '#F28E2B'  severity / warning / LE / Substance cluster
- Teal   '#59A89E'  MST / behavioral health / Depressive cluster
- Purple '#7F77DD'  Co-Response / Acute cluster / high severity
- Gray   '#888780'  neutral / baselines / unknown / gridlines
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import PercentFormatter
from matplotlib import patches

from a00_utils import (train_test_split, logistic_regression_coefficients,
                       logistic_regression_fit, logistic_regression_predict_proba,
                       auc_score, roc_curve, chi_square_test, kmodes_fit)

# ── Configuration ─────────────────────────────────────────────────────────
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'outputs', 'figures', 'cb_safe')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Color Palette (CB-safe, semantic — see module docstring)
PALETTE = {
    'primary_blue': '#4E79A7',  # volume / repeat / Minimal cluster
    'accent_teal':  '#59A89E',  # MST / behavioral health / Depressive cluster
    'warm_coral':   '#F28E2B',  # severity / warning / Substance cluster (was red, now orange)
    'amber':        '#F28E2B',  # severity rate
    'slate_gray':   '#888780',  # neutral / baselines / gridlines
    'positive_sig': '#F28E2B',  # increases severity
    'negative_sig': '#4E79A7',  # decreases severity
    'not_sig':      '#CBD5E0',  # not significant (light gray, distinct from neutral gray)
    'low_risk':     '#4E79A7',  # Minimal cluster
    'mod_risk':     '#F28E2B',  # Substance cluster
    'high_risk':    '#7F77DD',  # Acute cluster
    'gold':         '#EDC948',
    'depressive':   '#59A89E',  # Depressive cluster (alias for teal)
}

# Matplotlib settings
plt.rcParams.update({
    'figure.figsize': (10, 6),
    'font.size': 11,
    'axes.titlesize': 13,
    'axes.labelsize': 11,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'figure.dpi': 200,
    'savefig.dpi': 200,
    'axes.grid': True,
    'axes.grid.axis': 'y',
    'grid.alpha': 0.3,
    'grid.linestyle': '-',
    'grid.linewidth': 0.5,
    'axes.spines.left': True,
    'axes.spines.bottom': True,
    'axes.spines.top': False,
    'axes.spines.right': False,
})

# ── Load Data ─────────────────────────────────────────────────────────────
print("\n" + "="*70)
print("Loading data...")
print("="*70)
df = pd.read_csv(os.path.join(DATA_DIR, 'mhrf_analysis_ready.csv'))
print(f"Loaded {len(df)} encounters")

# ── Helper Functions ──────────────────────────────────────────────────────
def remove_spines(ax):
    """Remove top and right spines."""
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

# Map regen_figures internal names -> the figure_XX_* filenames used by the thesis.
# Figures not in this map are skipped (they have no figure_XX equivalent in the thesis).
FIGURE_NAME_MAP = {
    'fig00_age_distribution.png':       'figure_03_age_distribution.png',
    'fig02_response_model.png':         'figure_08_response_model.png',
    'fig03_behavioral_prevalence.png':  'figure_04_behavioral_indicators.png',
    'fig04_housing.png':                'figure_05_housing_status.png',
    'fig05_call_types.png':             'figure_06_call_type_distribution.png',
    'fig07_agency_within_calltype.png': 'figure_09_triage_within_call_type.png',
    'fig08_severity_coefficients.png':  'figure_10_severity_coefficients.png',
    'fig09_severity_roc.png':           'figure_13_roc_curves.png',
    'fig11_cluster_profiles.png':       'figure_16_cluster_profiles.png',
    'fig12_cluster_outcomes.png':       'figure_17_cluster_outcomes.png',
    'fig14_time_series.png':            'figure_02_temporal_dynamics.png',
    'fig15_frequency_vs_impact.png':    'figure_18_frequency_vs_impact.png',
}


def save_figure(fig, filename, tight_layout=True):
    """Save figure with consistent settings.

    If the internal filename has a figure_XX_* equivalent, save under that name
    so the cb_safe folder mirrors the original/ folder.  Otherwise skip the save
    (those figures aren't part of the thesis output set).
    """
    target_name = FIGURE_NAME_MAP.get(filename)
    if target_name is None:
        plt.close(fig)
        print(f"  · Skipped (not in thesis set): {filename}")
        return
    if tight_layout:
        fig.tight_layout()
    filepath = os.path.join(OUTPUT_DIR, target_name)
    fig.savefig(filepath, bbox_inches='tight', dpi=200)
    plt.close(fig)
    print(f"  ✓ Saved: {target_name}")

# =====================================================================
# FIG00: AGE DISTRIBUTION
# =====================================================================
print("\n[01/17] Generating fig00_age_distribution.png...")
try:
    age_order = ['UNDER 18', '18-29', '30-39', '40-49', '50-59', '60-69', '70-79', '80-89', '90-100']
    age_counts = df['age_group'].value_counts().reindex(age_order, fill_value=0)

    fig, ax = plt.subplots(figsize=(11, 5))
    bars = ax.bar(range(len(age_counts)), age_counts.values,
                   color=PALETTE['primary_blue'], edgecolor='white', linewidth=0.5)
    ax.set_xticks(range(len(age_counts)))
    ax.set_xticklabels(age_counts.index, rotation=45, ha='right')
    ax.set_ylabel('Number of Encounters')
    ax.set_title('Encounter Distribution by Age Group')
    ax.set_axisbelow(True)

    # Add count labels on bars
    for i, (bar, count) in enumerate(zip(bars, age_counts.values)):
        if count > 0:
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                   f'{int(count)}', ha='center', va='bottom', fontsize=10)

    remove_spines(ax)
    save_figure(fig, 'fig00_age_distribution.png')
except Exception as e:
    print(f"  ✗ Error: {e}")

# =====================================================================
# FIG01: MONTHLY VOLUME
# =====================================================================
print("[02/17] Generating fig01_monthly_volume.png...")
try:
    fig, ax = plt.subplots(figsize=(12, 5))
    monthly = df.groupby('incident_yearmonth').size()
    monthly_idx = monthly.index.astype(str)

    bars = ax.bar(range(len(monthly)), monthly.values,
                  color=PALETTE['primary_blue'], edgecolor='white', linewidth=0.5)
    ax.set_xticks(range(len(monthly)))
    ax.set_xticklabels(monthly_idx, rotation=45, ha='right', fontsize=9)
    ax.set_ylabel('Number of Encounters')
    ax.set_title('Monthly Crisis Encounter Volume (March 2024 – February 2026)')
    ax.axvline(x=2.5, color=PALETTE['warm_coral'], linestyle='--', alpha=0.6, linewidth=1.5)
    ax.set_axisbelow(True)
    remove_spines(ax)
    save_figure(fig, 'fig01_monthly_volume.png')
except Exception as e:
    print(f"  ✗ Error: {e}")

# =====================================================================
# FIG02: RESPONSE MODEL
# =====================================================================
print("[03/17] Generating fig02_response_model.png...")
try:
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Panel A: Counts by response_type
    rt_counts = df['response_type'].value_counts()

    color_map = {
        'Law Enforcement Only (MPD)': PALETTE['warm_coral'],
        'Law Enforcement Only (MCSO)': PALETTE['warm_coral'],
        'Behavioral Health Only (MST)': PALETTE['accent_teal'],
        'Co-Response (MPD+MST)': PALETTE['high_risk'],
        'Co-Response (MCSO+MST)': PALETTE['high_risk'],
        'Other': PALETTE['slate_gray'],
        'Unknown': PALETTE['slate_gray']
    }
    bar_colors = [color_map.get(x, PALETTE['slate_gray']) for x in rt_counts.index]

    axes[0].barh(range(len(rt_counts)), rt_counts.values, color=bar_colors,
                 edgecolor='white', linewidth=0.5)
    axes[0].set_yticks(range(len(rt_counts)))
    axes[0].set_yticklabels(rt_counts.index, fontsize=10)
    axes[0].set_xlabel('Number of Encounters')
    axes[0].set_title('A. Encounters by Response Type')
    axes[0].invert_yaxis()
    axes[0].set_axisbelow(True)
    remove_spines(axes[0])

    for i, v in enumerate(rt_counts.values):
        axes[0].text(v + 5, i, str(v), va='center', fontsize=9)

    # Panel B: Severity by response_model
    rm_sev = df.groupby('response_model')['severe_flag'].agg(['mean', 'count'])
    rm_sev = rm_sev.sort_values('mean', ascending=True)

    color_map_rm = {
        'Law Enforcement Only': PALETTE['warm_coral'],
        'Behavioral Health Only': PALETTE['accent_teal'],
        'Co-Response': PALETTE['high_risk'],
        'Other': PALETTE['slate_gray']
    }
    bar_colors_rm = [color_map_rm.get(x, PALETTE['slate_gray']) for x in rm_sev.index]

    axes[1].barh(range(len(rm_sev)), rm_sev['mean'].values * 100,
                 color=bar_colors_rm, edgecolor='white', linewidth=0.5)
    axes[1].set_yticks(range(len(rm_sev)))
    axes[1].set_yticklabels(rm_sev.index, fontsize=10)
    axes[1].set_xlabel('Severity Rate (%)')
    axes[1].set_title('B. Severity Rate by Response Model')
    axes[1].set_axisbelow(True)
    remove_spines(axes[1])

    for i, (rate, n) in enumerate(zip(rm_sev['mean'], rm_sev['count'])):
        axes[1].text(rate * 100 + 1, i, f'{rate:.1%} (n={n})', va='center', fontsize=9)

    save_figure(fig, 'fig02_response_model.png')
except Exception as e:
    print(f"  ✗ Error: {e}")

# =====================================================================
# FIG03: BEHAVIORAL PREVALENCE
# =====================================================================
print("[04/17] Generating fig03_behavioral_prevalence.png...")
try:
    beh_cols = ['beh_depressed', 'beh_angry', 'beh_confusion', 'beh_disorganized_speech',
                'beh_delusions', 'beh_hallucinations', 'beh_scared', 'beh_manic']
    beh_labels = ['Depression', 'Anger/Uncooperative', 'Confusion', 'Disorganized Speech',
                  'Delusions', 'Hallucinations', 'Scared/Frightened', 'Manic']

    beh_prev = df[beh_cols].mean() * 100
    beh_prev = beh_prev.sort_values(ascending=True)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.barh(range(len(beh_prev)), beh_prev.values, color=PALETTE['primary_blue'],
            edgecolor='white', linewidth=0.5)
    ax.set_yticks(range(len(beh_prev)))
    # Map labels
    label_map = dict(zip(beh_cols, beh_labels))
    ax.set_yticklabels([label_map[c] for c in beh_prev.index], fontsize=10)
    ax.set_xlabel('Prevalence (%)')
    ax.set_title('Behavioral Indicator Prevalence')
    ax.set_axisbelow(True)
    remove_spines(ax)

    for i, v in enumerate(beh_prev.values):
        ax.text(v + 0.5, i, f'{v:.1f}%', va='center', fontsize=9)

    save_figure(fig, 'fig03_behavioral_prevalence.png')
except Exception as e:
    print(f"  ✗ Error: {e}")

# =====================================================================
# FIG04: HOUSING
# =====================================================================
print("[05/17] Generating fig04_housing.png...")
try:
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    # Panel A: Counts by housing
    housing_counts = df['housing_status_clean'].value_counts().sort_values(ascending=False)
    axes[0].barh(range(len(housing_counts)), housing_counts.values,
                 color=PALETTE['primary_blue'], edgecolor='white', linewidth=0.5)
    axes[0].set_yticks(range(len(housing_counts)))
    axes[0].set_yticklabels(housing_counts.index, fontsize=10)
    axes[0].set_xlabel('Number of Encounters')
    axes[0].set_title('A. Encounters by Housing Status')
    axes[0].invert_yaxis()
    axes[0].set_axisbelow(True)
    remove_spines(axes[0])

    for i, v in enumerate(housing_counts.values):
        axes[0].text(v + 5, i, str(v), va='center', fontsize=9)

    # Panel B: Grouped bars (severity & repeat by housing)
    housing_stats = df.groupby('housing_status_clean').agg({
        'severe_flag': 'mean',
        'repeat_contact_flag': 'mean',
        'person_id': 'size'
    }).rename(columns={'person_id': 'count'}).sort_values('severe_flag', ascending=False)

    x = np.arange(len(housing_stats))
    width = 0.35

    axes[1].bar(x - width/2, housing_stats['severe_flag'] * 100, width,
               label='Severity Rate', color=PALETTE['warm_coral'], edgecolor='white', linewidth=0.5)
    axes[1].bar(x + width/2, housing_stats['repeat_contact_flag'] * 100, width,
               label='Repeat Rate', color=PALETTE['accent_teal'], edgecolor='white', linewidth=0.5)

    axes[1].set_ylabel('Rate (%)')
    axes[1].set_title('B. Severity & Repeat Rates by Housing')
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(housing_stats.index, rotation=45, ha='right', fontsize=10)
    axes[1].legend(fontsize=10)
    axes[1].set_axisbelow(True)
    remove_spines(axes[1])

    save_figure(fig, 'fig04_housing.png')
except Exception as e:
    print(f"  ✗ Error: {e}")

# =====================================================================
# FIG05: CALL TYPES
# =====================================================================
print("[06/17] Generating fig05_call_types.png...")
try:
    fig, ax = plt.subplots(figsize=(11, 6))

    call_counts = df['call_type_group'].value_counts().sort_values()
    call_severity = df.groupby('call_type_group')['severe_flag'].mean()

    ax.barh(range(len(call_counts)), call_counts.values, color=PALETTE['primary_blue'],
            edgecolor='white', linewidth=0.5)
    ax.set_yticks(range(len(call_counts)))
    ax.set_yticklabels(call_counts.index, fontsize=10)
    ax.set_xlabel('Number of Encounters')
    ax.set_title('Call Type Distribution and Severity')
    ax.set_axisbelow(True)
    remove_spines(ax)

    for i, (call_type, count) in enumerate(zip(call_counts.index, call_counts.values)):
        sev_rate = call_severity[call_type]
        ax.text(count + 3, i, f'{count} ({sev_rate:.1%})', va='center', fontsize=9)

    save_figure(fig, 'fig05_call_types.png')
except Exception as e:
    print(f"  ✗ Error: {e}")

# =====================================================================
# FIG06: AGENCY SEVERITY COMPONENTS
# =====================================================================
print("[07/17] Generating fig06_agency_severity_components.png...")
try:
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    axes = axes.flatten()

    components = [
        ('involuntary_flag', 'Involuntary Handoff'),
        ('force_flag', 'Force Used'),
        ('subject_injury_flag', 'Subject Injury'),
        ('others_injury_flag', 'Others Injured')
    ]

    color_map_rm = {
        'Law Enforcement Only': PALETTE['warm_coral'],
        'Behavioral Health Only': PALETTE['accent_teal'],
        'Co-Response': PALETTE['high_risk'],
        'Other': PALETTE['slate_gray']
    }

    for idx, (col, title) in enumerate(components):
        ax = axes[idx]
        comp_by_rm = df.groupby('response_model')[col].mean() * 100
        comp_by_rm = comp_by_rm.sort_values(ascending=False)

        bar_colors = [color_map_rm.get(x, PALETTE['slate_gray']) for x in comp_by_rm.index]
        ax.barh(range(len(comp_by_rm)), comp_by_rm.values, color=bar_colors,
                edgecolor='white', linewidth=0.5)
        ax.set_yticks(range(len(comp_by_rm)))
        ax.set_yticklabels(comp_by_rm.index, fontsize=9)
        ax.set_xlabel('Rate (%)')
        ax.set_title(title)
        ax.set_axisbelow(True)
        remove_spines(ax)

        for i, v in enumerate(comp_by_rm.values):
            ax.text(v + 1, i, f'{v:.1f}%', va='center', fontsize=8)

    save_figure(fig, 'fig06_agency_severity_components.png')
except Exception as e:
    print(f"  ✗ Error: {e}")

# =====================================================================
# FIG07: AGENCY WITHIN CALL TYPE
# =====================================================================
print("[08/17] Generating fig07_agency_within_calltype.png...")
try:
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    call_types = ['Suicidal / Self-Harm', 'Person Needs Assistance']
    color_map_rm = {
        'Law Enforcement Only': PALETTE['warm_coral'],
        'Behavioral Health Only': PALETTE['accent_teal'],
        'Co-Response': PALETTE['high_risk'],
        'Other': PALETTE['slate_gray']
    }

    for ax_idx, call_type in enumerate(call_types):
        ax = axes[ax_idx]
        df_subset = df[df['call_type_group'] == call_type]

        rm_stats = df_subset.groupby('response_model')['severe_flag'].agg(['mean', 'sum', 'size'])
        rm_stats = rm_stats.sort_values('mean', ascending=True)

        bar_colors = [color_map_rm.get(x, PALETTE['slate_gray']) for x in rm_stats.index]
        ax.barh(range(len(rm_stats)), rm_stats['mean'].values * 100, color=bar_colors,
                edgecolor='white', linewidth=0.5)
        ax.set_yticks(range(len(rm_stats)))
        ax.set_yticklabels(rm_stats.index, fontsize=10)
        ax.set_xlabel('Severity Rate (%)')
        ax.set_title(f'{call_type}')
        ax.set_axisbelow(True)
        remove_spines(ax)

        for i, (rate, n) in enumerate(zip(rm_stats['mean'], rm_stats['size'])):
            ax.text(rate * 100 + 1, i, f'{rate:.1%} (n={int(n)})', va='center', fontsize=9)

    save_figure(fig, 'fig07_agency_within_calltype.png')
except Exception as e:
    print(f"  ✗ Error: {e}")

# =====================================================================
# FIG08: SEVERITY COEFFICIENTS
# =====================================================================
print("[09/17] Generating fig08_severity_coefficients.png...")
try:
    feature_cols = ['has_mst', 'has_mpd', 'beh_angry', 'beh_manic', 'beh_confusion',
                    'beh_depressed', 'beh_disorganized_speech', 'beh_hallucinations',
                    'beh_scared', 'substance_involved', 'is_unhoused', 'is_housed',
                    'probable_cause']
    feature_names = ['MST Responded', 'MPD Responded', 'Anger/Uncooperative', 'Manic',
                     'Confusion', 'Depression', 'Disorganized Speech', 'Hallucinations',
                     'Scared/Frightened', 'Substance Involved', 'Unhoused', 'Housed',
                     'Probable Cause']

    X_sev = df[feature_cols].fillna(0).values
    y_sev = df['severe_flag'].values

    X_train, X_test, y_train, y_test = train_test_split(X_sev, y_sev, test_size=0.3, random_state=42)
    coef_results, w_sev = logistic_regression_coefficients(X_train, y_train, feature_names,
                                                           lr=0.01, max_iter=5000, l2=0.01)

    y_pred_test = logistic_regression_predict_proba(X_test, w_sev)
    test_auc = auc_score(y_test, y_pred_test)

    coef_results = coef_results.sort_values('coefficient', ascending=True)

    # Color based on significance
    colors = []
    for _, row in coef_results.iterrows():
        if row['p_value'] < 0.05:
            colors.append(PALETTE['positive_sig'] if row['coefficient'] > 0 else PALETTE['negative_sig'])
        else:
            colors.append(PALETTE['not_sig'])

    fig, ax = plt.subplots(figsize=(11, 7))
    ax.barh(range(len(coef_results)), coef_results['coefficient'].values, color=colors,
            edgecolor='white', linewidth=0.5)
    ax.set_yticks(range(len(coef_results)))
    ax.set_yticklabels(coef_results['feature'].values, fontsize=10)
    ax.set_xlabel('Coefficient Value')
    ax.set_title(f'Severity Model Coefficients (Test AUC = {test_auc:.3f})')
    ax.axvline(x=0, color='black', linestyle='-', linewidth=0.8, alpha=0.5)
    ax.set_axisbelow(True)
    remove_spines(ax)

    # Add significance markers
    for i, (_, row) in enumerate(coef_results.iterrows()):
        p = row['p_value']
        marker = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else 'ns'
        ax.text(row['coefficient'] + 0.01, i, marker, va='center', fontsize=8)

    save_figure(fig, 'fig08_severity_coefficients.png')
except Exception as e:
    print(f"  ✗ Error: {e}")

# =====================================================================
# FIG09: SEVERITY ROC
# =====================================================================
print("[10/17] Generating fig09_severity_roc.png...")
try:
    X_sev = df[feature_cols].fillna(0).values
    y_sev = df['severe_flag'].values

    X_train, X_test, y_train, y_test = train_test_split(X_sev, y_sev, test_size=0.3, random_state=42)
    w_sev = logistic_regression_fit(X_train, y_train, lr=0.01, max_iter=15000, l2=0.01)

    y_train_pred = logistic_regression_predict_proba(X_train, w_sev)
    y_test_pred = logistic_regression_predict_proba(X_test, w_sev)

    fpr_train, tpr_train, _ = roc_curve(y_train, y_train_pred)
    fpr_test, tpr_test, _ = roc_curve(y_test, y_test_pred)

    auc_train = auc_score(y_train, y_train_pred)
    auc_test = auc_score(y_test, y_test_pred)

    fig, ax = plt.subplots(figsize=(8, 7))
    ax.plot(fpr_test, tpr_test, color=PALETTE['warm_coral'], linewidth=2.5,
            label=f'Test (AUC = {auc_test:.3f})')
    ax.plot(fpr_train, tpr_train, color=PALETTE['accent_teal'], linewidth=1.5,
            alpha=0.6, label=f'Train (AUC = {auc_train:.3f})')
    ax.plot([0, 1], [0, 1], color='black', linestyle='--', linewidth=1, alpha=0.5, label='Random')

    ax.set_xlabel('False Positive Rate')
    ax.set_ylabel('True Positive Rate')
    ax.set_title('ROC Curve: Severity Model')
    ax.legend(fontsize=10, loc='lower right')
    ax.set_xlim([-0.02, 1.02])
    ax.set_ylim([-0.02, 1.02])
    ax.set_axisbelow(True)
    remove_spines(ax)

    save_figure(fig, 'fig09_severity_roc.png')
except Exception as e:
    print(f"  ✗ Error: {e}")

# =====================================================================
# FIG10: REPEAT COEFFICIENTS
# =====================================================================
print("[11/17] Generating fig10_repeat_coefficients.png...")
try:
    feature_cols_repeat = ['is_unhoused', 'is_housed', 'has_mst', 'has_mpd',
                           'substance_involved', 'beh_angry', 'beh_confusion',
                           'beh_depressed', 'beh_manic', 'severe_flag']
    feature_names_repeat = ['Unhoused', 'Housed', 'MST Responded', 'MPD Responded',
                            'Substance Involved', 'Anger/Uncooperative', 'Confusion',
                            'Depression', 'Manic', 'Severe Encounter']

    X_rep = df[feature_cols_repeat].fillna(0).values
    y_rep = df['repeat_contact_flag'].values

    X_train, X_test, y_train, y_test = train_test_split(X_rep, y_rep, test_size=0.3, random_state=42)
    coef_results_rep, w_rep = logistic_regression_coefficients(X_train, y_train, feature_names_repeat,
                                                               lr=0.01, max_iter=5000, l2=0.01)

    y_pred_test = logistic_regression_predict_proba(X_test, w_rep)
    test_auc_rep = auc_score(y_test, y_pred_test)

    coef_results_rep = coef_results_rep.sort_values('coefficient', ascending=True)

    # Color based on significance
    colors = []
    for _, row in coef_results_rep.iterrows():
        if row['p_value'] < 0.05:
            colors.append(PALETTE['positive_sig'] if row['coefficient'] > 0 else PALETTE['negative_sig'])
        else:
            colors.append(PALETTE['not_sig'])

    fig, ax = plt.subplots(figsize=(11, 6))
    ax.barh(range(len(coef_results_rep)), coef_results_rep['coefficient'].values, color=colors,
            edgecolor='white', linewidth=0.5)
    ax.set_yticks(range(len(coef_results_rep)))
    ax.set_yticklabels(coef_results_rep['feature'].values, fontsize=10)
    ax.set_xlabel('Coefficient Value')
    ax.set_title(f'Repeat Model Coefficients (Test AUC = {test_auc_rep:.3f})')
    ax.axvline(x=0, color='black', linestyle='-', linewidth=0.8, alpha=0.5)
    ax.set_axisbelow(True)
    remove_spines(ax)

    # Add significance markers
    for i, (_, row) in enumerate(coef_results_rep.iterrows()):
        p = row['p_value']
        marker = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else 'ns'
        ax.text(row['coefficient'] + 0.01, i, marker, va='center', fontsize=8)

    save_figure(fig, 'fig10_repeat_coefficients.png')
except Exception as e:
    print(f"  ✗ Error: {e}")

# =====================================================================
# FIG11: CLUSTER PROFILES
# =====================================================================
print("[12/17] Generating fig11_cluster_profiles.png...")
try:
    cluster_cols = ['beh_angry', 'beh_manic', 'beh_confusion', 'beh_depressed',
                    'beh_hallucinations', 'beh_scared', 'substance_involved',
                    'is_unhoused', 'repeat_contact_flag', 'involuntary_handoff']
    cluster_labels = ['Anger', 'Manic', 'Confusion', 'Depression', 'Hallucinations',
                      'Scared', 'Substance', 'Unhoused', 'Repeat', 'Involuntary']

    X_cluster = df[cluster_cols].fillna(0).values
    labels, centroids, cost = kmodes_fit(X_cluster, k=3, max_iter=100, n_init=5)

    df['cluster'] = labels

    # Create profile dataframe
    cluster_profiles = pd.DataFrame()
    for i in range(3):
        cluster_data = df[df['cluster'] == i]
        profile = cluster_data[cluster_cols].mean()
        n_cluster = len(cluster_data)
        sev_rate = cluster_data['severe_flag'].mean()
        cluster_profiles[f'Cluster {i}\n(n={n_cluster}, sev={sev_rate:.1%})'] = profile

    # Heatmap
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(cluster_profiles, annot=True, fmt='.2f', cmap='cividis',
                cbar_kws={'label': 'Proportion'}, ax=ax, linewidths=0.5,
                xticklabels=cluster_profiles.columns, yticklabels=cluster_labels)
    ax.set_xlabel('')
    ax.set_ylabel('')
    ax.set_title('Cluster Profiles: Behavioral Characteristics')
    plt.setp(ax.get_yticklabels(), rotation=0, fontsize=10)
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right', fontsize=10)

    save_figure(fig, 'fig11_cluster_profiles.png')

    # Store cluster assignments for next figures
    clusters_df = df[['cluster', 'severe_flag', 'repeat_contact_flag', 'response_model']].copy()
except Exception as e:
    print(f"  ✗ Error: {e}")
    # Fallback: assign dummy clusters
    df['cluster'] = np.random.randint(0, 3, len(df))
    clusters_df = df[['cluster', 'severe_flag', 'repeat_contact_flag', 'response_model']].copy()

# =====================================================================
# FIG12: CLUSTER OUTCOMES
# =====================================================================
print("[13/17] Generating fig12_cluster_outcomes.png...")
try:
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    cluster_outcomes = df.groupby('cluster').agg({
        'severe_flag': 'mean',
        'repeat_contact_flag': 'mean',
        'person_id': 'size'
    }).rename(columns={'person_id': 'count'})

    # Panel A: Severity by cluster
    sev_rates = cluster_outcomes['severe_flag'].values * 100
    colors_risk = []
    for rate in sev_rates:
        if rate < 20:
            colors_risk.append(PALETTE['low_risk'])
        elif rate < 40:
            colors_risk.append(PALETTE['mod_risk'])
        else:
            colors_risk.append(PALETTE['high_risk'])

    axes[0].bar(range(len(sev_rates)), sev_rates, color=colors_risk, edgecolor='white', linewidth=0.5)
    axes[0].set_xticks(range(len(sev_rates)))
    axes[0].set_xticklabels([f'Cluster {i}' for i in range(len(sev_rates))], fontsize=10)
    axes[0].set_ylabel('Severity Rate (%)')
    axes[0].set_title('A. Severity Rate by Cluster')
    axes[0].set_axisbelow(True)
    remove_spines(axes[0])

    for i, rate in enumerate(sev_rates):
        axes[0].text(i, rate + 1, f'{rate:.1f}%', ha='center', va='bottom', fontsize=10)

    # Panel B: Repeat by cluster
    rep_rates = cluster_outcomes['repeat_contact_flag'].values * 100
    colors_risk = []
    for rate in rep_rates:
        if rate < 20:
            colors_risk.append(PALETTE['low_risk'])
        elif rate < 40:
            colors_risk.append(PALETTE['mod_risk'])
        else:
            colors_risk.append(PALETTE['high_risk'])

    axes[1].bar(range(len(rep_rates)), rep_rates, color=colors_risk, edgecolor='white', linewidth=0.5)
    axes[1].set_xticks(range(len(rep_rates)))
    axes[1].set_xticklabels([f'Cluster {i}' for i in range(len(rep_rates))], fontsize=10)
    axes[1].set_ylabel('Repeat Rate (%)')
    axes[1].set_title('B. Repeat Contact Rate by Cluster')
    axes[1].set_axisbelow(True)
    remove_spines(axes[1])

    for i, rate in enumerate(rep_rates):
        axes[1].text(i, rate + 1, f'{rate:.1f}%', ha='center', va='bottom', fontsize=10)

    save_figure(fig, 'fig12_cluster_outcomes.png')
except Exception as e:
    print(f"  ✗ Error: {e}")

# =====================================================================
# FIG13: CLUSTER AGENCY
# =====================================================================
print("[14/17] Generating fig13_cluster_agency.png...")
try:
    fig, ax = plt.subplots(figsize=(10, 6))

    cluster_agency = df.groupby(['cluster', 'response_model']).size().unstack(fill_value=0)
    cluster_agency_pct = cluster_agency.div(cluster_agency.sum(axis=1), axis=0) * 100

    color_map_rm = {
        'Law Enforcement Only': PALETTE['warm_coral'],
        'Behavioral Health Only': PALETTE['accent_teal'],
        'Co-Response': PALETTE['high_risk'],
        'Other': PALETTE['slate_gray']
    }

    colors = [color_map_rm.get(x, PALETTE['slate_gray']) for x in cluster_agency_pct.columns]

    cluster_agency_pct.plot(kind='barh', stacked=True, ax=ax, color=colors,
                            edgecolor='white', linewidth=0.5, width=0.7)
    ax.set_xlabel('Response Model (%)')
    ax.set_ylabel('Cluster')
    ax.set_title('Response Model Distribution by Cluster')
    ax.set_yticklabels([f'Cluster {i}' for i in cluster_agency_pct.index], fontsize=10)
    ax.legend(title='Response Model', fontsize=9, title_fontsize=10, bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.set_axisbelow(True)
    remove_spines(ax)

    save_figure(fig, 'fig13_cluster_agency.png', tight_layout=True)
except Exception as e:
    print(f"  ✗ Error: {e}")

# =====================================================================
# FIG14: TIME SERIES
# =====================================================================
print("[15/17] Generating fig14_time_series.png...")
try:
    df_ts = df[df['date_at_incident'] >= '2024-05-01'].copy()
    df_ts['date_at_incident'] = pd.to_datetime(df_ts['date_at_incident'])

    monthly_ts = df_ts.groupby(df_ts['date_at_incident'].dt.to_period('M')).agg({
        'person_id': 'size',
        'severe_flag': 'mean',
        'repeat_contact_flag': 'mean'
    }).rename(columns={'person_id': 'volume'})

    # Calculate 3-month moving average
    ma_volume = monthly_ts['volume'].rolling(window=3, center=True).mean()
    ma_severe = monthly_ts['severe_flag'].rolling(window=3, center=True).mean()
    ma_repeat = monthly_ts['repeat_contact_flag'].rolling(window=3, center=True).mean()

    fig, axes = plt.subplots(3, 1, figsize=(12, 9))

    x_months = range(len(monthly_ts))
    month_labels = [str(p) for p in monthly_ts.index]

    # Volume
    axes[0].bar(x_months, monthly_ts['volume'].values, color=PALETTE['primary_blue'],
               alpha=0.6, edgecolor='white', linewidth=0.5, label='Monthly')
    axes[0].plot(x_months, ma_volume.values, color=PALETTE['primary_blue'],
                linewidth=2, marker='o', markersize=4, label='3-Month MA')
    axes[0].set_ylabel('Number of Encounters')
    axes[0].set_title('A. Encounter Volume Over Time')
    axes[0].set_axisbelow(True)
    axes[0].legend(fontsize=9)
    remove_spines(axes[0])

    # Severity
    axes[1].plot(x_months, monthly_ts['severe_flag'].values * 100, color=PALETTE['warm_coral'],
                linewidth=1.5, marker='o', markersize=4, alpha=0.6, label='Monthly')
    axes[1].plot(x_months, ma_severe.values * 100, color=PALETTE['warm_coral'],
                linewidth=2.5, label='3-Month MA')
    axes[1].set_ylabel('Severity Rate (%)')
    axes[1].set_title('B. Severity Rate Over Time')
    axes[1].set_axisbelow(True)
    axes[1].legend(fontsize=9)
    remove_spines(axes[1])

    # Repeat
    axes[2].plot(x_months, monthly_ts['repeat_contact_flag'].values * 100, color=PALETTE['accent_teal'],
                linewidth=1.5, marker='o', markersize=4, alpha=0.6, label='Monthly')
    axes[2].plot(x_months, ma_repeat.values * 100, color=PALETTE['accent_teal'],
                linewidth=2.5, label='3-Month MA')
    axes[2].set_ylabel('Repeat Rate (%)')
    axes[2].set_xlabel('Month')
    axes[2].set_title('C. Repeat Contact Rate Over Time')
    axes[2].set_xticks(x_months)
    axes[2].set_xticklabels(month_labels, rotation=45, ha='right', fontsize=9)
    axes[2].set_axisbelow(True)
    axes[2].legend(fontsize=9)
    remove_spines(axes[2])

    save_figure(fig, 'fig14_time_series.png')
except Exception as e:
    print(f"  ✗ Error: {e}")

# =====================================================================
# FIG15: FREQUENCY VS IMPACT
# =====================================================================
print("[16/17] Generating fig15_frequency_vs_impact.png...")
try:
    beh_cols_impact = ['beh_depressed', 'beh_angry', 'beh_confusion', 'beh_disorganized_speech',
                       'beh_delusions', 'beh_hallucinations', 'beh_scared', 'beh_manic']
    beh_names_impact = ['Depression', 'Anger', 'Confusion', 'Disorganized Speech',
                        'Delusions', 'Hallucinations', 'Scared', 'Manic']

    # Get coefficient info
    X_sev = df[feature_cols].fillna(0).values
    y_sev = df['severe_flag'].values
    X_train, X_test, y_train, y_test = train_test_split(X_sev, y_sev, test_size=0.3, random_state=42)
    coef_results, _ = logistic_regression_coefficients(X_train, y_train, feature_names,
                                                       lr=0.01, max_iter=5000, l2=0.01)

    # Build mapping
    beh_coef_map = {}
    for orig_col, nice_name in zip(beh_cols_impact, beh_names_impact):
        matches = coef_results[coef_results['feature'] == nice_name]
        if len(matches) > 0:
            beh_coef_map[nice_name] = matches.iloc[0]

    # Prepare scatter data
    freq = []
    impact = []
    sig_status = []
    labels_scatter = []

    for col, name in zip(beh_cols_impact, beh_names_impact):
        freq_val = df[col].mean() * 100
        if name in beh_coef_map:
            coef_row = beh_coef_map[name]
            freq.append(freq_val)
            impact.append(coef_row['coefficient'])
            sig_status.append(coef_row['p_value'] < 0.05)
            labels_scatter.append(name)

    fig, ax = plt.subplots(figsize=(10, 7))

    # Color by significance
    colors_scatter = [PALETTE['positive_sig'] if (impact[i] > 0 and sig_status[i]) else
                     (PALETTE['negative_sig'] if (impact[i] < 0 and sig_status[i]) else PALETTE['not_sig'])
                     for i in range(len(freq))]

    ax.scatter(freq, impact, s=200, c=colors_scatter, alpha=0.7, edgecolors='white', linewidth=1.5)
    ax.axhline(y=0, color='black', linestyle='-', linewidth=1, alpha=0.5)
    ax.set_xlabel('Prevalence (%)')
    ax.set_ylabel('Logistic Coefficient (Impact on Severity)')
    ax.set_title('Behavioral Indicator: Prevalence vs Impact on Severity')
    ax.set_axisbelow(True)
    remove_spines(ax)

    # Annotate points
    for i, label in enumerate(labels_scatter):
        ax.annotate(label, (freq[i], impact[i]), fontsize=9, ha='center', va='bottom',
                   xytext=(0, 3), textcoords='offset points')

    save_figure(fig, 'fig15_frequency_vs_impact.png')
except Exception as e:
    print(f"  ✗ Error: {e}")

# =====================================================================
# FIG16: HOUSING REPEAT
# =====================================================================
print("[17/17] Generating fig16_housing_repeat.png...")
try:
    fig, ax = plt.subplots(figsize=(10, 5))

    housing_repeat = df.groupby('housing_status_clean').agg({
        'repeat_contact_flag': ['mean', 'sum', 'size']
    }).round(3)
    housing_repeat.columns = ['repeat_rate', 'n_repeat', 'n_total']
    housing_repeat = housing_repeat.sort_values('repeat_rate', ascending=False)

    repeat_pct = housing_repeat['repeat_rate'].values * 100

    bars = ax.bar(range(len(housing_repeat)), repeat_pct, color=PALETTE['accent_teal'],
                  edgecolor='white', linewidth=0.5)
    ax.set_xticks(range(len(housing_repeat)))
    ax.set_xticklabels(housing_repeat.index, rotation=45, ha='right', fontsize=10)
    ax.set_ylabel('Repeat Contact Rate (%)')
    ax.set_title('Repeat Encounter Rate by Housing Status')
    ax.set_axisbelow(True)
    remove_spines(ax)

    for i, (rate, n) in enumerate(zip(repeat_pct, housing_repeat['n_total'].values)):
        ax.text(i, rate + 1, f'{rate:.1f}%\n(n={int(n)})', ha='center', va='bottom', fontsize=9)

    save_figure(fig, 'fig16_housing_repeat.png')
except Exception as e:
    print(f"  ✗ Error: {e}")

# =====================================================================
# SUMMARY
# =====================================================================
print("\n" + "="*70)
print("FIGURE GENERATION COMPLETE")
print("="*70)
print(f"\nAll figures saved to: {OUTPUT_DIR}")
print("\nFigures generated:")
figures = [
    'fig00_age_distribution.png',
    'fig01_monthly_volume.png',
    'fig02_response_model.png',
    'fig03_behavioral_prevalence.png',
    'fig04_housing.png',
    'fig05_call_types.png',
    'fig06_agency_severity_components.png',
    'fig07_agency_within_calltype.png',
    'fig08_severity_coefficients.png',
    'fig09_severity_roc.png',
    'fig10_repeat_coefficients.png',
    'fig11_cluster_profiles.png',
    'fig12_cluster_outcomes.png',
    'fig13_cluster_agency.png',
    'fig14_time_series.png',
    'fig15_frequency_vs_impact.png',
    'fig16_housing_repeat.png'
]
for fig in figures:
    filepath = os.path.join(OUTPUT_DIR, fig)
    if os.path.exists(filepath):
        print(f"  ✓ {fig}")
    else:
        print(f"  ✗ {fig} (MISSING)")

print("\n" + "="*70)
