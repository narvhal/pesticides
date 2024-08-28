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


toc = stoc()

# Title
st.title("Stanislaus County Pesticide Use Reports and School Locations")


st.header("1. Select filters")




##########################
permittee, site_id, permit_num, permit_yr, loc_narr, is_active, size =load_standard_colnames()

df, fbs = prepare_df_from_stanag()

# if st.button("Show filter options"):
#     print_col_uniques(df)

selcol = "Appl. Method"
selcolval = "Aircraft"
# with st.popover("Select filter"):
#     for i,d in enumerate(df.columns.to_list()):
#         selcol = st.checkbox(str(d), key = "selcol_chkbox_" + str(i))
#     if selcol in df.columns.to_list():
#         scu = df[selcol].unique()
#         if len(scu)<100:
#             for j, scv in enumerate(scu):
#                 selcolval = st.checkbox(str(scv), key = "selcolval_chkbox_" + str(j))

# if selcol in df.columns.to_list():
#     if selcolval in df[selcol].unique():

dfn = filt_df(df, selcol, selcolval, type_compare="==")
add_geometry2(dfn, fbs)
# st.write("Filter applied!")
#################


st.header("2. Map")
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

du = dfn["Product Name"].unique()
ins = [c for c in du if "insect" in c.lower()]
herb = [c for c in du if "herbi" in c.lower()]
fung = [c for c in du if "fungi" in c.lower()]
other = [c for c in du if c not in ins + herb]
ccnames = ["Insecticides", "Herbicides", "Fungicides", "Other"]
ccl = [ins, herb, fung, other]
ccd1 = {c:ccnames[0] for c in ins}
ccd2 = {c:ccnames[1] for c in herb}
ccd3 = {c:ccnames[2] for c in fung}
ccd4 = {c:ccnames[3] for c in other}
ccd1.update(ccd2)
ccd1.update(ccd3)
ccd1.update(ccd4)

# ccd = {ccnames[i]:ccl[i] for i in ccnames}
dfc = None
colorcol = None


colorcol = "Product Name"
dfc = df.copy()
dfc["color_category"] = dfc[colorcol].map(ccd1)
# with st.popover("Select column to colorize map"):
#     st.write("PUR data: ")
#     for i, d in enumerate(ccnames):
#         colorcol = st.checkbox(d, key = "colorcol_chkbox1_" + str(i))
#         dfc = df.copy()
    # st.write("Field Bounds Data: ")
    # for i, d in enumerate(fbs.columns.to_list()):
    #     colorcol = st.checkbox(str(d), key = "colorcol_chkbox2_" + str(i))
    #     dfc = fbs.copy()
    # st.write("Private Schools Data: ")
    # for  i, d in enumerate(spriv.columns.to_list()):
    #     colorcol = st.checkbox(str(d), key = "colorcol_chkbox3_" + str(i))
    #     dfc = spriv.copy()
    # st.write("Public Schools Data: ")
    # for  i, d in enumerate(spub.columns.to_list()):
    #     colorcol = st.checkbox(str(d), key = "colorcol_chkbox4_" + str(i))
    #     dfc = spub.copy()



colorcol = "color_category"
colorcol_desc = "Aerial Application Product"
if dfc is not None:
    # if colorcol in dfc.columns.to_list():

    colormap = branca.colormap.StepColormap(
        # vmin=dfc[colorcol].quantile(0.0),
        # vmax=dfc[colorcol].quantile(1),
        colors=["red", "lightblue", "green", "yellow"],
        caption=colorcol_desc,
    )

    m = folium.Map(location=[35.3, -97.6], zoom_start=4)

    popup = folium.GeoJsonPopup(
        fields=["Site Location", colorcol],
        aliases=["Site Location", colorcol_desc],
        localize=True,
        labels=True,
        style="background-color: yellow;",
    )

    tooltip = folium.GeoJsonTooltip(
        fields=["Site Location", "Application Date", colorcol],
        aliases=["Site Location", "Application Date", colorcol_desc],
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
