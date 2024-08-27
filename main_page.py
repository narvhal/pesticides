import folium
import streamlit as st
from streamlit_folium import st_folium
import pandas as pd
import geopandas
import requests
import branca

# center on Liberty Bell, add marker
m = folium.Map(location=[37.5, -120.8], zoom_start=5)

#folium.Marker(
#    [39.949610, -75.150282], popup="Liberty Bell", tooltip="Liberty Bell"
#).add_to(m)

# call to render Folium map in Streamlit



### geojson map like: https://folium.streamlit.app/geojson_popup, https://python-visualization.github.io/folium/latest/user_guide/geojson/geojson_popup_and_tooltip.html
#GeoJSON popup and tooltip
data = ".\pesticides\data_sources\AgComm_Stanislaus\merged_pur_sites_fieldbds.shp"
pur = geopandas.GeoDataFrame.from_file(data, crs="EPSG:3310")

fpsch = r".\pesticides\data_sources\CA_Dept_Education"
schl_priv = r"\California_Private_Schools.geojson"
schl_pub = r"\SchoolSites2324_1647203305444761460.geojson"

spriv = geopandas.read_file(fpsch+schl_priv)
st_data = st_folium(m, width=725)
spub = geopandas.read_file(fpsch+schl_pub)



colorcol = 'Quantity Used'
colorcol_desc = "description"

colormap = branca.colormap.LinearColormap(
    vmin=pur[colorcol].quantile(0.0),
    vmax=pur[colorcol].quantile(1),
    colors=["red", "orange", "lightblue", "green", "darkgreen"],
    caption=colorcol_desc,
)

m = folium.Map(location=[35.3, -97.6], zoom_start=4)

popup = folium.GeoJsonPopup(
    fields=["name", colorcol],
    aliases=["State", "% Change"],
    localize=True,
    labels=True,
    style="background-color: yellow;",
)

tooltip = folium.GeoJsonTooltip(
    fields=["name", "medianincome", colorcol],
    aliases=["State:", "2015 Median Income(USD):", "Median % Change:"],
    localize=True,
    sticky=False,
    labels=True,
    style="""
        background-color: #F0EFEF;
        border: 2px solid black;
        border-radius: 3px;
        box-shadow: 3px;
    """,
    max_width=800,
)


g = folium.GeoJson(
    pur,
    style_function=lambda x: {
        "fillColor": colormap(x["properties"][colorcol])
        if x["properties"][colorcol] is not None
        else "transparent",
        "color": "black",
        "fillOpacity": 0.4,
    },
    tooltip=tooltip,
    popup=popup,
).add_to(m)

colormap.add_to(m)
