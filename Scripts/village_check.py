import pandas as pd

# Read village data
df = pd.read_csv(r"C:\Users\User\Documents\LESOTHO_CLIMATE_DASHBOARD\Data\village_list.csv")

print("Data loaded successfully!")

print("\nNumber of villages:")
print(len(df))

print("\nColumn names:")
print(df.columns)

print("\nFirst 5 villages:")
print(df.head())