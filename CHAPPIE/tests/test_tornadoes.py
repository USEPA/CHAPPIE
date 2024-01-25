# -*- coding: utf-8 -*-
"""
Test tornadoes 

@author: jbousqui
"""
import os
import geopandas
from geopandas.testing import assert_geodataframe_equal
from CHAPPIE.hazards import tornadoes
import pytest


# CI inputs/expected
DIRPATH = os.path.dirname(os.path.realpath(__file__))
#DIRPATH = r'L:\Public\jbousqui\Code\GitHub\CHAPPIE\CHAPPIE\tests'

EXPECTED_DIR = os.path.join(DIRPATH, 'expected')  # Expected
DATA_DIR = os.path.join(DIRPATH, 'data')  # inputs
# TEST_DIR = os.path.join(DIRPATH, 'results')  # test results (have to create)

AOI = os.path.join(DATA_DIR, "BreakfastPoint_ServiceArea.shp")


@pytest.fixture(scope='session')
def test_get_tornadoes():
    actual = tornadoes.get_tornadoes(DATA_DIR)
    #NOTE/TODO: 1950-2022-torn-aspath is too big to save in expected?
    expected_file = os.path.join(EXPECTED_DIR, '1950-2022-torn-aspath.shp')
    expected = geopandas.read_file(expected_file)
    # First check that results are same lenth
    assert(len(actual)==len(expected)), f'{len(actual)}!={len(expected)}'
    # check same results (order doesn't matter)
    assert_geodataframe_equal(actual, expected, check_less_precise=True)
    
    return actual


# get() may need to be a fixture to assure full dataset has been downloaded 1st
def test_process_tornadoes(test_get_tornadoes):
    aoi_gdf = geopandas.read_file(AOI)
    actual = tornadoes.process_tornadoes(test_get_tornadoes, aoi_gdf)
    expected_file = os.path.join(EXPECTED_DIR, 'FLROAR20231108_Torn_Buffer_AOI_Intersection_1996_2016.shp')
    expected = geopandas.read_file(expected_file)
    
    assert_geodataframe_equal(actual, expected, check_like=True)