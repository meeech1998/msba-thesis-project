import pandas as pd
import numpy as np

# -------------------------------------------------------------------
# STEP 5: Pre vs Post descriptive comparison for Missoula Law Enforcement (MLE)
#
# Goal:
# Before running any statistical tests, I want a clean, simple snapshot
# of how the average KSA scores changed from Pre-training (April 1)
# to Immediate Post-training (April 5) for MLE participants.
#
# Output:
# - output/mle_pre_post_descriptives.csv
# -------------------------------------------------------------------

# Load the numeric-ready dataset (Likert text already mapped to 1–5 scale)
df = pd.read_csv("output/combined_numeric.csv")

# These are the two key columns I need to define my analytic group and stage
role_col = (
    "Which of the following most closely reflects your professional role at the time of the 8th Annual CIT Training Academy? Select one."
)
when_col = "When are you taking this survey? Select one."

# -------------------------------------------------------------------
# Step 1: Filter down to the core group I’m evaluating: Missoula Law Enforcement
# -------------------------------------------------------------------

mle = df[df[role_col].str.contains("Missoula Law Enforcement", na=False)].copy()

# -------------------------------------------------------------------
# Step 2: For the immediate training impact analysis, I only use the pre_post file
# This is where I can separate Pre (April 1) vs Post (April 5).
# -------------------------------------------------------------------

mle_prepost = mle[mle["timepoint"] == "pre_post"].copy()

# -------------------------------------------------------------------
# Step 3: Identify the numeric KSA columns created in Step 4
# These columns all end in "_num" and represent the 1–5 KSA scale.
# -------------------------------------------------------------------

num_cols = [col for col in mle_prepost.columns if col.endswith("_num")]

# -------------------------------------------------------------------
# Step 4: Compute Pre vs Post means for each KSA metric
# I store:
# - sample sizes (n_pre, n_post)
# - mean scores at each stage
# - the difference (post minus pre)
#
# This gives me a ranked list of which areas improved the most.
# -------------------------------------------------------------------

results = []

for col in num_cols:
    pre = mle_prepost[mle_prepost[when_col] == "April 1, 2024"][col].dropna()
    post = mle_prepost[mle_prepost[when_col] == "April 5, 2024"][col].dropna()

    results.append(
        {
            "metric": col.replace("_num", ""),
            "n_pre": len(pre),
            "mean_pre": round(pre.mean(), 3) if len(pre) > 0 else np.nan,
            "n_post": len(post),
            "mean_post": round(post.mean(), 3) if len(post) > 0 else np.nan,
            "difference_post_minus_pre": round(post.mean() - pre.mean(), 3)
            if len(pre) > 0 and len(post) > 0
            else np.nan,
        }
    )

# Convert results into a table and sort by biggest improvement
impact_df = pd.DataFrame(results).sort_values(
    by="difference_post_minus_pre", ascending=False
)

# Save as a clean output file so I can use it in reporting + figures
impact_df.to_csv("output/mle_pre_post_descriptives.csv", index=False)

# Print to terminal so I can sanity check quickly without opening the CSV
print("\n" + "=" * 90)
print("MISSoula LE PRE VS POST DESCRIPTIVE IMPACT")
print(impact_df.to_string(index=False))

print("\nSaved: output/mle_pre_post_descriptives.csv")