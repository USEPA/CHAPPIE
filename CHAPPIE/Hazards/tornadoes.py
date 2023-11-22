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