"""
11_overall_ksa_index_trajectory.py

Creates a column chart showing the overall KSA index across training stages
for Missoula Law Enforcement (MLE).

Input:
- output/combined_numeric.csv

Outputs:
- output/figures/figure_2_overall_ksa_index_trajectory.png
- output/figure_2_overall_ksa_index_table.csv
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

    for col in [role_col, timepoint_col, when_col]:
        if col not in df.columns:
            raise KeyError(f"Expected column not found: {col}")

    # --------------------------------------------------
    # Numeric KSA columns
    # --------------------------------------------------
    num_cols = [c for c in df.columns if c.endswith("_num")]
    if len(num_cols) != 8:
        print(f"WARNING: Expected 8 numeric KSA columns, found {len(num_cols)}")

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
    # Assign unified stage labels
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

    # --------------------------------------------------
    # Overall KSA index
    # --------------------------------------------------
    mle["ksa_index"] = mle[num_cols].mean(axis=1, skipna=True)

    # --------------------------------------------------
    # Summarize by stage
    # --------------------------------------------------
    stage_order = ["Pre", "Post", "3–6 Month", "12 Month"]

    summary = (
        mle.groupby("stage")["ksa_index"]
        .agg(n="count", mean="mean", std="std")
        .reindex(stage_order)
        .reset_index()
    )

    table_out = "output/figure_2_overall_ksa_index_table.csv"
    summary.to_csv(table_out, index=False)

    # --------------------------------------------------
    # Plot: column chart
    # --------------------------------------------------
    fig, ax = plt.subplots(figsize=(9.5, 6))

    bars = ax.bar(
        summary["stage"],
        summary["mean"],
        width=0.55
    )

    ax.set_ylim(1, 5)
    ax.set_ylabel("Mean Overall KSA Index")
    ax.set_xlabel("Stage")
    ax.set_title(
        "Overall KSA Scores Increased After Training and Remained Above Baseline Over Time",
        loc="left",
        fontsize=12,
        pad=10
    )

    # clean style
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # no top labels, only bottom x-axis labels
    ax.tick_params(axis="x", top=False, labeltop=False, bottom=True, labelbottom=True)

    # add n labels above bars
    for bar, (_, row) in zip(bars, summary.iterrows()):
        if pd.notna(row["mean"]):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                row["mean"] + 0.05,
                f"n={int(row['n'])}",
                ha="center",
                va="bottom",
                fontsize=9
            )

    fig_path = os.path.join(figures_dir, "figure_2_overall_ksa_index_trajectory.png")
    plt.tight_layout()
    plt.savefig(fig_path, dpi=300)
    plt.close()

    # --------------------------------------------------
    # Run summary
    # --------------------------------------------------
    print("\nSaved:")
    print(f"- {fig_path}")
    print(f"- {table_out}")
    print("\nStage counts used in index:")
    print(summary[["stage", "n"]].to_string(index=False))
    print("Done ✅")


if __name__ == "__main__":
    main()