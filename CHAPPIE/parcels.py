# -*- coding: utf-8 -*-
"""Module to query Regrid API.

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
        GeoDataFrame for Regrid parcels within AOI bounding box.

    """

    if api_key is None:
        api_key = os.environ['REGRID_API_KEY']
    url = f"{_regrid_base_url}{api_key}{_regrid_fs_path}"
    xmin, ymin, xmax, ymax = aoi.total_bounds
    bbox = [xmin, ymin, xmax, ymax]

    return layer_query.get_bbox(aoi=bbox,
                                url=url,
                                layer=0,
                                in_crs=aoi.crs.to_epsg(),
                                out_fields="id,geoid,parcelnumb,fema_flood_zone")


def process_regrid(regrid_gdf):
    """Convert Regrid parcel geometry from Polygon to Point centroid.

    Parameters
    ----------
    aoi : geopandas.GeoDataFrame
        GeoDataFrame for Regrid parcels (polygons) within AOI bounding box.

    Returns
    -------
    geopandas.GeoDataFrame
        GeoDataFrame for Regrid parcels (centroid points) within AOI bounding box.

    """
    regrid_gdf.geometry = regrid_gdf.geometry.centroid

    return regrid_gdf
