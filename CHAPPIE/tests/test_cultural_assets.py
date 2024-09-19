# -*- coding: utf-8 -*-
"""
Test flood 

@author: tlomba01
"""
import os
import geopandas
from geopandas.testing import assert_geodataframe_equal
from CHAPPIE.assets import cultural

# CI inputs/expected
DIRPATH = os.path.dirname(os.path.realpath(__file__))

EXPECTED_DIR = os.path.join(DIRPATH, 'expected')  # Expected
DATA_DIR = os.path.join(DIRPATH, 'data')  # inputs

AOI = os.path.join(DATA_DIR, "BreakfastPoint_ServiceArea.shp")
aoi_gdf = geopandas.read_file(AOI)

def test_get_fema_nfhl():
    actual = cultural.get_historic(aoi_gdf)
    actual.drop(columns=['OBJECTID'], inplace=True)
    actual.sort_values(by=['CertDate', 'RESNAME', 'geometry'], inplace=True, ignore_index=True)
    #actual.to_parquet(os.path.join(EXPECTED_DIR, 'cultural_historic.parquet'))

    # assert no changes
    expected_file = os.path.join(EXPECTED_DIR, 'cultural_historic.parquet')
    expected = geopandas.read_parquet(expected_file)
 
    assert_geodataframe_equal(actual, 
                              expected)