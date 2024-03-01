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


def get_tornadoes(out_dir, component='torn-aspath', years='1950-2022'):
    """ Get tornadoes dataframe

    Parameters
    ----------
    out_dir : str
        Directory to save download.
    component : str, optional
        The Tornadoe component. The default is 'torn-aspath'.
    years : str, optional
        The year range for the tornadoe component url. The default is '1950-2022'.

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


def process_tornadoes(tornadoe_gdf, aoi_gdf):
    """ Get buffered (based on 'wid' column) tornadoe paths for AOI

    Parameters
    ----------
    tornadoe_gdf : geopandas.geodataframe.GeoDataFrame
        All tornadoe paths.
    aoi_gdf : geopandas.geodataframe.GeoDataFrame
        Area of Interest. CRS must be in meters.

    Returns
    -------
    torn_path_aoi : geopandas.geodataframe.GeoDataFrame
        Buffered tornadoe paths for AOI.

    """
    # tornadoe_shp = r"L:\Priv\SHC_1012\Florida ROAR\Data\Hazards\Tornadoes\1950-2022-torn-aspath\1950-2022-torn-aspath\1950-2022-torn-aspath.shp"
    #tornadoe_gdf = geopandas.read_file(tornadoe_shp)
    # aoi = r"L:\Public\jbousqui\Code\GitHub\CHAPPIE\CHAPPIE\tests\data\FlGulfCoast_ServiceArea.shp"
    #aoi_gdf = geopandas.read_file(aoi)
    
    # Add column for storm path buffer
    tornadoe_gdf['radM'] = tornadoe_gdf['wid'] / 2.188
    # project to aoi CRS
    tornadoe_gdf = tornadoe_gdf.to_crs(aoi_gdf.crs)
    
    # Filter on aoi bbox
    max_buff = math.ceil(max(tornadoe_gdf['radM']))  # distance to add to bbox
    # NOTE: assumes aoi_gdf in meters
    xmin, ymin, xmax, ymax = aoi_gdf.total_bounds
    # index on bbox
    torn_aoi = tornadoe_gdf.cx[xmin-max_buff:xmax+max_buff, ymin-max_buff:ymax+max_buff]
    
    # buffer lines in filtered tornadoes (sf::st_buffer defaults join_style and cap_style are same)
    torn_path = torn_aoi.buffer(torn_aoi['radM'])
    
    # clip buffered paths to aoi
    torn_path_aoi = torn_path.clip(aoi_gdf)

    # Do we want full path or just the path that intersects?
    
    return torn_path_aoi


def max_buffer():
    baseurl = 'https://services2.arcgis.com/FiaPA4ga0iQKduv3/ArcGIS/rest/services/'
    #url = f'{baseurl}Tornadoes_1950_2017_1/FeatureServer'
    url = f'{baseurl}Tornado_Tracks_1950_2017_1/FeatureServer'  # same as above
    layer = 0
    wid = layer_query.get_field_where(url, layer, 'wid', 2000, oper='>')
    return math.ceil(max(wid['wid'])/ 2.188)


def get_tornadoes_aoi(aoi):
    """ Get tornaodes for area of interest

    Parameters
    ----------
    aoi : geopandas.GeoDataFrame
        area of interest to get tornadoes for

    Returns
    -------
    geopandas.GeoDataFrame
        Tornadoes lines in raw format.

    """
    baseurl = 'https://services2.arcgis.com/FiaPA4ga0iQKduv3/ArcGIS/rest/services/'
    #url_pnts = f'{baseurl}Tornadoes_1950_2017_1/FeatureServer'
    url = f'{baseurl}Tornado_Tracks_1950_2017_1/FeatureServer'
    
    max_buff = max_buffer()
    # NOTE: assumes aoi_gdf in meters
    # TODO: assert aoi.crs in meters
    xmin, ymin, xmax, ymax = aoi.total_bounds
    #bbox = [xmin-max_buff, xmax+max_buff, ymin-max_buff, ymax+max_buff]
    #bbox = [xmin, xmax, ymin, ymax]
    bbox = [xmin, ymin, xmax,  ymax]
    out_fields = ['yr', 'date', 'om', 'mag', 'wid']
    
    return layer_query.get_bbox(bbox, url, 0, out_fields, aoi.crs.to_epsg(), max_buff)
    

def process_tornadoes_aoi(tornadoes_gdf, aoi):
    tornadoes_gdf = tornadoes_gdf.to_crs(aoi.crs)  # match crs for clip
    # buffer lines in filtered tornadoes (sf::st_buffer defaults join_style and cap_style are same)
    tornadoes_gdf['radM'] = tornadoes_gdf['wid'] / 2.188
    # TODO: assert aoi.crs is in meters
    tornadoes_gdf['geometry'] = tornadoes_gdf.buffer(tornadoes_gdf['radM'])
    
    # clip buffered paths to aoi
    torn_path_aoi = tornadoes_gdf.clip(aoi)
    
    # rename cols
    update_cols = {'yr': 'Year',
                   'date': 'Date',
                   'om': 'TornNo',
                   'mag': 'Magnitude'}

    return torn_path_aoi.rename(columns=update_cols)
