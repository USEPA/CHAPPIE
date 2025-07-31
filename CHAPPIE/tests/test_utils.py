"""
Test education assets 

@author: tlomba01
"""
import os
import geopandas
from geopandas.testing import assert_geodataframe_equal
from CHAPPIE import utils


# CI inputs/expected
DIRPATH = os.path.dirname(os.path.realpath(__file__))

EXPECTED_DIR = os.path.join(DIRPATH, 'expected')  # Expected
DATA_DIR = os.path.join(DIRPATH, 'data')  # inputs
TEST_DIR = os.path.join(DIRPATH, 'results')  # test results (have to create)

AOI = os.path.join(DATA_DIR, "MangrovePoint_ServiceArea.shp")
aoi_gdf = geopandas.read_file(AOI)


def test_get_regrid():
    actual = utils.get_regrid(aoi_gdf)
    # actual.drop(columns=['OBJECTID'], inplace=True)
    # actual.sort_values(by=['NCESID', 'geometry', 'NAME'], inplace=True, ignore_index=True)
    actual.to_file(os.path.join(EXPECTED_DIR, 'get_regrid.shp'))

    # assert no changes
    expected_file = os.path.join(EXPECTED_DIR, 'get_regrid.shp')
    expected = geopandas.read_file(expected_file)
    
    assert_geodataframe_equal(actual, expected)