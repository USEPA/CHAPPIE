# -*- coding: utf-8 -*-
"""
Module for food assets. 

For additional definitions: https://www.usdalocalfoodportal.com/fe/definitions/

@author: jbousqui
"""
import requests
import geopandas
import pandas
from shapely import Point
from pyproj import Transformer
from math import ceil

API_URL = "https://www.usdalocalfoodportal.com/api/"
USDA_header = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'}


def search_pnt_radius(aoi, outEPSG=4326):
    """Get central point and radius around point to use in spatial search.

    Note: aoi is expected to be in CRS with units in 'm', otherwise it is re-projected in ESRI:102005

    Parameters
    ----------
    aoi : geopandas.GeoDataFrame
        Geodataframe defining the area to search for results within.
    outEPSG : int, optional
        EPSG code for the point returned. The default is 4326 (WGS1984).

    Returns
    -------
    Tuple : (shapely.Point, int)
        Central point in outEPSG and search radius in miles (rounded up).

    """

    # Check crs units are meters and re-project if not
    crs_units = aoi.crs.to_dict()['units']
    if crs_units != 'm':
        # TODO: better equa-distant projection for CONUS?
        aoi = aoi.to_csr('ESRI:102005')
        inEPSG = 'ESRI:102005'
    else:
        inEPSG = aoi.crs.to_epsg()

    # center point (not==centroid)
    xmin, ymin, xmax, ymax = aoi.total_bounds
    x_mid = (xmin+xmax)/2.0
    y_mid = (ymin+ymax)/2.0
    pnt = Point(x_mid, y_mid)
    max_pnt = Point(xmax, ymax)
    radius = pnt.distance(max_pnt)
    
    # transform center point to desired EPSG
    transformer = Transformer.from_crs(inEPSG, "epsg:{}".format(outEPSG), always_xy=True)
    pnt_out = transformer.transform(pnt.x, pnt.y)

    return Point(pnt_out), ceil(radius/1609)


def usda_res_as_gdf(res):
    if res.content==b'{"data":""}':
        # empty result, return empty gdf
        return geopandas.GeoDataFrame()
    try:
        df = pandas.DataFrame(res.json()['data'])
    except Exception as e:
        # TODO: catch just TypeError if not seeing anything else
        print(f'Check {res.url}')
        print(e)
    geom = geopandas.points_from_xy(df['location_x'], df['location_y'])
    gdf = geopandas.GeoDataFrame(df, geometry=geom, crs=4326)
    return gdf

def get_agritourism(aoi, api_key):
    """Get businesses from the USDA Agritourism Business Directory.

    Examples include u-pick farms, pumpkin patches, corn mazes, and Christmas tree farms.

    Parameters
    ----------
    aoi : geopandas.GeoDataFrame
        Spatial definition for Area Of Interest (AOI).
    api_key : str
        API key. Request a key at https://www.usdalocalfoodportal.com/fe/fregisterpublicapi/

    Returns
    -------
    geopandas.GeoDataFrame
        GeoDataFrame for agritourism business locations.

    """

    url = f"{API_URL}agritourism/"

    # Get query geos
    pnt, radius = search_pnt_radius(aoi)
    
    params = {
        'apikey': api_key,
        'x': pnt.x,
        'y': pnt.y,
        'radius': radius,
        'ftype': 'fjson'}

    res = requests.get(url, params, headers=USDA_header)
    if res.ok:
        usda_res_as_gdf(res)
    # there was a problem
    print(f'Problem, check {res.url}')
    #TODO: throw error?


def get_CSA(aoi, api_key):
    """Get Community Supported Agriculture from the USDA CSA Enterprise Directory.

    Parameters
    ----------
    aoi : geopandas.GeoDataFrame
        Spatial definition for Area Of Interest (AOI).
    api_key : str
        API key. Request a key at https://www.usdalocalfoodportal.com/fe/fregisterpublicapi/

    Returns
    -------
    geopandas.GeoDataFrame
        GeoDataFrame for CSA locations.

    """

    url = f"{API_URL}csa/"

    # Get query geos
    pnt, radius = search_pnt_radius(aoi)
    
    params = {
        'apikey': api_key,
        'x': pnt.x,
        'y': pnt.y,
        'radius': radius,
        'ftype': 'fjson'}

    res = requests.get(url, params, headers=USDA_header)
    if res.ok:
        usda_res_as_gdf(res)
    # there was a problem
    print(f'Problem, check {res.url}')
    #TODO: throw error?


def get_farmers_market(aoi, api_key):
    """Get farmers markets from the USDA Farmers Market Directory.

    Parameters
    ----------
    aoi : geopandas.GeoDataFrame
        Spatial definition for Area Of Interest (AOI).
    api_key : str
        API key. Request a key at https://www.usdalocalfoodportal.com/fe/fregisterpublicapi/

    Returns
    -------
    geopandas.GeoDataFrame
        GeoDataFrame for farmers market locations.

    """

    url = f"{API_URL}farmersmarket/"

    # Get query geos
    pnt, radius = search_pnt_radius(aoi)
    
    params = {
        'apikey': api_key,
        'x': pnt.x,
        'y': pnt.y,
        'radius': radius,
        'ftype': 'fjson'}

    res = requests.get(url, params, headers=USDA_header)
    if res.ok:
        usda_res_as_gdf(res)
    # there was a problem
    print(f'Problem, check {res.url}')
    #TODO: throw error?


def get_food_hub(aoi, api_key):
    """Get food hubs from the USDA Food Hub Directory.

    Food hubs aggregate and distribute local source-identified food products.

    Parameters
    ----------
    aoi : geopandas.GeoDataFrame
        Spatial definition for Area Of Interest (AOI).
    api_key : str
        API key. Request a key at https://www.usdalocalfoodportal.com/fe/fregisterpublicapi/

    Returns
    -------
    geopandas.GeoDataFrame
        GeoDataFrame for food hub locations.

    """

    url = f"{API_URL}foodhub/"

    # Get query geos
    pnt, radius = search_pnt_radius(aoi)
    
    params = {
        'apikey': api_key,
        'x': pnt.x,
        'y': pnt.y,
        'radius': radius,
        'ftype': 'fjson'}

    res = requests.get(url, params, headers=USDA_header)
    if res.ok:
        usda_res_as_gdf(res)
    # there was a problem
    print(f'Problem, check {res.url}')
    #TODO: throw error?


def get_farm_store(aoi, api_key):
    """Get on-farm markets from the USDA On-farm Market Directory.

    On-farm markets are farms selling produce and products directly to consumers.

    Parameters
    ----------
    aoi : geopandas.GeoDataFrame
        Spatial definition for Area Of Interest (AOI).
    api_key : str
        API key. Request a key at https://www.usdalocalfoodportal.com/fe/fregisterpublicapi/

    Returns
    -------
    geopandas.GeoDataFrame
        GeoDataFrame for on-farm market locations.

    """

    url = f"{API_URL}onfarmmarket/"

    # Get query geos
    pnt, radius = search_pnt_radius(aoi)
    
    params = {
        'apikey': api_key,
        'x': pnt.x,
        'y': pnt.y,
        'radius': radius,
        'ftype': 'fjson'}

    res = requests.get(url, params, headers=USDA_header)
    if res.ok:
        return usda_res_as_gdf(res)
    # there was a problem
    print(f'Problem, check {res.url}')
    #TODO: throw error?
