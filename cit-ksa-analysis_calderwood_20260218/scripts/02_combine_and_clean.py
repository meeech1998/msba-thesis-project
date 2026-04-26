import pandas as pd

# --------------------------------------------------
# Step 1: Load each raw survey file
# I’m labeling each dataset with its timepoint
# so I can track where responses came from later
# --------------------------------------------------

paths = {
    "pre_post": "data/pre_post.xlsx",
    "m3_6": "data/m3_6.xlsx",
    "m12": "data/m12.xlsx",
}

dfs = []

for timepoint, path in paths.items():
    # Read each Excel file
    df = pd.read_excel(path)
    
    # Add a timepoint column so I can analyze stages later
    df["timepoint"] = timepoint
    
    dfs.append(df)

# --------------------------------------------------
# Step 2: Combine all timepoints into one dataset
# I’m stacking them vertically because they have
# the same structure but represent different stages
# --------------------------------------------------

combined = pd.concat(dfs, ignore_index=True)

# --------------------------------------------------
# Step 3: Clean column names
# I noticed earlier that some columns had hidden
# characters (\xa0) and trailing spaces, which
# would break column matching later.
# This function standardizes all column names.
# --------------------------------------------------

def clean_col(col):
    return str(col).strip().replace("\xa0", " ")

combined.columns = [clean_col(c) for c in combined.columns]

# --------------------------------------------------
# Step 4: Save the cleaned combined dataset
# This becomes the master file used for all
# downstream analysis scripts.
# --------------------------------------------------

combined.to_csv("output/combined_clean.csv", index=False)

print("\nCombined dataset saved to: output/combined_clean.csv")
print("Combined shape:", combined.shape)

print("\nCleaned columns:")
for c in combined.columns:
    print(repr(c))