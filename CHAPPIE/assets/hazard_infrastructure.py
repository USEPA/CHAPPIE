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

    url = 'https://services.arcgis.com/xOi1kZaI0eWDREZv/ArcGIS/rest/services/NTAD_Dams/FeatureServer'
    xmin, ymin, xmax, ymax = aoi.total_bounds
    bbox = [xmin, ymin, xmax, ymax]
    
    return layer_query.get_bbox(aoi=bbox,
                                url=url,
                                layer=0,
                                in_crs=aoi.crs.to_epsg())

def get_levee(aoi):
    """Get leveed area locations within AOI.

    Parameters
    ----------
    aoi : geopandas.GeoDataFrame
        Spatial definition for Area Of Interest (AOI).

    Returns
    -------
    geopandas.GeoDataFrame
        GeoDataFrame for leveed area locations.

    """

    url = 'https://geospatial.sec.usace.army.mil/dls/rest/services/NLD/Public/FeatureServer'
    xmin, ymin, xmax, ymax = aoi.total_bounds
    bbox = [xmin, ymin, xmax, ymax]
    
    return layer_query.get_bbox(aoi=bbox,
                                url=url,
                                layer=17,
                                in_crs=aoi.crs.to_epsg())
