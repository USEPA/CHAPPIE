# -*- coding: utf-8 -*-
"""
Test cultural assets

@author: tlomba01, jbousquin, edamico
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
AOI_MIT_BANK_SA = os.path.join(DATA_DIR, "BreakfastPoint_ServiceArea.shp")
aoi_gdf = geopandas.read_file(AOI)
aoi_gdf_sa = geopandas.read_file(AOI_MIT_BANK_SA)

def test_get_historic():
    actual = cultural.get_historic(aoi_gdf)
    actual.drop(columns=['OBJECTID'], inplace=True)
    actual.sort_values(by=['CertDate', 'RESNAME', 'geometry'],
                       inplace=True,
                       ignore_index=True)
    #actual.to_parquet(os.path.join(EXPECTED_DIR, 'cultural_historic.parquet'))

    # assert no changes
    expected_file = os.path.join(EXPECTED_DIR, 'cultural_historic.parquet')
    expected = geopandas.read_parquet(expected_file)

    assert_geodataframe_equal(actual,
                              expected)


def test_get_library():
    actual = cultural.get_library(aoi_gdf)
    actual.sort_values(by=['LIBID', 'geometry'], inplace=True, ignore_index=True)

    # assert no changes
    expected_file = os.path.join(EXPECTED_DIR, 'cultural_lib.parquet')
    expected = geopandas.read_parquet(expected_file)

    assert_geodataframe_equal(actual,
                              expected)


def test_get_museums():
    actual = cultural.get_museums(aoi_gdf)
    actual.sort_values(by=['MID', 'geometry'], inplace=True, ignore_index=True)

    # assert no changes
    expected_file = os.path.join(EXPECTED_DIR, 'cultural_museum.parquet')
    expected = geopandas.read_parquet(expected_file)

    assert_geodataframe_equal(actual,
                              expected)


def test_get_worship():
    actual = cultural.get_worship(aoi_gdf)
    actual.drop(columns=['FID'], inplace=True)
    actual.sort_values(by=['EIN', 'NAME'], inplace=True, ignore_index=True)
    # actual.to_parquet(os.path.join(EXPECTED_DIR, 'cultural_worship.parquet'))

    expected_file = os.path.join(EXPECTED_DIR, 'cultural_worship.parquet')
    expected = geopandas.read_parquet(expected_file)

    assert_geodataframe_equal(actual, expected)


def test_get_recAreas():
    actual = cultural.process_recreationalArea(aoi_gdf_sa)
    actual.sort_values(by=['NAME', 'geometry'], inplace=True, ignore_index=True)
    actual.to_parquet(os.path.join(EXPECTED_DIR, 'recArea.parquet'))

    # assert no changes
    expected_file = os.path.join(EXPECTED_DIR, 'recArea.parquet')
    expected = geopandas.read_parquet(expected_file)

    assert_geodataframe_equal(actual,
                              expected,
                              check_less_precise=True)
