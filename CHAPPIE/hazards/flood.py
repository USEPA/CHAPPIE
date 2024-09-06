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

    url = 'https://services.arcgis.com/P3ePLMYs2RVChkJx/ArcGIS/rest/services/USA_Flood_Hazard_Reduced_Set_gdb/FeatureServer'
    xmin, ymin, xmax, ymax = aoi.total_bounds
    bbox = [xmin, ymin, xmax, ymax]
    # out_fields = ['geometry', 'DFIRM_ID', 'FLD_AR_ID', 'FLD_ZONE', 'ZONE_SUBTY']

    count = layer_query.get_count_only(aoi=bbox,
                                url=url,
                                layer=0,
                                in_crs=aoi.crs.to_epsg())

    return layer_query.get_bbox(aoi=bbox,
                                url=url,
                                # out_fields=out_fields,
                                layer=0,
                                in_crs=aoi.crs.to_epsg(),
                                count=count)