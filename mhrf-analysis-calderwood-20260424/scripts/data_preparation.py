"""
data_preparation.py
Full data preparation: cleaning, feature engineering, behavioral indicator parsing,
responding agency categorization, severity construction.
"""
import pandas as pd
import numpy as np
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'outputs')

def load_and_prepare():
    # Load the severity dataset (most complete)
    df = pd.read_csv(os.path.join(DATA_DIR, 'mhrf_with_severity.csv'))

    # Drop the 20 fully null rows
    df = df.dropna(subset=['record_id']).copy()
    print(f"Records after dropping nulls: {len(df)}")

    # Remove 19 trailing blank/duplicate rows (880 -> 861)
    # These are content-identical empty rows at the end of the raw Excel
    orig_cols = [c for c in df.columns if not c.startswith('beh_') and 'flag' not in c
                 and c not in ['record_id', 'person_id', 'Unnamed: 0', 'age_midpoint']]
    before = len(df)
    df = df.drop_duplicates(subset=orig_cols[:25], keep='first').reset_index(drop=True)
    print(f"Records after deduplication: {len(df)} (removed {before - len(df)} blank/duplicate rows)")

    # ── Parse Date ─────────────────────────────────────────────────────
    df['date_at_incident'] = pd.to_datetime(df['date_at_incident'], errors='coerce')
    df['incident_year'] = df['date_at_incident'].dt.year
    df['incident_month'] = df['date_at_incident'].dt.month
    df['incident_yearmonth'] = df['date_at_incident'].dt.to_period('M')

    # ── Parse Behavioral Indicators ────────────────────────────────────
    beh_field = 'behaviors_evident_at_time_of_incident_check_all_that_apply'
    behaviors = {
        'beh_depressed': 'Depressed',
        'beh_angry': 'Angry/uncooperative',
        'beh_confusion': 'Disorientation/confusion',
        'beh_disorganized_speech': 'Disorganized speech',
        'beh_delusions': 'Delusions',
        'beh_hallucinations': 'Hallucinations',
        'beh_scared': 'Unusually scared/frightened',
        'beh_manic': 'Manic',
    }
    for col, keyword in behaviors.items():
        df[col] = df[beh_field].fillna('').str.contains(keyword, case=False).astype(int)

    df['beh_any_documented'] = df[beh_field].notna().astype(int)
    df['beh_count'] = df[list(behaviors.keys())].sum(axis=1)

    # ── Parse Responding Agencies ──────────────────────────────────────
    agency_field = 'responding_agencies_select_all_agencies_involved_in_the_incident_response'

    def has_agency(row, agency):
        if pd.isna(row): return False
        return agency in str(row)

    df['has_mpd'] = df[agency_field].apply(lambda x: has_agency(x, 'MPD')).astype(int)
    df['has_mst'] = df[agency_field].apply(lambda x: has_agency(x, 'MST')).astype(int)
    df['has_mcso'] = df[agency_field].apply(lambda x: has_agency(x, 'MCSO')).astype(int)

    def response_type(row):
        if pd.isna(row): return 'Unknown'
        mpd = 'MPD' in str(row)
        mst = 'MST' in str(row)
        mcso = 'MCSO' in str(row)
        if mpd and mst: return 'Co-Response (MPD+MST)'
        elif mpd and not mst and not mcso: return 'Law Enforcement Only (MPD)'
        elif mst and not mpd and not mcso: return 'Behavioral Health Only (MST)'
        elif mcso and mst: return 'Co-Response (MCSO+MST)'
        elif mcso and not mst: return 'Law Enforcement Only (MCSO)'
        else: return 'Other'

    df['response_type'] = df[agency_field].apply(response_type)

    # Simplified: LE-only vs BH-only vs Co-response
    def response_model(row):
        if row in ['Law Enforcement Only (MPD)', 'Law Enforcement Only (MCSO)']:
            return 'Law Enforcement Only'
        elif row == 'Behavioral Health Only (MST)':
            return 'Behavioral Health Only'
        elif row in ['Co-Response (MPD+MST)', 'Co-Response (MCSO+MST)']:
            return 'Co-Response'
        else:
            return 'Other'

    df['response_model'] = df['response_type'].apply(response_model)

    # ── Parse Form Completer Agency ────────────────────────────────────
    agency_aff = 'agency_affiliation_of_professional_completing_this_form_select_one'
    df['form_agency'] = df[agency_aff].fillna('Unknown')
    df.loc[~df['form_agency'].isin(['MPD', 'MST', 'MCSO']), 'form_agency'] = 'Other'

    # ── Drug/Alcohol ───────────────────────────────────────────────────
    df['substance_involved'] = (df['drug_or_alcohol_involvement'] == 'Yes').astype(int)
    df['substance_unsure'] = (df['drug_or_alcohol_involvement'] == 'Unsure').astype(int)

    # ── Criminal Justice ───────────────────────────────────────────────
    df['probable_cause'] = (df['does_probable_cause_exist_for_criminal_charges'] == 'Yes').astype(int)

    # ── Incident Origination ──────────────────────────────────────────
    orig_field = 'how_did_the_incident_originate_select_one'
    def origin_clean(row):
        if pd.isna(row): return 'Unknown'
        if 'flagged as mental health' in str(row).lower(): return 'MH-Flagged Dispatch'
        elif 'not flagged' in str(row).lower(): return 'Non-MH Dispatch'
        elif 'self-initiated' in str(row).lower(): return 'Self-Initiated'
        else: return 'Other'
    df['incident_origin'] = df[orig_field].apply(origin_clean)

    # ── Housing (already cleaned) ─────────────────────────────────────
    df['is_unhoused'] = (df['housing_status_clean'] == 'Unhoused').astype(int)
    df['is_housed'] = (df['housing_status_clean'] == 'Housed').astype(int)

    # ── Handoff Status ────────────────────────────────────────────────
    df['involuntary_handoff'] = df['status_at_handoff_clean'].isin(
        ['Involuntary', 'Involuntary & Under Arrest']).astype(int)

    # ── Commitment Criteria ───────────────────────────────────────────
    ds_field = 'criteria_for_commitment_imminent_danger_to_self_check_all_that_apply'
    do_field = 'criteria_for_commitment_imminent_danger_to_others_check_all_that_apply'
    bn_field = 'criteria_for_commitment_unable_to_meet_basic_needs_check_all_that_apply'

    df['has_danger_self'] = (df[ds_field].notna() & ~df[ds_field].fillna('').str.contains('Not applicable', case=False)).astype(int)
    df['has_danger_others'] = (df[do_field].notna() & ~df[do_field].fillna('').str.contains('Not applicable', case=False)).astype(int)
    df['has_basic_needs'] = (df[bn_field].notna() & ~df[bn_field].fillna('').str.contains('Not applicable', case=False)).astype(int)
    df['commitment_any'] = ((df['has_danger_self'] + df['has_danger_others'] + df['has_basic_needs']) > 0).astype(int)

    # ── Age numeric midpoint ──────────────────────────────────────────
    age_map = {'UNDER 18': 15, '18-29': 24, '30-39': 35, '40-49': 45,
               '50-59': 55, '60-69': 65, '70-79': 75, '80-89': 85, '90-100': 95}
    df['age_midpoint'] = df['age_group'].map(age_map)

    # ── Save ──────────────────────────────────────────────────────────
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df.to_csv(os.path.join(DATA_DIR, 'mhrf_analysis_ready.csv'), index=False)
    print(f"Saved analysis-ready dataset: {df.shape}")

    return df

if __name__ == '__main__':
    df = load_and_prepare()

    # Quick summary
    print(f"\n{'='*60}")
    print(f"DATASET SUMMARY")
    print(f"{'='*60}")
    print(f"Total encounters: {len(df)}")
    print(f"Unique persons: {df['person_id'].nunique()}")
    print(f"Date range: {df['date_at_incident'].min()} to {df['date_at_incident'].max()}")
    print(f"Severity rate: {df['severe_flag'].mean():.1%}")
    print(f"Repeat rate: {df['repeat_contact_flag'].dropna().mean():.1%}")
    print(f"\nResponse model distribution:")
    print(df['response_model'].value_counts())
    print(f"\nSeverity by response model:")
    print(df.groupby('response_model')['severe_flag'].agg(['mean','count']).round(3))
