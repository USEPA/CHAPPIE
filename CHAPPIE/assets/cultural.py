"""
Module for cultural assets

@author: tlomba01, jbousquin, edamico
"""
import geopandas
from numpy import nan

from CHAPPIE import layer_query, utils

IMLS_URL = "https://www.imls.gov/sites/default/files"
REC_AREA_URL = "https://epa.maps.arcgis.com/sharing/rest/content/items/4f14ea9215d1498eb022317458437d19/data"

def get_historic(aoi):
    """Get culturally historic sites within AOI.

    Parameters
    ----------
    aoi : geopandas.GeoDataFrame
        Spatial definition for Area Of Interest (AOI).

    Returns
    -------
    geopandas.GeoDataFrame
        GeoDataFrame for culturally historic sites.

    """

    url = 'https://services2.arcgis.com/FiaPA4ga0iQKduv3/ArcGIS/rest/services/nrhp_points_v1/FeatureServer'
    xmin, ymin, xmax, ymax = aoi.total_bounds
    bbox = [xmin, ymin, xmax, ymax]
    # out_fields = ['geometry', 'DFIRM_ID', 'FLD_AR_ID', 'FLD_ZONE', 'ZONE_SUBTY']

    return layer_query.get_bbox(aoi=bbox,
                                url=url,
                                # out_fields=out_fields,
                                layer=0,
                                in_crs=aoi.crs.to_epsg())

def get_library(aoi):
    """Get library data from IMLS.

    Parameters
    ----------
    aoi : geopandas.GeoDataFrame
        Spatial definition for Area Of Interest (AOI).

    Returns
    -------
    geopandas.GeoDataFrame
        GeoDataFrame for library points within aoi.
    """
    # TODO: use refresh or parent url to identify latest?
    zip_url = f"{IMLS_URL}/2024-06/pls_fy2022_csv.zip"

    expected_csvs = ["PLS_FY2022 PUD_CSV/PLS_FY22_AE_pud22i.csv",
                     "PLS_FY2022 PUD_CSV/pls_fy22_outlet_pud22i.csv"]

    df = utils.get_from_zip(zip_url, expected_csvs, encoding="Windows-1252")

    geom = geopandas.points_from_xy(df['LATITUDE'], df['LONGITUD'])
    gdf = geopandas.GeoDataFrame(df, geometry=geom, crs=4326)
    gdf.to_crs(aoi.crs, inplace=True)  # Coerce to export crs
    # Filter by those within aoi
    return gdf[gdf.geometry.within(aoi)]


def get_museums(aoi):
    """Get museums data from IMLS.

    Parameters
    ----------
    aoi : geopandas.GeoDataFrame
        Spatial definition for Area Of Interest (AOI).

    Returns
    -------
    geopandas.GeoDataFrame
        GeoDataFrame for museum points within aoi.
    """
    zip_url = f"{IMLS_URL}/2018_csv_museum_data_files.zip"

    expected_csvs = ["MuseumFile2018_File1_Nulls.csv",
                     "MuseumFile2018_File2_Nulls.csv",
                     "MuseumFile2018_File3_Nulls.csv"]

    df = utils.get_from_zip(zip_url, expected_csvs, encoding="Windows-1252")
    #TODO: null geom?
    df_geoms = df[['LATITUDE', 'LONGITUDE']].copy()
    df_geoms.replace(" ", nan, inplace=True)  # Must be able to coerce to float

    geom = geopandas.points_from_xy(df_geoms['LATITUDE'], df_geoms['LONGITUDE'])
    gdf = geopandas.GeoDataFrame(df, geometry=geom, crs=4326)
    gdf.to_crs(aoi.crs, inplace=True)   # Coerce to export crs
    # Filter by those within aoi
    return gdf[gdf.geometry.within(aoi)]


def get_worship(aoi):
    """Get worship locations within AOI.

    Parameters
    ----------
    aoi : geopandas.GeoDataFrame
        Spatial definition for Area Of Interest (AOI).

    Returns
    -------
    geopandas.GeoDataFrame
        GeoDataFrame for worship locations.

    """

    url = 'https://services.arcgis.com/XG15cJAlne2vxtgt/ArcGIS/rest/services/All_Places_Of_Worship__HiFLD_Open_/FeatureServer'
    xmin, ymin, xmax, ymax = aoi.total_bounds
    bbox = [xmin, ymin, xmax, ymax]

    return layer_query.get_bbox(aoi=bbox,
                                url=url,
                                layer=42,
                                in_crs=aoi.crs.to_epsg())


def get_recreationalArea():
    """Get recreational areas

    Parameters
    ----------
    None

    Returns
    -------
    geopandas.GeoDataFrame
        GeoDataFrame for recreation areas.

    """

    recAreas_gdf = utils.download_unzip_lyrpkg(REC_AREA_URL)
    return recAreas_gdf


def process_recreationalArea(aoi):
    """Process recreational areas for AOI.

    Parameters
    ----------
    recAreas_gdf : geopandas.GeoDataFrame
        Recreational areas in raw format.
    aoi : geopandas.GeoDataFrame
        Spatial definition for Area Of Interest (AOI). CRS must be in meters.

    Returns
    -------
    geopandas.GeoDataFrame
        GeoDataFrame for recreational areas with expected columns.

    """
    #get all recreational areas

    recAreas_gdf = get_recreationalArea()
    recAreas_gdf = recAreas_gdf.to_crs(aoi.crs)  # match crs for clip

    # clip buffered paths to aoi extent
    recAreas_aoi = recAreas_gdf.clip(aoi.total_bounds)

    return recAreas_aoi
