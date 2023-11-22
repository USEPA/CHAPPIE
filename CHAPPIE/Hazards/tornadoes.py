# -*- coding: utf-8 -*-
"""
Test tropical cyclones 

@author: jbousqui
"""
import os
import math
import urllib.request
import zipfile
import pandas
import geopandas


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
    
    urllib.request.urlretrieve(url, temp)  # Download zip

    # Extract        
    with zipfile.ZipFile(temp, 'r') as zip_ref:
        zip_ref.extractall(out_dir)

    # Read component file to geodataframe
    sub_dir = f'{os.sep}{years}-{component}'
    #return geopandas.read_file(f'{out_dir}{sub_dir}{sub_dir}{sub_dir}.shp')
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
