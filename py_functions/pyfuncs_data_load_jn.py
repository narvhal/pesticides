import folium
import streamlit as st
from streamlit_folium import st_folium
import pandas as pd
import geopandas as gpd
import requests
import branca
import numpy as np
import matplotlib.pyplot as plt

###########################

# Data filtering widgets

# check if df is in projected coords.
#to_crs(crs =df.crs)



def list_cols(df, as_vert = True):
    if as_vert:
        dfc = df.columns.to_list()
    else:
        dfc = sorted(df.columns.to_list())
    return dfc


def load_standard_colnames():
    permittee = 'permittee'
    site_id = 'site_id'
    permit_num =  'permit_num'
    permit_yr = 'permit_yr'
    loc_narr =  'loc_narr'
    is_active = 'is_active'
    size =  'size'
    return permittee, site_id, permit_num, permit_yr, loc_narr, is_active, size



def update_colnames(df, dfnewcolsdict):
    for key in list(dfnewcolsdict.keys()):
        df[dfnewcolsdict[key]] = df[key].copy()
        df.drop(key, axis = 1, inplace = True)


def unify_pn(df):
    if isinstance(df['permit_num'].iloc[0], str):
        df['permit_num'] = [int(cpm) for cpm in df['permit_num'] ]
    else:
        df['permit_num'] = [int(cpm) if not np.isnan(cpm) else cpm for cpm in df['permit_num'] ]


def unify_py(df):
    df['permit_yr'] = [int(py) for py in df['permit_yr']]



def print_col_uniques(df):
    for col in df.columns.to_list():
        st.write(col)
        st.write("\t", df[col].iloc[0])
    if len(df[col].unique())<100:
        st.write("\t", df[col].unique())
    else: 
        st.write("\t", len(df[col].unique()), " unique values")


def prepare_school_pts():
    flag_gh = False

    if flag_gh:
        fpsch_priv = "https://github.com/narvhal/pesticides/raw/main/data_sources/CA_Dept_Education/California_Private_Schools_Stanislaus.geojson"
        fpsch_pub ="https://github.com/narvhal/pesticides/raw/main/data_sources/CA_Dept_Education/California_Public_Schools_Stanislaus.geojson"
    else:
        fpsch = r".\pesticides\data_sources\CA_Dept_Education"
        schl_priv =fpsch + r"\California_Private_Schools.geojson"
        schl_pub = fpsch + r"\SchoolSites2324_1647203305444761460.geojson"

    spriv = gpd.read_file(fpsch_priv)
    spub = gpd.read_file(fpsch_pub)
    return spriv, spub


