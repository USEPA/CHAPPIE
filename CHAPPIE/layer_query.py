# -*- coding: utf-8 -*-
"""Module to query Esri service layers.

Created on Fri Oct 23 10:36:03 2020

@author: jbousqui
"""
import os
import copy
import math
import zipfile
import urllib.request
import requests
import pandas
import geopandas
import json
from io import BytesIO
import warnings
from time import sleep

_basequery = {
    "where": "",  # sql query component
    "text": "",  # raw text search
    "objectIds": "",  # only grab these objects
    "time": "",  # time instant/time extend to query
    "geometry": "",  # spatial filter to apply to query
    "geometryType": "esriGeometryEnvelope",  # spatial support
    "inSR": "",  # spatial ref of input geometry
    "spatialRel": "",  # what to do in a DE9IM spatial query
    "relationParam": "",  # used if arbitrary spatialRel is applied
    "outFields": "*",  # fields to pass from the header out
    "returnGeometry": False,  # bool describing whether to pass geometry out
    "maxAllowableOffset": "",  # set a spatial offset
    "geometryPrecision": "",
    "outSR": "",  # spatial reference of returned geometry
    "returnIdsOnly": False,  # bool stating to only return ObjectIDs
    "returnCountOnly": False,  # int count of features meeting specified params
    "orderByFields": "",  # results sorting for the sql
    "groupByFieldsForStatistics": "",  # equivalent to sql group by
    "outStatistics": "",  # stats (mean, max, etc.) for specified fields
    "returnZ": False,  # whether to return z components of shp-z
    "returnM": False,  # whether to return m components of shp-m
    "gdbVersion": "",  # geodatabase version name
    "returnDistinctValues": False,
}

_baseComputeStatisticsHistograms = {
    "geometry": "",
    "geometryType": "",
    "mosaicRule": "",
    "renderingRule": "",
    "pixelSize": "",
    "time": "",  # time instant/time extend to compute statistics and histograms
    "processAsMultidimensional": False,
    "f": "",
}

_tiger_url = "tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb"


def get_zip(url, temp_file):
    """Retaining  this retrive function here for now - but not in use."""
    out_dir = os.path.dirname(temp_file)
    urllib.request.urlretrieve(url, temp_file)  # Download zip

    # Extract
    with zipfile.ZipFile(temp_file, "r") as zip_ref:
        zip_ref.extractall(out_dir)


def get_from_zip(url, expected_csvs, encoding="utf-8"):
    """Get csvs from zip as pandas.DataFrame.

    Parameters
    ----------
        url : str
            Uniform Resource Locator (URL) for the zip file.
        expected_csvs : list | str
            csv file(s) to retrieve from zip.
        encoding : str, optional
            Encoding for pandas to use. Defaults to "utf-8".

    Returns
    -------
        df : pandas.DataFrame
            Combined table of results from expected csv file(s).
    """    
    # TODO: try except encoding instead?
    if isinstance(expected_csvs, str):
        expected_csvs = list(expected_csvs)
    res = requests.get(url)
    res.raise_for_status()  # exception if not OK
    with zipfile.ZipFile(BytesIO(res.content)) as zip_file:
        dfs = []
        for filename in expected_csvs:
            with zip_file.open(filename) as extracted_file:
                content = extracted_file.read()
                dfs.append(pandas.read_csv(BytesIO(content), encoding=encoding))
    df = pandas.concat(dfs, ignore_index=True) 
    return df


def getCRSUnits(CRS):
    """Get the units value of a pyproj CRS instance.

    Parameters
    ----------
    CRS : CRS
        input coordinate reference system object

    Returns
    -------
    string containing the units of the CRS

    """
    crsDict = CRS.to_dict()
    if "units" in crsDict.keys():
        return crsDict["units"]
    if crsDict["proj"] == "longlat":
        return "degrees"
    else:
        return "unknown"


def getZipCode(aoi):
    """Get the zipcodes intersecting polygon extent."""
    # Build ESRI layer object to query
    baseurl = f"{_tiger_url}/tigerWMS_Current/MapServer"
    layer = 2
    #feature_layer = ESRILayer(baseurl, layer)
    # Note: "ZCTA5" == "GEOID" == "BASENAME"
    outFields = ["ZCTA5"]
    # Note: currently "returnGeometry": "true" to allow overlay
    res = get_bbox(aoi, baseurl, layer, in_crs=102039, out_fields=outFields)
    # Reduce to intersecting aoi
    aoi_prj = aoi.to_crs(res.crs)
    res2 = res.overlay(aoi_prj[['geometry']], how="intersection")
    # Reduce to list of zipcodes
    return res2['ZCTA5'].to_list()


