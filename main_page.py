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
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
from matplotlib_scalebar.scalebar import ScaleBar
import pyarrow as pa
st.set_page_config(layout="wide" )


# toc = stoc()

# Title
st.title("Pesticide Use Reports and School Locations")
st.header("Stanislaus County")

# st.header("1. Select filters")




##########################
permittee, site_id, permit_num, permit_yr, loc_narr, is_active, size =load_standard_colnames()

df, fbs = prepare_df_from_stanag()

# st.write(df.columns.to_list())
# if st.button("Show filter options"):
#     print_col_uniques(df)
#################################

# def get_new_values_list():
#     st.write(st.session_state[key])

st_list = ["Chemical Type", "Product Name"]
lc,mc, rc = st.columns([0.3,0.3, 0.3])

# Data vis options:
with lc:
    selection_type = st.radio("Select Way to Filter Pesticide Use Reports", st_list, key='sel pn or ct')

flag_keep_going= False
catcol = "color_category"

if selection_type == "Chemical Type":

    ccnames = ["Insecticides", "Herbicides", "Fungicides", "Other"]
    ccc = ["red", "lightblue", "olive", "yellow"]
    cni = range(4)
    cndd = {ccnames[i]:cni[i] for i in range(len(ccnames))}
    key = "multisel_products"
    with mc:
        def get_new_values_list():
            st.session_state["multisel_products"]
        cname = st.multiselect("Select Products", ccnames,default = ccnames[0], on_change = get_new_values_list, key = key )

    colorcol = "Product Name"

    du = df["Product Name"].unique()
    ins = [c for c in du if "insect" in c.lower()]
    du = list(set(du)-set(ins))
    herb = [c for c in du if "herbi" in c.lower()]
    du = list(set(du)-set(herb))
    fung = [c for c in du if "fungi" in c.lower()]
    other = list(set(du)-set(fung))
    ccl = [ins, herb, fung, other]
    ccd1 = {c:ccnames[0] for c in ins}
    ccd2 = {c:ccnames[1] for c in herb}
    ccd3 = {c:ccnames[2] for c in fung}
    ccd4 = {c:ccnames[3] for c in other}
    ccdd = [ccd1, ccd2, ccd3, ccd4]
    cccddd = {}
    for cn in cname:
        ix = cndd[cn]
        cccddd.update(ccdd[ix])
        ccd2 = {ccnames[ix]:ccc[ix] for i in range(len(cname))}

    if st.checkbox("Done selecting", key='done selecting by type'):

        dfc = df[df["Product Name"].isin(list(cccddd.keys()))].copy()
        flag_keep_going= True
        catcol = "color_category"
        dfc["color_category"] = dfc[colorcol].map(ccd1)
        dfc["color"] = dfc[colorcol].map(ccd2)
    # Determing colors
elif selection_type == "Product Name":
    maxsel = 5
    key = "multisel_products2"
    with mc:
        def get_new_values_list2():
            st.session_state["multisel_products2"]

        cname = st.multiselect(f"Select up to {maxsel} Products", df["Product Name"].unique(), max_selections = maxsel, on_change = get_new_values_list2, key = key)
    if st.checkbox("Done selecting", key='done selecting pn'):
        dfc = df[df["Product Name"].isin(cname)].copy()

        ccc = ["red", "lightblue", "olive", "yellow", "orange"]
        ccd2 = {cname[i]:ccc[i] for i in range(maxsel)}
        catcol = 'Product Name'
        flag_keep_going= True


#####################################1111111

# if st.button("Only Aircraft-delivered Products"):
#     selcol = "Appl. Method"
#     selcolval = "Aircraft"
#     # with st.popover("Select filter"):
#     #     for i,d in enumerate(df.columns.to_list()):
#     #         selcol = st.checkbox(str(d), key = "selcol_chkbox_" + str(i))
#     #     if selcol in df.columns.to_list():
#     #         scu = df[selcol].unique()
#     #         if len(scu)<100:
#     #             for j, scv in enumerate(scu):
#     #                 selcolval = st.checkbox(str(scv), key = "selcolval_chkbox_" + str(j))

#     # if selcol in df.columns.to_list():
#     #     if selcolval in df[selcol].unique():

#     dfn = filt_df(dfc, selcol, selcolval, type_compare="==")
# else:
#     dfn = dfc.copy()
# st.write(ccd2)
lc, rc = st.columns([0.5, 0.5])

