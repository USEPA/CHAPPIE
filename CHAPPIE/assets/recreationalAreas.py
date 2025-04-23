"""
Module for recreation areas

@author:  edamico
"""
import os
import py7zr
import re
import geopandas
import layer_query
import requests



#zip7file = lyrPackage.replace(".lpk", ".7z")

def download_file(url, save_path):
    try:
        # Send GET request to the URL
        response = requests.get(url)
        
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Write the content of the response to a local file
            with open(save_path, 'wb') as file:
                file.write(response.content)
            print(f"File downloaded successfully: {save_path}")
        else:
            print(f"Failed to download file. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")


def get_recreationalArea(aoi):
    """Get protected area sites within AOI.

    Parameters
    ----------
    aoi : geopandas.GeoDataFrame
        Spatial definition for Area Of Interest (AOI).

    Returns
    -------
    geopandas.GeoDataFrame
        GeoDataFrame for protected area sites from recreation areas.

    """

    url = r"https://epa.maps.arcgis.com/sharing/rest/content/items/4f14ea9215d1498eb022317458437d19/data"
    save_path = r"C:\Users\EDamico\Work\Chappie\originals\recarea.7z"  # Replace with the desired path and file name
    #download and save zip file to folder
    download_file(url, save_path)
    #archive = py7zr.SevenZipFile(save_path, mode='r')

    #extract just the recareas.gdb
    zip7file = save_path
    filter_pattern = re.compile(r'v107/recareas.gdb')
    with py7zr.SevenZipFile(zip7file, 'r') as archive:
        allfiles = archive.getnames()
        selective_files = [f for f in allfiles if filter_pattern.match(f)]
        archive.extract(path = r'C:\Users\EDamico\Work\Chappie\originals',targets=selective_files)

    gdf = geopandas.read_file(r'v107/recareas.gdb', layer="recareas", driver='OpenFileGDB')
    xmin, ymin, xmax, ymax = aoi.total_bounds
    bbox = [xmin, ymin, xmax, ymax]

    return layer_query.get_bbox(aoi=bbox,
                                url=url,
                                layer=0,
                                in_crs=aoi.crs.to_epsg())





def get_bbox(aoi, url, layer, out_fields=None, in_crs=None, buff_dist_m=None):
    """Query layer by bounding box.

    Parameters
    ----------
    aoi : geopandas.GeoDataFrame, list, str
        Area of Interest as GeoDataFrame or bounding box as list or str of coordinates.
    url : str
        Service URL.
    layer : int
        Service layer to query.
    out_fields : list, optional
        Fields to return. The default is None and returns all fields.
    in_crs : int, optional
        Input Coordinate Referent System. The default is None and uses aoi.crs.
    buff_dist_m : int, optional
        Number of meters to buffer around the bounding box.
        The default is None and applies a buffer of 0 meters.

    Returns
    -------
    geopandas.GeoDataFrame, pandas.DataFrame
        Table of results.
    """
    # if geodataframe get bbox str
    if isinstance(aoi, geopandas.GeoDataFrame):
        bbox = ",".join(map(str, aoi.total_bounds))
        if not in_crs:
            in_crs = aoi.crs
    elif isinstance(aoi, list):
        bbox = ",".join(map(str, aoi))
    else:
        bbox = aoi
        # assert in_crs!=None?

    feature_layer = ESRILayer(url, layer)

    # Query
    query_params = {
        "geometry": bbox,
        "geometryType": "esriGeometryEnvelope",
        "spatialRel": "esriSpatialRelIntersects",
        "inSR": in_crs,
        "returnGeometry": "True",
    }

    if out_fields:
        if isinstance(out_fields, list):
            query_params["outFields"] = ",".join(out_fields)
        else:
            query_params["outFields"] = out_fields

    # Buffer distance
    if buff_dist_m:
        query_params["distance"] = buff_dist_m
        query_params["units"] = "esriSRUnit_Meter"

    result = feature_layer.query(**query_params)  # Get result

    # Compare result against count limit
    maxRecordCount = feature_layer.count()
    if len(result) < maxRecordCount:
        return result
    else:
        return _batch_query(feature_layer, query_params, maxRecordCount)



