"""
12_small_multiples_ksa_trajectories.py

Creates a small-multiples bar chart showing mean KSA scores across training
stages for Missoula Law Enforcement (MLE).

Stages used:
- Pre (April 1, 2024)
- Post (April 5, 2024)
- 3–6 Month follow-up
- 12 Month follow-up

Important limitation:
- Respondents are deidentified and not linked across timepoints, so this is a
  group-level mean trajectory by stage (not within-person longitudinal change).

Input:
- output/combined_numeric.csv

Outputs:
- output/figures/figure_3_small_multiples_ksa_trajectories.png
- output/figure_3_stage_means_by_metric.csv
"""

from __future__ import annotations

import os
import pandas as pd
import matplotlib.pyplot as plt


def main() -> None:
    # --------------------------------------------------
    # Paths
    # --------------------------------------------------
    input_path = "output/combined_numeric.csv"
    figures_dir = "output/figures"
    os.makedirs(figures_dir, exist_ok=True)

    # --------------------------------------------------
    # Load data
    # --------------------------------------------------
    df = pd.read_csv(input_path)

    # --------------------------------------------------
    # Required columns
    # --------------------------------------------------
    role_col = (
        "Which of the following most closely reflects your professional role at the time of the 8th Annual CIT Training Academy? Select one."
    )
    timepoint_col = "timepoint"
    when_col = "When are you taking this survey? Select one."

    for c in [role_col, timepoint_col, when_col]:
        if c not in df.columns:
            raise KeyError(f"Expected column not found: {c}")

    # --------------------------------------------------
    # Numeric KSA columns
    # --------------------------------------------------
    num_cols = [c for c in df.columns if c.endswith("_num")]
    if not num_cols:
        raise ValueError("No numeric KSA columns found ending with '_num'.")

    # --------------------------------------------------
    # Filter to MLE
    # --------------------------------------------------
    mle_label = (
        "Missoula Law Enforcement (inclusive of City Police, Sheriff's Deputies, University of Montana Police, Probation and Parole, and Detention Officers)"
    )
    mle = df[df[role_col] == mle_label].copy()
    if mle.empty:
        raise ValueError("MLE subset is empty. Check role label values.")

    # --------------------------------------------------
    # Assign unified stage variable
    # --------------------------------------------------
    def assign_stage(row) -> str | None:
        tp = row[timepoint_col]

        if tp == "pre_post":
            when = row[when_col]
            if when == "April 1, 2024":
                return "Pre"
            if when == "April 5, 2024":
                return "Post"
            return None

        if tp == "m3_6":
            return "3–6 Month"

        if tp == "m12":
            return "12 Month"

        return None

    mle["stage"] = mle.apply(assign_stage, axis=1)
    mle = mle.dropna(subset=["stage"]).copy()

    stage_order = ["Pre", "Post", "3–6 Month", "12 Month"]

    # --------------------------------------------------
    # Compute stage means for each KSA metric
    # --------------------------------------------------
    means = (
        mle.groupby("stage")[num_cols]
        .mean(numeric_only=True)
        .reindex(stage_order)
    )

    # --------------------------------------------------
    # Save tidy stage means
    # --------------------------------------------------
    tidy = (
        means.reset_index()
        .melt(id_vars="stage", var_name="metric", value_name="mean_score")
    )
    tidy["metric"] = tidy["metric"].str.replace("_num", "", regex=False)
    tidy_out = "output/figure_3_stage_means_by_metric.csv"
    tidy.to_csv(tidy_out, index=False)

    # --------------------------------------------------
    # Short titles for panels
    # --------------------------------------------------
    short_title_map = {
        "current knowledge of mental illness": "Mental Illness",
        "community resources available": "Resources",
        "civil commitment laws": "Commitment Laws",
        "professional liability considerations": "Liability",
        "roles of various actors or organizations": "System Roles",
        "well prepared do you feel": "Preparedness",
        "comfort level in appropriately engaging": "Engagement",
        "confidence in using de-escalation skills": "De-escalation",
    }

    def shorten_metric(full_q: str) -> str:
        clean = full_q.replace("_num", "").replace("Select one.", "").strip().lower()

        for key, label in short_title_map.items():
            if key in clean:
                return label

        return full_q.replace("_num", "").replace("Select one.", "").strip()[:25]

    # --------------------------------------------------
    # Plot: 2x4 small multiples, bar charts
    # --------------------------------------------------
    fig, axes = plt.subplots(2, 4, figsize=(16, 8), sharey=True)
    axes = axes.flatten()

    for i, col in enumerate(num_cols[:8]):
        ax = axes[i]
        y = means[col].values

        ax.bar(stage_order, y, width=0.55)

        ax.set_title(shorten_metric(col), fontsize=10)
        ax.set_ylim(1, 5)

        # Only bottom row keeps x-axis labels
        if i < 4:
            ax.tick_params(axis="x", bottom=False, labelbottom=False)
        else:
            ax.tick_params(axis="x", rotation=20)

        # Only left column gets y-axis label
        if i % 4 == 0:
            ax.set_ylabel("Mean Score")

        # clean style
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    # Hide any unused panels
    for j in range(len(num_cols), 8):
        axes[j].axis("off")

    fig.suptitle(
        "Training Gains Were Immediate and Generally Remained Above Baseline Over Time",
        fontsize=14,
        x=0.01,
        ha="left"
    )

    fig.tight_layout(rect=[0, 0.02, 1, 0.93])

    fig_path = os.path.join(figures_dir, "figure_3_small_multiples_ksa_trajectories.png")
    fig.savefig(fig_path, dpi=300)
    plt.close(fig)

    print("\nSaved:")
    print(f"- {fig_path}")
    print(f"- {tidy_out}")
    print("\nDone ✅")


if __name__ == "__main__":
    main()