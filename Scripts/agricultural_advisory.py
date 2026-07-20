import pandas as pd

# 1. Load your brand-new live meteorological dataset
input_file = "../Data/village_live_weather.csv"
df = pd.read_csv(input_file)

print(f"Analyzing climate data for {len(df)} villages to generate agricultural advisories...")

advisories = []

# 2. Loop through each village to generate intelligent context-aware advice
for index, row in df.iterrows():
    zone = row['CLIMATE_ZONE']
    frost = row['FROST_RISK']
    temp = row['CURRENT_TEMP_C']
    rain = row['CURRENT_RAIN_MM']
    
    # Check for empty or missing API data fields safely
    if pd.isna(temp):
        advisories.append("Advisory unavailable: Weather data stream offline.")
        continue
        
    # Logic Engine: Constructing custom farming recommendations dynamically
    advice = ""
    
    # Scenario A: Cold/Frost Alerts for High Elevation Zones
    if zone in ['Mountain', 'Highland'] and temp < 4:
        advice += "CRITICAL ALERT: Near-freezing temperatures detected. High risk of immediate frost damage. Shelter vulnerable high-altitude crops tonight. Delay any planned sensitive sowing."
    
    # Scenario B: Soil Moisture / Sowing Guidance based on current rain fields
    elif rain > 5:
        if zone in ['Valley', 'Foothill']:
            advice += "MOISTURE OPTIMAL: Significant recent rainfall detected in lower zone. High soil moisture content. Ideal window to begin or resume maize and sorghum sowing if trends persist."
        else:
            advice += "MOISTURE DETECTED: Rain present in upper terrain. Check soil warmth status before planting due to delayed seasonal heating in elevated zones."
            
    # Scenario C: Dry conditions / Conservative water usage guidelines
    else:
        if temp > 25:
            advice += "DRY/WARM WINDOW: High evaporation rates expected. Supplemental irrigation recommended for horticultural beds. Hold off on dry-land sowing until next rain cycle."
        else:
            advice += "STABLE/DRY CONDITIONS: Normal operational window. Safe for weeding and field clearing. Monitor moisture closely before attempting field propagation."
            
    advisories.append(advice)

# 3. Add our generated insights as a fresh column layer
df['AGRICULTURAL_ADVISORY'] = advisories

# 4. Save to your next production stage file
output_file = "../Data/village_climate_intelligence.csv"
df.to_csv(output_file, index=False)

print("\n=========================================================")
print("SUCCESS: Agricultural Intelligence Engine Completed!")
print(f"Saved advisory-enhanced database to: {output_file}")
print("=========================================================")
