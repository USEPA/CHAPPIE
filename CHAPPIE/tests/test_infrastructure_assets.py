# -*- coding: utf-8 -*-
"""
Test food assets. 

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
aoi_gdf = geopandas.read_file(AOI)


def test_get_dams():
    actual = hazard_infrastructure.get_dams(aoi_gdf)
    actual.drop(columns=['OBJECTID'], inplace=True)
    actual.sort_values(by=['id', 'name'], inplace=True, ignore_index=True)
    
    expected_file = os.path.join(EXPECTED_DIR, 'dams.parquet')
    expected = geopandas.read_parquet(expected_file)
 
    assert_geodataframe_equal(actual, expected)