import pandas as pd

# Load file
df = pd.read_csv("../Data/village_climate.csv")

# Frost classification
def frost_risk(elevation):

    if elevation < 1800:
        return "Low"

    elif elevation < 2200:
        return "Moderate"

    else:
        return "High"

# Create column
df["FROST_RISK"] = df["RASTERVALU"].apply(frost_risk)

# Save file
df.to_csv("../Data/village_climate_profile.csv", index=False)

print("Frost risk added successfully!")