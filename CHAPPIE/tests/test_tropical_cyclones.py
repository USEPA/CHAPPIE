# -*- coding: utf-8 -*-
"""
Test tropical cyclones 

@author: jbousqui
"""
import os
import geopandas
from geopandas.testing import assert_geodataframe_equal
from CHAPPIE.hazards import tropical_cyclones
import pytest

# CI inputs/expected
DIRPATH = os.path.dirname(os.path.realpath(__file__))
#DIRPATH = r'L:\Public\jbousqui\Code\GitHub\CHAPPIE\CHAPPIE\tests'

EXPECTED_DIR = os.path.join(DIRPATH, f'expected{os.sep}hazards')  # Expected
DATA_DIR = os.path.join(DIRPATH, 'data')  # inputs
TEST_DIR = os.path.join(DIRPATH, 'results')  # test results (have to create)

AOI = os.path.join(DATA_DIR, "BreakfastPoint_ServiceArea.shp")
aoi_gdf = geopandas.read_file(AOI)


@pytest.fixture(scope='session')
def test_get_tropical_cyclones_aoi():
    actual = tropical_cyclones.get_tropical_cyclones_aoi(aoi_gdf)
    
    # save for now
    #actual.to_file(os.path.join(TEST_DIR, 'get_cyclones_aoi.shp'))

    return actual


def test_process_tropical_cyclones_aoi(test_get_tropical_cyclones_aoi):
    actual = tropical_cyclones.process_tropical_cyclones_aoi(test_get_tropical_cyclones_aoi, aoi_gdf)
    expected_file = os.path.join(EXPECTED_DIR, 'Hurr_Buffer_AOI_Intersection_1996_2016.shp')
    expected = geopandas.read_file(expected_file)    
    
    assert_geodataframe_equal(actual, expected, check_like=True)


@pytest.mark.skip(reason="depricating")
def test_get_tropical_cyclones():
    actual = tropical_cyclones.get_tropical_cyclones(DATA_DIR, ['points'])

    # Restrict to ~CONUS for test
    min_y, max_y = 24, 50
    min_x, max_x = -125, -66

    expected_file = os.path.join(EXPECTED_DIR, '<FILE>')
    expected = geopandas.read_file(expected_file)

    assert_geodataframe_equal(actual, expected, check_like=True)


# get() may need to be a fixture to assure full dataset has been downloaded 1st
@pytest.mark.skip(reason="incomplete")
def test_process_tropical_cyclones():
    #aoi_input = geopandas.read_file()  # may be able to pass it filename
    actual = tropical_cyclones.process_tropical_cyclones()
    expected_file = os.path.join(EXPECTED_DIR, '<FILE>')
    expected = geopandas.read_file(expected_file)
    
    assert_geodataframe_equal(actual, expected, check_like=True)