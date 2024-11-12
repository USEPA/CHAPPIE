"""
Module for health assets.

@author: tlomba01
"""
import requests
import pandas
from warnings import warn
from CHAPPIE import layer_query

_npi_url = "https://npiregistry.cms.hhs.gov/api"

def get_hospitals(aoi):
    """Get Hospital locations within AOI.

    Parameters
    ----------
    aoi : geopandas.GeoDataFrame
        Spatial definition for Area Of Interest (AOI).

    Returns
    -------
    geopandas.GeoDataFrame
        GeoDataFrame for Hospital locations.

    """

    url = 'https://services2.arcgis.com/FiaPA4ga0iQKduv3/arcgis/rest/services/Medicare_Hospitals/FeatureServer'
    xmin, ymin, xmax, ymax = aoi.total_bounds
    bbox = [xmin, ymin, xmax, ymax]
    
    return layer_query.get_bbox(aoi=bbox,
                                url=url,
                                layer=0,
                                in_crs=aoi.crs.to_epsg())

def get_urgent_care(aoi):
    """Get Urgent Care locations within AOI.

    Parameters
    ----------
    aoi : geopandas.GeoDataFrame
        Spatial definition for Area Of Interest (AOI).

    Returns
    -------
    geopandas.GeoDataFrame
        GeoDataFrame for Urgent Care locations.

    """

    url = 'https://services1.arcgis.com/Hp6G80Pky0om7QvQ/ArcGIS/rest/services/Urgent_Care_Facilities/FeatureServer'
    xmin, ymin, xmax, ymax = aoi.total_bounds
    bbox = [xmin, ymin, xmax, ymax]
    
    return layer_query.get_bbox(aoi=bbox,
                                url=url,
                                layer=0,
                                in_crs=aoi.crs.to_epsg())


# def _paged_get(params, i=0, dfs=[]):
#     if i>0:
#         params["skip"]=i
#     res = requests.get(_npi_url, params)
#     if res.ok:
#         df = pandas.DataFrame(res.json()['results'])
#         if res.json()['result_count']==200:
#             _paged_get(params, i+=200, dfs.append(df))
#         else:
#             return dfs.append(df)

#     return pandas.concat(dfs.


def get_providers(aoi):
    zips = layer_query.getZipCode(aoi)
    params = {"version": 2.1, "limit": 200, "address_purpose" : "LOCATION"}

    dfs = []
    for zip in zips:
        params['postal_code']=zip
        #dfs.append(_paged_get(params))
        # Split org vs provider
        for type in ["NPI-1", "NPI-2"]:
            i=0
            new_results=True
            params['enumeration_type']=type
            while new_results:
                params["skip"]=i
                res = requests.get(_npi_url, params)
                res.raise_for_status()
                #if res.ok:
                df= pandas.DataFrame(res.json()['results'])
                df["zip5"]=zip  # Add 5-digit zipcode to show retrieval set
                dfs.append(df)
                if res.json()['result_count']==200:
                    # Presumably not reached the end of results
                    if i>=1200:
                        warn(f"Reached NPI skip limit for zip {zip} & {type}")
                        break  # Limits to 1400 results (last 200 duplicated)
                    else:
                        new_results = True
                        i+=200
                else:
                    new_results = False
    return pandas.concat(dfs)
