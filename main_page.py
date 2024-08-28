import folium
import streamlit as st
from streamlit_folium import st_folium
import pandas as pd
import geopandas as gpd
import requests
import branca
import numpy as np
import matplotlib.pyplot as plt
import unidecode
from py_functions.pyfuncs_data_load import *
import fiona

st.set_page_config(layout="wide" )


permittee, site_id, permit_num, permit_yr, loc_narr, is_active, size =load_standard_colnames()
##########################

df, fbs = prepare_df_from_stanag()

# if st.button("Show filter options"):
#     print_col_uniques(df)

selcol = st.empty()
selcolval = st.empty()
with st.popover("Select filter"):
    for i,d in enumerate(df.columns.to_list()):
        selcol = st.checkbox(str(d), key = "selcol_chkbox_" + str(i))
    if selcol in df.columns.to_list():
        scu = df[selcol].unique()
        if len(scu)<100:
            for j, scv in enumerate(scu):
                selcolval = st.checkbox(str(scv), key = "selcolval_chkbox_" + str(j))

if selcol in df.columns.to_list():
    if selcolval in df[selcol].unique():
        dfn = filt_df(df, selcol, selcolval, type_compare="==")
        add_geometry2(dfn, fbs)

#################
toc = stoc()

# Title
st.title("Stanislaus County Pesticide Use Reports and School Locations")


st.header("1. Select filters")
# center on Liberty Bell, add marker
m = folium.Map(location=[37.5, -120.8], zoom_start=5)

#folium.Marker(
#    [39.949610, -75.150282], popup="Liberty Bell", tooltip="Liberty Bell"
#).add_to(m)

# call to render Folium map in Streamlit



# ### geojson map like: https://folium.streamlit.app/geojson_popup, https://python-visualization.github.io/folium/latest/user_guide/geojson/geojson_popup_and_tooltip.html
# #GeoJSON popup and tooltip
# data = ".\pesticides\data_sources\AgComm_Stanislaus\merged_pur_sites_fieldbds.shp"
# pur = geopandas.GeoDataFrame.from_file(data, crs="EPSG:3310")

dfc = None
colorcol = None
with st.popover("Select column to colorize map"):
    st.write("PUR data: ")
    for d in df.columns.to_list():
        colorcol = st.checkbox(str(d))
        dfc = df.copy()
    st.write("Field Bounds Data: ")
    for d in fbs.columns.to_list():
        colorcol = st.checkbox(str(d))
        dfc = fbs.copy()
    st.write("Private Schools Data: ")
    for d in spriv.columns.to_list():
        colorcol = st.checkbox(str(d))
        dfc = spriv.copy()
    st.write("Public Schools Data: ")
    for d in spub.columns.to_list():
        colorcol = st.checkbox(str(d))
        dfc = spub.copy()




colorcol_desc = "description"
if dfc is not None:


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
        dfc,
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
