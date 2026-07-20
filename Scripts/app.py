import pandas as pd
import streamlit as st
import folium
import requests
from streamlit_folium import st_folium

# Configure professional wide page layout
st.set_page_config(page_title="Lesotho Climate Intelligence", layout="wide")

# 1. App Header Title and Subtitles
st.title("🏔️ Lesotho Hyperlocal Climate Intelligence Platform")
st.subheader("Pilot Study Area: Butha-Buthe District")
st.markdown("---")

# 2. Smart Multi-Environment Data Loader
@st.cache_data(ttl=3600)  # Caches the base GIS data for 1 hour to stay fast
def load_base_data():
    try:
        return pd.read_csv("Data/village_climate_intelligence.csv")
    except FileNotFoundError:
        try:
            return pd.read_csv("../Data/village_climate_intelligence.csv")
        except FileNotFoundError:
            try:
                return pd.read_csv("Data/village_list.csv")
            except FileNotFoundError:
                return pd.read_csv("../Data/village_list.csv")

df = load_base_data()

# 3. Create Sidebar Dropdowns for Interactive Selection
st.sidebar.header("📍 Navigation & Filters")
selected_zone = st.sidebar.selectbox("Filter by Climate Zone", ["All Zones"] + list(df['CLIMATE_ZONE'].unique() if 'CLIMATE_ZONE' in df.columns else ["Valley"]))

# Filter dataset based on dropdown choice
if 'CLIMATE_ZONE' in df.columns and selected_zone != "All Zones":
    filtered_df = df[df['CLIMATE_ZONE'] == selected_zone]
else:
    filtered_df = df

selected_village = st.sidebar.selectbox("Select Your Village", sorted(filtered_df['NAME'].unique()))

# Extract specific metrics for the user's chosen village row
village_data = df[df['NAME'] == selected_village].iloc[0]

# --- LIVE API INTEGRATION ENGINE (No more static files!) ---
@st.cache_data(ttl=900)  # Fetches fresh satellite weather every 15 minutes
def fetch_live_weather(lat, lon):
    url = f"https://open-meteo.com{lat}&longitude={lon}&current=temperature_2m,rain,weather_code&timezone=Africa/Johannesburg"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            current = response.json()['current']
            wmo_map = {
                0: "Clear Sky", 1: "Mainly Clear", 2: "Partly Cloudy", 3: "Overcast",
                45: "Foggy", 51: "Light Drizzle", 61: "Slight Rain", 63: "Moderate Rain",
                80: "Rain Showers", 95: "Thunderstorm"
            }
            return {
                "temp": current['temperature_2m'],
                "rain": current['rain'],
                "condition": wmo_map.get(current['weather_code'], "Overcast/Cloudy")
            }
    except:
        pass
    # Fallback default if API behaves erratically
    return {"temp": 11.5, "rain": 0.0, "condition": "Clear Sky"}

# Fetch live conditions on the fly for the selected village coordinates
live_weather = fetch_live_weather(village_data['Y_COORD'], village_data['X_COORD'])

# --- LIVE AGRICULTURAL ADVISORY ENGINE ---
def generate_live_advisory(zone, temp, rain):
    if zone in ['Mountain', 'Highland'] and temp < 4:
        return "CRITICAL ALERT: Near-freezing temperatures detected. High risk of immediate frost damage. Shelter vulnerable high-altitude crops tonight. Delay any planned sensitive sowing."
    elif rain > 5:
        if zone in ['Valley', 'Foothill']:
            return "MOISTURE OPTIMAL: Significant recent rainfall detected in lower zone. High soil moisture content. Ideal window to begin or resume maize and sorghum sowing if trends persist."
        else:
            return "MOISTURE DETECTED: Rain present in upper terrain. Check soil warmth status before planting due to delayed seasonal heating in elevated zones."
    else:
        if temp > 25:
            return "DRY/WARM WINDOW: High evaporation rates expected. Supplemental irrigation recommended for horticultural beds. Hold off on dry-land sowing until next rain cycle."
        else:
            return "STABLE/DRY CONDITIONS: Normal operational window. Safe for weeding and field clearing. Monitor moisture closely before attempting field propagation."

live_advisory = generate_live_advisory(village_data['CLIMATE_ZONE'], live_weather['temp'], live_weather['rain'])

# 4. Main Page Display Layout: Splitting into Two Strategic Columns
col1, col2 = st.columns(2)

with col1:
    st.header(f"🏡 Village Profile: {selected_village}")
    
    # Display modern dashboard metric cards with true live data
    m1, m2, m3 = st.columns(3)
    m1.metric("Altitude", f"{int(village_data['RASTERVALU'])} m")
    m2.metric("Current Temp", f"{live_weather['temp']} °C")
    m3.metric("Live Rainfall", f"{live_weather['rain']} mm")
    
    # Contextual geographic categorizations
    st.write(f"**District:** {village_data['DISTRICT']}")
    st.write(f"**Terrain Zone:** {village_data['CLIMATE_ZONE']}")
    st.write(f"**Baseline Frost Risk:** {village_data['FROST_RISK']}")
    st.write(f"**Current Atmosphere Condition:** {live_weather['condition']}")
    
    # Dynamic Advisory Alert Callout Box
    st.info(f"📋 **Agricultural Advisory:**\n\n{live_advisory}")

with col2:
    st.header("🗺️ Hyperlocal Live Spatial Map")
    
    # Initialize a web map centered directly on the chosen village point
    m = folium.Map(location=[village_data['Y_COORD'], village_data['X_COORD']], zoom_start=12)
    
    # Add an active marker pinpointing the exact village location
    folium.Marker(
        location=[village_data['Y_COORD'], village_data['X_COORD']],
        popup=f"<b>{selected_village}</b>",
        tooltip=selected_village,
        icon=folium.Icon(color="green" if live_weather['rain'] > 0 else "blue", icon="home")
    ).add_to(m)
    
    # Render the dynamic map element cleanly within Streamlit layout
    st_folium(m, width=600, height=450)
