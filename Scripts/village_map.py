import pandas as pd
import folium

# 1. Load the data
df = pd.read_csv("../Data/village_list.csv")

print("Generating color-coded climate map...")

# 2. Initialize the map
lesotho_map = folium.Map(location=[-28.7, 28.2], zoom_start=10)

# 3. Create a helper function to decide marker color based on RASTERVALU
def get_marker_color(val):
    if val < 1630:
        return 'green'
    elif 1630 <= val <= 1670:
        return 'orange'
    else:
        return 'red'

# 4. Loop through the rows to add custom colored markers
for index, row in df.iterrows():
    # Call our function to get the right color for this specific row
    village_color = get_marker_color(row['RASTERVALU'])
    
    folium.Marker(
        location=[row['Y_COORD'], row['X_COORD']],
        popup=f"<b>Village:</b> {row['NAME']}<br><b>District:</b> {row['DISTRICT']}<br><b>Raster Value:</b> {row['RASTERVALU']}",
        tooltip=row['NAME'],
        # Set the dynamic color here
        icon=folium.Icon(color=village_color, icon='info-sign')
    ).add_to(lesotho_map)

# 5. Save the updated map
lesotho_map.save("village_map.html")

print("Success! Refresh your web browser page to see the new color-coded map.")
