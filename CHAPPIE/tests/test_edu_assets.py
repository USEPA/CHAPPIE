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
base_url = "https://services1.arcgis.com/Hp6G80Pky0om7QvQ/arcgis/rest/services/"

def test_get_schools_public():
    actual = education.get_schools_public(base_url, aoi_gdf)
    actual.drop(columns=['OBJECTID'], inplace=True)
    actual.sort_values(by=['NCESID', 'geometry', 'NAME'], inplace=True, ignore_index=True)

    # assert no changes
    expected_file = os.path.join(EXPECTED_DIR, 'schools_public.parquet')
    expected = geopandas.read_parquet(expected_file)
    
    assert_geodataframe_equal(actual, expected)