def getTract(aoi, year="Current"):
    "Get the GEOID for tracts intersecting polygon extent."
    # Specifcying "inSR": aoi.crs returned empty
    aoi_temp = aoi.to_crs(3857)
    # TODO: use pyproj transform bbox instead of whole gdf
    year_lyr = {"2010": 14,
                "2020": 6,
                "Current": 8}
    assert year in year_lyr.keys()
    layer = year_lyr[year]
    if year in ["2010", "2020"]:
        year = f"Census{year}"
    baseurl = f"{_tiger_url}/tigerWMS_{year}/MapServer"
    feature_layer = ESRILayer(baseurl, layer)
    query_params = {
        "geometry": ",".join(map(str, aoi_temp.total_bounds)),
        "geometryType": "esriGeometryEnvelope",
        "spatialRel": "esriSpatialRelIntersects",
        "returnGeometry": "false",
        "outFields": "GEOID",
    }

    return feature_layer.query(**query_params)

def getCounty(aoi):
    """Get the GEOID and county intersecting polygon extent."""
    # Build ESRI layer object to query
    baseurl = f"{_tiger_url}/tigerWMS_Census2010/MapServer"
    layer = 100  # County _id
    feature_layer = ESRILayer(baseurl, layer)
    # NOTE: Surgo currently uses 2010 counties but may update to 2020
    # ~'Census2020'
    # layer = 82 # Counties ID: 82
    # TODO: it was coming back empty so I transformed to layer CRS - EPSG 3857
    # and dropped "inSR": aoi.CRS.to_json(),
    # query from aoi object
    query_params = {
        "geometry": ",".join(map(str, aoi.bbox)),
        "geometryType": "esriGeometryEnvelope",
        "spatialRel": "esriSpatialRelIntersects",
        "returnGeometry": "false",
        "outFields": ", ".join(["GEOID", "NAME"]),
    }

    return feature_layer.query(**query_params)


def getState(geoids):
    """Get state information from aoi geoids."""
    ids = list(set(geo_id[:2] for geo_id in geoids))  # Reduce to unique
    ids = [f"'{x}'" for x in ids]  # Format ids as str for query

    # Build ESRI layer object to query
    baseurl = f"{_tiger_url}/tigerWMS_Census2010/MapServer"
    layer = 98  # County _id
    feature_layer = ESRILayer(baseurl, layer)

    # query
    query_params = {
        "where": "GEOID=" + " OR GEOID=".join(ids),
        "returnGeometry": "false",
        "outFields": ", ".join(["GEOID", "NAME", "STUSAB"]),
    }

    return feature_layer.query(**query_params)


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


def get_field_where(url, layer, field, value, oper="="):
    """Query layer by where fields meet criteria.

    Parameters
    ----------
    url : str
        Service URL.
    layer : int
        Service layer to query.
    field : str
        Field name to use to where query.
    value : str, int
        Value to compare value in field against.
    oper : str, optional
        Operand to use when comparing values. The default is "=" to check for equality.

    Returns
    -------
    geopandas.GeoDataFrame, pandas.DataFrame
        Table of results.

    """
    feature_layer = ESRILayer(url, layer)
    query_params = {
        "where": f"{field}{oper}{value}",
        "returnGeometry": "false",
        "outFields": field,
    }
    return feature_layer.query(**query_params)


def _batch_query(feature_layer, query_params, count_limit=None):
    """Run query in batch.

    Parameters
    ----------
    feature_layer : layer_query.ESRILayer
        Layer query object.
    query_params : dict
        Keyword args as dict.
    count_limit : int, optional
        The layer maxRecordCount parameter. The default is None and gets queried.

    Returns
    -------
    geopandas.GeoDataFrame, pandas.DataFrame
        Table of combined results.

    """
    if not count_limit:
        count_limit = feature_layer.count()  # re-query
    # Get count of features in query result
    count = _get_count_only(feature_layer, query_params)
    if count:
        # Get rid of returnCountOnly
        if "returnCountOnly" in query_params.keys():
            query_params.pop("returnCountOnly")
        # Compare to maxRecordCount from service
        num_requests = math.ceil(count / count_limit)
        list_of_results = []
        # Offset is request number * service maxRecordCount
        for offset in [idx * count_limit for idx in range(num_requests)]:
            query_params["resultOffset"] = offset
            list_of_results.append([feature_layer.query(**query_params)])
    else:
        if "returnCountOnly" in query_params.keys():
            query_params.pop("returnCountOnly")
        # Compare to maxRecordCount from service
        list_of_results = []
        # Offset starts at zero
        offset = 0
        query_params["orderByFields"] = 'parcelnumb'
        while True:
            query_params["resultOffset"] = offset
            # returned raw datadict, so can only take a few attributes from response and to check the exceedTransferLimit to break the loop
            res = feature_layer.query(raw=True, **query_params)
            list_of_results.append([pandas.DataFrame.from_records(
                        [(x["attributes"]["geoid"], x["attributes"]["parcelnumb"], x["attributes"]["fema_flood_zone"], x["geometry"]) for x in res["features"]]
                    )])
            if res["exceededTransferLimit"] == False:
                break
            offset += count_limit
    # Convert each result to geodataframe
    # TODO: may need to drop all-NA results in FutureWarning
    gdfs = [geopandas.GeoDataFrame(result[0]) for result in list_of_results]

    return pandas.concat(gdfs)


