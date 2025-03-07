"""
Module for transit assets.

@author: edamico
"""
from CHAPPIE import layer_query

BASE_URL = "https://services.arcgis.com/xOi1kZaI0eWDREZv/arcgis/rest/services"

def get_air(aoi):
    """Get Airport locations within AOI.

    Parameters
    ----------
    aoi : geopandas.GeoDataFrame
        Spatial definition for Area Of Interest (AOI).

    Returns
    -------
    geopandas.GeoDataFrame
        GeoDataFrame for Airport locations.

    """

    url = f'{BASE_URL}/NTAD_Aviation_Facilities/FeatureServer'
    xmin, ymin, xmax, ymax = aoi.total_bounds
    bbox = [xmin, ymin, xmax, ymax]

    return layer_query.get_bbox(aoi=bbox,
                                url=url,
                                layer=0,
                                in_crs=aoi.crs.to_epsg())

def get_bus(aoi):
    """Get Bus station locations within AOI.

    Parameters
    ----------
    aoi : geopandas.GeoDataFrame
        Spatial definition for Area Of Interest (AOI).

    Returns
    -------
    geopandas.GeoDataFrame
        GeoDataFrame for Bus station locations.

    """

    url = f'{BASE_URL}/NTAD_National_Transit_Map_Stops/FeatureServer'

    xmin, ymin, xmax, ymax = aoi.total_bounds
    bbox = [xmin, ymin, xmax, ymax]

    return layer_query.get_bbox(aoi=bbox,
                                url=url,
                                layer=0,
                                in_crs=aoi.crs.to_epsg())

def get_rail(aoi):
    """Get Amtrak station locations within AOI.

    Parameters
    ----------
    aoi : geopandas.GeoDataFrame
        Spatial definition for Area Of Interest (AOI).

    Returns
    -------
    geopandas.GeoDataFrame
        GeoDataFrame for Amtrak station locations.

    """

    url = f'{BASE_URL}/NTAD_Amtrak_Stations/FeatureServer'

    xmin, ymin, xmax, ymax = aoi.total_bounds
    bbox = [xmin, ymin, xmax, ymax]

    return layer_query.get_bbox(aoi=bbox,
                                url=url,
                                layer=0,
                                in_crs=aoi.crs.to_epsg())
