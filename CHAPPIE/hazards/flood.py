"""
Module for flood hazards

@author: tlomba01
"""
from CHAPPIE import layer_query

def get_fema_nfhl(aoi):
    """Get FEMA NFHL sites within AOI.

    Parameters
    ----------
    aoi : geopandas.GeoDataFrame
        Spatial definition for Area Of Interest (AOI).

    Returns
    -------
    geopandas.GeoDataFrame
        GeoDataFrame for FEMA NFHL.

    """

    url = 'https://hazards.fema.gov/gis/nfhl/rest/services/public/NFHL/MapServer'
    xmin, ymin, xmax, ymax = aoi.total_bounds
    bbox = [xmin, ymin, xmax,  ymax]
    
    return layer_query.get_bbox(aoi=bbox,
                                url=url,
                                layer=28,
                                in_crs=aoi.crs.to_epsg())