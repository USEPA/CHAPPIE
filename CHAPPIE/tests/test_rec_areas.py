# -*- coding: utf-8 -*-
"""
Test recreation assets.

@author: edamico
"""
import os

import geopandas
from geopandas.testing import assert_geodataframe_equal

from CHAPPIE.assets import recreationalAreas

# CI inputs/expected
DIRPATH = os.path.dirname(os.path.realpath(__file__))

EXPECTED_DIR = os.path.join(DIRPATH, 'expected')  # Expected
DATA_DIR = os.path.join(DIRPATH, 'data')  # inputs

AOI_MIT_BANK_SA = os.path.join(DATA_DIR, "BreakfastPoint_ServiceArea.shp")
aoi_gdf_sa = geopandas.read_file(AOI_MIT_BANK_SA)

def test_get_recAreas():
    actual = recreationalAreas.process_recreationalArea(aoi_gdf_sa)
    actual.sort_values(by=['NAME', 'geometry'], inplace=True, ignore_index=True)
    #actual.to_parquet(os.path.join(EXPECTED_DIR, 'recArea.parquet'))

    # assert no changes
    expected_file = os.path.join(EXPECTED_DIR, 'recArea.parquet')
    expected = geopandas.read_parquet(expected_file)

    assert_geodataframe_equal(actual,
                              expected,
                              check_less_precise=True)

