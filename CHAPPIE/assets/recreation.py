"""
Module for recreation assets

@author: tlomba01, edamico
"""
from CHAPPIE import layer_query


def get_padus(aoi):
    """Get protected area sites within AOI.

    Parameters
    ----------
    aoi : geopandas.GeoDataFrame
        Spatial definition for Area Of Interest (AOI).

    Returns
    -------
    geopandas.GeoDataFrame
        GeoDataFrame for protected area sites from PADUS.

    """

    url = 'https://services.arcgis.com/v01gqwM5QqNysAAi/ArcGIS/rest/services/PADUS_Public_Access/FeatureServer'
    xmin, ymin, xmax, ymax = aoi.total_bounds
    bbox = [xmin, ymin, xmax, ymax]

    return layer_query.get_bbox(aoi=bbox,
                                url=url,
                                layer=0,
                                in_crs=aoi.crs.to_epsg())

def get_parks(aoi):
    """Get USA parks within AOI.

    Parameters
    ----------
    aoi : geopandas.GeoDataFrame
        Spatial definition for Area Of Interest (AOI).

    Returns
    -------
    geopandas.GeoDataFrame
        GeoDataFrame for USA parks.

    """

    url = 'https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_Detailed_Parks/FeatureServer'
    
    xmin, ymin, xmax, ymax = aoi.total_bounds
    bbox = [xmin, ymin, xmax, ymax]

    return layer_query.get_bbox(aoi=bbox,
                                url=url,
                                layer=0,
                                in_crs=aoi.crs.to_epsg())