def prepare_df_from_stanag():
    #### 2 Hr lesson:: NEED TO RIGHT CLICK ON "Raw" to copy link to download file on GITHUB
    flag_gh = False
    if flag_gh:
        fn = "https://github.com/narvhal/pesticides/raw/main/data_sources/AgComm_Stanislaus/field_boundaries/Crops_02_12_2024.shp"
        fbs = gpd.read_file(fn)
        fn = "https://github.com/narvhal/pesticides/raw/main/data_sources/AgComm_Stanislaus/allpurs2023.xlsb"
        pur = pd.read_excel(fn)
        fn = "https://github.com/narvhal/pesticides/raw/main/data_sources/AgComm_Stanislaus/AllSites2023.xlsb"
        sites = pd.read_excel(fn)

    else:
        fp_agcomm = r".\data_sources\AgComm_Stanislaus"
        fbs = gpd.read_file(fp_agcomm + r"\field_boundaries\Crops_02_12_2024.shp")
        pur = pd.read_excel(fp_agcomm + r"\allpurs2023.xlsb")
        sites = pd.read_excel(fp_agcomm + r"\AllSites2023.xlsb")


    sites.drop_duplicates(inplace = True, ignore_index = True)
    pur.drop_duplicates(inplace = True, ignore_index = True)
    fbs.drop_duplicates(inplace = True, ignore_index=True)

    permittee, site_id, permit_num, permit_yr, loc_narr, is_active, size =load_standard_colnames()

    pur_newcolnames = {'Permit #': permit_num,
     'Permitee': permittee,
     'Site ID': site_id}

    sites_newcolnames = {'Permit Number': 'permit_num',
     'Permit Year': 'permit_yr',
     'Site-ID': site_id,
     'Location Narrative': loc_narr,
     'Size': size,
     'M':'Meridian',  # fROM pur
     'T':'Township',
     'R': 'Range',
     'S':  'Section',
     'Site Active': is_active,
     'Comm Code': 'Commodity Code'}

    update_colnames(pur, pur_newcolnames)
    update_colnames(sites, sites_newcolnames)

    unify_pn(pur)
    unify_pn(sites)
    unify_pn(fbs)

    # unify_py(pur)
    unify_py(sites)
    unify_py(fbs)

    # Unify datatype of Commodity Code in pur with sites. 
    pur["Commodity Code0"] = [int(cs.split("-")[0]) for cs in pur["Commodity Code"]]
    pur["Commodity Code1"] = [int(cs.split("-")[1]) for cs in pur["Commodity Code"]]
    pur["Commodity Code"] = pur["Commodity Code0"].copy()

    purlc = list_cols(pur)
    sitlc = list_cols(sites)
    fbslc = list_cols(fbs)
    # Get common cols if needed
    psc = [c for c in purlc if c in sitlc]
    pfc = [c for c in purlc if c in fbslc]
    sfc = [c for c in sitlc if c in fbslc]

    df = pur.merge(sites,on = psc,how = 'left', suffixes = ("_pur", "_site"))  # Merge automatically uses all common column names...afaik

    return df, fbs




def filt_df(df, selcol, val, type_compare="=="):
    if type_compare == "==":
        dfn = df[df[selcol] == val].copy()
    elif type_compare == "isin":
        dfn = df[df[selcol].isin(val)].copy()
    elif type_compare == "!=":
        dfn = df[df[selcol] != val].copy()
    else:
        print("Compare?? ")
    return dfn


def add_geometry2(df, gdf, on = ['site_id', 'permit_num']):
    # usually for PUR and SITES from STAN AG COmm
    # Create a composite key for merging
    df['key'] = df[on].apply(tuple, axis=1)
    gdf['key'] = gdf[on].apply(tuple, axis=1)

    # Merge the DataFrames on the composite key
    merged_df = pd.merge(df, gdf, on='key', how='left')

    # Drop the key column as it's no longer needed
    # merged_df.drop(columns=['key'], inplace=True)

    # Convert the merged DataFrame into a GeoDataFrame
    if 'geometry' in merged_df.columns:
        merged_gdf = gpd.GeoDataFrame(merged_df, geometry='geometry', crs=gdf.crs)
         # Identify the rows that did not find a match in the GeoDataFrame
        c1 = merged_gdf['geometry'].isna()
        c2 = merged_gdf['geometry'] == None
        c3 = merged_gdf['geometry'] == "None"
        # reject_df = merged_gdf[(c1)|(c2)| (c3)].drop(columns='geometry').copy()
        # merged_gdfsm = merged_gdf[(~c1)|(merged_gdf['geometry'] != None)|(merged_gdf['geometry'] != "None")].copy()
        reject_df = merged_gdf[c2].drop(columns='geometry').copy()
        merged_gdfsm = merged_gdf[merged_gdf['geometry'] != None].copy()
        print(len(merged_gdfsm))
    else:
        merged_gdfsm = pd.DataFrame(merged_df)
        reject_df = []

    return merged_gdfsm, reject_df


def school_buffer(df, size):
    # Assume input size is in "miles"
    # Convert to meters for projected map
    sizemetric = size*1609  # miles *meters/mile
    dfb = df.copy()
    dfb['geometry'] = dfb['geometry'].buffer(sizemetric)   # unit is in meters.
    return dfb





