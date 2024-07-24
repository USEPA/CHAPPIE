"""
Module for health assets.

@author: tlomba01
"""
from CHAPPIE import layer_query

def get_fire_ems(aoi):
    """Get Fire EMS locations within AOI.

    Parameters
    ----------
    aoi : geopandas.GeoDataFrame
        Spatial definition for Area Of Interest (AOI).

    Returns
    -------
    geopandas.GeoDataFrame
        GeoDataFrame for Fire EMS locations.

    """

    url = 'https://carto.nationalmap.gov/arcgis/rest/services/structures/MapServer'
    xmin, ymin, xmax, ymax = aoi.total_bounds
    bbox = [xmin, ymin, xmax, ymax]
    
    return layer_query.get_bbox(aoi=bbox,
                                url=url,
                                layer=51,
                                in_crs=aoi.crs.to_epsg())
