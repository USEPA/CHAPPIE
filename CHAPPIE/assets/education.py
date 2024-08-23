"""
Module for education assets.

@author: tlomba01
"""
from CHAPPIE import layer_query

def get_schools_public(aoi):
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
    
    base_url = "https://services1.arcgis.com/Hp6G80Pky0om7QvQ/arcgis/rest/services/"
    url = f"{base_url}/Public_Schools/FeatureServer"
    xmin, ymin, xmax, ymax = aoi.total_bounds
    bbox = [xmin, ymin, xmax, ymax]
    
    return layer_query.get_bbox(aoi=bbox,
                                url=url,
                                layer=0,
                                in_crs=aoi.crs.to_epsg())

def get_schools_private(aoi):
    """Get Private School locations within AOI.

    Parameters
    ----------
    aoi : geopandas.GeoDataFrame
        Spatial definition for Area Of Interest (AOI).

    Returns
    -------
    geopandas.GeoDataFrame
        GeoDataFrame for Private School locations.

    """

    base_url = "https://services1.arcgis.com/Hp6G80Pky0om7QvQ/arcgis/rest/services/"
    url = f"{base_url}/Private_Schools/FeatureServer"
    xmin, ymin, xmax, ymax = aoi.total_bounds
    bbox = [xmin, ymin, xmax, ymax]
    
    return layer_query.get_bbox(aoi=bbox,
                                url=url,
                                layer=0,
                                in_crs=aoi.crs.to_epsg())

def get_child_care(aoi):
    """Get Child Care locations within AOI.

    Parameters
    ----------
    aoi : geopandas.GeoDataFrame
        Spatial definition for Area Of Interest (AOI).

    Returns
    -------
    geopandas.GeoDataFrame
        GeoDataFrame for Child Care locations.

    """

    base_url = "https://services1.arcgis.com/Hp6G80Pky0om7QvQ/arcgis/rest/services/"
    url = f"{base_url}/ChildCareCenter1/FeatureServer"
    xmin, ymin, xmax, ymax = aoi.total_bounds
    bbox = [xmin, ymin, xmax, ymax]
    
    return layer_query.get_bbox(aoi=bbox,
                                url=url,
                                layer=0,
                                in_crs=aoi.crs.to_epsg())