def _get_count_only(feature_layer, count_query_params):
    """Query ESRI feature layer and return count only."""
    # Return count only
    count_query_params["returnCountOnly"] = "True"
    # Run query
    # TOD0: regrid batch processing is getting bad gateway here sometimes, probably need error handling here
    try: 
        datadict = feature_layer.query(raw=True, **count_query_params)
        count = datadict["count"]
        return count
    except requests.exceptions.HTTPError as e:
        warnings.warn(f"Error: {e}")
        return False


class ESRILayer(object):
    """Fundamental building block to access a layer in an ESRI MapService."""

    def __init__(self, baseurl, layer, **kwargs):
        """Class representing a layer.

        Parameters
        ----------
        baseurl :   str
                    the url for the Layer.

        """
        if baseurl[:4] != "http":
            baseurl = "https://" + baseurl
        self.__dict__.update({"_" + k: v for k, v in kwargs.items()})
        if hasattr(self, "_fields"):
            self.variables = pandas.DataFrame(self._fields)
        self._baseurl = baseurl + "/" + str(layer)

    def __repr__(self):
        try:
            return "(ESRILayer) " + self._name
        except:
            return ""

    # TODO: Extend method to return other service properties from self._baseurl?

    def count(self):
        """Get the maximum number of records the layer allows to be returned.

        Returns
        -------
        int
            maxRecordCount.

        """
        res = requests.get(self._baseurl + "?f=pjson")
        return res.json()["maxRecordCount"]

    def query(self, raw=False, **kwargs):
        """Run query to extract data out of MapServer layers.

        Note: All options currently exposed.

        Parameters
        ----------
        where: str, required
                    sql query string.
        out_fields: list or str
                    fields to pass from the header out (default: '*')
        return_geometry: bool
                    bool describing whether to return geometry or just the
                    dataframe. (default: True)
        geometry_precision: str
                    a number of significant digits to which the output of the
                    query should be truncated (default: None)
        out_sr: int or str
                    ESRI WKID spatial reference into which to reproject
                    the geodata (default: None)
        return_ids_only: bool
                    bool stating to only return ObjectIDs. (default: False)
        return_z: bool
                     whether to return z components of shp-z, (default: False)
        return_m: bool
                     whether to return m components of shp-m, (default: False)
        raw : bool
              whether to provide the raw geometries from the API (default: False)

        Returns
        -------
        Dataframe or GeoDataFrame containing entries from the geodatabase
        Notes
        -----
        Most of the time, this should be used leaning on the SQL "where"
        argument:
        cxn.query(where='GEOID LIKE "06*"')
        In most cases, you'll be querying against layers, not MapServices
        overall.
        """
        # Parse args
        kwargs = {"".join(k.split("_")): v for k, v in kwargs.items()}

        # construct query string
        self._basequery = copy.deepcopy(_basequery)
        for k, v in kwargs.items():
            try:
                self._basequery[k] = v
            except KeyError:
                raise KeyError("Option '{k}' not recognized, check parameters")
        qstr = "&".join([f"{k}={v}" for k, v in self._basequery.items()])
        self._last_query = self._baseurl + "/query?" + qstr
        # Note: second condition to not overide raw
        if kwargs.get("returnGeometry", "true") == "True" and raw is False:
            try:
                return geopandas.read_file(self._last_query + "&f=geojson")
            except requests.exceptions.HTTPError as e:
                # TODO: this needs improvement, but getting url is good for debug
                print(self._last_query())
                raise e
        resp = requests.get(self._last_query + "&f=json")
        resp.raise_for_status()
        datadict = resp.json()
        if raw:
            return datadict
        if kwargs.get("returnGeometry", "true") == "false":
            return pandas.DataFrame.from_records(
                [x["attributes"] for x in datadict["features"]]
            )
        else:
            # return resp
            raise KeyError("Returning geometry is currently disabled")

