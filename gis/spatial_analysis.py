"""GIS: Conflict KDE hotspots, incident clustering, animated timeline map."""
import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import Point
import folium
from folium.plugins import HeatMap, MarkerCluster
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from data.generate_data import generate_conflict_incidents, generate_state_security_index

EVENT_COLORS = {
    "Armed Clash": "red", "Attack on Civilians": "darkred",
    "Bombing/Explosion": "black", "Kidnapping/Abduction": "orange",
    "Armed Robbery": "orange", "Farmer-Herder Clash": "purple",
    "Protest/Riot": "blue", "Remote Violence": "darkred",
    "Strategic Development": "green",
}


def build_conflict_map(incidents_df: pd.DataFrame,
                        security_df: pd.DataFrame) -> folium.Map:
    m = folium.Map(location=[9.08, 8.67], zoom_start=6, tiles="CartoDB dark_matter")

    heat = [[r.lat, r.lon, r.fatalities + 1]
            for _, r in incidents_df[incidents_df["fatalities"] > 0].iterrows()]
    HeatMap(heat, radius=16, blur=14, min_opacity=0.35,
            gradient={"0.2": "yellow", "0.5": "orange", "1.0": "red"}).add_to(m)

    cluster = MarkerCluster(name="Incidents").add_to(m)
    for _, row in incidents_df.sample(min(400, len(incidents_df)), random_state=42).iterrows():
        color = EVENT_COLORS.get(row["event_type"], "gray")
        folium.CircleMarker(
            location=[row.lat, row.lon], radius=4,
            color=color, fill=True, fill_opacity=0.8,
            popup=(f"<b>{row['event_type']}</b><br>{row['state']}<br>"
                   f"Date: {str(row['date'])[:10]}<br>"
                   f"Fatalities: {row['fatalities']}<br>Actor: {row['actor1']}"),
        ).add_to(cluster)

    for _, row in security_df.iterrows():
        risk = row["security_index"]
        color = "#d32f2f" if risk > 0.65 else "#f57c00" if risk > 0.40 else "#388e3c"
        folium.CircleMarker(
            location=[row.lat, row.lon],
            radius=max(8, risk * 25),
            color=color, fill=True, fill_opacity=0.4,
            popup=(f"<b>{row['state']}</b><br>Security Index: {risk:.2f}<br>"
                   f"Incidents 2023: {row['incidents_2023']}<br>"
                   f"Ag Impact: {row['ag_impact_pct']}%"),
            tooltip=row["state"],
        ).add_to(m)

    folium.LayerControl().add_to(m)
    return m


if __name__ == "__main__":
    incidents = generate_conflict_incidents(500)
    security = generate_state_security_index()
    m = build_conflict_map(incidents, security)
    os.makedirs("app", exist_ok=True)
    m.save("app/conflict_map.html")
    print("Map saved.")
