# -*- coding: utf-8 -*-
"""
Test tropical cyclones 

@author: jbousqui
"""
import os
import math
import pandas
import geopandas
from CHAPPIE import layer_query

def get_tornadoes_all(out_dir, component='torn-aspath', years='1950-2022'):
    """ Get tornadoes dataframe

    Parameters
    ----------
    out_dir : str
        Directory to save download.
    component : str, optional
        The Tornado component. The default is 'torn-aspath'.
    years : str, optional
        The year range for the tornado component url. The default is '1950-2022'.

    Returns
    -------
    pandas.core.frame.DataFrame or geopandas.geodataframe.GeoDataFrame
        Results as in memory dataframe.

    """
    assert component in ['torn-aspath', 'torn-initpoint', 'torn.csv'], f'"{component}" invalid'
    
    base_url = "https://www.spc.noaa.gov/"

    if component=='torn.csv':
        url = f"{base_url}wcm/data/{years}_torn.csv.zip"
        # Cache the original download?
        return pandas.read_csv(url)
    
    temp = os.path.join(out_dir, "temp.zip")  # temp out_file for zip
    url = f"{base_url}gis/svrgis/zipped/{years}-{component}.zip"
    
    layer_query.get_zip(url, temp)  # Download & extract zip

    # Read component file to geodataframe
    sub_dir = f'{os.sep}{years}-{component}'
    return geopandas.read_file(f'{out_dir}{sub_dir}{sub_dir}.shp')


def max_buffer():
    """ Get max buffer based on max wid value in service for all records.

    Returns
    -------
    int
        Max buffer needed for any track in tornado tracks service.

    """
    baseurl = 'https://services2.arcgis.com/FiaPA4ga0iQKduv3/ArcGIS/rest/services/'
    #url_pnts = f'{baseurl}Tornadoes_1950_2017_1/FeatureServer'
    url = f'{baseurl}Tornado_Tracks_1950_2017_1/FeatureServer'  # same as above
    layer = 0
    #wid = layer_query.get_field_where(url, layer, 'wid', 2000, oper='>')
    #return math.ceil(max(wid['wid'])/ 2.188)
    feature_layer = layer_query.ESRILayer(url,layer)
    query_params = {"outStatistics":[{
                        "statisticType": "max",
                        "onStatisticField": "wid", 
                        "outStatisticFieldName": "max_wid"
                    }],
                    'returnGeometry': "false"}
    query_response = feature_layer.query(**query_params)
    return math.ceil(query_response['max_wid']/ 2.188)

def get_tornadoes(aoi):
    """ Get tornaodes for area of interest

    Parameters
    ----------
    aoi : geopandas.GeoDataFrame
        area of interest to get tornadoes for

    Returns
    -------
    geopandas.GeoDataFrame
        Tornado tracks (lines) in raw format.

    """
    baseurl = 'https://services2.arcgis.com/FiaPA4ga0iQKduv3/ArcGIS/rest/services/'
    #url_pnts = f'{baseurl}Tornadoes_1950_2017_1/FeatureServer'
    url = f'{baseurl}Tornado_Tracks_1950_2017_1/FeatureServer'
    
    max_buff = max_buffer()
    # NOTE: assumes aoi_gdf in meters
    # TODO: assert aoi.crs in meters
    assert layer_query.getCRSUnits(aoi.crs) == 'm', f"Expected units to be meters, found {layer_query.getCRSUnits(aoi.crs)}"
    xmin, ymin, xmax, ymax = aoi.total_bounds
    #bbox = [xmin-max_buff, xmax+max_buff, ymin-max_buff, ymax+max_buff]
    #bbox = [xmin, xmax, ymin, ymax]
    bbox = [xmin, ymin, xmax,  ymax]
    out_fields = ['yr', 'date', 'om', 'mag', 'wid']
    
    return layer_query.get_bbox(bbox, url, 0, out_fields, aoi.crs.to_epsg(), max_buff)
    

def process_tornadoes(tornadoes_gdf, aoi):
    """Get buffered (based on 'wid' column) tornado paths for AOI.

    Parameters
    ----------
    tornadoes_gdf : geopandas.GeoDataFrame
        Tornado tracks (lines) in raw format.
    aoi : geopandas.GeoDataFrame
        Spatial definition for Area Of Interest (AOI). CRS must be in meters.

    Returns
    -------
    geopandas.GeoDataFrame
        GeoDataFrame for buffered tornado tracks with expected columns.

    """
    tornadoes_gdf = tornadoes_gdf.to_crs(aoi.crs)  # match crs for clip
    # buffer lines in filtered tornadoes (sf::st_buffer defaults join_style and cap_style are same)
    tornadoes_gdf['radM'] = tornadoes_gdf['wid'] / 2.188
    assert layer_query.getCRSUnits(aoi.crs) == 'm', f"Expected units to be meters, found {layer_query.getCRSUnits(aoi.crs)}"
    tornadoes_gdf['geometry'] = tornadoes_gdf.buffer(tornadoes_gdf['radM'])
    
    # clip buffered paths to aoi extent
    torn_path_aoi = tornadoes_gdf.clip(aoi.total_bounds)
    
    # rename cols
    update_cols = {'yr': 'Year',
                   'date': 'Date',
                   'om': 'TornNo',
                   'mag': 'Magnitude'}

    return torn_path_aoi.rename(columns=update_cols)
