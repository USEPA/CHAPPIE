"""
Module for Get Assessment Total Maximum Daily Load (TMDL) Tracking and Implementation System (ATTAINS) geometry

@author:  edamico
"""
from CHAPPIE import layer_query


def get_attains_points(aoi):
    """Get ATTAINS points within AOI.

    Parameters
    ----------
    aoi : geopandas.GeoDataFrame
        Spatial definition for Area Of Interest (AOI).

    Returns
    -------
    geopandas.GeoDataFrame
        GeoDataFrame for ATTAINS points.

    """

    url = 'https://gispub.epa.gov/arcgis/rest/services/OW/ATTAINS_Assessment/MapServer'
    xmin, ymin, xmax, ymax = aoi.total_bounds
    bbox = [xmin, ymin, xmax, ymax]

    return layer_query.get_bbox(aoi=bbox,
                                url=url,
                                layer=0,
                                in_crs=aoi.crs.to_epsg())

def get_attains_lines(aoi):
    """Get ATTAINS lines within AOI.

    Parameters
    ----------
    aoi : geopandas.GeoDataFrame
        Spatial definition for Area Of Interest (AOI).

    Returns
    -------
    geopandas.GeoDataFrame
        GeoDataFrame for ATTAINS lines.

    """

    url = 'https://gispub.epa.gov/arcgis/rest/services/OW/ATTAINS_Assessment/MapServer'
    xmin, ymin, xmax, ymax = aoi.total_bounds
    bbox = [xmin, ymin, xmax, ymax]

    return layer_query.get_bbox(aoi=bbox,
                                url=url,
                                layer=1,
                                in_crs=aoi.crs.to_epsg())

def get_attains_polygons(aoi):
    """Get ATTAINS polygons within AOI.

    Parameters
    ----------
    aoi : geopandas.GeoDataFrame
        Spatial definition for Area Of Interest (AOI).

    Returns
    -------
    geopandas.GeoDataFrame
        GeoDataFrame for GeoDataFrame for ATTAINS polygons.

    """

    url = 'https://gispub.epa.gov/arcgis/rest/services/OW/ATTAINS_Assessment/MapServer'
    xmin, ymin, xmax, ymax = aoi.total_bounds
    bbox = [xmin, ymin, xmax, ymax]

    return layer_query.get_bbox(aoi=bbox,
                                url=url,
                                layer=2,
                                in_crs=aoi.crs.to_epsg())