import pandas as pd
import matplotlib.pyplot as plt
import os

# ---------------------------------------------------------
# STEP 9: Visualization — Mean Trajectories Over Time
# ---------------------------------------------------------

df = pd.read_csv("output/combined_numeric.csv")

role_col = "Which of the following most closely reflects your professional role at the time of the 8th Annual CIT Training Academy? Select one."
when_col = "When are you taking this survey? Select one."

# Filter Missoula Law Enforcement
mle = df[df[role_col].str.contains("Missoula Law Enforcement", na=False)].copy()

# Assign stage
def assign_stage(row):
    if row["timepoint"] == "pre_post":
        if row[when_col] == "April 1, 2024":
            return "Pre"
        elif row[when_col] == "April 5, 2024":
            return "Post"
    elif row["timepoint"] == "m3_6":
        return "3–6 Month"
    elif row["timepoint"] == "m12":
        return "12 Month"
    return None

mle["stage"] = mle.apply(assign_stage, axis=1)

stage_order = ["Pre", "Post", "3–6 Month", "12 Month"]

num_cols = [col for col in mle.columns if col.endswith("_num")]

# Create output folder for figures
os.makedirs("output/figures", exist_ok=True)

for col in num_cols:

    means = []
    for stage in stage_order:
        subset = mle[mle["stage"] == stage][col].dropna()
        means.append(subset.mean() if len(subset) > 0 else None)

    plt.figure()
    plt.plot(stage_order, means, marker="o")
    plt.ylim(1, 5)
    plt.title(col.replace("_num", ""))
    plt.xlabel("Stage")
    plt.ylabel("Mean Score (1–5)")
    plt.grid(True)

    filename = col.replace("_num", "").replace(" ", "_")[:60]
    plt.savefig(f"output/figures/{filename}.png", bbox_inches="tight")
    plt.close()

print("\nSaved figures to: output/figures/")