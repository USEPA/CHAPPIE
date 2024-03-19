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
TEST_DIR = os.path.join(DIRPATH, 'results')  # test results (have to create)

AOI = os.path.join(DATA_DIR, "BreakfastPoint_ServiceArea.shp")
aoi_gdf = geopandas.read_file(AOI)

# get() as fixture to assure full dataset has been downloaded 1st
#@pytest.fixture(scope='session')
@pytest.mark.skip(reason="no change")
def test_get_tornadoes_all():
    actual = tornadoes.get_tornadoes_all(DATA_DIR)
    #NOTE/TODO: 1950-2022-torn-aspath is too big to save in expected?
    expected_file = os.path.join(EXPECTED_DIR, '1950-2022-torn-aspath.shp')
    expected = geopandas.read_file(expected_file)
    # First check that results are same lenth
    assert(len(actual)==len(expected)), f'{len(actual)}!={len(expected)}'
    # check same results (order doesn't matter)
    assert_geodataframe_equal(actual, expected, check_less_precise=True)
    
    return actual


#@pytest.mark.skip(reason="incomplete")
#def test_process_tornadoes_all(test_get_tornadoes):
#    actual = tornadoes.process_tornadoes(test_get_tornadoes, aoi_gdf)
#    expected_file = os.path.join(EXPECTED_DIR, 'hazards\\FLROAR20231108_Torn_Buffer_AOI_Intersection_1996_2016.shp')
#    expected = geopandas.read_file(expected_file)
    
#    assert_geodataframe_equal(actual, expected, check_like=True)
    
    
@pytest.fixture(scope='session')
def test_get_tornadoes():
    actual = tornadoes.get_tornadoes(aoi_gdf)
    
    # save for test (sorted so expeccted doesn't have to be)
    actual.sort_values(by=['geometry', 'date'], inplace=True, ignore_index=True)
    #actual.to_file(os.path.join(TEST_DIR, 'get_tornaodes_aoi.shp'))
    
    # assert no changes
    expected_file = os.path.join(EXPECTED_DIR, 'get_tornaodes_aoi.shp')
    expected = geopandas.read_file(expected_file)
    expected.sort_values(by=['geometry', 'date'], inplace=True, ignore_index=True)

    assert_geodataframe_equal(actual, expected)
    
    return actual
    

def test_process_tornadoes_aoi(test_get_tornadoes):
    actual = tornadoes.process_tornadoes(test_get_tornadoes, aoi_gdf)
    
    # save for now (sorted so expeccted doesn't have to be)
    actual.sort_values(by=['geometry', 'wid', 'Date'], inplace=True, ignore_index=True)
    #actual.to_file(os.path.join(EXPECTED_DIR, 'process_tornaodes_aoi.shp'))
    
    # check columns
    expected_cols = ['Year', 'Date', 'TornNo', 'Magnitude', 'geometry']
    missing_cols = set(expected_cols) - set(actual.columns)
    assert not missing_cols, f"Columns missing: {', '.join(missing_cols)}"
    
    # assert no changes
    expected_file = os.path.join(EXPECTED_DIR, 'process_tornaodes_aoi.shp')
    expected = geopandas.read_file(expected_file)
    expected.sort_values(by=['geometry', 'wid', 'Date'], inplace=True, ignore_index=True)
    assert_geodataframe_equal(actual, expected, check_like=True)
    
    # check rows
    #expected_file = os.path.join(EXPECTED_DIR, '1950-2022-torn-aspath.shp')
    #expected = geopandas.read_file(expected_file)
    #assert(len(actual)==len(expected)), f'{len(actual)}!={len(expected)}'
