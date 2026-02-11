"""Module for get function discovery"""

from collections import namedtuple

import geopandas
from numpy import nan

from CHAPPIE import layer_query, utils

MD = namedtuple("MetaData", ["domain", "category", "description"])
# NOTE: aternative would be TypedDict (mutable and can set value types)
Layer = namedtuple("get_bbox", ["url", "layer"])
# layer_query.get_bbox() optional: out_fields=None, in_crs=None, buff_dist_m=None
ZipCSV = namedtuple("get_from_zip", ["url", "expected_csvs"])
# utils.get_from_zip() encoding is optional
Package = namedtuple("download_unzip_ly", ["url", "save_path"], defaults=[None])
# utils.download_unzip_lyrpkg() save_path is optional

IMLS_URL = "https://www.imls.gov/sites/default/files"

URLS = {
    "historic": "https://services2.arcgis.com/FiaPA4ga0iQKduv3/ArcGIS/rest/services/nrhp_points_v1/FeatureServer",
    "library": f"{IMLS_URL}/2024-06/pls_fy2022_csv.zip",
    "museums": f"{IMLS_URL}/2018_csv_museum_data_files.zip",
    "worship": "https://services.arcgis.com/XG15cJAlne2vxtgt/ArcGIS/rest/services/All_Places_Of_Worship__HiFLD_Open_/FeatureServer",
    "recreationalArea": "https://epa.maps.arcgis.com/sharing/rest/content/items/4f14ea9215d1498eb022317458437d19/data",
}

GET_DICT = {
    "historic": {
        "metadata": MD(
            "assets",
            "cultural",
            "Get culturally historic sites",
        ),
        "args": Layer(
            URLS["historic"],
            0,
        ),
    },
    "library": {
        "metadata": MD("assets", "cultural", "Get library data from IMLS"),
        "args": ZipCSV(
            URLS["library"],
            [
                "PLS_FY2022 PUD_CSV/PLS_FY22_AE_pud22i.csv",
                "PLS_FY2022 PUD_CSV/pls_fy22_outlet_pud22i.csv",
            ],
        ),
    },
    "museums": {
        "metadata": MD("assets", "cultural", "Get museums data from IMLS"),
        "args": ZipCSV(
            URLS["museums"],
            [
                "MuseumFile2018_File1_Nulls.csv",
                "MuseumFile2018_File2_Nulls.csv",
                "MuseumFile2018_File3_Nulls.csv",
            ],
        ),
    },
    "worship": {
        "metadata": MD(
            "assets",
            "cultural",
            "Get worship locations",
        ),
        "args": Layer(
            URLS["worship"],
            42,
        ),
    },
    "recreationalArea": {
        "metadata": MD(
            "assets",
            "cultural",
            "Get recreational areas",
        ),
        "args": Package(URLS["recreationalArea"]),
    },
}


def run_get(dataset, aoi):
    args = GET_DICT[dataset]['args']
    params = args._asdict()
    if isinstance(args, Layer):
        #params['aoi']=aoi
        #params['in_crs'] = aoi.crs.to_epsg()
        return layer_query.get_bbox(aoi=aoi, in_crs=aoi.crs.to_epsg(), **params)
    if isinstance(args, ZipCSV):
        df = utils.get_from_zip(encoding="Windows-1252", **params)

        # Fix up geo fields where missing
        df_geoms = df[['LATITUDE', 'LONGITUDE']].copy()
        df_geoms.replace(" ", nan, inplace=True)  # Must be able to coerce to float
        # df -> gdf
        geom = geopandas.points_from_xy(df_geoms['LATITUDE'], df_geoms['LONGITUDE'])
        gdf = geopandas.GeoDataFrame(df, geometry=geom, crs=4326)
        gdf.to_crs(aoi.crs, inplace=True)   # Coerce to export crs
        # Filter by those within aoi
        return gdf[gdf.geometry.within(aoi)]
    if isinstance(args, Package):
        gdf = utils.download_unzip_lyrpkg(**params)
        gdf = gdf.to_crs(aoi.crs)  # match crs for clip
        return gdf.clip(aoi.total_bounds)
