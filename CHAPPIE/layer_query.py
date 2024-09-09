# -*- coding: utf-8 -*-
"""
Created on Fri Oct 23 10:36:03 2020

@author: jbousqui
"""
import os 
import copy
import pandas
import requests
import urllib.request
import zipfile
import geopandas
import json
import math

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


# Retaining  this retrive function here for now
def get_zip(url, temp_file):
    out_dir = os.path.dirname(temp_file)
    urllib.request.urlretrieve(url, temp_file)  # Download zip

    # Extract
    with zipfile.ZipFile(temp_file, 'r') as zip_ref:
        zip_ref.extractall(out_dir)

def getCRSUnits(CRS):
    """ Function to return the units value of a pyproj CRS instance

    Parameters
    ----------
    CRS : CRS
        input coordinate reference system object

    Returns
    -------
    string containing the units of the CRS

    """
    crsDict = CRS.to_dict()
    if 'units' in crsDict.keys():
        return crsDict['units']
    elif crsDict['proj'] == 'longlat':
        return 'degrees'
    else:
        return 'unknown'

def getCounty(aoi):
    """Returns GEOID and county intersecting polygon extent"""
    # Build ESRI layer object to query
    baseurl = '{}/tigerWMS_{}/MapServer'.format(_tiger_url, 'Census2010')
    layer = 100  # County _id
    feature_layer = ESRILayer(baseurl, layer)
    # NOTE: Surgo currently uses 2010 counties but may update to 2020
    # ~'Census2020'
    # layer = 82 # Counties ID: 82
    # TODO: it was coming back empty so I transformed to layer CRS - EPSG 3857
    # and dropped "inSR": aoi.CRS.to_json(),
    # query from aoi object
    query_params = {
            "geometry": ','.join(map(str, aoi.bbox)),
            "geometryType": "esriGeometryEnvelope",
            "spatialRel": "esriSpatialRelIntersects",
            'returnGeometry': "false",
            "outFields": ", ".join(['GEOID', 'NAME']),
            }

    return feature_layer.query(**query_params)


def getState(geoids):
    """Retrurns state infor from aoi geoids"""
    ids = list(set([geo_id[:2] for geo_id in geoids]))  # Reduce to unique
    ids = ["'{}'".format(x) for x in ids]  # Format ids as str for query

    # Build ESRI layer object to query
    baseurl = '{}/tigerWMS_{}/MapServer'.format(_tiger_url, 'Census2010')
    layer = 98  # County _id
    feature_layer = ESRILayer(baseurl, layer)

    # query
    query_params = {
            "where": "GEOID=" + " OR GEOID=".join(ids),
            'returnGeometry': "false",
            "outFields": ", ".join(['GEOID', 'NAME', 'STUSAB'])
            }

    return feature_layer.query(**query_params)


def get_bbox(aoi, url, layer, out_fields=None, in_crs=None, buff_dist_m=None, count=0):
    # if geodataframe get bbox str
    if isinstance(aoi, geopandas.GeoDataFrame):
        bbox = ','.join(map(str, aoi.total_bounds))
        if not in_crs:
            in_crs = aoi.crs
    elif isinstance(aoi, list):
        bbox = ','.join(map(str, aoi))
    else:
        bbox = aoi
        #assert in_crs!=None?
    
    feature_layer = ESRILayer(url, layer)
    
    # query
    query_params = {       
            "geometry": bbox,
            "geometryType": "esriGeometryEnvelope",
            "spatialRel": "esriSpatialRelIntersects",
            "inSR": in_crs,
            'returnGeometry': "True",
            }
    
    if out_fields:
        if isinstance(out_fields, list):
            query_params["outFields"] = ",".join(out_fields)
        else:
            query_params["outFields"] = out_fields

    # Buffer distance
    if buff_dist_m:
        query_params["distance"] = buff_dist_m
        query_params["units"] = 'esriSRUnit_Meter'
    
    # Send multiple queries to rest service and specify resultOffset parameter
    if count < 2000: #TODO: compare to maxRecordCount from service
        result = feature_layer.query(**query_params)
        return result
    else:
        num_requests_needed = math.ceil(count/2000) # compare to maxRecordCount from service
        list_of_results = []
        for request_count in list(range(num_requests_needed)):
            offset_factor = request_count
            query_params['resultOffset'] = (offset_factor * 2000) # compare to maxRecordCount from service
            result = feature_layer.query(**query_params)
            list_of_results.append([result])
        df = [geopandas.GeoDataFrame(result[0]) for result in list_of_results]
        dftot = pandas.concat(df)
                
        return dftot


