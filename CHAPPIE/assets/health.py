"""
Module for health assets.

@author: tlomba01
"""
import requests
import pandas
from json import dumps
from warnings import warn
from CHAPPIE import layer_query


_npi_url = "https://npiregistry.cms.hhs.gov/api"
_npi_url_backup = f"{_npi_url[:-3]}RegistryBack/search"
param_list = ["firstName", "lastName", "organizationName", "aoFirstName", "skip",
              "enumerationType", "number", "city", "state", "country",
              "taxonomyDescription", "postalCode", "exactMatch", "addressType"]
_npi_backup_basedict = {key: None for key in param_list}


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
                df = pandas.DataFrame(res.json()['results'])
                df["zip5"]=zip  # Add 5-digit zipcode to show retrieval set
                dfs.append(df)
                if res.json()['result_count']==200:
                    # Presumably not reached the end of results
                    if i>=1200:
                        warn(f"Reached NPI skip limit for zip {zip} & {type}")
                        break  # Limits to 1400 results (last 200 duplicated)
                        #TODO: switch to using _npi_url_backup
                        dfs.append(npi_registry_search(params))
                    else:
                        new_results = True
                        i+=200
                else:
                    new_results = False
    return pandas.concat(dfs)


def npi_registry_search(api_params):   
    
    params = _npi_backup_basedict
    headers = {'Content-Type': 'application/json'}    
  
    # Pull over matching from api_params
    #NOTE: version, limit, skip are purposely ignored, many other
    #keys:values could be converted (e.g., first_name)
    
    # Define params from select api_params
    # "enumeration_type" -> enumerationType (values match)
    if "enumeration_type" in api_params:
        params["enumerationType"] = api_params["enumeration_type"]
    # "address_purpose" -> addressType (VALUES don't match)
    if "address_purpose" in api_params:
        if api_params["address_purpose"] == "LOCATION":
            params["addressType"] = "PR"
        #TODO: else "SE" for secondary or do nothing for all?
        # From API doc: address_purpose: Refers to whether the address information entered
        #pertains to the provider's Mailing Address or the provider's Practice Location Address.
        #When not specified, the results will contain the providers where either the Mailing Address or
        #any of Practice Location Addresses match the entered address information. PRIMARY will only
        #search against Primary Location Address. While Secondary will only search against Secondary
        #Location Addresses. Valid values are: [LOCATION, MAILING, PRIMARY, SECONDARY]

    #postal_code -> postalCode, currently requires zip (raise KeyError)
    zips = extend_postal(api_params['postal_code'])

    # Exact match zip
    params["postalCode"] = api_params['postal_code']
    params["exactMatch"] = True
    params["skip"] = 0  # Default None may work (TODO test)
    dfs = []
    new_results=True
    while new_results:
        res = requests.post(_npi_url_backup, dumps(params), headers=headers)
        res.raise_for_status()
        df = pandas.DataFrame(res.json())
        df["zip5"] = params["postalCode"]
        dfs.append(df)
        # Get all pages of results
        if len(df)==101:
            # TODO: RegistryBack/search site says 2100 results (BREAK)
            new_results = True
            params['skip'] = params['skip']+101  # Note: something weird w/ 101 results
            #params['skip']+=101 (TODO: this short hand would be nice if it works)
        else:
            new_results = False

    # wildcard 9-digit postal codes
    params["exactMatch"] = False
    for zip in zips:
        params["skip"] = 0
        params["postalCode"] = zip
        new_results=True
        while new_results:
            res = requests.post(_npi_url_backup, dumps(params), headers=headers)
            res.raise_for_status()
            df = pandas.DataFrame(res.json())
            df["zip5"] = params["postalCode"]
            dfs.append(df)
        if len(df)==101:
            # TODO: RegistryBack/search site says 2100 results (BREAK)
            new_results = True
            params['skip'] = params['skip']+101  # Note: something weird w/ 101 results
            #params['skip']+=101 (TODO: this short hand would be nice if it works)
        else:
            new_results = False
    return pandas.concat(dfs)


def extend_postal(zip):
    wildcard = '*' * (8 -len(zip))  #extend to 9 digits w/ wilcard
    return [f"{zip}{digit}{wildcard}" for digit in range(0, 10)]
