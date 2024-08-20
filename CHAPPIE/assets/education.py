"""
Module for education assets.

@author: tlomba01
"""
from CHAPPIE import layer_query

def get_schools_public(base_url, aoi):
    """Get Public School locations within AOI.

    Parameters
    ----------
    aoi : geopandas.GeoDataFrame
        Spatial definition for Area Of Interest (AOI).

    Returns
    -------
    geopandas.GeoDataFrame
        GeoDataFrame for Public School locations.

    """

    url = f"{base_url}/Public_Schools/FeatureServer"
    xmin, ymin, xmax, ymax = aoi.total_bounds
    bbox = [xmin, ymin, xmax, ymax]
    
    return layer_query.get_bbox(aoi=bbox,
                                url=url,
                                layer=0,
                                in_crs=aoi.crs.to_epsg())

