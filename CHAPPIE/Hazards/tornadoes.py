# -*- coding: utf-8 -*-
"""
Test tropical cyclones 

@author: jbousqui
"""
import os
import urllib.request
import zipfile


def get_tornadoes(out_dir):
    base_url = "https://www.spc.noaa.gov/"
    URLS = [f"{base_url}gis/svrgis/zipped/1950-2022-torn-aspath.zip",
            f"{base_url}gis/svrgis/zipped/1950-2022-torn-initpoint.zip",
            f"{base_url}wcm/data/1950-2022_torn.csv.zip"]
    
    for url in URLS:
        temp = os.path.join(out_dir, "temp.zip")
        urllib.request.urlretrieve(url, temp)
        
        with zipfile.ZipFile(temp, 'r') as zip_ref:
            zip_ref.extractall(out_dir)




def process_tornadoes(tornadoe_paths, aoi):
    
    return gdf