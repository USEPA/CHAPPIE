# -*- coding: utf-8 -*-
"""
Test health assets

@author: tlomba01, jbousqui
"""
import os
from unittest.mock import MagicMock, patch

import geopandas
import pandas
import pytest
from geopandas.testing import assert_geodataframe_equal
from pandas.testing import assert_frame_equal
from requests.exceptions import ConnectionError, HTTPError

from CHAPPIE.assets import health

# get key from env
geocode_api_key = os.environ['GEOCODE_API_KEY']

# CI inputs/expected
DIRPATH = os.path.dirname(os.path.realpath(__file__))

EXPECTED_DIR = os.path.join(DIRPATH, 'expected')  # Expected
DATA_DIR = os.path.join(DIRPATH, 'data')  # inputs
TEST_DIR = os.path.join(DIRPATH, 'results')  # test results (have to create)

PROVIDER_ADDRESSES = os.path.join(EXPECTED_DIR, "provider_address.parquet")
AOI = os.path.join(DATA_DIR, "BreakfastPoint_ServiceArea.shp")
aoi_gdf = geopandas.read_file(AOI)
provider_address_df = pandas.read_parquet(PROVIDER_ADDRESSES)

def test_get_hospitals():
    actual = health.get_hospitals(aoi_gdf)
    #actual.drop(columns=['FID'], inplace=True)
    actual.drop(columns=['ObjectID'], inplace=True)
    sort_cols = ["USER_Facility_ID", "geometry", "USER_Hospital_Type"]
    actual.sort_values(by=sort_cols, inplace=True, ignore_index=True)

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

@pytest.fixture(scope="session")
def static_providers():
    expected_file = os.path.join(EXPECTED_DIR, 'static_providers.parquet')
    return pandas.read_parquet(expected_file)

def test_get_providers(providers: pandas.DataFrame):
    # Check zips are correct
    actual_zips = sorted(list(providers['zip5'].unique()))
    expected = ['32401', '32404', '32405', '32407', '32408', '32409',
                '32413', '32444', '32465', '32466']
    assert actual_zips==expected
    # Check number of results for each zip
    actual_len = [len(providers[providers['zip5']==zip]) for zip in expected]
    #expected_len = [1069, 311, 1841, 398, 149, 26, 168, 306, 44, 27]
    #expected_len = [1071, 311, 1841, 398, 149, 26, 168, 306, 44, 27]
    expected_len = [1072, 313, 1849, 412, 155, 28, 171, 309, 46, 29]
    assert actual_len==expected_len

    # Test result dataframes
    expected_file = os.path.join(EXPECTED_DIR, 'get_providers.parquet')
    expected = pandas.read_parquet(expected_file)  # No geo (addresses only)
    # NOTE: dict are not ordered, drop all columns where it contains a dict
    # 'addresses', 'practiceLocations', 'basic', 'endpoints', 'other_names',
    # 'taxonomies',
    cols = ['created_epoch', 'enumeration_type', 'last_updated_epoch', 'number',
            'identifiers', 'zip5']

    assert_frame_equal(providers[cols].sort_values(by=['number', 'zip5']).reset_index(drop=True),
                       expected[cols].sort_values(by=['number', 'zip5']).reset_index(drop=True))


def test_provider_address(static_providers: pandas.DataFrame):
    actual = health.provider_address(static_providers)

    expected_file = os.path.join(EXPECTED_DIR, 'provider_address.parquet')
    expected = pandas.read_parquet(expected_file)  # No geo (addresses only)
    cols = ['address_1', 'address_2', 'city', 'state', 'postal_code']

    # Overwite expected with actual (only used to update results)
    #actual.to_parquet(expected_file)

    assert_frame_equal(actual.sort_values(by=cols), expected.sort_values(by=cols))


def test_batch_geocode():
    actual = health.batch_geocode(provider_address_df, geocode_api_key)
    actual.sort_values(by=['OBJECTID'], inplace=True)
    assert len(actual) == len(provider_address_df)
    #actual.to_file(os.path.join(EXPECTED_DIR, 'provider_geocode.shp'))
    #actual.to_parquet(os.path.join(EXPECTED_DIR, 'provider_geocode.parquet'))
    assert isinstance(actual, geopandas.geodataframe.GeoDataFrame)

    expected_file = os.path.join(EXPECTED_DIR, 'provider_geocode.parquet')
    expected = geopandas.read_parquet(expected_file)

    assert_geodataframe_equal(actual, expected, check_less_precise=True)


#Test how Connection error is handled, but patch the post_request call
@patch('CHAPPIE.assets.health.requests.post')
def test_post_request_connection_error(mock_post):
    mock_resp = MagicMock()
    mock_resp.raise_for_status.side_effect = ConnectionError
    mock_post.return_value = mock_resp
    url = "https://fake.epa.gov/GeocodeServer"
    data = {}

    result = health.post_request(url=url, data=data)
    #assert mock_resp.raise_for_status.called
    assert mock_resp.raise_for_status.called == True
    assert mock_post.call_count == 2 # Ensures the mocked method was called twice (one plus a retry)
    assert result == {"url": url, "status": "error", "reason": "Connection error, 2 attempts", "text": ""}


# Test other exception branch of post_request function, which has no retry
@patch('CHAPPIE.assets.health.requests.post')
def test_post_request_502_error(mock_post):
    mock_resp = MagicMock()
    mock_resp.status_code = 502
    mock_resp.raise_for_status.side_effect = HTTPError
    mock_post.return_value = mock_resp
    url = "https://fake.epa.gov/GeocodeServer"
    data = {}

    result = health.post_request(url=url, data=data)
    #assert mock_resp.raise_for_status.called
    assert mock_resp.raise_for_status.called == True
    assert mock_post.call_count == 1 # Ensures the mocked method was called once, no retries
    assert result == {"url": url, "data": data, "status": 502}

# patch post_request function response to have no 'token' in response.keys; expect a ValueError
@patch('CHAPPIE.assets.health.requests.post')
def test_get_geocode_token_keys(mock_post):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        'tokn': 'ttt'
    }
    mock_post.return_value = mock_resp
    username = 'chaps'
    with pytest.raises(ValueError):
        health.get_geocode_token(user_name=username)


