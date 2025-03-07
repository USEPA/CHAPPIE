"""
Module for hazard infrastructure assets.

@author: tlomba01
"""
import pandas

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

def get_levee_pump_stations(df):
    """Get the number of pump stations per Leveed Area.
    
    Parameters
    ----------
    df : pandas.DataFrame
        Dataframe for Leveed Areas.

    Returns
    -------
    pandas.Series
        Table of count of levee pump stations per levee area by SYSTEM_ID.

    """

    url = 'https://geospatial.sec.usace.army.mil/dls/rest/services/NLD/Public/FeatureServer'
    field = "SYSTEM_ID"
    dfs = []
    for val in df[field].to_list():
        resp = (layer_query.get_field_where(url=url,
                                        layer=4,
                                        field=field,
                                        value=val))
        dfs.append(resp)
    
    pump_stations = pandas.concat(dfs)
    
    return pandas.Series(pump_stations[field].value_counts())