"""
Module for recreation areas

@author:  edamico
"""
import os

#import re
from io import BytesIO
from tempfile import TemporaryDirectory

import geopandas

#from CHAPPIE import layer_query
import py7zr
import requests


url = "https://epa.maps.arcgis.com/sharing/rest/content/items/4f14ea9215d1498eb022317458437d19/data"


def download_unzip_lyrpkg(url, save_path=None):
    """Download and unzip recreation area layer packages from URL

    Parameters
    ----------
    url : str
        The layer package download url
    save_path : str, optional
        Folder path for download, by default None uses a tempfile.TemporaryDirectory

    Returns
    -------
    geopandas.GeoDataFrame
        GeoDataFrame for recreation areas.
    """
    #try:
    #Download the file from `url` and save it locally under `save_path`
    response = requests.get(url)  # Send GET request to the URL
    response.raise_for_status()  # Assert request was successful

        
    with TemporaryDirectory() as temp_dir:
        with py7zr.SevenZipFile(BytesIO(response.content), mode='r') as z:
                # List all archived file names from the zip
                file_list = z.namelist()
                # List all top level folders (unique). NOTE: no sort/order
                folders = list(set([f.split('/')[0] for f in file_list]))
                # List folder version suffix
                v_sufs = ["".join(c for c in x if c.isdigit()) for x in folders]
                # Folder name with largest version suffix
                folder = [x for x in folders if x.endswith(max(v_sufs))][0]
                # Get files in desired folder (excludes ~/0000USA Recreational Areas.lyr')
                select_files = [f for f in file_list if f.startswith(f'{folder}/recareas.gdb')]
                # Extract the selected files to a temp directory
                z.extract(path=temp_dir, targets=select_files)
                #extract the selected files using the custom factory
                gdf = geopandas.read_file(os.path.join(temp_dir, f'{folder}', "recareas.gdb"))


        
    return gdf
   

def get_recreationalArea():
    """Get recreational areas

    Parameters
    ----------
    None

    Returns
    -------
    geopandas.GeoDataFrame
        GeoDataFrame for recreation areas.

    """
    
    recAreas_gdf = download_unzip_lyrpkg(url)
    return recAreas_gdf


def process_recreationalArea(aoi):
    """Process recreational areas for AOI.

    Parameters
    ----------
    recAreas_gdf : geopandas.GeoDataFrame
        Recreational areas in raw format.
    aoi : geopandas.GeoDataFrame
        Spatial definition for Area Of Interest (AOI). CRS must be in meters.

    Returns
    -------
    geopandas.GeoDataFrame
        GeoDataFrame for recreational areas with expected columns.

    """
    #get all recreational areas
    
    recAreas_gdf = get_recreationalArea()
    recAreas_gdf = recAreas_gdf.to_crs(aoi.crs)  # match crs for clip

    # clip buffered paths to aoi extent
    recAreas_aoi = recAreas_gdf.clip(aoi.total_bounds)

    return recAreas_aoi




