# -*- coding: utf-8 -*-
"""
Module to query and process tropical cyclone hazards

@author: jbousquin, rennis
"""

import os

import geopandas

from CHAPPIE import layer_query, utils


def get_cyclones(aoi):
    """Get hurricane tracks within 100 miles (160934 meters) of  AOI.

    Parameters
    ----------
    aoi : geopandas.GeoDataFrame
        Spatial definition for Area Of Interest (AOI).

    Returns
    -------
    geopandas.GeoDataFrame
        GeoDataFrame for hurricane tracks back to 1950.

    """
    baseurl = 'https://services2.arcgis.com/FiaPA4ga0iQKduv3/ArcGIS/rest/services/'
    # starting w/ lines only
    url = f'{baseurl}IBTrACS_ALL_list_v04r00_lines_1/FeatureServer'
    #url_pnts =
    max_buff = 160934
    query_crs = layer_query.getCRSUnits(aoi.crs)
    assert query_crs == 'm', f"Expected units to be meters, found {query_crs}"

    xmin, ymin, xmax, ymax = aoi.total_bounds
    bbox = [xmin, ymin, xmax,  ymax]
    out_fields = ['SID', 'NAME', 'USA_WIND', 'USA_PRES', 'year', 'month', 'day']

    return layer_query.get_bbox(bbox,
                                url,
                                0,
                                out_fields,
                                aoi.crs.to_authority()[1],
                                buff_dist_m = max_buff)


def process_cyclones(cyclones_gdf, aoi):
    """Buffer hurricane tracks by 100 miles (160934 meters) and fix up columns.

    Note: where there are multiple track segments for a single storm these are
    combined and the attributes of the first are kept.

    Parameters
    ----------
    cyclones_gdf : geopandas.GeoDataFrame
        GeoDataFrame for hurricane tracks back to 1950.
    aoi : geopandas.GeoDataFrame
        Spatial definition for Area Of Interest (AOI).

    Returns
    -------
    geopandas.GeoDataFrame
        GeoDataFrame for buffered hurricane tracks and expected columns.

    """
    # project to aoi CRS
    query_crs = layer_query.getCRSUnits(aoi.crs)
    assert query_crs == 'm', f"Expected units to be meters, found {query_crs}"
    cyclones_gdf = cyclones_gdf.to_crs(aoi.crs)  # match crs for clip
    # Fix up geometries
    # Note: this uses default first for groupby
    cyclones_gdf = cyclones_gdf.dissolve(by='SID', aggfunc='max')
    cyclones_gdf['geometry'] = cyclones_gdf.buffer(160934)  # Buffer track
    # clip buffered paths to aoi extent
    cyclones_gdf = cyclones_gdf.clip(aoi.total_bounds)

    # Fix up fields
    cyclones_gdf.reset_index(inplace=True)
    # Add storm level
    cyclones_gdf['StormLevel'] = "Category 5"
    cyclones_gdf.loc[cyclones_gdf.USA_WIND < 137, 'StormLevel'] = "Category 4"
    cyclones_gdf.loc[cyclones_gdf.USA_WIND < 113, 'StormLevel'] = "Category 3"
    cyclones_gdf.loc[cyclones_gdf.USA_WIND < 96, 'StormLevel'] = "Category 2"
    cyclones_gdf.loc[cyclones_gdf.USA_WIND < 83, 'StormLevel'] = "Category 1"
    cyclones_gdf.loc[cyclones_gdf.USA_WIND < 64, 'StormLevel'] = "Tropical Storm"
    cyclones_gdf.loc[cyclones_gdf.USA_WIND < 34, 'StormLevel'] = "Tropical Depression"
    # Date
    cyclones_gdf['Date'] = [f'{row.year}-{row.month}-{row.day}' for _, row in cyclones_gdf.iterrows()]
    # Rename cols
    update_cols = {'SID': 'SID',
                   'year': 'Year',
                   'NAME': 'StormName',
                   'USA_WIND': 'WindSpdKts',
                   'USA_PRES': 'PressureMb',
                   }
    return cyclones_gdf.rename(columns=update_cols)


def get_cyclones_all(out_dir, dataset=['lines', 'points']):
    """Get all hurricane points or tracks.

    Parameters
    ----------
    out_dir : str
        Directory to save the resulting file in.
    dataset : list, optional
        List with dataset to return.
        The default is ['lines', 'points'] to get both.

    Returns
    -------
    geopandas.GeoDataFrame
        GeoDataFrame for all hurricane tracks or event points.

    """
    base_url = "https://www.ncei.noaa.gov/data/international-best-track-archive-for-climate-stewardship-ibtracs/v04r00/access/shapefile/"
    results = []  # use named tuple instead?
    for data in dataset:
        url = f'{base_url}IBTrACS.ALL.list.v04r00.{data}.zip'
        temp = os.path.join(out_dir, f"{data}_temp.zip")  # temp zip out_file
        utils.get_zip(url, temp)  # Download & extract zip
        shp = os.path.join(out_dir, f"IBTrACS.ALL.list.v04r00.{data}.shp")
        results.append(geopandas.read_file(shp))

    if len(results)==1:
        return results[0]

    return results
