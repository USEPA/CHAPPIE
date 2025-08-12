"""
Module for recreation assets

@author: tlomba01, edamico, jbousquin
"""
import re

import geopandas
import pandas
import requests
from numpy import nan
from shapely.geometry import LineString, Point

from CHAPPIE import layer_query


def get_padus(aoi):
    """Get protected area sites within AOI.

    Parameters
    ----------
    aoi : geopandas.GeoDataFrame
        Spatial definition for Area Of Interest (AOI).

    Returns
    -------
    geopandas.GeoDataFrame
        GeoDataFrame for protected area sites from PADUS.

    """

    url = 'https://services.arcgis.com/v01gqwM5QqNysAAi/ArcGIS/rest/services/PADUS_Public_Access/FeatureServer'
    xmin, ymin, xmax, ymax = aoi.total_bounds
    bbox = [xmin, ymin, xmax, ymax]

    return layer_query.get_bbox(aoi=bbox,
                                url=url,
                                layer=0,
                                in_crs=aoi.crs.to_epsg())

def get_parks(aoi):
    """Get USA parks within AOI.

    Parameters
    ----------
    aoi : geopandas.GeoDataFrame
        Spatial definition for Area Of Interest (AOI).

    Returns
    -------
    geopandas.GeoDataFrame
        GeoDataFrame for USA parks.

    """

    url = 'https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_Detailed_Parks/FeatureServer'

    xmin, ymin, xmax, ymax = aoi.total_bounds
    bbox = [xmin, ymin, xmax, ymax]

    return layer_query.get_bbox(aoi=bbox,
                                url=url,
                                layer=0,
                                in_crs=aoi.crs.to_epsg())

def get_trails(aoi):
    """Get Recreational trails of the United States within AOI.

    Parameters
    ----------
    aoi : geopandas.GeoDataFrame
        Spatial definition for Area Of Interest (AOI).

    Returns
    -------
    geopandas.GeoDataFrame
        GeoDataFrame for Recreational trails.

    """

    url = 'https://carto.nationalmap.gov/arcgis/rest/services/transportation/MapServer'

    xmin, ymin, xmax, ymax = aoi.total_bounds
    bbox = [xmin, ymin, xmax, ymax]

    return layer_query.get_bbox(aoi=bbox,
                                url=url,
                                layer=37,
                                in_crs=aoi.crs.to_epsg())


def get_water_access(aoi):
    """Get water access info dataframe from BEACON for the area of interest.

    Note: this function leverages functions from the dependency for CHAPPIE.

    Parameters
    ----------
    aoi : geopandas.GeoDataFrame
        Area Of Interest (AOI) polygon(s).

    Returns
    -------
    aoi : geopandas.GeoDataFrame
        Lines for BEACON water access sites.
    """
    df_ids = get_BEACON_ids()
    # Get aoi county FIPS
    county_names = layer_query.get_county(aoi)['NAME'].to_list()
    state_abrevs = layer_query.getState(aoi)['STUSAB'].to_list()
    #subset by state and county columns
    st_df = df_ids[df_ids.BEACH_STATE.isin(state_abrevs)]
    beach_ids = st_df[st_df.BEACH_COUNTY.isin(county_names)]["BEACH_ID"].to_list()
    # get all the locations for those beach_ids
    gdf_beacon = get_BEACON_by_id(beach_ids)
    #subset those location by clipping them to the aoi
    gdf = gdf_beacon.clip(aoi)

    return gdf


def get_BEACON_ids(date='20240228'):
    #package.get_BEACON_ids()
    base_url = "https://dmap-data-commons-ow.s3.amazonaws.com/data/beach"
    beach_data_url = f"{base_url}/geospatial/beach_attributes_20240228.xlsx"
    changelog_url = f"{base_url}/geospatial/beach_changelog_20240228.xlsx"
    beaches = pandas.read_excel(beach_data_url, header=2)
    chngs = pandas.read_excel(changelog_url)

    date_match = re.search(r"\(([^()]+)\)", chngs.iloc[0, 1])
    if date_match:
        print(f"Beach attribute information was last updated on {date_match.group(1)}\n")

    return beaches


