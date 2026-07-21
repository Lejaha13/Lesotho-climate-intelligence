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

# 2. Base Data Loader
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

if 'CLIMATE_ZONE' in df.columns and selected_zone != "All Zones":
    filtered_df = df[df['CLIMATE_ZONE'] == selected_zone]
else:
    filtered_df = df

selected_village = st.sidebar.selectbox("Select Your Village", sorted(filtered_df['NAME'].unique()))

# Extract specific metrics for the user's chosen village row safely using explicit row indexing
village_data = df[df['NAME'] == selected_village].iloc[0]

# --- GEOGRAPHIC TERRAIN ANALYSIS MODELING (OROGRAPHIC RAINFALL POTENTIAL) ---
altitude = int(village_data['RASTERVALU'])
zone_str = str(village_data['CLIMATE_ZONE'])

if altitude < 1800:
    orographic_potential, potential_badge, potential_desc = "Moderate", "🟢", "Rain shadow valley dynamics. Standard precipitation capture baseline."
elif 1800 <= altitude < 2000:
    orographic_potential, potential_badge, potential_desc = "Good", "🔵", "Foothill transition zone. Increased condensation likelihood via minor wind upward thrust."
elif 2000 <= altitude < 2200:
    orographic_potential, potential_badge, potential_desc = "Very Good", "🟣", "Highland zone. Enhanced cloud development zone due to consistent cool air cooling limits."
else:
    orographic_potential, potential_badge, potential_desc = "Excellent", "🔥", "Mountain peaks. Maximized orographic lifecycles. Dominant local watershed rain generation zone."

# --- ADVANCED LIVE API SATELLITE ENGINE WITH MULTI-DAY FORECAST & SMART CACHING ---
@st.cache_data(ttl=600)  # Caches for 10 minutes to maintain speed and avoid rate-limits
def fetch_comprehensive_weather(lat, lon):
    # FIXED: correct Open-Meteo API endpoint (was pointing at the marketing
    # homepage "open-meteo.com" which returns HTML, not JSON -> caused the
    # "Expecting value: line 1 column 1 (char 0)" JSON decode error)
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}"
        f"&current=temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,weather_code"
        f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,rain_sum"
        f"&timezone=Africa/Johannesburg"
    )
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            current = data['current']
            daily = data['daily']

            wmo_map = {
                0: "☀️ Clear Sky", 1: "🌤️ Mainly Clear", 2: "⛅ Partly Cloudy", 3: "☁️ Overcast",
                45: "🌫️ Foggy", 51: "🌧️ Light Drizzle", 61: "🌧️ Slight Rain", 63: "🌧️ Moderate Rain",
                80: "🌦️ Rain Showers", 95: "⚡ Thunderstorm"
            }
            return {
                "success": True,
                "temp": float(current['temperature_2m']),
                "humidity": float(current['relative_humidity_2m']),
                "wind": float(current['wind_speed_10m']),
                "rain": float(current['precipitation']),
                "condition": wmo_map.get(current['weather_code'], "☁️ Overcast/Cloudy"),
                "forecast_days": daily['time'],
                "forecast_max_temps": [float(x) for x in daily['temperature_2m_max']],
                "forecast_min_temps": [float(x) for x in daily['temperature_2m_min']],
                "forecast_rain": [float(x) for x in daily['precipitation_sum']]
            }
        else:
            st.sidebar.error(f"API Connection Diagnostic: HTTP {response.status_code}")
    except Exception as e:
        st.sidebar.error(f"API Connection Diagnostic: {e}")

    # Fallback default data (used only if the live API call fails)
    return {
        "success": False,
        "temp": 5.8,
        "humidity": 65.0,
        "wind": 4.2,
        "rain": 0.0,
        "condition": "❄️ Winter Air Normal",
        "forecast_days": ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5", "Day 6", "Day 7"],
        "forecast_max_temps": [10.0, 11.0, 12.0, 13.0, 12.0, 11.0, 10.0],
        "forecast_min_temps": [-2, -1, -3, -2, 0, -1, -2],
        "forecast_rain": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    }

# Execute live calculation loops
weather = fetch_comprehensive_weather(village_data['Y_COORD'], village_data['X_COORD'])

if not weather.get("success", False):
    st.sidebar.warning("⚠️ Showing fallback weather data — live API call failed. Check the diagnostic message above.")

