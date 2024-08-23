# -*- coding: utf-8 -*-
"""
Test technological 

@author: tlomba01
"""
import os
import geopandas
from geopandas.testing import assert_geodataframe_equal
from CHAPPIE.assets import education
#import pytest

# CI inputs/expected
DIRPATH = os.path.dirname(os.path.realpath(__file__))

EXPECTED_DIR = os.path.join(DIRPATH, 'expected')  # Expected
DATA_DIR = os.path.join(DIRPATH, 'data')  # inputs
TEST_DIR = os.path.join(DIRPATH, 'results')  # test results (have to create)

AOI = os.path.join(DATA_DIR, "BreakfastPoint_ServiceArea.shp")
aoi_gdf = geopandas.read_file(AOI)


def test_get_schools_public():
    actual = education.get_schools_public(aoi_gdf)
    actual.drop(columns=['OBJECTID'], inplace=True)
    actual.sort_values(by=['NCESID', 'geometry', 'NAME'], inplace=True, ignore_index=True)

    # assert no changes
    expected_file = os.path.join(EXPECTED_DIR, 'schools_public.parquet')
    expected = geopandas.read_parquet(expected_file)
    
    assert_geodataframe_equal(actual, expected)

def test_get_schools_private():
    actual = education.get_schools_private(aoi_gdf)
    actual.drop(columns=['OBJECTID'], inplace=True)
    actual.sort_values(by=['NCESID', 'geometry', 'NAME'], inplace=True, ignore_index=True)
    #actual.to_parquet(os.path.join(EXPECTED_DIR, 'schools_private.parquet'))

    # assert no changes
    expected_file = os.path.join(EXPECTED_DIR, 'schools_private.parquet')
    expected = geopandas.read_parquet(expected_file)
    
    assert_geodataframe_equal(actual, expected)