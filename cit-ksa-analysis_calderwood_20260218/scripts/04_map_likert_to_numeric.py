import pandas as pd

# -------------------------------------------------------------------
# STEP 4: Convert Likert responses to numeric values
# Input:  output/combined_clean.csv
# Output: output/combined_numeric.csv
#
# In this step, I standardize all KSA survey responses so I can run
# statistical tests. Likert text responses must be converted into
# numeric form before computing means, t-tests, ANOVA, etc.
# -------------------------------------------------------------------

df = pd.read_csv("output/combined_clean.csv")

# -------------------------------------------------------------------
# Identify which columns contain Likert-style KSA questions.
# I search by keyword rather than hard-coding column names so the
# script stays flexible and reproducible.
# -------------------------------------------------------------------

LIKERT_KEYWORDS = [
    "How comfortable",
    "How aware",
    "How knowledgeable",
    "How familiar",
    "How well prepared",
    "How would you rate",
]

likert_cols = [
    col for col in df.columns
    if any(keyword in col for keyword in LIKERT_KEYWORDS)
]

print("\n" + "=" * 90)
print("LIKERT COLUMNS FOUND:", len(likert_cols))
for col in likert_cols:
    print("-", col)

# -------------------------------------------------------------------
# Clean text formatting
# I remove trailing spaces and normalize text so that mapping works
# consistently. This prevents subtle string mismatches.
# -------------------------------------------------------------------

def clean_text(x):
    if pd.isna(x):
        return x
    return str(x).strip()

for col in likert_cols:
    df[col] = df[col].apply(clean_text)

# -------------------------------------------------------------------
# Define full ordinal mapping based on the official survey forms.
# I verified these anchors against the PDFs to ensure consistency.
#
# Scale interpretation:
# 1 = lowest perceived competence
# 5 = highest perceived competence
# -------------------------------------------------------------------

mapping = {

    # Knowledge / Awareness / Familiarity / Comfort
    "Not at all comfortable": 1,
    "Not aware": 1,
    "Not at all knowledgeable": 1,
    "Not at all familiar": 1,

    "A little comfortable": 2,
    "A little aware": 2,
    "A little knowledgeable": 2,
    "A little familiar": 2,

    "Comfortable": 3,
    "Aware": 3,
    "Knowledgeable": 3,
    "Familiar": 3,

    "Very comfortable": 4,
    "Very aware": 4,
    "Very knowledgeable": 4,
    "Very familiar": 4,

    "Expert": 5,

    # Preparedness scale
    "Not at all prepared": 1,
    "Somewhat prepared": 2,
    "Moderately prepared": 3,
    "Very prepared": 4,

    # Engagement comfort scale
    "Somewhat comfortable": 2,
    "Moderately comfortable": 3,

    # Confidence scale
    "Not at all confident": 1,
    "Somewhat confident": 2,
    "Moderately confident": 3,
    "Very confident": 4,
}

# -------------------------------------------------------------------
# Apply mapping to each Likert column
# I create new numeric columns instead of overwriting originals.
# This preserves raw data and improves transparency.
# -------------------------------------------------------------------

numeric_cols = []

for col in likert_cols:
    new_col = f"{col}_num"
    df[new_col] = df[col].map(mapping)
    numeric_cols.append(new_col)

# -------------------------------------------------------------------
# Validate that every non-null response was mapped.
# If anything appears unmapped, I print it so I can fix the dictionary.
# -------------------------------------------------------------------

print("\n" + "=" * 90)
print("UNMAPPED VALUES CHECK")

any_unmapped = False

for col in likert_cols:
    new_col = f"{col}_num"
    unmapped = df.loc[df[new_col].isna() & df[col].notna(), col].unique()

    if len(unmapped) > 0:
        any_unmapped = True
        print(f"\nUnmapped in: {col}")
        for val in unmapped:
            print(" -", repr(val))

if not any_unmapped:
    print("✅ No unmapped values. Mapping is clean.")

# -------------------------------------------------------------------
# Save the numeric-ready dataset
# This becomes the analytical dataset used in all inferential scripts.
# -------------------------------------------------------------------

df.to_csv("output/combined_numeric.csv", index=False)

print("\n" + "=" * 90)
print("Saved: output/combined_numeric.csv")
print("Numeric columns created:", len(numeric_cols))