# -*- coding: utf-8 -*-
"""
Test tornadoes 

@author: jbousqui
"""
import os
import geopandas
from geopandas.testing import assert_geodataframe_equal
from CHAPPIE.Hazards import tornadoes

# CI inputs/expected
DIRPATH = os.path.dirname(os.path.realpath(__file__))
#DIRPATH = r'D:\code\CHAPPIE\CHAPPIE\tests'

EXPECTED_DIR = os.path.join(DIRPATH, 'expected')  # Expected
DATA_DIR = os.path.join(DIRPATH, 'data')  # inputs

AOI = os.path.join(DATA_DIR, "BreakfastPoint_ServiceArea.shp")


def test_get_tornadoes():
    actual = tornadoes.get_tornadoes()
    #NOTE/TODO: 1950-2022-torn-aspath is too big to save in expected?
    expected_file = os.path.join(EXPECTED_DIR, '1950-2022-torn-aspath')
    expected = geopandas.read_file(expected_file)
    
    assert_geodataframe_equal(actual, expected, check_like=True)

# get() may need to be a fixture to assure full dataset has been downloaded 1st
def test_process_tornadoes():
    #aoi_input = geopandas.read_file()  # may be able to pass it filename
    actual = tornadoes.process_tornadoes()
    expected_file = os.path.join(EXPECTED_DIR, 'FLROAR20231108_Torn_Buffer_AOI_Intersection_1996_2016.shp')
    expected = geopandas.read_file(expected_file)
    
    assert_geodataframe_equal(actual, expected, check_like=True)