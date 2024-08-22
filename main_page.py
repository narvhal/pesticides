import folium
import streamlit as st
from streamlit_folium import st_folium
import pandas as pd
import geopandas
import requests

# center on Liberty Bell, add marker
m = folium.Map(location=[39.949610, -75.150282], zoom_start=16)
folium.Marker(
    [39.949610, -75.150282], popup="Liberty Bell", tooltip="Liberty Bell"
).add_to(m)

# call to render Folium map in Streamlit
st_data = st_folium(m, width=725)



### geojson map like: https://folium.streamlit.app/geojson_popup, https://python-visualization.github.io/folium/latest/user_guide/geojson/geojson_popup_and_tooltip.html
#GeoJSON popup and tooltip
income = pd.read_csv(
    "https://raw.githubusercontent.com/pri-data/50-states/master/data/income-counties-states-national.csv",
    dtype={"fips": str})
income["income-2015"] = pd.to_numeric(income["income-2015"], errors="coerce")


data = requests.get(
    "https://raw.githubusercontent.com/python-visualization/folium-example-data/main/us_states.json"
).json()
states = geopandas.GeoDataFrame.from_features(data, crs="EPSG:4326")

states.head()
