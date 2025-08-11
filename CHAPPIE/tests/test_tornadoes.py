# -*- coding: utf-8 -*-
"""
Test tornadoes

@author: jbousqui
"""
import os

import geopandas
import pytest
from geopandas.testing import assert_geodataframe_equal

from CHAPPIE.hazards import tornadoes

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
def get_tornadoes():
    actual = tornadoes.get_tornadoes(aoi_gdf)

    # save for test (sorted so expeccted doesn't have to be)
    actual = actual.sort_values(by=['geometry', 'date'], ignore_index=True)
    #actual.to_file(os.path.join(TEST_DIR, 'get_tornaodes_aoi.shp'))

    return actual

def expected_32(file_name):
    """
    Read expected file to GeoDataFrame and convert int 64 to int32

    Parameters
    ----------
    file_name : str
        File name in EXPECTED_DIR.

    Returns
    -------
    gdf : geopandas.GeoDataFrame
        Expected with int64 updated to int32

    """
    expected_file = os.path.join(EXPECTED_DIR, file_name)
    gdf = geopandas.read_file(expected_file)
    gdf_int64 = gdf.select_dtypes(include='int64')
    gdf[gdf_int64.columns] = gdf_int64.astype('int32')
    return gdf

def test_get_tornadoes(get_tornadoes):
    actual = get_tornadoes
    # assert no changes
    expected_file = os.path.join(EXPECTED_DIR, 'get_tornaodes_aoi.parquet')
    expected = geopandas.read_parquet(expected_file)
    #expected['date'] = expected['date'].astype('datetime64[ms]')
    #expected = expected.sort_values(by=['geometry', 'date'], ignore_index=True)

    assert_geodataframe_equal(actual, expected)

    return actual


def test_process_tornadoes_aoi(get_tornadoes):
    actual = tornadoes.process_tornadoes(get_tornadoes, aoi_gdf)

    # save for now (sorted so expeccted doesn't have to be)
    actual = actual.sort_values(by=['TornNo', 'Date'], ignore_index=True)
    #actual.to_file(os.path.join(EXPECTED_DIR, 'process_tornaodes_aoi.shp'))
    #actual.to_parquet(os.path.join(EXPECTED_DIR, 'process_tornaodes_aoi.parquet'))

    # check columns
    expected_cols = ['Year', 'Date', 'TornNo', 'Magnitude', 'geometry']
    missing_cols = set(expected_cols) - set(actual.columns)
    assert not missing_cols, f"Columns missing: {', '.join(missing_cols)}"

    # assert no changes
    expected_file = os.path.join(EXPECTED_DIR, 'process_tornaodes_aoi.parquet')
    expected = geopandas.read_parquet(expected_file)
    expected = expected.sort_values(by=['TornNo', 'Date'], ignore_index=True)
    expected['Date'] = expected['Date'].astype('datetime64[ms]')
    field_list = ['Year', 'TornNo', 'Magnitude', 'wid']
    for i in range(len(field_list)):
        expected[field_list[i]] = expected[field_list[i]].astype('int32')

    assert_geodataframe_equal(actual,
                              expected,
                              check_like=True,
                              check_less_precise=True)

def test_max_buffer():
    max_buffer = tornadoes.max_buffer()
    expected_max_buffer = 2092
    assert max_buffer == expected_max_buffer, f"Expected max buffer of {expected_max_buffer}, got {max_buffer}"
