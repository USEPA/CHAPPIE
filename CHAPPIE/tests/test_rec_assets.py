# -*- coding: utf-8 -*-
"""
Test recreation assets. 

@author: tlomba01, edamico
"""
import os
import geopandas
from geopandas.testing import assert_geodataframe_equal
from CHAPPIE.assets import recreation

# CI inputs/expected
DIRPATH = os.path.dirname(os.path.realpath(__file__))

EXPECTED_DIR = os.path.join(DIRPATH, 'expected')  # Expected
DATA_DIR = os.path.join(DIRPATH, 'data')  # inputs

AOI_MIT_BANK = os.path.join(DATA_DIR, "BreakfastPoint_RIBITS2020.shp")
AOI_MIT_BANK_SA = os.path.join(DATA_DIR, "BreakfastPoint_ServiceArea.shp")
aoi_gdf = geopandas.read_file(AOI_MIT_BANK)
aoi_gdf_sa = geopandas.read_file(AOI_MIT_BANK_SA) 

def test_get_padus():
    actual = recreation.get_padus(aoi_gdf)
    actual.drop(columns=['OBJECTID'], inplace=True)
    actual.sort_values(by=['Unit_Nm', 'geometry'], inplace=True, ignore_index=True)
    #actual.to_parquet(os.path.join(EXPECTED_DIR, 'padus.parquet'))

    # assert no changes
    expected_file = os.path.join(EXPECTED_DIR, 'padus.parquet')
    expected = geopandas.read_parquet(expected_file)
 
    assert_geodataframe_equal(actual, 
                              expected,
                              check_less_precise=True)


def test_get_parks():
    actual = recreation.get_parks(aoi_gdf_sa)
    actual.drop(columns=['OBJECTID'], inplace=True)
    actual.sort_values(by=['NAME', 'geometry'], inplace=True, ignore_index=True)
    actual.rename(columns={'GEOMETRY': 'geometry'}, inplace=True)
    #actual.to_parquet(os.path.join(EXPECTED_DIR, 'park.parquet'))

    #assert no changes
    expected_file = os.path.join(EXPECTED_DIR, 'park.parquet')
    expected = geopandas.read_parquet(expected_file)
 
    assert_geodataframe_equal(actual, 
                              expected,
                              check_less_precise=True)
    
def test_get_trails():
    actual = recreation.get_trails(aoi_gdf_sa)
    actual.drop(columns=['objectid'], inplace=True)
    actual.sort_values(by=['permanentidentifier', 'geometry'], inplace=True, ignore_index=True)
    actual.rename(columns={'GEOMETRY': 'geometry'}, inplace=True)
   # actual.to_parquet(os.path.join(EXPECTED_DIR, 'trails.parquet'))

    #assert no changes
    expected_file = os.path.join(EXPECTED_DIR, 'trails.parquet')
    expected = geopandas.read_parquet(expected_file)
 
    assert_geodataframe_equal(actual, 
                              expected,
                              check_less_precise=True)