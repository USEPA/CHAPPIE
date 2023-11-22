# -*- coding: utf-8 -*-
"""
Test tropical cyclones 

@author: jbousqui
"""
import os
import urllib.request
import zipfile
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
    return geopandas.read_file(f'{out_dir}{sub_dir}{sub_dir}{sub_dir}.shp')


def process_tornadoes(tornadoe_dir, aoi):
    
    return gdf

#import magrittr
#import sf
#import purrr
#import dplyr

torn_path = geopandas.read_file("L:\\Priv\\SHC_1012\\Florida ROAR\\Data\\Hazards\\Tornadoes\\1950-2022-torn-aspath\\1950-2022-torn-aspath", "1950-2022-torn-aspath")

def project_torn_path(paths, zone):
    if len(zone) > 1:
        return purrr.map(.x = unlist(lapply(zone, lambda x: paste0("+proj=utm +zone=", x, " +ellps=GRS80 +units=m +no_defs"))),
                         .f = sf.st_transform,
                         x = paths) %>%
               purrr.set_names(unlist(lapply(zone, lambda x: paste0("torn_proj_", x)))) %>%
               lapply(., lambda x: {cbind(x, radM = (x.wid / 2) / 1.094)})
    else:
        return sf.st_transform(paths, paste0("+proj=utm +zone=", zone, " +ellps=GRS80 +units=m +no_defs")) |>
               dplyr.mutate(radM = (wid / 2) / 1.094)