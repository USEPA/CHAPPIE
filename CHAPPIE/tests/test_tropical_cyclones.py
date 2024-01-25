# -*- coding: utf-8 -*-
"""
Test tropical cyclones 

@author: jbousqui
"""
import os
import geopandas
from geopandas.testing import assert_geodataframe_equal
from CHAPPIE.hazards import tropical_cyclones

# CI inputs/expected
DIRPATH = os.path.dirname(os.path.realpath(__file__))
#DIRPATH = r'D:\code\CHAPPIE\CHAPPIE\tests'

EXPECTED_DIR = os.path.join(DIRPATH, f'expected{os.sep}hazards')  # Expected
DATA_DIR = os.path.join(DIRPATH, 'data')  # inputs

AOI = os.path.join(DATA_DIR, "BreakfastPoint_ServiceArea.shp")


def test_get_tropical_cyclones():
    actual = tropical_cyclones.get_tropical_cyclones(DATA_DIR, ['points'])
    
    # Restrict to ~CONUS for test
    min_y, max_y = 24, 50
    min_x, max_x = -125, -66
    
    expected_file = os.path.join(EXPECTED_DIR, '<FILE>')
    expected = geopandas.read_file(expected_file)
    
    assert_geodataframe_equal(actual, expected, check_like=True)

# get() may need to be a fixture to assure full dataset has been downloaded 1st
def test_process_tropical_cyclones():
    #aoi_input = geopandas.read_file()  # may be able to pass it filename
    actual = tropical_cyclones.process_tropical_cyclones()
    expected_file = os.path.join(EXPECTED_DIR, '<FILE>')
    expected = geopandas.read_file(expected_file)
    
    assert_geodataframe_equal(actual, expected, check_like=True)