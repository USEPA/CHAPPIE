# -*- coding: utf-8 -*-
"""
Test nlcd functions.

@author: jbousquin
"""
import os

import geopandas

from CHAPPIE.eco_services import nlcd

# CI inputs/expected
DIRPATH = os.path.dirname(os.path.realpath(__file__))
#DIRPATH = r'L:\lab\GitHub\CHAPPIE\CHAPPIE\tests'

EXPECTED_DIR = os.path.join(DIRPATH, 'expected')  # Expected
DATA_DIR = os.path.join(DIRPATH, 'data')  # inputs

AOI_MIT_BANK = os.path.join(DATA_DIR, "Somerset_30mBuffer.shp")
#AOI_MIT_BANK_poly = os.path.join(DATA_DIR, "Somerset_30mBuffer.shp")
aoi_gdf = geopandas.read_file(AOI_MIT_BANK)

def test_get_NLCD():
    actual = nlcd.get_NLCD(aoi_gdf, 2021, dataset="Land_Cover")

#def tests_check_year_NLCD():
# run through other datasets and failure cases
#TODO: additional years available now?
