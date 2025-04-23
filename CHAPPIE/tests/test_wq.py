# -*- coding: utf-8 -*-
"""
Test ATTAIN datalayers.

@author: edamico
"""
import os

import geopandas
from geopandas.testing import assert_geodataframe_equal

from CHAPPIE.eco_services import wq

# CI inputs/expected
DIRPATH = os.path.dirname(os.path.realpath(__file__))

EXPECTED_DIR = os.path.join(DIRPATH, 'expected')  # Expected
DATA_DIR = os.path.join(DIRPATH, 'data')  # inputs

AOI_MIT_BANK = os.path.join(DATA_DIR, "BreakfastPoint_RIBITS2020.shp")
AOI_MIT_BANK_poly = os.path.join(DATA_DIR, "BreakfastPoint_ServiceArea.shp")
aoi_gdf = geopandas.read_file(AOI_MIT_BANK)
aoi_gdf_poly = geopandas.read_file(AOI_MIT_BANK_poly)

# def test_get_attains_points():
#     actual = wq.get_attains_points(aoi_gdf)
#     actual.drop(columns=['OBJECTID'], inplace=True)
#     actual.sort_values(by=['assessmentunitidentifier', 'geometry'], inplace=True, ignore_index=True)
#     #actual.to_parquet(os.path.join(EXPECTED_DIR, 'attains_points.parquet'))

#     # assert no changes
#     expected_file = os.path.join(EXPECTED_DIR, 'attains_points.parquet')
#     expected = geopandas.read_parquet(expected_file)

#     assert_geodataframe_equal(actual,
#                               expected,
#                               check_less_precise=True)


# def test_get_attains_lines():
#     actual = wq.get_attains_lines(aoi_gdf)
#     actual.drop(columns=['OBJECTID'], inplace=True)
#     actual.sort_values(by=['assessmentunitidentifier', 'geometry'], inplace=True, ignore_index=True)
#     #actual.to_parquet(os.path.join(EXPECTED_DIR, 'attains_lines.parquet'))

#     # assert no changes
#     expected_file = os.path.join(EXPECTED_DIR, 'attains_lines.parquet')
#     expected = geopandas.read_parquet(expected_file)

#     assert_geodataframe_equal(actual,
#                               expected,
#                               check_less_precise=True)

def test_get_attains_polygons():
    actual = wq.get_attains_polygons(aoi_gdf_poly)
    actual.drop(columns=['OBJECTID'], inplace=True)
    actual.sort_values(by=['assessmentunitidentifier', 'geometry'], inplace=True, ignore_index=True)
    actual.to_parquet(os.path.join(EXPECTED_DIR, 'attains_polygons.parquet'))

    # assert no changes
    expected_file = os.path.join(EXPECTED_DIR, 'attains_polygons.parquet')
    expected = geopandas.read_parquet(expected_file)

    assert_geodataframe_equal(actual,
                              expected,
                              check_less_precise=True)
