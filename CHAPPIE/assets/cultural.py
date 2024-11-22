"""
Module for cultural assets

@author: tlomba01, jbousquin
"""
import geopandas
from numpy import nan
from CHAPPIE import layer_query


IMLS_URL = "https://www.imls.gov/sites/default/files"

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

    df = layer_query.get_from_zip(zip_url, expected_csvs, encoding="Windows-1252")
    
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

    df = layer_query.get_from_zip(zip_url, expected_csvs, encoding="Windows-1252")
    #TODO: null geom?
    df_geoms = df[['LATITUDE', 'LONGITUDE']].copy()
    df_geoms.replace(" ", nan, inplace=True)  # Must be able to coerce to float
    
    geom = geopandas.points_from_xy(df_geoms['LATITUDE'], df_geoms['LONGITUDE'])
    gdf = geopandas.GeoDataFrame(df, geometry=geom, crs=4326)
    gdf.to_crs(aoi.crs, inplace=True)   # Coerce to export crs
    # Filter by those within aoi
    return gdf[gdf.geometry.within(aoi)]