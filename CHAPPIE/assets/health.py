"""
Module for health assets.

@author: tlomba01, jbousquin
"""
from json import dumps
from warnings import warn

import pandas
import requests

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

    #url = 'https://services1.arcgis.com/Hp6G80Pky0om7QvQ/ArcGIS/rest/services/Urgent_Care_Facilities/FeatureServer'
    #lyr=0
    # new resource while above is down
    url = 'https://maps.nccs.nasa.gov/mapping/rest/services/hifld_open/public_health/FeatureServer/'
    xmin, ymin, xmax, ymax = aoi.total_bounds
    bbox = [xmin, ymin, xmax, ymax]

    return layer_query.get_bbox(aoi=bbox,
                                url=url,
                                layer=4,
                                in_crs=aoi.crs.to_epsg())


def _get_npi_api(params):
    """Query API using params.

    Parameters
    ----------
    params : dict
        Parameters for the query.

    Returns
    -------
    pandas.DataFrame
        Table of API results
    """
    res = requests.get(_npi_url, params)
    res.raise_for_status()
    return pandas.DataFrame(res.json()['results'])


def get_providers(aoi):
    """Get providers in area from National Provider Identifier (NPI) records.

    Parameters
    ----------
    aoi : geopandas.GeoDataFrame
        Table with geometries defining the Area of Interest. Overlapping zip
        codes for this area are used to search for addresses.

    Returns
    -------
    pandas.DataFrame
        Table of providers from NPI in zipcodes in the area of Interest.
    """
    zips = layer_query.getZipCode(aoi)
    params = {"version": 2.1, "limit": 200, "address_purpose" : "LOCATION"}

    dfs = []
    for z_code in zips:
        params['postal_code']=z_code
        # Split org vs provider
        for typ in ["NPI-1", "NPI-2"]:
            zip_dfs=[]
            i=0
            new_results=True
            params['enumeration_type']=typ
            while new_results:
                params["skip"]=i
                df = _get_npi_api(params)
                zip_dfs.append(df)
                if len(df)==200:
                    # Presumably not reached the end of results
                    if i>=1000:
                        # Limits to 1200 results, otherwise last 200 duplicated
                        warn(f"Reached NPI skip limit for zip {z_code} & {typ}")
                        # Get IDs from _npi_url_backup
                        numbers = npi_registry_search(params)['number'].to_list()
                        # Compare against current result ids
                        retrieved = list(pandas.concat(zip_dfs)['number'].unique())
                        missing_numbers = [x for x in numbers if x not in retrieved]
                        # Get missing_numbers from API one by one
                        zip_dfs.append(npi_api_by_number(params, missing_numbers))
                        new_results = False
                    else:
                        new_results = True
                        i+=200
                else:
                    new_results = False
            df_z = pandas.concat(zip_dfs).reset_index(drop=True)
            df_z["zip5"]=z_code  # Add 5-digit zipcode to show retrieval set
            dfs.append(df_z)
    return pandas.concat(dfs).reset_index(drop=True)


def npi_api_by_number(params, numbers):
    """Query API using list of numbers

    Parameters
    ----------
    params : dict
        Parameters for the query.
    numbers : list
        Numbers to query API with one at a time.

    Returns
    -------
    pandas.DataFrame
        Table of API results
    """
    params.pop('skip', None)  # Avoid skipping
    dfs=[]
    for num in numbers:
        params['number']=num
        dfs.append(_get_npi_api(params))
    params.pop('number', None)  # Avoid this going up to global
    return pandas.concat(dfs)


def npi_registry_search(api_params):
    """Run query against registry search using api query params.

    Parameters
    ----------
    api_params : dict
        API search query parameters. Expected key:value pairs are updated.

    Returns
    -------
    pandas.DataFrame
        Table of search query results. Not all fields match API results.
    """
    params = _npi_backup_basedict

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
    # From API doc: address_purpose: Refers to whether the address information
    # entered pertains to the provider's Mailing Address or the provider's Practice
    # Location Address. When not specified, the results will contain the providers
    # where either the Mailing Address or any of Practice Location Addresses match
    # the entered address information. PRIMARY will only search against Primary
    # Location Address. While Secondary will only search against Secondary
    #Location Addresses. Valid values are: [LOCATION, MAILING, PRIMARY, SECONDARY]

    # Exact match zip
    params["postalCode"] = api_params['postal_code']
    params["exactMatch"] = True
    dfs = [_get_npi_registry(params)]


    # wildcard 9-digit postal codes
    params["exactMatch"] = False
    # postal_code -> postalCode, currently requires zip (raise KeyError)
    for z_code in extend_postal(api_params['postal_code']):
        params["skip"] = 0
        params["postalCode"] = z_code
        dfs.append(_get_npi_registry(params))

    results = pandas.concat(dfs).reset_index(drop=True)
    return results.rename({"enumerationType":"enumeration_type"})


def _get_npi_registry(params):
    """Query registry using params.

    Parameters
    ----------
    params : dict
        Parameters for the query.

    Returns
    -------
    pandas.DataFrame
        Table of registry search results
    """
    headers = {'Content-Type': 'application/json'}
    params["skip"] = 0  # Default None may work (TODO test)
    dfs=[]
    new_results=True
    while new_results:
        res = requests.post(_npi_url_backup, dumps(params), headers=headers)
        res.raise_for_status()
        df = pandas.DataFrame(res.json())
        dfs.append(df)
        # Get all pages of results
        if len(df)==101:
            # TODO: RegistryBack/search site says 2100 results (RAISE)
            if params['skip']>2100:
                break
            new_results = True
            params['skip']+=101  # Note: something weird w/ 101 results
        else:
            new_results = False
    return pandas.concat(dfs)


def extend_postal(z_code, api=False):
    """List of possible zip with one more digit added as string.

    Parameters
    ----------
    zip : str
        5-digit zip code
    api : bool, optional
        If api is True wildcards are added to make it 9-digit, by default False.

    Returns
    -------
    list
        Ten possible values when zip gets an additional digit.
    """
    if api:
        wildcard = '*' * (8 -len(z_code))  #extend to 9 digits w/ wilcard
        return [f"{z_code}{digit}{wildcard}" for digit in range(0, 10)]
    #else:
    return [f"{z_code}{digit}" for digit in range(0, 10)]


def provider_address(df, typ="LOCATION"):
    """ Get a set of addresses to geo locate based on address of typ

    Parameters
    ----------
    df : pandas.DataFrame
        Provider results DataFrame
    typ : str, optional
        Type of address to return, MAILING or LOCATION, by default "LOCATION"

    Returns
    -------
    pandas.DataFrame
        Reduced join (many-to-one) table with number-to-address
    """
    adds_lst = df.addresses.to_list()
    # Take the first location address for each (should only be one)
    add_lst = [[d for d in x if d['address_purpose']==typ][0] for x in adds_lst]
    df_temp = pandas.DataFrame(add_lst)  # Read to dataFrame
    # Assign index using unique id 'number'
    df_temp["number"] = df.number.to_list()
    # Add combined address column
    cols = ["address_1", "city", "state", "postal_code"]
    df_temp["street_address"] = df_temp[cols].agg(", ".join, axis=1)
    # Groupby combined address column and list the IDs (number) for each
    return df_temp.groupby("street_address")['number'].apply(list).reset_index()
