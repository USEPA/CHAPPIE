# -*- coding: utf-8 -*-
"""Module to query regrid API.

@author: tlomba01
"""
import os
from CHAPPIE import layer_query

_regrid_base_url = "https://fs.regrid.com/"
_regrid_fs_path = "/rest/services/premium/FeatureServer"

def get_regrid(aoi, api_key=None):
    """Get Regrid parcels within AOI.

    Parameters
    ----------
    aoi : geopandas.GeoDataFrame
        Spatial definition for Area Of Interest (AOI).

    Returns
    -------
    geopandas.GeoDataFrame
        GeoDataFrame for Hospital locations.

    """
    
    if api_key == None:
        api_key = os.environ['REGRID_API_KEY']
    url = f"{_regrid_base_url}{api_key}{_regrid_fs_path}"
    xmin, ymin, xmax, ymax = aoi.total_bounds
    bbox = [xmin, ymin, xmax, ymax]

    return layer_query.get_bbox(aoi=bbox,
                                url=url,
                                layer=0,
                                in_crs=aoi.crs.to_epsg())
    
