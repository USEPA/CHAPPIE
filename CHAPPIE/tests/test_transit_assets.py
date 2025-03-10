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

AOI = os.path.join(DATA_DIR, "BreakfastPoint_ServiceArea.shp")
aoi_gdf = geopandas.read_file(AOI)


def test_get_air():
    actual = transit.get_air(aoi_gdf)
    actual.drop(columns=['OBJECTID'], inplace=True)
    actual.rename(columns={'GEOMETRY': 'geometry'}, inplace=True)
    actual.sort_values(by=['ARPT_ID', 'geometry', 'ARPT_NAME'],
                       inplace=True,
                       ignore_index=True)
    #actual.to_parquet(os.path.join(EXPECTED_DIR, 'get_air.parquet'))

    # assert no changes
    expected_file = os.path.join(EXPECTED_DIR, 'get_air.parquet')
    expected = geopandas.read_parquet(expected_file)

   
    assert_geodataframe_equal(actual.sort_index(axis=1),
                              expected.sort_index(axis=1),
                              check_less_precise=True)

def test_get_bus():
    actual = transit.get_bus(aoi_gdf)
    actual.drop(columns=['OBJECTID'], inplace=True)
    actual.rename(columns={'GEOMETRY': 'geometry'}, inplace=True)
    sortList = ["ntd_id","stop_id","stop_name", 'geometry']
    actual.sort_values(by=sortList,
                       inplace=True,
                       ignore_index=True)
    #actual.to_parquet(os.path.join(EXPECTED_DIR, 'get_bus.parquet'))

    # assert no changes
    expected_file = os.path.join(EXPECTED_DIR, 'get_bus.parquet')
    expected = geopandas.read_parquet(expected_file)
    assert_geodataframe_equal(actual.sort_index(axis=1),
                              expected.sort_index(axis=1),
                              check_less_precise=True)



def test_get_rail():
    actual = transit.get_rail(aoi_gdf)
    actual.rename(columns={'GEOMETRY': 'geometry'}, inplace=True)
    #actual.to_parquet(os.path.join(EXPECTED_DIR, 'get_rail.parquet'))

    # assert no changes
    expected_file = os.path.join(EXPECTED_DIR, 'get_rail.parquet')
    expected = geopandas.read_parquet(expected_file)

   
    assert_geodataframe_equal(actual.sort_index(axis=1),
                              expected.sort_index(axis=1),
                              check_less_precise=True)
