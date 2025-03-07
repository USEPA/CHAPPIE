# -*- coding: utf-8 -*-
"""
Test transit assets.

@author: edamico
"""
import os

import geopandas
from geopandas.testing import assert_geodataframe_equal

from CHAPPIE.assets import transit

# CI inputs/expected
DIRPATH = os.path.dirname(os.path.realpath(__file__))

EXPECTED_DIR = os.path.join(DIRPATH, 'expected')  # Expected
DATA_DIR = os.path.join(DIRPATH, 'data')  # inputs
TEST_DIR = os.path.join(DIRPATH, 'results')  # test results (have to create)
PARCEL_DIR = os.path.join(EXPECTED_DIR, 'parcels')

AOI = os.path.join(DATA_DIR, "BreakfastPoint_ServiceArea.shp")
PARCELS = os.path.join(PARCEL_DIR, "BP_Regrid.shp")
aoi_gdf = geopandas.read_file(AOI)
parcels_gdf = geopandas.read_file(PARCELS)

def test_get_air():
    actual = transit.get_air(aoi_gdf)
    actual.drop(columns=['OBJECTID'], inplace=True)
    #actual.to_parquet(os.path.join(EXPECTED_DIR, 'get_air.parquet'))

    # assert no changes
    expected_file = os.path.join(EXPECTED_DIR, 'get_air.parquet')
    expected = geopandas.read_parquet(expected_file)

    assert_geodataframe_equal(actual, expected)

def test_get_bus():
    actual = transit.get_bus(aoi_gdf)
    actual.drop(columns=['OBJECTID'], inplace=True)
    #actual.to_parquet(os.path.join(EXPECTED_DIR, 'get_bus.parquet'))

    # assert no changes
    expected_file = os.path.join(EXPECTED_DIR, 'get_bus.parquet')
    expected = geopandas.read_parquet(expected_file)

    assert_geodataframe_equal(actual, expected)

def test_get_rail():
    actual = transit.get_rail(aoi_gdf)
    #actual.drop(columns=['OBJECTID'], inplace=True)
    #actual.to_parquet(os.path.join(EXPECTED_DIR, 'get_rail.parquet'))

    # assert no changes
    expected_file = os.path.join(EXPECTED_DIR, 'get_rail.parquet')
    expected = geopandas.read_parquet(expected_file)

    assert_geodataframe_equal(actual, expected)
