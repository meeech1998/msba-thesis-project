import pandas as pd
import numpy as np
from scipy import stats

# -------------------------------------------------------------------
# STEP 8: One-Way ANOVA across stages (Missoula Law Enforcement)
#
# Goal:
# In Step 7 I summarized long-term mean trajectories across stages.
# Here, I’m formally testing whether stage (Pre, Post, 3–6 month, 12 month)
# is associated with statistically different mean KSA scores.
#
# Why ANOVA:
# I’m comparing MORE than two groups (four stages), so ANOVA is the standard
# way to test whether at least one stage mean differs from the others.
#
# Important note:
# This is NOT a repeated-measures analysis because respondents are deidentified.
# So this is a between-groups comparison by stage, not within-person change.
#
# Output:
# - output/mle_stage_anova.csv
# -------------------------------------------------------------------

df = pd.read_csv("output/combined_numeric.csv")

role_col = (
    "Which of the following most closely reflects your professional role at the time of the 8th Annual CIT Training Academy? Select one."
)
when_col = "When are you taking this survey? Select one."

# -------------------------------------------------------------------
# Step 1: Filter to Missoula Law Enforcement (MLE)
# This keeps the analysis consistent with the core evaluation group.
# -------------------------------------------------------------------

mle = df[df[role_col].str.contains("Missoula Law Enforcement", na=False)].copy()

# -------------------------------------------------------------------
# Step 2: Create a unified stage variable across the three datasets.
# Pre and Post are both inside the pre_post file, separated using April 1 vs April 5.
# Follow-ups are stored as their own datasets: m3_6 and m12.
# -------------------------------------------------------------------

def assign_stage(row):
    if row["timepoint"] == "pre_post":
        if row[when_col] == "April 1, 2024":
            return "Pre"
        elif row[when_col] == "April 5, 2024":
            return "Post"
    elif row["timepoint"] == "m3_6":
        return "3_6_month"
    elif row["timepoint"] == "m12":
        return "12_month"
    return None

mle["stage"] = mle.apply(assign_stage, axis=1)

# Numeric KSA columns (created in Step 4 via Likert mapping)
num_cols = [col for col in mle.columns if col.endswith("_num")]

results = []

# -------------------------------------------------------------------
# Step 3: Run ANOVA for each KSA metric across available stages.
# I only include a stage if it has enough data to estimate variance (n > 1).
# This matters because the 12-month group is small and some metrics may be sparse.
# -------------------------------------------------------------------

for col in num_cols:
    groups = []
    group_labels = []

    for stage in ["Pre", "Post", "3_6_month", "12_month"]:
        values = mle[mle["stage"] == stage][col].dropna()

        # Require at least 2 values in a stage to include it in ANOVA
        if len(values) > 1:
            groups.append(values)
            group_labels.append(stage)

    # ANOVA only makes sense if we have at least two valid groups
    if len(groups) >= 2:
        f_stat, p_value = stats.f_oneway(*groups)

        results.append({
            "metric": col.replace("_num", ""),
            "f_stat": round(f_stat, 3),
            "p_value": round(p_value, 4),
        })

# Put results into a clean output table and sort by significance
anova_df = pd.DataFrame(results).sort_values(by="p_value")

anova_df.to_csv("output/mle_stage_anova.csv", index=False)

print("\n" + "=" * 100)
print("MISSoula LE — ANOVA ACROSS STAGES")
print(anova_df.to_string(index=False))

print("\nSaved: output/mle_stage_anova.csv")