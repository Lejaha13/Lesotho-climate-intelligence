import pandas as pd

# Load your processed dataset
df = pd.read_csv("../Data/village_climate_profile.csv")

# Function to estimate rainfall potential
def rainfall_potential(zone):

    if zone == "Valley":
        return "Moderate"

    elif zone == "Foothill":
        return "Good"

    elif zone == "Highland":
        return "Very Good"

    elif zone == "Mountain":
        return "Excellent"

    else:
        return "Unknown"

# Apply model
df["RAINFALL_POTENTIAL"] = df["CLIMATE_ZONE"].apply(rainfall_potential)

# Save output
df.to_csv("../Data/village_climate_intelligence.csv", index=False)

print("Rainfall potential added successfully!")