# --- RE-ENGINEERED MULTI-VARIABLE PREDICTIVE AGRICULTURAL ADVISORY ---
def generate_predictive_advisory(zone, current_temp, forecast_data):
    total_7day_rain = sum(forecast_data['forecast_rain'])
    lowest_forecast_min = min(forecast_data['forecast_min_temps'])

    advice = ""
    # Advanced Frost Warning Integration
    if lowest_forecast_min <= 0:
        if zone in ['Mountain', 'Highland']:
            advice += f"⚠️ **CRITICAL FROST HAZARD:** Weekly minimums will drop to {lowest_forecast_min}°C in this upper elevation zone. Severe black frost risk active. Conditions currently unsuitable for sensitive crops.\n\n"
        else:
            advice += f"❄️ **VALLEY FROST INVERSION ALERT:** Thermal radiation cooling will pull valley floor minimums down to {lowest_forecast_min}°C. Ground frost pockets expected across low vegetation zones.\n\n"

    # Cross-matching Terrain Zones with Forecast Precipitation Limits
    if total_7day_rain > 30:
        if zone in ['Mountain', 'Highland']:
            advice += f"🌊 **OROGRAPHIC RUN-OFF WARNING:** High cumulative total ({total_7day_rain} mm) over steep mountain slopes increases soil wash risks. Conditions highly unfavorable for open tilling operations."
        else:
            advice += f"🌱 **CONDITIONS HIGHLY FAVOURABLE FOR CROP ESTABLISHMENT:** Total forecast rainfall ({total_7day_rain} mm) combines with warm valley soils to create an optimal forthcoming moisture window."
    elif total_7day_rain > 5:
        advice += f"🌾 **MODERATE RECEPTIVITY PROFILE:** Minor rainfall tracking ({total_7day_rain} mm) will support base moisture. Safe for land preparation, targeted weeding, and organic layering."
    else:
        if zone in ['Mountain', 'Highland']:
            advice += "🚜 **DRY SEEDBED CONSTRAINT:** Deficit rainfall expected over high terrain. Soil structures remain cold and dry. Conditions currently unsuitable for early propagation; prioritize compost management."
        else:
            advice += "☀️ **STABLE DRY OPERATIONAL WINDOW:** Valley floor will remain dry over the next 7 days. Soil conditions are highly suitable for active turning, field clearance, and harvesting root crops."

    return advice

live_advisory = generate_predictive_advisory(zone_str, weather['temp'], weather)

# 4. Main Page Display Layout: Splitting into Two Strategic Columns
col1, col2 = st.columns(2)

with col1:
    st.header(f"🏡 Village Climate Profile: {selected_village}")

    # Modernized Variable Dashboard Metric Cards
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Altitude", f"{altitude} m")
    m2.metric("Temperature", f"{weather['temp']} °C")
    m3.metric("Humidity", f"{int(weather['humidity'])} %")
    m4.metric("Wind Speed", f"{weather['wind']} km/h")

    st.write(f"**Administrative District:** {village_data['DISTRICT']}")
    st.write(f"**Baseline Terrain Classification:** {zone_str} Zone")
    st.write(f"**Baseline Historical Frost Risk:** {village_data['FROST_RISK']}")
    st.write(f"**Current Weather:** {weather['condition']}")
    st.write(f"**Current Direct Precipitation:** {weather['rain']} mm")

    st.markdown("---")
    # Terrain Innovation Parameter Box
    st.subheader("💡 Terrain Modeling Matrix")
    st.write(f"**Orographic Rainfall Potential:** {potential_badge} **{orographic_potential}**")
    st.caption(f"*Model Insight:* {potential_desc}")
    st.markdown("---")

    # Dynamic Multi-Day Advisory Alert Callout Box
    st.info(f"📋 **7-Day Agronomic Predictive Decision Advisory:**\n\n{live_advisory}")

with col2:
    st.header("🗺️ Hyperlocal Live Spatial Map")
    m = folium.Map(location=[village_data['Y_COORD'], village_data['X_COORD']], zoom_start=12)
    folium.Marker(
        location=[village_data['Y_COORD'], village_data['X_COORD']],
        popup=f"<b>{selected_village}</b>",
        tooltip=selected_village,
        icon=folium.Icon(color="green" if weather['rain'] > 0 else "blue", icon="home")
    ).add_to(m)
    st_folium(m, width=600, height=400)

    st.markdown("---")
    # 7-DAY FORECAST METRIC HORIZON DATA TABLE
    st.subheader("📅 7-Day Hyperlocal Predictive Outlook Horizon")
    forecast_df = pd.DataFrame({
        "Date/Day": weather['forecast_days'],
        "Max Temp (°C)": weather['forecast_max_temps'],
        "Min Temp (°C)": weather['forecast_min_temps'],
        "Expected Rain (mm)": weather['forecast_rain']
    })
    st.dataframe(forecast_df, use_container_width=True, hide_index=True)