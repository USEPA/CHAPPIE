# -*- coding: utf-8 -*-
"""
Get weather related natural hazards data

@author: jbousqui
"""
import json

import pandas
import requests

from CHAPPIE import layer_query

_EPH_URL = "https://ephtracking.cdc.gov/apigateway/api/v1"

def get_heat_events(aoi, stratificationLevelId=2194, localIDs=None, years=["2023"]):
    """get tract level heat event information.

    MetricID 1427: Annual Number of Extreme Heat Days (Full Year)

    Note: this is currently set up to work with defaults but the API is very
    restrictive and will just return empty results for non-complimentary params.

    Parameters
    ----------
    aoi : geopandas.GeoDataFrame
        Area of Interest as GeoDataFrame.
    stratificationLevelId : int, optional
        Stratification IDs, default 2194 for Relative Threshold, use 2195
        instead for Absolute Threshold.
    localIDs : dict, optional
        Dict where Key is columnName and value is localId
    years : list, optional
        List of years as string, default is for 2023 (current latest year).
    Returns
    -------
    pandas.DataFrame
        Table of results.
    """
    # Get tracts for aoi
    tracts = layer_query.getTract(aoi)["GEOID"].to_list()
    # Measure ID from: f"{_EPH_URL}/measuresearch"
    measureId = 1427
    # 1427: Annual Number of Extreme Heat Days (Full Year)

    # Stratification Levels from: f"{_EPH_URL}/stratificationlevel/1427/7/0"
    # 2194: State x Census Tract x Temperature/Heat Index x Relative Threshold
    # 2195: State x Census Tract x Temperature/Heat Index x Absolute Threshold

    # localIDs from type 22: f"{_EPH_URL}/stratificationtypes/1427/7/0}"
    if not localIDs:
        localIDs={}
        localIDs["TemperatureHeatIndexId"] = 2
        # 1: Daily Maximum Temperature
        # 2: Daily Maximum Heat Index
        # if 2194 use:
        localIDs["RelativeThresholdId"] = 1
        # 1: 90th Percentile
        # 2: 95th Percentile
        # 3: 98th Percentile
        # 4: 99th Percentile
        # if 2195 use:
        # AbsoluteThresholdId = 1
        # 1: 90 degrees F
        # 2: 95 degrees F
        # 3: 100 degrees F
        # 4: 105 degrees F
    localIDs_str = "&".join([f"{k}={v}" for k, v in localIDs.items()])
    #TemperatureHeatIndexId=2&RelativeThresholdId=1


    # Construct url for request
    EPH_url = f"{_EPH_URL}/getCoreHolder/{measureId}/{stratificationLevelId}"

    # The majority of measures do not have smoothing value.
    isSmoothed = 0  # False (1=True)
    # Do not need full core holder for most purposes.
    getFullCoreHolder = 0  # False (1=True)
    url_tail = f"/{isSmoothed}/{getFullCoreHolder}?{localIDs_str}"

    # NOTE: These can be moved down as just part of params?
    #geographicTypeIdFilter = "7"  # Census Tract
    #geographicItemsFilter = ",".join(tracts)  #tracts[0]
    #temporalTypeIdFilter = "1"
    #temporalItemsFilter = ",".join(years)

    # Request as get
    #get_body = f"{geographicTypeIdFilter}/{geographicItemsFilter}/"
    #get_body += f"{temporalTypeIdFilter}/{temporalItemsFilter}"
    #res = requests.get(f"{EPH_url}/{get_body}{url_tail}")

    # Request as post
    params = {"geographicTypeIdFilter": "7",
              "geographicItemsFilter": ",".join(tracts),
              "temporalTypeIdFilter": "1",
              "temporalItemsFilter": ",".join(years),
              }
    headers = {"Content-Type": "application/json"}
    res = requests.post(f"{EPH_url}{url_tail}", json.dumps(params), headers=headers)
    res.raise_for_status() # res.ok True even on failure, check len of results?
    # TODO: catch the following error to tell user to get token?
    #"code":429,"errorTypeId":8,"helpURL":"http://ephtracking.cdc.gov/apihelp",
    # "message":"Server has serviced too many non-token requests",
    # "status":"Too Many Requests"
    # TODO: response seems to contain metadata and results (split)
    df = pandas.DataFrame(res.json()['tableResult'])
    if len(df)>0:
        return df
    return None
