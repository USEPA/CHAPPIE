"""
Module for flood hazards

@author: tlomba01
"""
from CHAPPIE import layer_query
import pandas

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
    out_fields = ['geometry', 'DFIRM_ID', 'FLD_AR_ID', 'FLD_ZONE', 'ZONE_SUBTY']

    return layer_query.get_bbox(aoi=bbox,
                                url=url,
                                out_fields=out_fields,
                                layer=0,
                                in_crs=aoi.crs.to_epsg())

def get_flood(aoi):
    """Get flood imagery statistics and histogram for polygon within AOI.

    Parameters
    ----------
    aoi : geopandas.GeoDataFrame
        Parcel polygons to be summarized for Area Of Interest (AOI).

    Returns
    -------
    JSON
        Statistics and Histogram JSON object.

    """
    url = 'https://enviroatlas.epa.gov/arcgis/rest/services/Supplemental/Estimated_floodplain_CONUS_WM/ImageServer'
    
    df = pandas.DataFrame(columns=['parcelnumb', 'mean'])
    aoi = aoi[:100]
    for i in range(len(aoi)):
        data = []
        data.append(aoi.loc[[i]]['parcelnumb'][i])
        row = aoi.loc[[i]]
        actual = layer_query.get_image_by_poly(aoi=aoi, url=url, row=row)
        data.append(actual)
        df.loc[len(df)] = data
        return df