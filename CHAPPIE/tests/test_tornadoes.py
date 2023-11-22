# -*- coding: utf-8 -*-
"""
Test tornadoes 

@author: jbousqui
"""
import os
import geopandas
from geopandas.testing import assert_geodataframe_equal
from CHAPPIE.Hazards import tornadoes
import pytest


# CI inputs/expected
DIRPATH = os.path.dirname(os.path.realpath(__file__))
#DIRPATH = r'D:\code\CHAPPIE\CHAPPIE\tests'

EXPECTED_DIR = os.path.join(DIRPATH, 'expected')  # Expected
DATA_DIR = os.path.join(DIRPATH, 'data')  # inputs
TEST_DIR = os.path.join(DIRPATH, 'results')  # test results

AOI = os.path.join(DATA_DIR, "BreakfastPoint_ServiceArea.shp")


@pytest.fixture(scope='session')
def test_get_tornadoes():
    actual = tornadoes.get_tornadoes(TEST_DIR)
    #NOTE/TODO: 1950-2022-torn-aspath is too big to save in expected?
    expected_file = os.path.join(EXPECTED_DIR, '1950-2022-torn-aspath')
    expected = geopandas.read_file(expected_file)
    
    assert_geodataframe_equal(actual, expected, check_like=True)
    
    return actual


# get() may need to be a fixture to assure full dataset has been downloaded 1st
def test_process_tornadoes(test_get_tornadoes):
    aoi_gdf = geopandas.read_file(AOI)
    actual = tornadoes.process_tornadoes(test_get_tornadoes, aoi_gdf)
    expected_file = os.path.join(EXPECTED_DIR, 'FLROAR20231108_Torn_Buffer_AOI_Intersection_1996_2016.shp')
    expected = geopandas.read_file(expected_file)
    
    assert_geodataframe_equal(actual, expected, check_like=True)