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

#try:
#    DIRPATH = os.path.dirname(os.path.realpath(__file__))
#except NameError:
#    DIRPATH = r'C:\Users\EDamico\Work\Chappie_Git\CHAPPIE'

#DATA_DIR = os.path.join(DIRPATH, 'lyrpkg')  # inputs

url = "https://epa.maps.arcgis.com/sharing/rest/content/items/4f14ea9215d1498eb022317458437d19/data"

# class InMemoryIOFactory:
#     def __init__(self):
#         self.files = {}

#     def create(self, filename):
#         # Create a BytesIO object for the file
#         bio = BytesIO()
#         self.files[filename] = bio
#         return bio

#     def close(self, bio):
#         # Optional: Perform any cleanup or finalization here
#         pass


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

        #factory = InMemoryIOFactory()
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
                    #z.extract(path=r"L:\lab\GitHub\CHAPPIE\CHAPPIE\tests\results", targets=select_files)
            gdf = geopandas.read_file(os.path.join(temp_dir, "v108", "recareas.gdb"))


        #below code is not working - need to figure out how to read the in-memory gdb
        # for filename, bio_object in factory.files():
        #     print(filename)

        # for filename, bio_object in factory.files.items():
        #     if filter_pattern.match(filename):
        #         print(f"Extracted file to memory: {filename}")
        #         # Seek to the beginning of the BytesIO object to read its content
        #         bio_object.seek(0)
        #         content = bio_object.read()
        #         # with content.open() as src:
        #         #     crs = src.crs
        #         #     gdf = geopandas.GeoDataFrame.from_features(src, crs=crs)
        #         #     print(gdf.head())
        #         gdf = geopandas.read_file(content, layer="recareas", driver='OpenFileGDB')

        # #gdf = geopandas.read_file('in_memory/recareas.gdb', layer="recareas", driver='OpenFileGDB')
        # gdf = geopandas.read_file("OpenFileGDB:v108/recareas.gdb")
    return gdf
    # except Exception as e:
    #     print(f"Error: {e}")


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
    #out_path = os.path.join(DATA_DIR, 'recarea.7z')
    recAreas_gdf = download_unzip_lyrpkg(url)
    return recAreas_gdf


def process_recreationalArea(recAreas_gdf, aoi):
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