def get_BEACON_by_id(beachids, year=2024):
    """ Get table of BEACON beach information for beach id.

    Parameters
    ----------
    beachids : [str] | str
        BEACON BEACH_ID.
    year : int | str, optional
        Year to get BEACON information for. The default is 2024.

    Returns
    -------
    pandas.DataFrame
        Table with row(s) containing beach information.

    """
    #TODO: default year current?

    # Make sure ids is a list and it contains strings
    if isinstance(beachids, (str, int)):
        beachids = [str(beachids)]
    else:
        beachids = [str(b_id) for b_id in beachids]

    # Static variables in query
    base_url = "https://beacon.epa.gov/ords/beacon2/r/beacon_apex/beacon2"
    profile_url = f"{base_url}/beach-profile-details"

    dfs = []

    for beachid in beachids:
        try:
            params = {"beach_id":beachid, "year":year}
            res = requests.get(profile_url, params)  # Get html
            # Read into table
            res_table = pandas.read_html(res.content, flavor='bs4')

            # General info
            for tbl in range(0, len(res_table)+1):
                # Note: we +1 to error if it doesn't find
                if res_table[tbl][0][0]=="General and Map":
                    # Currentlt skips col:
                    #'Percent of Swim Season Days for the effective year that do not have a Beach Action (advisory, closure, etc.)'
                    cols = res_table[tbl][0][2:16]
                    row = res_table[tbl][1][2:16]
                    break  # Once found stop looping over tables

            # TODO: fixup cols by splitting at ":"
            # SKIP: Links to Additional Data Reports
            # SKIP: Swim Season and Water Quality Monitoring Frequency
            # SKIP: WQS Criteria Names and Values
            # SKIP: Local Action Decision Procedures
            # SKIP: Advisories

            # Location - loop over a few of the tables to find the right one
            for tbl in range(11, len(res_table)+1):
                # Note: we +1 to error if it doesn't find
                additions = parse_table(res_table[tbl], 'Location', 'Start Latitude:')
                if additions is not None:
                    cols = pandas.concat([cols, additions[0]], ignore_index=True)
                    row = pandas.concat([row, additions[1]], ignore_index=True)
                    break

            # SKIP: Contact Information

            # Renames (drop colon)
            cols = [col.strip(':') for col in cols]
            # Build df from lists
            df = pandas.DataFrame([row])
            df.columns = cols
            dfs+=[df]  # Add to list of resulting tables
        except Exception as E:
            # TODO: this needs better handling
            # IndexError - tends to be when site not longer has a website
            # ValueError - ?
            print(beachid)
            print(E)

    out_df = pandas.concat(dfs)  # combine
    # Replace '-' with numpy.nan
    for col in out_df.columns:
        out_df.loc[out_df[col]=='-', col] = nan

    # Fix up Beach ID index field
    for col_name in ["Beach ID", "Beach Id"]:
        if col_name in out_df.columns:
            beach_id_col = col_name
    out_df["BEACH_ID"] = out_df[beach_id_col]

    return out_df


def parse_table(table, expected_name, col1):
    """_summary_

    Parameters
    ----------
    table : _type_
        _description_
    expected_name : _type_
        _description_
    col1 : _type_
        _description_

    Returns
    -------
    _type_
        _description_
    """
    if 0 not in table.columns:
        # Named columns - skip it
        return None
    if table[0][0]==expected_name:
        # First col shoud be 'Start Latitude:'
        for i, col in enumerate(table[0].to_list()):
            if col==col1:
                return table[0][i:], table[1][i:]


def points_BEACON(df, crs_out=4269):
    """ Create GeoDataFrame of beach lines segments from BEACON DataFrame.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame for BEACON. Retrieve using get_BEACON_by_id().
    crs_out : int, optional
        EPSG code for the output coordinate reference system.
        The default is 4269.

    Returns
    -------
    gdf : geopandas.GeoDataFrame
        GeoDataFrame with specified coordinate reference system.

    """
    # Start/End points to line in geoDataFrame
    x1, x2 = 'Start Longitude', 'End Longitude'
    y1, y2 = 'Start Latitude', 'End Latitude'
    df['pnt1'] = [Point(xy) for xy in zip(df[x1], df[y1])]
    df['pnt2'] = [Point(xy) for xy in zip(df[x2], df[y2])]

    #df['geometry'] = [LineString(pnts) for pnts in zip(df['pnt1'], df['pnt2'])]
    geoms=[]
    # Currently deals w/ Point Empty by returning LineString Empty
    # Shapely.geometry.LineString init uses pnt.coords[0] (see line 66), but
    # errors because len(Point Empty) is 0
    for pnts in zip(df['pnt1'], df['pnt2']):
        if pnts[0].is_empty or pnts[1].is_empty:
            geoms+=[LineString()]
        #if pnts[0] == pnts[1]:
        # TODO: special handling when x1,y1==x2, y2?
        else:
            geoms+=[LineString(pnts)]
    gdf = geopandas.GeoDataFrame(df, geometry=geoms)

    # Set/transform CRS based on field in dataframe
    crs_list = list(set(gdf['Horizontal Ref Datum Name']))
    if len(crs_list) == 1:
        # Will throw CRSError if all NaN
        gdf = gdf.set_crs(crs_list[0])  # Set crs to input
        gdf = gdf.to_crs(crs_out)  # Convert to CRS_out
    elif len(crs_list) > 1:
        gdfs = []
        for crs in crs_list:
            if pandas.isnull(crs):
                gdf_partial = gdf[gdf['Horizontal Ref Datum Name'].isna()]
                gdf_partial = gdf_partial.set_crs(crs_out)  # Set crs to default
            else:
                # Set CRS for part of gdf using mask
                gdf_partial = gdf[gdf['Horizontal Ref Datum Name'] == crs]
                gdf_partial = gdf_partial.set_crs(crs)  # Set crs to input
                gdf_partial = gdf_partial.to_crs(crs_out)  # Convert to CRS_out
            gdfs.append(gdf_partial)
        gdf = pandas.concat(gdfs)
    # Note: if 0 gdf.crs will remain None
    return gdf
