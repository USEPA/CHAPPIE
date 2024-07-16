# -*- coding: utf-8 -*-
"""
Test technological 

@author: tlomba01
"""
import os
import geopandas
from geopandas.testing import assert_geodataframe_equal
from CHAPPIE.assets import health
#import pytest

# CI inputs/expected
DIRPATH = os.path.dirname(os.path.realpath(__file__))

EXPECTED_DIR = os.path.join(DIRPATH, 'expected')  # Expected
DATA_DIR = os.path.join(DIRPATH, 'data')  # inputs
TEST_DIR = os.path.join(DIRPATH, 'results')  # test results (have to create)

AOI = os.path.join(DATA_DIR, "BreakfastPoint_ServiceArea.shp")
aoi_gdf = geopandas.read_file(AOI)

def test_get_hospitals():
    actual = health.get_hospitals(aoi_gdf)
    actual.drop(columns=['FID'], inplace=True)
    actual.sort_values(by=['USER_Facil', 'geometry', 'USER_Hospi'], inplace=True, ignore_index=True)

    # assert no changes
    expected_file = os.path.join(EXPECTED_DIR, 'get_hospitals.parquet')
    gdf = geopandas.read_parquet(expected_file)
    gdf_int64 = gdf.select_dtypes(include='int64')
    gdf[gdf_int64.columns] = gdf_int64.astype('int32')
    
    assert_geodataframe_equal(actual, gdf)
