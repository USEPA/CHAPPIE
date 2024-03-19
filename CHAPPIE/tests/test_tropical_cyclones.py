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

EXPECTED_DIR = os.path.join(DIRPATH, 'expected')  # Expected
DATA_DIR = os.path.join(DIRPATH, 'data')  # inputs
TEST_DIR = os.path.join(DIRPATH, 'results')  # test results (have to create)

AOI = os.path.join(DATA_DIR, "BreakfastPoint_ServiceArea.shp")
aoi_gdf = geopandas.read_file(AOI)


@pytest.fixture(scope='session')
def test_get_cyclones():
    actual = tropical_cyclones.get_cyclones(aoi_gdf)
    
    # save to results (sorted so expected doesn't need to be)
    #actual.sort_values(by=['geometry','day'], inplace=True, ignore_index=True)
    #actual.to_file(os.path.join(TEST_DIR, 'cyclones_aoi_1851_2022.shp'))
    
    # assert no changes
    expected_file = os.path.join(EXPECTED_DIR, 'cyclones_aoi_1851_2022.shp')
    expected = geopandas.read_file(expected_file)

    actual.sort_values(by=['geometry','day'], inplace=True, ignore_index=True)
    
    assert_geodataframe_equal(actual, expected)
    
    return actual


def test_process_cyclones(test_get_cyclones):
    actual = tropical_cyclones.process_cyclones(test_get_cyclones, aoi_gdf)
    
    # save to results
    #actual.to_file(os.path.join(TEST_DIR, 'cyclones_processed_1851_2022.shp'))
    
    #expected_file = os.path.join(EXPECTED_DIR,
    #                             'Hurr_Buffer_AOI_Intersection_1996_2016.shp')
    expected_file = os.path.join(EXPECTED_DIR,'cyclones_processed_1851_2022.shp')
    expected = geopandas.read_file(expected_file)    

    assert_geodataframe_equal(actual, expected, check_like=True)
    #assert(len(actual)==len(expected)), f'{len(actual)}!={len(expected)}'


@pytest.mark.skip(reason="depricating")
def test_get_cyclones_all():
    actual = tropical_cyclones.get_cyclones_all(DATA_DIR, ['points'])

    # TODO: subset result and then save it to test against (replacing <FILE>)
    # Restrict to ~CONUS for test (full is too big)
    #min_y, max_y = 24, 50
    #min_x, max_x = -125, -66

    expected_file = os.path.join(EXPECTED_DIR, '<FILE>')
    expected = geopandas.read_file(expected_file)

    assert_geodataframe_equal(actual, expected, check_like=True)

