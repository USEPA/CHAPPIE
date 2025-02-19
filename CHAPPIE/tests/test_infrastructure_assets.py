# -*- coding: utf-8 -*-
"""
Test hazard mitigating infrastructure assets.

@author: tlomba01
"""
import os

import geopandas
from geopandas.testing import assert_geodataframe_equal

from CHAPPIE.assets import hazard_infrastructure

# CI inputs/expected
DIRPATH = os.path.dirname(os.path.realpath(__file__))

EXPECTED_DIR = os.path.join(DIRPATH, 'expected')  # Expected
DATA_DIR = os.path.join(DIRPATH, 'data')  # inputs

AOI = os.path.join(DATA_DIR, "BreakfastPoint_ServiceArea.shp")
AOI2 = os.path.join(DATA_DIR, "LittlePineIsland_ServiceArea.shp")
aoi_gdf = geopandas.read_file(AOI)
aoi_gdf2 = geopandas.read_file(AOI2)


def test_get_dams():
    actual = hazard_infrastructure.get_dams(aoi_gdf)
    actual.drop(columns=['OBJECTID', "primaryPurposeId"], inplace=True)
    # Note: "primaryPurposeId"==None is problematic
    actual.sort_values(by=['id', 'name'], inplace=True, ignore_index=True)

    expected_file = os.path.join(EXPECTED_DIR, 'dams.parquet')
    expected = geopandas.read_parquet(expected_file)

    # Overwrite results
    #actual.to_parquet(expected_file)

    field_list = ['nidHeight', 'distance', 'damHeight', 'damLength', 'volume',
                  'nidStorage', 'normalStorage', 'surfaceArea']
    for col in field_list:
        expected[col] = expected[col].astype('int32')
    
    col_list = ["dataUpdated", "inspectionDate", "conditionAssessDate"]
    for col in col_list:
        expected[col] = expected[col].astype('datetime64[ms, UTC]')

    assert_geodataframe_equal(actual, expected, check_less_precise=True)


def test_get_levees():
    actual = hazard_infrastructure.get_levee(aoi_gdf2)
    assert isinstance(actual, geopandas.geodataframe.GeoDataFrame)
    actual.drop(columns=['OBJECTID'], inplace=True)
    actual.sort_values(by=['SYSTEM_ID', 'SYSTEM_NAME'], inplace=True, ignore_index=True)

    expected_file = os.path.join(EXPECTED_DIR, 'levees.parquet')
    expected = geopandas.read_parquet(expected_file)

    assert_geodataframe_equal(actual, expected)
