# -*- coding: utf-8 -*-
"""
Test flood 

@author: tlomba01
"""
import os
import geopandas
from geopandas.testing import assert_geodataframe_equal
from CHAPPIE.hazards import flood
# import pytest

# CI inputs/expected
DIRPATH = os.path.dirname(os.path.realpath(__file__))

EXPECTED_DIR = os.path.join(DIRPATH, 'expected')  # Expected
DATA_DIR = os.path.join(DIRPATH, 'data')  # inputs
TEST_DIR = os.path.join(DIRPATH, 'results')  # test results (have to create)

AOI = os.path.join(DATA_DIR, "BreakfastPoint_ServiceArea.shp")
aoi_gdf = geopandas.read_file(AOI)

def test_get_fema_nfhl():
    actual = flood.get_fema_nfhl(aoi_gdf)
    actual.drop(columns=['OBJECTID', 'VERSION_ID', 'STUDY_TYP', 'SFHA_TF', 
                         'STATIC_BFE', 'V_DATUM', 'DEPTH', 'LEN_UNIT', 
                         'VELOCITY', 'VEL_UNIT', 'DUAL_ZONE', 'SOURCE_CIT', 
                         'GFID', 'esri_symbology', 'GlobalID', 'Shape__Area', 
                         'Shape__Length'], inplace=True)
    actual.sort_values(by=['DFIRM_ID', 'FLD_AR_ID', 'geometry'], inplace=True, ignore_index=True)
    #actual.to_parquet(os.path.join(EXPECTED_DIR, 'get_fema_nfhl.parquet'))

    # assert no changes
    expected_file = os.path.join(EXPECTED_DIR, 'get_fema_nfhl.parquet')
    expected = geopandas.read_parquet(expected_file)
 
    assert_geodataframe_equal(actual, 
                              expected,
                              check_like=True,
                              check_less_precise=True)