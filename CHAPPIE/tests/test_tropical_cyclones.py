# -*- coding: utf-8 -*-
"""
Test tropical cyclones

@author: jbousqui
"""
import os

import geopandas
import pytest
from geopandas.testing import assert_geodataframe_equal

from CHAPPIE.hazards import tropical_cyclones

# CI inputs/expected
DIRPATH = os.path.dirname(os.path.realpath(__file__))
#DIRPATH = r'L:\Public\jbousqui\Code\GitHub\CHAPPIE\CHAPPIE\tests'

EXPECTED_DIR = os.path.join(DIRPATH, 'expected')  # Expected
DATA_DIR = os.path.join(DIRPATH, 'data')  # inputs
TEST_DIR = os.path.join(DIRPATH, 'results')  # test results (have to create)

AOI = os.path.join(DATA_DIR, "BreakfastPoint_ServiceArea.shp")
aoi_gdf = geopandas.read_file(AOI)


@pytest.fixture(scope='session')
def get_cyclones():
    actual = tropical_cyclones.get_cyclones(aoi_gdf)
    actual = actual.sort_values(by=["SID", "day", "USA_WIND", "geometry"],
                                ignore_index=True)
    actual.reset_index(drop=True, inplace=True)

    return actual

def test_get_cyclones(get_cyclones: DataFrame):
    actual = get_cyclones

    # assert no changes
    expected_file = os.path.join(EXPECTED_DIR, 'cyclones_aoi.parquet')
    #expected = geopandas.read_file(expected_file)
    expected = geopandas.read_parquet(expected_file)

    # save to fixture results (sorted so expected doesn't need to be)
    #actual.to_parquet(os.path.join(expected)

    field_list = ['USA_WIND', 'USA_PRES', 'year', 'month', 'day']
    for i in range(len(field_list)):
        expected[field_list[i]] = expected[field_list[i]].astype('int32')

    assert_geodataframe_equal(actual, expected)

    return actual


def test_process_cyclones(get_cyclones: DataFrame):
    actual = tropical_cyclones.process_cyclones(get_cyclones, aoi_gdf)

    # save to results
    #actual.to_file(os.path.join(TEST_DIR, 'cyclones_processed_1851_2022.shp'))

    #expected_file = os.path.join(EXPECTED_DIR,
    #                             'Hurr_Buffer_AOI_Intersection_1996_2016.shp')

    expected_file = os.path.join(EXPECTED_DIR, 'cyclones_processed.parquet')
    expected = geopandas.read_parquet(expected_file)

    actual.sort_values(by='SID', inplace=True, ignore_index=True)

    # save to results
    #actual.to_parquet(expected_file)
    field_list = ['WindSpdKts', 'PressureMb', 'Year', 'month', 'day']
    for i in range(len(field_list)):
        expected[field_list[i]] = expected[field_list[i]].astype('int32')

    assert_geodataframe_equal(actual,
                              expected,
                              check_like=True,
                              check_less_precise=True)


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

