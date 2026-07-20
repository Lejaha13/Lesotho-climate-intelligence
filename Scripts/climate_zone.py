import pandas as pd

# Load village data
df = pd.read_csv("../Data/village_list.csv")

# Function to classify villages
def classify_zone(elevation):

    if elevation < 1800:
        return "Valley"

    elif elevation < 2000:
        return "Foothill"

    elif elevation < 2200:
        return "Highland"

    else:
        return "Mountain"

# Create new column
df["CLIMATE_ZONE"] = df["RASTERVALU"].apply(classify_zone)

# Save updated file
df.to_csv("../Data/village_climate.csv", index=False)

print("Climate zones created successfully!")