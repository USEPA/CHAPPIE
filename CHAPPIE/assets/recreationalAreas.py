"""
Module for recreation areas

@author:  edamico
"""

import os
import geopandas
import requests
import io
from io import BytesIO
#from CHAPPIE import layer_query
import py7zr, re
try:
    DIRPATH = os.path.dirname(os.path.realpath(__file__))
except:
    DIRPATH = os.path.dirname(os.path.realpath(r'C:\Users\EDamico\Work\Chappie_Git\CHAPPIE\assets'))

DATA_DIR = os.path.join(DIRPATH, 'lyrpkg')  # inputs

url = r"https://epa.maps.arcgis.com/sharing/rest/content/items/4f14ea9215d1498eb022317458437d19/data"

class InMemoryIOFactory:
    def __init__(self):
        self.files = {}

    def create(self, filename):
        # Create a BytesIO object for the file
        bio = BytesIO()
        self.files[filename] = bio
        return bio

    def close(self, bio):
        # Optional: Perform any cleanup or finalization here
        pass



def download_unzip_lyrpkg(url, save_path):
    """Download and unzip recreation area layer packages from URL

    Parameters
    ----------
    url: url for downloading the layer package
    save_path: path to save the downloaded layer package and unzipped file

    Returns
    -------
    geopandas.GeoDataFrame
        GeoDataFrame for recreation areas.

    """
    try:
        #Download the file from `url` and save it locally under `save_path`
        # Send GET request to the URL
        response = requests.get(url)
        folderList = []
        # Check if the request was successful (status code 200)
        factory = InMemoryIOFactory()
        if response.status_code == 200:
            with py7zr.SevenZipFile(BytesIO(response.content), mode='r') as z:
                    #get a list of all archived file names from the zip
                    file_list = z.namelist()
                    for filename in file_list:
                        if filename.split('/')[0]  not in folderList: # Get the first part of the path
                            folderList.append(filename.split('/')[0])
                    #create a filter pattern to match the desired folder
                    filter_pattern = re.compile(f'{folderList[-1]}/recareas.gdb')
                    select_files = [f for f in file_list if filter_pattern.match(f)]
                    #extract the selected files using the custom factory
                    z.extract(targets=select_files, factory=factory)
            
            

            #below code is not working - need to figure out how to read the in-memory gdb        
            for filename, bio_object in factory.files():
                print(filename)

            for filename, bio_object in factory.files.items():
                if filter_pattern.match(filename):
                    print(f"Extracted file to memory: {filename}")
                    # Seek to the beginning of the BytesIO object to read its content
                    bio_object.seek(0)
                    content = bio_object.read()
                    # with content.open() as src:
                    #     crs = src.crs
                    #     gdf = geopandas.GeoDataFrame.from_features(src, crs=crs)
                    #     print(gdf.head())
                    gdf = geopandas.read_file(content, layer="recareas", driver='OpenFileGDB')
            
            #gdf = geopandas.read_file('in_memory/recareas.gdb', layer="recareas", driver='OpenFileGDB')
            gdf = geopandas.read_file("OpenFileGDB:v108/recareas.gdb")
            return gdf
    except Exception as e:
        print(f"Error: {e}")


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
    out_path = os.path.join(DATA_DIR, 'recarea.7z')
    recAreas_gdf = download_unzip_lyrpkg(url, out_path)
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




