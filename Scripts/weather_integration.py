import pandas as pd
import requests
import time

# 1. Load the most advanced dataset you've produced so far
input_file = "../Data/village_climate_intelligence.csv"
try:
    df = pd.read_csv(input_file)
except FileNotFoundError:
    df = pd.read_csv("../Data/village_list.csv")

print(f"Loaded {len(df)} villages. Connecting to Open-Meteo Weather API...")

# 2. Lists to store our live meteorological metrics
current_temps = []
current_rain = []
weather_descriptions = []

# Simplified, bulletproof code dictionary (No syntax errors possible)
def interpret_wmo_code(code):
    wmo_map = {
        0: "Clear Sky",
        1: "Mainly Clear", 2: "Partly Cloudy", 3: "Overcast",
        45: "Foggy", 48: "Depositing Rime Fog",
        51: "Light Drizzle", 53: "Moderate Drizzle", 55: "Dense Drizzle",
        61: "Slight Rain", 63: "Moderate Rain", 65: "Heavy Rain",
        71: "Slight Snow", 73: "Moderate Snow", 75: "Heavy Snow",
        80: "Slight Rain Showers", 81: "Moderate Rain Showers", 82: "Violent Rain Showers",
        95: "Thunderstorm", 96: "Thunderstorm with Hail", 99: "Thunderstorm with Heavy Hail"
    }
    # Return translated code text, or default to generic Cloudy/Overcast if not found
    return wmo_map.get(code, "Overcast/Cloudy")

# 3. Loop through each village and fetch its exact real-time weather
for index, row in df.iterrows():
    lat = row['Y_COORD']
    lon = row['X_COORD']
    name = row['NAME']
    
    # Construct the API request URL for current conditions
    url = f"https://open-meteo.com{lat}&longitude={lon}&current=temperature_2m,rain,weather_code&timezone=Africa/Johannesburg"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            current_data = data['current']
            
            temp = current_data['temperature_2m']
            rain = current_data['rain']
            wmo_code = current_data['weather_code']
            condition = interpret_wmo_code(wmo_code)
            
            current_temps.append(temp)
            current_rain.append(rain)
            weather_descriptions.append(condition)
            
            print(f"[{index + 1}/{len(df)}] Fetched {name}: {temp}°C, {condition}")
        else:
            current_temps.append(None)
            current_rain.append(None)
            weather_descriptions.append("API Error")
            print(f"[{index + 1}/{len(df)}] Failed to fetch data for {name}")
            
    except Exception as e:
        current_temps.append(None)
        current_rain.append(None)
        weather_descriptions.append("Connection Error")
        print(f"Error connecting for {name}: {e}")
    
    # Respectful API pacing delay (prevents rate-limiting)
    time.sleep(0.1)

# 4. Append live data back to our data framework
df['CURRENT_TEMP_C'] = current_temps
df['CURRENT_RAIN_MM'] = current_rain
df['CURRENT_CONDITION'] = weather_descriptions

# 5. Save out both database stages so they are perfectly mirrored
df.to_csv("../Data/village_live_weather.csv", index=False)
df.to_csv("../Data/village_climate_intelligence.csv", index=False)

print("\n=========================================================")
print(f"SUCCESS! Live weather merged into database.")
print("=========================================================")