def join_buf_w_df(dfb, dfc, howjoin = "inner", pred = "intersects"):
    # Returns dfc WHERE intersects with dfb, i.e. a subset of dfc
    dfj = gpd.sjoin(dfb, dfc, how = howjoin, predicate = pred)
    return dfj



# copied stoc
#####################
# https://raw.githubusercontent.com/arnaudmiribel/stoc/main/stoc.py
# https://github.com/arnaudmiribel/stoc/blob/main/stoc.py


DISABLE_LINK_CSS = """
<style>
a.toc {
    color: inherit;
    text-decoration: none; /* no underline */
}
</style>"""


class stoc:
    def __init__(self):
        self.toc_items = list()

    def h1(self, text: str, write: bool = True):
        if write:
            st.write(f"# {text}")
        self.toc_items.append(("h1", text))

    def h2(self, text: str, write: bool = True):
        if write:
            st.write(f"## {text}")
        self.toc_items.append(("h2", text))

    def h3(self, text: str, write: bool = True):
        if write:
            st.write(f"### {text}")
        self.toc_items.append(("h3", text))

    def toc(self):
        st.write(DISABLE_LINK_CSS, unsafe_allow_html=True)
        st.sidebar.caption("Table of contents")
        markdown_toc = ""
        for title_size, title in self.toc_items:
            h = int(title_size.replace("h", ""))
            markdown_toc += (
                " " * 2 * h
                + "- "
                + f'<a href="#{normalize(title)}" class="toc"> {title}</a> \n')
        st.sidebar.write(markdown_toc, unsafe_allow_html=True)

    @classmethod
    def from_markdown(cls, text: str):
        self = cls()
        for line in text.splitlines():
            if line.startswith("###"):
                self.h3(line[3:], write=False)
            elif line.startswith("##"):
                self.h2(line[2:], write=False)
            elif line.startswith("#"):
                self.h1(line[1:], write=False)
        st.write(text)
        self.toc()

def normalize(s):
    """
    Normalize titles as valid HTML ids for anchors
    >>> normalize("it's a test to spot how Things happ3n héhé")
    "it-s-a-test-to-spot-how-things-happ3n-h-h"
    """
    # Replace accents with "-"
    s_wo_accents = unidecode.unidecode(s)
    accents = [s for s in s if s not in s_wo_accents]
    for accent in accents:
        s = s.replace(accent, "-")
    # Lowercase
    s = s.lower()
    # Keep only alphanum and remove "-" suffix if existing
    normalized = ("".join([char if char.isalnum() else "-" for char in s]).strip("-").lower())
    return normalized



def make_legend(m):
    # Import necessary functions from branca library
    from branca.element import Template, MacroElement

    # Create the legend template as an HTML element
    legend_template = """
    {% macro html(this, kwargs) %}
    <div id='maplegend' class='maplegend'
        style='position: absolute; z-index: 9999; background-color: rgba(255, 255, 255, 0.5);
         border-radius: 6px; padding: 10px; font-size: 10.5px; right: 20px; top: 20px;'>
    <div class='legend-scale'>
      <ul class='legend-labels'>
        <li><span style='background: red; opacity: 0.75;'></span>Insecticides </li>
        <li><span style='background: lightblue; opacity: 0.75;'></span>Herbicides</li>
        <li><span style='background: green; opacity: 0.75;'></span>Fungicides</li>
        <li><span style='background: yellow; opacity: 0.75;'></span>Other</li>
      </ul>
    </div>
    </div>
    <style type='text/css'>
      .maplegend .legend-scale ul {margin: 0; padding: 0; color: #0f0f0f;}
      .maplegend .legend-scale ul li {list-style: none; line-height: 18px; margin-bottom: 1.5px;}
      .maplegend ul.legend-labels li span {float: left; height: 16px; width: 16px; margin-right: 4.5px;}
    </style>
    {% endmacro %}
    """

    # Create a Folium map

    # Add the legend to the map
    macro = MacroElement()
    macro._template = Template(legend_template)
    m.get_root().add_child(macro)


