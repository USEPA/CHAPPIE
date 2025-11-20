# -*- coding: utf-8 -*-
"""
Test technological

@author: tlomba01
"""
import os
import pytest

import geopandas
from geopandas.testing import assert_geodataframe_equal

from CHAPPIE.assets import emergency

#import pytest

# CI inputs/expected
DIRPATH = os.path.dirname(os.path.realpath(__file__))

EXPECTED_DIR = os.path.join(DIRPATH, 'expected')  # Expected
DATA_DIR = os.path.join(DIRPATH, 'data')  # inputs
TEST_DIR = os.path.join(DIRPATH, 'results')  # test results (have to create)

AOI = os.path.join(DATA_DIR, "BreakfastPoint_ServiceArea.shp")
aoi_gdf = geopandas.read_file(AOI)

@pytest.mark.skip(reason="Waiting on local env updates")
def test_get_fire_ems():
    actual = emergency.get_fire_ems(aoi_gdf)
    # Drop columns that are not needed and int (32 vs 64)
    int_cols = ["DATA_SECURITY", "LOADDATE", "FTYPE", "FCODE", "ISLANDMARK",
                "POINTLOCATIONTYPE"]
    actual.drop(columns=['OBJECTID']+int_cols, inplace=True)

    actual.sort_values(by=['PERMANENT_IDENTIFIER', 'geometry', 'NAME'],
                       inplace=True,
                       ignore_index=True)

    # assert no changes
    expected_file = os.path.join(EXPECTED_DIR, 'fire_ems.parquet')
    expected = geopandas.read_parquet(expected_file)

    assert_geodataframe_equal(actual, expected)

def test_get_police():
    actual = emergency.get_police(aoi_gdf)
    # Drop columns that are not needed and int (32 vs 64)
    int_cols = ["DATA_SECURITY", "LOADDATE", "FTYPE", "FCODE", "ISLANDMARK",
                "POINTLOCATIONTYPE"]
    actual.drop(columns=['OBJECTID']+int_cols, inplace=True)

    actual.sort_values(by=['PERMANENT_IDENTIFIER', 'geometry', 'NAME'],
                       inplace=True,
                       ignore_index=True)
    #actual.to_parquet(os.path.join(EXPECTED_DIR, 'get_police.parquet'))

    # assert no changes
    expected_file = os.path.join(EXPECTED_DIR, 'get_police.parquet')
    expected = geopandas.read_parquet(expected_file)

    assert_geodataframe_equal(actual, expected)
