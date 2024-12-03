# -*- coding: utf-8 -*-
"""
Test health assets

@author: tlomba01, jbousqui
"""
import os

import geopandas
import pandas
import pytest
from geopandas.testing import assert_geodataframe_equal
from pandas.testing import assert_frame_equal

from CHAPPIE.assets import health

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
    actual.sort_values(by=['USER_Facil', 'geometry', 'USER_Hospi'],
                       inplace=True,
                       ignore_index=True)

    # assert no changes
    expected_file = os.path.join(EXPECTED_DIR, 'get_hospitals.parquet')
    gdf = geopandas.read_parquet(expected_file)
    gdf_int64 = gdf.select_dtypes(include='int64')
    gdf[gdf_int64.columns] = gdf_int64.astype('int32')

    assert_geodataframe_equal(actual, gdf)

#@pytest.mark.skip(reason="https://services1.arcgis.com/Hp6G80Pky0om7QvQ/ArcGIS/rest/services/Urgent_Care_Facilities/FeatureServer")
def test_get_urgent_care():
    actual = health.get_urgent_care(aoi_gdf)

    # Special handling for NASA srevice to match old HIFLD
    actual.rename(columns=str.upper, inplace=True)
    actual.rename(columns={'GEOMETRY': 'geometry'}, inplace=True)
    actual.drop(columns=['OBJECTID_1'], inplace=True)

    actual.drop(columns=['OBJECTID'], inplace=True)
    actual.sort_values(by=['ID', 'geometry', 'NAME'],
                       inplace=True,
                       ignore_index=True)

    # assert no changes
    expected_file = os.path.join(EXPECTED_DIR, 'get_urgent_care.parquet')
    expected = geopandas.read_parquet(expected_file)

    # For NASA source convert to datetime
    expected["CONTDATE"] = pandas.to_datetime(expected["CONTDATE"],
                                              unit='ms',
                                              utc=True)
    expected["GEODATE"] = pandas.to_datetime(expected["GEODATE"],
                                              unit='ms',
                                              utc=True)
    # Ensure expected times in ms
    expected["CONTDATE"] = expected["CONTDATE"].astype("datetime64[ms, UTC]")
    expected["GEODATE"] = expected["GEODATE"].astype("datetime64[ms, UTC]")

    #assert_geodataframe_equal(actual, expected)  # HIFLD
    assert_geodataframe_equal(actual.sort_index(axis=1),
                              expected.sort_index(axis=1),
                              check_less_precise=True)


@pytest.fixture(scope='session')
def providers():
    return health.get_providers(aoi_gdf)


def test_get_providers(providers: pandas.DataFrame):
    # Check zips are correct
    actual_zips = sorted(list(providers['zip5'].unique()))
    expected = ['32401', '32404', '32405', '32407', '32408', '32409',
                '32413', '32444', '32465', '32466']
    assert actual_zips==expected
    # Check number of results for each zip
    actual_len = [len(providers[providers['zip5']==zip]) for zip in expected]
    expected_len = [1069, 311, 1841, 398, 149, 26, 168, 306, 44, 27]
    assert actual_len==expected_len

    # Test result dataframes
    expected_file = os.path.join(EXPECTED_DIR, 'get_providers.parquet')
    expected = pandas.read_parquet(expected_file)  # No geo (addresses only)
    # NOTE: dict are not ordered, drop all columns where it contains a dict
    # 'addresses', 'practiceLocations', 'basic', 'endpoints', 'other_names',
    # 'taxonomies',
    cols = ['created_epoch', 'enumeration_type', 'last_updated_epoch', 'number',
            'identifiers', 'zip5']

    assert_frame_equal(providers[cols].sort_values(by='number').reset_index(drop=True),
                       expected[cols].sort_values(by='number').reset_index(drop=True))


def test_provider_address(providers: pandas.DataFrame):
    actual = health.provider_address(providers)

    expected_file = os.path.join(EXPECTED_DIR, 'provider_address.parquet')
    expected = pandas.read_parquet(expected_file)  # No geo (addresses only)

    assert_frame_equal(actual, expected)