class ESRIImageService(object):
    """Fundamental building block to access an image in an ESRI Image Service"""
 
    def __init__(self, baseurl, **kwargs):
        """
        Class representing an image service
 
        Parameters
        ----------
        baseurl :   str
                    the url for the image service.
 
        """
        if baseurl[:4] != 'http':
            baseurl = 'https://' + baseurl
        self.__dict__.update({"_" + k: v for k, v in kwargs.items()})
        if hasattr(self, "_fields"):
            self.variables = pandas.DataFrame(self._fields)
        self._baseurl = baseurl
 
    def __repr__(self):
        try:
            return "(ESRIImageService) " + self._name
        except:
            return ""
 
    def computeStatHist(self, **kwargs):
        retry = 0
        # Parse args
        kwargs = {"".join(k.split("_")): v for k, v in kwargs.items()}
       
        # construct query string
        self._baseComputeStatisticsHistograms = copy.deepcopy(_baseComputeStatisticsHistograms)
        for k, v in kwargs.items():
            try:
                self._baseComputeStatisticsHistograms[k] = v
            except KeyError:
                raise KeyError("Option '{k}' not recognized, check parameters")
        cstr = "&".join(["{}={}".format(k, v) for k, v in self._baseComputeStatisticsHistograms.items()])
        cstr = cstr.replace(" ", "").replace("[", "%5B").replace("]", "%5D").replace("{", "%7B").replace("}", "%7D").replace("'", "%27").replace(":", "%3A").replace(",", "%2C")
        self._last_query = self._baseurl + "/computeStatisticsHistograms?" + cstr
        #print(self._last_query)
        while True:
            try:
                resp = requests.get(self._last_query)
                resp.raise_for_status()
                datadict = resp.json()
                # moved this to parse in flood.py
                #mean = datadict["statistics"][0]["mean"]
                return datadict
            except requests.exceptions.HTTPError as e:
                #TODO: this needs improvement, but getting url is good for debug
                retry += 1
                if retry < 2:
                    warnings.warn(f"Retry number: {retry}")
                    sleep(5)
                    continue
                else:
                    print(self._last_query)
                    print(e)
                    return {}
        # Moved to flood.py
        # except IndexError as e:
            # TODO: if response is empty, provide some metadata for the response, like a warning
            # return 
            
    
def get_image_by_poly(aoi, url, row):
    # if geodataframe, get geometry of the row
    if isinstance(aoi, geopandas.GeoDataFrame):
        try:
            json_string = row.to_json(drop_id=True)
            data = json.loads(json_string)
            geometry_type = data["features"][0]["geometry"]["type"]
            # Implement else catch in case it ever isn't polygon / multipolygon
            if geometry_type == 'Polygon':
                # Parse geodataframe polygon object to get coordinates
                rings = data["features"][0]["geometry"]["coordinates"]
                # Make esri geometry object (polygon)
                geometry_object = { "rings": rings,
                    "spatialReference": { "wkid": aoi.crs.to_epsg() }
                    }
                    
            elif geometry_type == "MultiPolygon": 
                # Parse geodataframe polygon object to get coordinates
                rings = data["features"][0]["geometry"]["coordinates"]
                # Pull out polygons from exploded gdf and fit into rest syntax for rest request
                row_ex = row.explode(column='geometry',index_parts=False)
                # Make esri geometry object (multipolygon)
                multipoly = []
                for i in range(len(row_ex)):
                    row = row_ex.iloc[[i]]
                    json_string = row.to_json(drop_id=True)
                    data = json.loads(json_string)
                    rings = data["features"][0]["geometry"]["coordinates"][0]
                    multipoly.append(rings)
                
                geometry_object = { "rings": multipoly,
                    "spatialReference": { "wkid": aoi.crs.to_epsg() }
                    }
            else:
                warnings.warn(f"Unsupported geometry type: {geometry_type}")
                geometry_object = None
        except Exception as e:
            print(e)

        if geometry_object:
            try:    
                feature_layer = ESRIImageService(url)
                # query
                query_params = {       
                        "geometry": geometry_object,
                        "geometryType": "esriGeometryPolygon",
                        "f": "json"
                        }
                result = feature_layer.computeStatHist(**query_params)
                return result
            except Exception as e:
                print(e)
