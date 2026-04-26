"""
Horizontal Bar Chart — MLE Pre vs Post KSA Scores

Clean version:
- Pre (top bar), Post (bottom bar)
- No gridlines
- Color-coded title (Pre/Post)
- Left-aligned, presentation-ready
"""

from __future__ import annotations

import os
import pandas as pd
import matplotlib.pyplot as plt


def find_matching_num_col(columns: list[str], phrase: str) -> str:
    matches = [c for c in columns if c.endswith("_num") and phrase.lower() in c.lower()]
    if not matches:
        raise KeyError(f"No numeric column found containing phrase: {phrase}")
    return matches[0]


def main() -> None:
    # ---------------------------
    # Paths
    # ---------------------------
    input_path = "output/combined_numeric.csv"
    figures_dir = "output/figures"
    os.makedirs(figures_dir, exist_ok=True)

    df = pd.read_csv(input_path)

    # ---------------------------
    # Key columns
    # ---------------------------
    role_col = (
        "Which of the following most closely reflects your professional role at the time of the 8th Annual CIT Training Academy? Select one."
    )
    timepoint_col = "timepoint"
    when_col = "When are you taking this survey? Select one."

    # ---------------------------
    # Short labels
    # ---------------------------
    question_lookup = {
        "current knowledge of mental illness": "Mental Illness Knowledge",
        "community resources available": "Resource Awareness",
        "civil commitment laws": "Civil Commitment Knowledge",
        "professional liability considerations": "Liability Knowledge",
        "roles of various actors": "System Roles Familiarity",
        "well prepared do you feel": "Preparedness",
        "comfort level in appropriately engaging": "Comfort Level",
        "confidence in using de-escalation skills": "De-escalation Confidence",
    }

    matched_cols = []
    for phrase, short_label in question_lookup.items():
        col = find_matching_num_col(df.columns.tolist(), phrase)
        matched_cols.append((col, short_label))

    # ---------------------------
    # Filter data
    # ---------------------------
    mle_label = (
        "Missoula Law Enforcement (inclusive of City Police, Sheriff's Deputies, University of Montana Police, Probation and Parole, and Detention Officers)"
    )

    pre_label = "April 1, 2024"
    post_label = "April 5, 2024"

    mle = df[df[role_col] == mle_label]
    prepost = mle[mle[timepoint_col] == "pre_post"]

    pre = prepost[prepost[when_col] == pre_label]
    post = prepost[prepost[when_col] == post_label]

    # ---------------------------
    # Compute means
    # ---------------------------
    rows = []
    for col, label in matched_cols:
        rows.append({
            "label": label,
            "pre": pre[col].mean(),
            "post": post[col].mean(),
            "diff": post[col].mean() - pre[col].mean()
        })

    table = pd.DataFrame(rows)
    table = table.sort_values("diff", ascending=False)

    # ---------------------------
    # Plot
    # ---------------------------
    pre_color = "#4C78A8"
    post_color = "#F58518"

    y = list(range(len(table)))
    h = 0.35

    fig, ax = plt.subplots(figsize=(10.5, 7))

    # 🔥 FIXED ORDER:
    # PRE ON TOP, POST BELOW
    ax.barh(
        [i - h/2 for i in y],
        table["pre"],
        height=h,
        color=pre_color
    )

    ax.barh(
        [i + h/2 for i in y],
        table["post"],
        height=h,
        color=post_color
    )

    ax.set_yticks(y)
    ax.set_yticklabels(table["label"])

    ax.set_xlim(1, 5)
    ax.set_xlabel("Mean Score (1–5)")

    # ---------------------------
    # CLEAN TITLE (WITH COLOR)
    # ---------------------------
    ax.set_title("", loc="left")

    title_y = 1.04

    ax.text(0.00, title_y, "All KSA Categories Improved from ",
            transform=ax.transAxes, fontsize=13, fontweight="bold")

    ax.text(0.46, title_y, "Pre",
            transform=ax.transAxes, fontsize=13, fontweight="bold", color=pre_color)

    ax.text(0.50, title_y, " to ",
            transform=ax.transAxes, fontsize=13, fontweight="bold")

    ax.text(0.54, title_y, "Post",
            transform=ax.transAxes, fontsize=13, fontweight="bold", color=post_color)

    ax.text(0.61, title_y, " Training",
            transform=ax.transAxes, fontsize=13, fontweight="bold")

    # ---------------------------
    # CLEAN STYLE
    # ---------------------------
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # REMOVE GRIDLINES
    ax.grid(False)

    # ---------------------------
    # Save
    # ---------------------------
    output_path = os.path.join(figures_dir, "pre_vs_post_horizontal_bar.png")
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()

    print(f"\nSaved figure: {output_path}")
    print("Done ✅")


if __name__ == "__main__":
    main()