def get_field_where(url, layer, field, value, oper='='):
    feature_layer = ESRILayer(url, layer)
    query_params = {"where": f"{field}{oper}{value}",
                    "returnGeometry": "false",
                    "outFields": field
                    }
    return feature_layer.query(**query_params)

def get_count_only(aoi, url, layer, in_crs):
    """Query ESRI feature layer and return count only"""
    # if geodataframe get bbox str
    if isinstance(aoi, geopandas.GeoDataFrame):
        bbox = ','.join(map(str, aoi.total_bounds))
        if not in_crs:
            in_crs = aoi.crs
    elif isinstance(aoi, list):
        bbox = ','.join(map(str, aoi))
    else:
        bbox = aoi
        #assert in_crs!=None?
    feature_layer = ESRILayer(url, layer)
    
    # return count only
    return_count_params = {       
            "geometry": bbox,
            "geometryType": "esriGeometryEnvelope",
            "spatialRel": "esriSpatialRelIntersects",
            "inSR": in_crs,
            "returnCountOnly": "True",
            }    
    datadict = feature_layer.query(raw=True, **return_count_params)
    count = datadict["count"]
    return count

class ESRILayer(object):
    """Fundamental building block to access a layer in an ESRI MapService"""

    def __init__(self, baseurl, layer, **kwargs):
        """
        Class representing a layer

        Parameters
        ----------
        baseurl :   str
                    the url for the Layer.

        """
        if baseurl[:4] != 'http':
            baseurl = 'https://' + baseurl
        self.__dict__.update({"_" + k: v for k, v in kwargs.items()})
        if hasattr(self, "_fields"):
            self.variables = pandas.DataFrame(self._fields)
        self._baseurl = baseurl + "/" + str(layer)

    def __repr__(self):
        try:
            return "(ESRILayer) " + self._name
        except:
            return ""

    #TODO: Method to return service properties from self._baseurl, like maxRecordCount

    def query(self, raw=False, **kwargs):
        """
        A query function to extract data out of MapServer layers. All options
        currently exposed

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
        qstr = "&".join(["{}={}".format(k, v) for k, v in self._basequery.items()])
        self._last_query = self._baseurl + "/query?" + qstr

        if kwargs.get("returnGeometry", "true") == "True":
            # WARNING - this will override raw
            try:
                return geopandas.read_file(self._last_query + "&f=geojson")
            except requests.exceptions.HTTPError as e:
                #TODO: this needs improvement, but getting url is good for debug
                print(self._last_query())
                print(e)
        else:
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
            #return resp
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
        try:
            resp = requests.get(self._last_query)
            resp.raise_for_status()
            datadict = resp.json()
            mean = datadict["statistics"][0]["mean"]
            return mean
        except requests.exceptions.HTTPError as e:
            #TODO: this needs improvement, but getting url is good for debug
            print(self._last_query)
            print(e)
            pass
        except IndexError:
            return 'error'
            
    
def get_image_by_poly(aoi, url, row):
    # if geodataframe, get geometry of the row
    if isinstance(aoi, geopandas.GeoDataFrame):
        json_string = row.to_json(drop_id=True)
        data = json.loads(json_string)
        geometry_type = data["features"][0]["geometry"]["type"]
        # Consider polygons and multipolygon differently
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
            
        feature_layer = ESRIImageService(url)
    
        # query
        query_params = {       
                "geometry": geometry_object,
                "geometryType": "esriGeometryPolygon",
                "f": "json"
                }

        result = feature_layer.computeStatHist(**query_params)

        return result