if flag_keep_going:

    mdf, rdf = add_geometry2(dfc, fbs)

    # colormap.add_to(m)
    spriv, spub = prepare_school_pts()

    sz_options = np.arange(10)/2 + 0.5

    key = "Select distance"
    with lc:
        def get_new_values_list3():
            st.session_state["Select distance"]
        size  = st.select_slider('Select distance from schools (miles)', options=sz_options, on_change =get_new_values_list3, key=key)

    sprivb = school_buffer(spriv, size)
    spubb = school_buffer(spub, size)
    # st.write(spriv)
    # st.write(sprivb)
    dfjpriv = join_buf_w_df(sprivb, mdf, howjoin = "inner", pred = "intersects")
    dfjpub = join_buf_w_df(spubb, mdf, howjoin = "inner", pred = "intersects")
    # st.write(dfjpriv)
    df = gpd.GeoDataFrame( pd.concat([dfjpriv, dfjpub], ignore_index=True), crs=fbs.crs)
    dfjpriv2 = join_buf_w_df(mdf,spubb,  howjoin = "inner", pred = "intersects")
    dfjpub2 = join_buf_w_df(spubb,mdf, howjoin = "inner", pred = "intersects")
    dfjpriv3 = join_buf_w_df(mdf,spubb, howjoin = "left", pred = "intersects")
    dfjpriv4 = join_buf_w_df(spubb,mdf, howjoin = "left", pred = "intersects")
    # st.write(dfjpriv)
    df2 = gpd.GeoDataFrame( pd.concat([dfjpriv, dfjpub], ignore_index=True), crs=fbs.crs)
    # st.write("Filter applied!")
    #################


    st.header("Example Map: Aerial applications")

    lc2, cc2, rc2 = st.columns([0.75, 0.2, 0.05])
    with lc2:

        # Filter df even more (this could be done before joining data)
        fig, ax = plt.subplots()
        dfjpriv2.plot(ax = ax,color = 'blue', label = "mdf, school, inner join",zorder = 10, legend = True)
        spubb.plot(ax=ax, color = "yellowgreen", alpha = 0.3, label = "buf", zorder = 1)
        st.pyplot(fig)
        fig, ax = plt.subplots()
        dfjpub2.plot(ax = ax,color = 'purple', label = "school,mdf,  inner join",zorder = 10, legend = True)
        spubb.plot(ax=ax, color = "yellowgreen", alpha = 0.3, label = "buf",zorder = 1)

        st.pyplot(fig)
        fig, ax = plt.subplots()
        dfjpriv3.plot(ax = ax,color = 'red', label = "mdf,sch,   left join",zorder = 10, legend = True)
        spubb.plot(ax=ax, color = "yellowgreen", alpha = 0.3, label = "buf",zorder = 1)
        st.pyplot(fig)
        fig, ax = plt.subplots()
        dfjpriv4.plot(ax = ax,color = 'magenta', label = "sch, mdf,   left join",zorder = 10, legend = True)
        spubb.plot(ax=ax, color = "yellowgreen", alpha = 0.3,zorder = 1, label = "buf")
        st.pyplot(fig)

        st.write(len(dfjpriv2), len(dfjpub2), len(dfjpriv3), len(dfjpriv4))
    # center on Liberty Bell, add marker

        # Example usage:
        # Rectangle in legend:
        polygon_dfs = [fbs, df, sprivb, spubb]  # List of polygon GeoDataFrames
        polygon_colors = ['grey', 'red', 'yellowgreen', 'yellowgreen']  # Corresponding colors
        polygon_labels = ['Field Boundaries', 'Products close to schools', f'{size} mile buffer around schools', 'None']  # Corresponding labels
        polygon_alphas = [.5, 0.8, 0.5, 0.5]  # Corresponding labels
        polygon_legend_flags = [False, False, False, False]  # Whether to include in legend
        polygon_z_order = [2,4,1,1]

        point_dfs = [spriv, spub]  # List of point GeoDataFrames
        point_markers = ['*', '*']  # Corresponding markers
        point_colors = ['black', 'green']  # Corresponding colors
        point_sizes = [50, 50]  # Corresponding sizes
        point_labels = ['Private Schools', 'Public Schools']  # Corresponding labels
        point_legend_flags = [False, False]  # Whether to include in legend

        categorized_dfs = []  # List of categorized GeoDataFrames
        category_columns = []  # List of column names for categories
        category_colors_list = []  # List of dictionaries mapping categories to colors
        category_legend_flags = []  # Whether to include in legend

        buffer_dfs = []  # List of buffer GeoDataFrames
        buffer_colors = []  # Buffer colors
        buffer_labels = []  # Buffer labels
        buffer_alphas = []  # Buffer transparency
        buffer_legend_flags = []  # Whether to include in legend



        fig, ax = plt.subplots()# figsize = (6,9))

        fig  = plot_geopandas_with_legend(fig, ax,flegend = False,
            polygon_dfs=polygon_dfs,
            polygon_colors=polygon_colors,
            polygon_labels=polygon_labels,
            polygon_alphas=polygon_alphas,
            polygon_legend_flags=polygon_legend_flags,
            polygon_z_order = polygon_z_order,
            point_dfs=point_dfs,
            point_markers=point_markers,
            point_colors=point_colors,
            point_sizes=point_sizes,
            point_labels=point_labels,
            point_legend_flags=point_legend_flags,
            categorized_dfs=categorized_dfs,
            category_columns=category_columns,
            category_colors_list=category_colors_list,
            category_legend_flags=category_legend_flags,
            buffer_dfs=buffer_dfs,
            buffer_colors=buffer_colors,
            buffer_labels=buffer_labels,
            buffer_alphas=buffer_alphas,
            buffer_legend_flags=buffer_legend_flags,
            title=f'Fields within {size} miles of school'
        )
        # ax.get_legend().remove()
        ax.set_ylim([-88030.38276499984, 11734.455264999626])
        ax.set_xlim([-122326.77554000002, -36477.94346000049])
        plt.tight_layout()
        st.pyplot(fig)



    dfcg = pd.DataFrame(mdf)
    # dfgg = pa.Table.from_pandas(dfcg)
    # st.dataframe(dfgg)
    st.dataframe(dfcg)
    # st.write(dfcg)
