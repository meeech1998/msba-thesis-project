import pandas as pd
import numpy as np
from scipy import stats

# -------------------------------------------------------------------
# STEP 6: Pre vs Post statistical inference (Welch t-test + Cohen’s d)
#
# Goal:
# In Step 5 I looked at mean changes descriptively. In this step, I’m
# testing whether those Pre vs Post differences are statistically
# meaningful (not likely due to random variation).
#
# Why Welch’s t-test:
# My Pre and Post groups have different sample sizes and may not have
# equal variance, so Welch’s t-test is the safer option than a standard
# independent t-test with equal variances assumed.
#
# Why Cohen’s d:
# p-values tell me if a difference is statistically detectable.
# Cohen’s d tells me how BIG the difference is in practical terms.
#
# Output:
# - output/mle_pre_post_inference.csv
# -------------------------------------------------------------------

# Load the numeric-ready dataset (Likert responses already mapped to 1–5)
df = pd.read_csv("output/combined_numeric.csv")

# Columns used to define my subsample (MLE) and distinguish Pre vs Post
role_col = (
    "Which of the following most closely reflects your professional role at the time of the 8th Annual CIT Training Academy? Select one."
)
when_col = "When are you taking this survey? Select one."

# -------------------------------------------------------------------
# Step 1: Filter to Missoula Law Enforcement (MLE)
# This is the primary group I’m evaluating for training impact.
# -------------------------------------------------------------------

mle = df[df[role_col].str.contains("Missoula Law Enforcement", na=False)].copy()

# Only use the pre_post dataset here because this is where I have
# the immediate Pre (April 1) vs Post (April 5) comparison
mle_prepost = mle[mle["timepoint"] == "pre_post"].copy()

# Identify the KSA numeric columns created during Likert mapping (Step 4)
num_cols = [col for col in mle_prepost.columns if col.endswith("_num")]

results = []

# -------------------------------------------------------------------
# Step 2: For each KSA metric:
# - split into Pre vs Post groups
# - run Welch’s t-test
# - calculate effect size (Cohen’s d)
# - store results in a clean output table for reporting
# -------------------------------------------------------------------

for col in num_cols:
    pre = mle_prepost[mle_prepost[when_col] == "April 1, 2024"][col].dropna()
    post = mle_prepost[mle_prepost[when_col] == "April 5, 2024"][col].dropna()

    # Only run stats if both groups have enough data to estimate variance
    if len(pre) > 1 and len(post) > 1:

        # Welch’s independent samples t-test (does not assume equal variances)
        t_stat, p_value = stats.ttest_ind(post, pre, equal_var=False)

        # Cohen’s d effect size (uses pooled SD so results are interpretable)
        # This gives a standardized measure of practical impact.
        pooled_sd = np.sqrt(
            ((len(pre) - 1) * np.var(pre, ddof=1) +
             (len(post) - 1) * np.var(post, ddof=1)) /
            (len(pre) + len(post) - 2)
        )

        cohens_d = (post.mean() - pre.mean()) / pooled_sd

        results.append({
            "metric": col.replace("_num", ""),
            "mean_pre": round(pre.mean(), 3),
            "mean_post": round(post.mean(), 3),
            "difference": round(post.mean() - pre.mean(), 3),
            "t_stat": round(t_stat, 3),
            "p_value": round(p_value, 4),
            "cohens_d": round(cohens_d, 3),
        })

# Convert to a table and rank by biggest improvement
inference_df = pd.DataFrame(results).sort_values(by="difference", ascending=False)

# Save results for the thesis Results section tables
inference_df.to_csv("output/mle_pre_post_inference.csv", index=False)

# Print to terminal for quick validation
print("\n" + "=" * 100)
print("MISSoula LE PRE VS POST — STATISTICAL INFERENCE")
print(inference_df.to_string(index=False))

print("\nSaved: output/mle_pre_post_inference.csv")