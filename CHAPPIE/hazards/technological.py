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
    bbox = [xmin, ymin, xmax, ymax]
    
    return layer_query.get_bbox(aoi=bbox,
                                url=url,
                                layer=0,
                                in_crs=aoi.crs.to_epsg())

def get_FRS_ACRES(aoi):
    """ Get EPA's Facility Registry Service (FRS) sites that link
    to the Assessment Cleanup and Redevelopment Exchange System
    (ACRES) for Area Of Interest (AOI).
 
    Parameters
    ----------
    aoi : geopandas.GeoDataFrame
        Spatial definition for Area Of Interest (AOI).
 
    Returns
    -------
    geopandas.GeoDataFrame
        GeoDataFrame of FRS ACRES sites.
 
    """
 
    url = 'https://services.arcgis.com/cJ9YHowT8TU7DUyn/ArcGIS/rest/services/FRS_INTERESTS_ACRES/FeatureServer'
   
    xmin, ymin, xmax, ymax = aoi.total_bounds
    bbox = [xmin, ymin, xmax, ymax]
   
    return layer_query.get_bbox(aoi=bbox,
                                url=url,
                                layer=0,
                                in_crs=aoi.crs.to_epsg())

def get_landfills(aoi):
    """ Get landfills for Area Of Interest (AOI).
 
    Parameters
    ----------
    aoi : geopandas.GeoDataFrame
        Spatial definition for Area Of Interest (AOI).
 
    Returns
    -------
    geopandas.GeoDataFrame
        GeoDataFrame of landfills.
 
    """
 
    url = 'https://services.arcgis.com/cJ9YHowT8TU7DUyn/ArcGIS/rest/services/EPA_Disaster_Debris_Recovery_Data/FeatureServer'
   
    xmin, ymin, xmax, ymax = aoi.total_bounds
    bbox = [xmin, ymin, xmax, ymax]
   
    return layer_query.get_bbox(aoi=bbox,
                                url=url,
                                layer=0,
                                in_crs=aoi.crs.to_epsg())

def get_tri(aoi):
    """ Get TRI Reporting Facilities for Area Of Interest (AOI).
 
    Parameters
    ----------
    aoi : geopandas.GeoDataFrame
        Spatial definition for Area Of Interest (AOI).
 
    Returns
    -------
    geopandas.GeoDataFrame
        GeoDataFrame of TRI Reporting Facilities.
 
    """
 
    url = 'https://gispub.epa.gov/arcgis/rest/services/OCSPP/TRI_Reporting_Facilities/MapServer/'
   
    xmin, ymin, xmax, ymax = aoi.total_bounds
    bbox = [xmin, ymin, xmax, ymax]
   
    return layer_query.get_bbox(aoi=bbox,
                                url=url,
                                layer=0,
                                in_crs=aoi.crs.to_epsg())