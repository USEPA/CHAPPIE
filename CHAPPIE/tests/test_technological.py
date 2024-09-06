# -*- coding: utf-8 -*-
"""
Test technological 

@author: thultgre
"""
import os
import geopandas
from geopandas.testing import assert_geodataframe_equal
from CHAPPIE.hazards import technological
#import pytest

# CI inputs/expected
DIRPATH = os.path.dirname(os.path.realpath(__file__))

EXPECTED_DIR = os.path.join(DIRPATH, 'expected')  # Expected
DATA_DIR = os.path.join(DIRPATH, 'data')  # inputs
TEST_DIR = os.path.join(DIRPATH, 'results')  # test results (have to create)

AOI = os.path.join(DATA_DIR, "BreakfastPoint_ServiceArea.shp")
aoi_gdf = geopandas.read_file(AOI)


def expected_32(parquet_name):
    """
    Read expected parquet to GeoDataFrame and convert int 64 to int32

    Parameters
    ----------
    parquet_name : str
        Parquet file name in EXPECTED_DIR.

    Returns
    -------
    gdf : geopandas.GeoDataFrame
        Expected with int64 updated to int32

    """
    expected_file = os.path.join(EXPECTED_DIR, parquet_name)
    gdf = geopandas.read_parquet(expected_file)
    gdf_int64 = gdf.select_dtypes(include='int64')
    gdf[gdf_int64.columns] = gdf_int64.astype('int32')
    return gdf


def test_get_superfund():
    actual = technological.get_superfund_npl(aoi_gdf)
    actual.drop(columns=['OBJECTID'], inplace=True)
    #actual.to_parquet(os.path.join(EXPECTED_DIR, 'get_superfund.parquet'))
    
    # assert no changes
    expected_file = os.path.join(EXPECTED_DIR, 'get_superfund.parquet')
    expected = geopandas.read_parquet(expected_file)
    expected['REGION_CODE'] = expected['REGION_CODE'].astype('int32')
    expected['SITE_FEATURE_CLASS'] = expected['SITE_FEATURE_CLASS'].astype('int32')

    assert_geodataframe_equal(actual, expected)

def test_get_FRS_ACRES():
    actual = technological.get_FRS_ACRES(aoi_gdf)
    actual.drop(columns=['OBJECTID'], inplace=True)
    actual.sort_values(by=['KEY_FIELD', 'geometry', 'REGISTRY_ID'], inplace=True, ignore_index=True)
    #actual.to_parquet(os.path.join(EXPECTED_DIR, 'get_FRS_ACRES.parquet'))

    # assert no changes
    expected_file = os.path.join(EXPECTED_DIR, 'get_FRS_ACRES.parquet')
    expected = geopandas.read_parquet(expected_file)
    expected['ACCURACY_VALUE'] = expected['ACCURACY_VALUE'].astype('int32')
 
    assert_geodataframe_equal(actual, expected)

def test_get_landfills():
    actual = technological.get_landfills(aoi_gdf)
    actual.drop(columns=['OBJECTID'], inplace=True)
    actual.sort_values(by=['GlobalID', 'geometry', 'Company'], inplace=True, ignore_index=True)
 
    # assert no changes
    expected = expected_32('get_landfills.parquet')
    
    assert_geodataframe_equal(actual, expected, normalize=True)

def test_get_tri():
    actual = technological.get_tri(aoi_gdf)
    actual.drop(columns=['OBJECTID'], inplace=True)
    actual.sort_values(by=['EPA_REGISTRY_ID', 'geometry', 'FACILITY_NAME'], inplace=True, ignore_index=True)
 
    # assert no changes
    expected = expected_32('get_tri.parquet')
    
    assert_geodataframe_equal(actual, expected, normalize=True)