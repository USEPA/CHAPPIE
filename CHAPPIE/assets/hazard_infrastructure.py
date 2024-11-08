"""
Module for hazard infrastructure assets.

@author: tlomba01
"""
from CHAPPIE import layer_query

def get_dams(aoi):
    """Get dam locations within AOI.

    Parameters
    ----------
    aoi : geopandas.GeoDataFrame
        Spatial definition for Area Of Interest (AOI).

    Returns
    -------
    geopandas.GeoDataFrame
        GeoDataFrame for dam locations.

    """