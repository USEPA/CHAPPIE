"""
Module for cultural assets

@author: tlomba01
"""
from CHAPPIE import layer_query

def get_historic(aoi):
    """Get culturally historic sites within AOI.

    Parameters
    ----------
    aoi : geopandas.GeoDataFrame
        Spatial definition for Area Of Interest (AOI).

    Returns
    -------
    geopandas.GeoDataFrame
        GeoDataFrame for culturally historic sites.

    """

    url = 'https://services2.arcgis.com/FiaPA4ga0iQKduv3/ArcGIS/rest/services/nrhp_points_v1/FeatureServer'
    xmin, ymin, xmax, ymax = aoi.total_bounds
    bbox = [xmin, ymin, xmax, ymax]
    # out_fields = ['geometry', 'DFIRM_ID', 'FLD_AR_ID', 'FLD_ZONE', 'ZONE_SUBTY']

    return layer_query.get_bbox(aoi=bbox,
                                url=url,
                                # out_fields=out_fields,
                                layer=0,
                                in_crs=aoi.crs.to_epsg())