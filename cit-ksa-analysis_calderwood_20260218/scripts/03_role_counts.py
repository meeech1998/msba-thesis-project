import pandas as pd

# --------------------------------------------------
# Step 1: Load the cleaned master dataset
# This is the combined file I created in the previous step.
# All downstream analysis should use this file to ensure consistency.
# --------------------------------------------------

df = pd.read_csv("output/combined_clean.csv")

# Define the key columns I’ll repeatedly reference
role_col = "Which of the following most closely reflects your professional role at the time of the 8th Annual CIT Training Academy? Select one."
when_col = "When are you taking this survey? Select one."

# --------------------------------------------------
# Step 2: Understand overall response distribution
# I want to see how many responses exist at each stage.
# This helps me understand imbalance across timepoints.
# --------------------------------------------------

print("\n" + "=" * 90)
print("RESPONSES BY TIMEPOINT")
print(df["timepoint"].value_counts(dropna=False))

# --------------------------------------------------
# Step 3: Understand overall professional role breakdown
# Before narrowing to MLE, I want a full picture of who responded.
# --------------------------------------------------

print("\n" + "=" * 90)
print("ROLE COUNTS (OVERALL)")
print(df[role_col].value_counts(dropna=False))

# --------------------------------------------------
# Step 4: Cross-tab role by timepoint
# This shows how representation changes across survey waves.
# --------------------------------------------------

print("\n" + "=" * 90)
print("ROLE COUNTS BY TIMEPOINT")
print(pd.crosstab(df["timepoint"], df[role_col], dropna=False))

# --------------------------------------------------
# Step 5: Within the pre_post dataset,
# I separate April 1 (Pre) vs April 5 (Post).
# This is how I distinguish baseline vs immediate impact.
# --------------------------------------------------

pre_post = df[df["timepoint"] == "pre_post"].copy()

print("\n" + "=" * 90)
print("PRE_POST: APRIL 1 VS APRIL 5 COUNTS")
print(pre_post[when_col].value_counts(dropna=False))

# --------------------------------------------------
# Step 6: Examine professional roles within April 1 vs April 5.
# This ensures Pre/Post groups are comparable.
# --------------------------------------------------

print("\n" + "=" * 90)
print("PRE_POST: ROLE BREAKDOWN BY APRIL 1 VS APRIL 5")
print(pd.crosstab(pre_post[when_col], pre_post[role_col], dropna=False))

# --------------------------------------------------
# Step 7: Narrow to Missoula Law Enforcement (MLE).
# This is the analytic subsample used in the core evaluation.
# --------------------------------------------------

mle = df[df[role_col].astype(str).str.contains("Missoula Law Enforcement", na=False)].copy()

print("\n" + "=" * 90)
print("MISSoula LAW ENFORCEMENT COUNTS BY TIMEPOINT")
print(mle["timepoint"].value_counts(dropna=False))

# --------------------------------------------------
# Step 8: Within MLE, isolate Pre vs Post counts.
# This confirms the actual sample sizes used in
# my Pre/Post statistical tests.
# --------------------------------------------------

mle_pre_post = mle[mle["timepoint"] == "pre_post"].copy()

print("\n" + "=" * 90)
print("MISSoula LE: PRE VS POST COUNTS (APRIL 1 VS APRIL 5)")
print(mle_pre_post[when_col].value_counts(dropna=False))