#

flag_folium = False

if flag_folium:

    m = folium.Map(location=[37.5, -120.8], zoom_start=7)

    #folium.Marker(
    #    [39.949610, -75.150282], popup="Liberty Bell", tooltip="Liberty Bell"
    #).add_to(m)

    # call to render Folium map in Streamlit\

    # ### geojson map like: https://folium.streamlit.app/geojson_popup, https://python-visualization.github.io/folium/latest/user_guide/geojson/geojson_popup_and_tooltip.html
    # #GeoJSON popup and tooltip
    # data = ".\pesticides\data_sources\AgComm_Stanislaus\merged_pur_sites_fieldbds.shp"
    # pur = geopandas.GeoDataFrame.from_file(data, crs="EPSG:3310")

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
    # if dfc is not None:
        # if colorcol in dfc.columns.to_list():

    colormap = branca.colormap.StepColormap(
        # vmin=dfc[colorcol].quantile(0.0),
        # vmax=dfc[colorcol].quantile(1),
        colors=["red", "lightblue", "green", "yellow"],
        caption=colorcol_desc,
    )

    m = folium.Map(location=[37.5, -120.86], zoom_start=7)

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


    # g = folium.GeoJson(
    #     dfc,
    #     style_function=lambda x: {
    #         "fillColor": colormap(x["properties"][colorcol])
    #         if x["properties"][colorcol] is not None
    #         else "transparent",
    #         "color": "black",
    #         "fillOpacity": 0.4,
    #     },
    #     tooltip=tooltip,
    #     popup=popup,
    # ).add_to(m)


    for _, r in dfc.iterrows():
        # Without simplifying the representation of each borough,
        # the map might not be displayed
        sim_geo = gpd.GeoSeries(r["geometry"]).simplify(tolerance=0.001)
        geo_j = sim_geo.to_json()
        geo_j = folium.GeoJson(data=geo_j,
            style_function=lambda x: {"fillColor": r["color"], "fillOpacity":0.4})
        folium.Popup(r["color_category"]).add_to(geo_j)
        geo_j.add_to(m)
    # m



    # popup = folium.GeoJsonPopup(
    #     fields=["Site Location", colorcol],
    #     aliases=["Site Location", colorcol_desc],
    #     localize=True,
    #     labels=True,
    #     style="background-color: yellow;",
    # )

    # tooltip = folium.GeoJsonTooltip(
    #     fields=["Site Location", "Application Date", colorcol],
    #     aliases=["Site Location", "Application Date", colorcol_desc],
    #     localize=True,
    #     sticky=False,
    #     labels=True,
    #     style="""
    #         background-color: #F0EFEF;
    #         border: 2px solid black;
    #         border-radius: 3px;
    #         box-shadow: 3px;
    #     """,
    #     max_width=800,
    # )


    g = folium.GeoJson(
        sprivb,
        style_function=lambda x: {
            "color": "black",
            "fillOpacity": 0.4,
        },
    ).add_to(m)


    g2 = folium.GeoJson(
        spubb,
        style_function=lambda x: {
            "color": "green",
            "fillOpacity": 0.4,
        },
    ).add_to(m)


    make_legend(m)
    # folium.LayerControl().add_to(m)  ADDS TOO MANY ALL SHAPES

    map = st_folium(
        m,
        width=620, height=580,
        key="folium_map"
    )

    col1, col2, col3, col4 = st.columns([0.25, 0.25, 0.25, 0.25])
    cccol= [col1, col2, col3, col4]
    for i in range(4):
        with cccol[i]:
            st.write(ccnames[i])
            st.write(ccl[i])
