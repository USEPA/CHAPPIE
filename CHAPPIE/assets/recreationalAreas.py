"""
Module for recreation areas

@author:  edamico
"""

import os
import geopandas
import requests
from io import BytesIO
#from CHAPPIE import layer_query
import py7zr, re
try:
    DIRPATH = os.path.dirname(os.path.realpath(__file__))
except:
    DIRPATH = os.path.dirname(os.path.realpath(r'C:\Users\EDamico\Work\Chappie_Git\CHAPPIE\assets'))

DATA_DIR = os.path.join(DIRPATH, 'lyrpkg')  # inputs

url = r"https://epa.maps.arcgis.com/sharing/rest/content/items/4f14ea9215d1498eb022317458437d19/data"

class InMemoryFactory:
        def __init__(self):
            self.extracted_files = {}

        def create_io(self, filename):
            # This method is called by py7zr to get an IO object for each file
            in_memory_file = BytesIO()
            self.extracted_files[filename] = in_memory_file
            return in_memory_file

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
        
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Write the content of the response to a local file
            with open(save_path, 'wb') as file:
                file.write(response.content)
            print(f"File downloaded successfully: {save_path}")
        else:
            print(f"Failed to download file. Status code: {response.status_code}")
    
        #Unzip the file using py7zr
        #zip7file = save_path
        # zip7file = BytesIO(response.content)
        path = os.path.dirname(save_path) 
        folderList = []
        with py7zr.SevenZipFile(BytesIO(response.content), mode='r') as z:
                file_list = z.namelist()
                
                for filename in file_list:
                    if filename.split('/')[0]  not in folderList: # Get the first part of the path
                        folderList.append(filename.split('/')[0])
        filter_pattern = re.compile(folderList[-1])
        #dfList = []
        factory = InMemoryFactory()
        with py7zr.SevenZipFile( BytesIO(response.content), 'r') as archive:
            allfiles = archive.getnames()
            selective_files = [f for f in allfiles if filter_pattern.match(f)]
            #dfList.append(geopandas.read_file(path + f'//{folderList[-1]}/recareas.gdb', layer="recareas", driver='OpenFileGDB'))
            #archive.extract(path,targets=selective_files)
            archive.extract(factory, targets=selective_files)

        # #convert the layer to a geodataframe
        # if len(dfList) <= 1:
        #     gdf = dfList[0]
        
        gdf = geopandas.read_file(path + f'//{folderList[-1]}/recareas.gdb', layer="recareas", driver='OpenFileGDB')
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