import pandas as pd
import numpy as np

# -------------------------------------------------------------------
# STEP 7: Long-term sustainability analysis for Missoula Law Enforcement (MLE)
#
# Goal:
# In earlier steps, I evaluated immediate Pre vs Post impact.
# Here, I want to understand whether those improvements are sustained
# over time at 3–6 months and 12 months.
#
# This step builds a unified "stage" variable so I can compare:
# Pre → Post → 3–6 month → 12 month
#
# Output:
# - output/mle_long_term_trends.csv
# -------------------------------------------------------------------

df = pd.read_csv("output/combined_numeric.csv")

role_col = (
    "Which of the following most closely reflects your professional role at the time of the 8th Annual CIT Training Academy? Select one."
)
when_col = "When are you taking this survey? Select one."

# -------------------------------------------------------------------
# Step 1: Filter to Missoula Law Enforcement (MLE)
# This keeps the sustainability analysis aligned with my core subsample.
# -------------------------------------------------------------------

mle = df[df[role_col].str.contains("Missoula Law Enforcement", na=False)].copy()

# -------------------------------------------------------------------
# Step 2: Create a unified stage variable.
# Because Pre and Post are both inside the "pre_post" file,
# I need to split them using the survey date (April 1 vs April 5).
#
# This allows me to compare four clean stages:
# Pre, Post, 3–6 month, and 12 month.
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

# -------------------------------------------------------------------
# Step 3: Identify numeric KSA columns.
# These were created in Step 4 when I mapped Likert responses.
# -------------------------------------------------------------------

num_cols = [col for col in mle.columns if col.endswith("_num")]

results = []

# -------------------------------------------------------------------
# Step 4: Compute mean KSA score for each metric at each stage.
# I also store sample size (n) for transparency.
#
# This gives me the full trajectory of each KSA domain.
# -------------------------------------------------------------------

for col in num_cols:
    for stage in ["Pre", "Post", "3_6_month", "12_month"]:
        subset = mle[mle["stage"] == stage][col].dropna()

        results.append({
            "metric": col.replace("_num", ""),
            "stage": stage,
            "n": len(subset),
            "mean": round(subset.mean(), 3) if len(subset) > 0 else np.nan
        })

trend_df = pd.DataFrame(results)

# Pivot for cleaner reporting (metrics as rows, stages as columns)
trend_pivot = trend_df.pivot(index="metric", columns="stage", values="mean")

# Save for reporting + visualization
trend_pivot.to_csv("output/mle_long_term_trends.csv")

print("\n" + "=" * 100)
print("MISSoula LE LONG-TERM MEAN TRAJECTORY")
print(trend_pivot)

print("\nSaved: output/mle_long_term_trends.csv")