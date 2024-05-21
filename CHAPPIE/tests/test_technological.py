# -*- coding: utf-8 -*-
"""
Test technological 

@author: thultgre
"""
import os
import geopandas
from geopandas.testing import assert_geodataframe_equal
from CHAPPIE.hazards import technological
import pytest

# CI inputs/expected
DIRPATH = os.path.dirname(os.path.realpath(__file__))

EXPECTED_DIR = os.path.join(DIRPATH, 'expected')  # Expected
DATA_DIR = os.path.join(DIRPATH, 'data')  # inputs
TEST_DIR = os.path.join(DIRPATH, 'results')  # test results (have to create)

AOI = os.path.join(DATA_DIR, "BreakfastPoint_ServiceArea.shp")
aoi_gdf = geopandas.read_file(AOI)

def test_get_superfund():
    actual = technological.get_superfund_npl(aoi_gdf)

    # assert no changes
    expected_file = os.path.join(EXPECTED_DIR, 'get_superfund.parquet')
    expected = geopandas.read_parquet(expected_file)

    assert_geodataframe_equal(actual, expected)
    
    return actual
