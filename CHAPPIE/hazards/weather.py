# -*- coding: utf-8 -*-
"""
Get weather related natural hazards data

@author: jbousqui
"""
import pandas
import requests

from CHAPPIE import layer_query

_EPH_url = "https://ephtracking.cdc.gov/apigateway/api/v1"

def get_heat_events(aoi):
    # Get tracts for aoi
    tracts = layer_query.getTract(aoi)["GEOID"].to_list()
    # Annual Number of Extreme Heat Days (Full Year)
    measureId = 1427
    stratificationLevelId = 2194
    temporalItemsFilter = 2021
    #TODO: not sure what these are doing
    isSmoothed = 0
    getFullCoreHolder = 0
    # Construct url for request
    EPH_url_req = f"{_EPH_url}/getCoreHolder/{measureId}/{stratificationLevelId}"
    #{stratificationLevelId}/{isSmoothed}/{getFullCoreHolder}[?stratificationLevelLocalIds][?apiToken]

    # NOTE: These can be moved down as just part of params?
    geographicTypeId = 7  # Census Tract
    # stratificationTypes
    #{"id":25,"name":"Temperature/Heat Index","abbreviation":"TH","columnName":"TemperatureHeatIndexId"}
    #{"id":1084,"name":"Heat Exceedance","abbreviation":"HTE","columnName":"HeatExceedId"}

    # stratificationLevels
    # Note: there are many
    #{"id":2194,"name":"State x Census Tract x Temperature/Heat Index x Relative Threshold","abbreviation":"ST_CTC_TH_RT"}

    params = {"geographicTypeIdFilter": geographicTypeId,
              "geographicItemsFilter": tracts[0]}

    res = requests.post(EPH_url_req, params)
    EPH_url_req_get = EPH_url_req + f"/{geographicTypeId}/{tracts[0]}/{temporalItemsFilter}/{isSmoothed}/{getFullCoreHolder}"
    res = requests.get(EPH_url_req_get)
    # res.ok True even on failure
    # TODO: response seems to contain metadata and results (split)
    df = pandas.DataFrame(res.json())
    return df
