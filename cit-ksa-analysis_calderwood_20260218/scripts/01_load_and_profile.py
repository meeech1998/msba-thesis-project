import pandas as pd

# Step 1: Define where each raw survey file lives inside my data folder
# I’m using a dictionary so I can loop through them cleanly
paths = {
    "pre_post": "data/pre_post.xlsx",
    "m3_6": "data/m3_6.xlsx",
    "m12": "data/m12.xlsx",
}

# Step 2: Loop through each dataset to inspect structure before combining anything
# At this stage, I just want to understand shape and column names
for name, path in paths.items():
    print("\n" + "=" * 90)
    print(f"Loading: {name}")
    
    # Read the Excel file into a DataFrame
    df = pd.read_excel(path)
    
    # Print the number of rows and columns so I understand sample size and structure
    print(f"Shape: {df.shape}")
    
    # Print exact column names (using repr to catch hidden characters like \xa0)
    # This helps me detect formatting inconsistencies before cleaning
    print("\nColumns:")
    for col in df.columns:
        print(repr(col))