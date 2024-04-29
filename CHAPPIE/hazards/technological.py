"""
Module for technological hazards

@author: thultgre
"""
from CHAPPIE import layer_query

def get_superfund_npl(aoi):
    """Get Superfund NPL sites within AOI.

    Parameters
    ----------
    aoi : geopandas.GeoDataFrame
        Spatial definition for Area Of Interest (AOI).

    Returns
    -------
    geopandas.GeoDataFrame
        GeoDataFrame for superfund NPL sites.

    """

    url = 'https://services.arcgis.com/cJ9YHowT8TU7DUyn/ArcGIS/rest/services/FAC_Superfund_Site_Boundaries_EPA_Public/FeatureServer'
    xmin, ymin, xmax, ymax = aoi.total_bounds
    bbox = [xmin, ymin, xmax,  ymax]
    
    return layer_query.get_bbox(aoi=bbox,
                                url=url,
                                layer=0,
                                in_crs=aoi.crs.to_epsg())