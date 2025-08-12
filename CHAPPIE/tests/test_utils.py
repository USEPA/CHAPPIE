"""
Test education assets 

@author: tlomba01
"""
# Commenting this out for now since I don't think we want to automate tests for this
# import os
# import geopandas
# from geopandas.testing import assert_geodataframe_equal
# from CHAPPIE import utils


# # CI inputs/expected
# DIRPATH = os.path.dirname(os.path.realpath(__file__))

# EXPECTED_DIR = os.path.join(DIRPATH, 'expected')  # Expected
# DATA_DIR = os.path.join(DIRPATH, 'data')  # inputs
# TEST_DIR = os.path.join(DIRPATH, 'results')  # test results (have to create)

# AOI = os.path.join(DATA_DIR, "Somerset_30mBuffer.shp")
# aoi_gdf = geopandas.read_file(AOI)


# # Expected file is a user arg input so the test doesn't run from retained results
# def test_get_regrid(expected_file):
#     actual = utils.get_regrid(aoi_gdf)
#     #actual.drop(columns=['FID'], inplace=True)
#     actual.sort_values(by=['geometry', 'geoid'], inplace=True, ignore_index=True)
#     #actual.to_parquet(os.path.join(EXPECTED_DIR, 'get_regrid.parquet'))

#     # assert no changes
#     #expected_file = os.path.join(EXPECTED_DIR, 'get_regrid.parquet')

#     expected = geopandas.read_parquet(expected_file)

#     # First check that results are same lenth
#     assert(len(actual)==len(expected)), f'{len(actual)}!={len(expected)}'
#     assert_geodataframe_equal(actual, expected)