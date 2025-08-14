"""
Test get and process Regrid parcels.

@author: tlomba01
"""
# #Commenting this out for now since I don't think we want to automate tests for this
# import os
# import geopandas
# import pytest
# from geopandas.testing import assert_geodataframe_equal
# from CHAPPIE import parcels


# # CI inputs/expected
# DIRPATH = os.path.dirname(os.path.realpath(__file__))

# EXPECTED_DIR = os.path.join(DIRPATH, 'expected')  # Expected
# DATA_DIR = os.path.join(DIRPATH, 'data')  # inputs
# TEST_DIR = os.path.join(DIRPATH, 'results')  # test results (have to create)

# AOI = os.path.join(DATA_DIR, "Somerset_30mBuffer.shp")
# aoi_gdf = geopandas.read_file(AOI)


# # Expected file is a user arg input so the test doesn't run from retained results
# @pytest.fixture(scope='session')
# def parcels_gdf():
#     return parcels.get_regrid(aoi_gdf)

# def test_get_regrid(parcels_gdf: geopandas.GeoDataFrame):
#     #actual.drop(columns=['FID'], inplace=True)
#     parcels_gdf.sort_values(by=['geometry', 'geoid'], inplace=True, ignore_index=True)
#     #parcels_gdf.to_parquet(os.path.join(EXPECTED_DIR, 'get_regrid.parquet'))

#     # assert no changes
#     expected_file = os.path.join(EXPECTED_DIR, 'get_regrid.parquet')

#     expected = geopandas.read_parquet(expected_file)

#     # First check that results are same lenth
#     assert(len(parcels_gdf)==len(expected)), f'{len(parcels_gdf)}!={len(expected)}'
#     assert_geodataframe_equal(parcels_gdf, expected)
    

# def test_process_regrid(parcels_gdf: geopandas.GeoDataFrame):
#     actual_centroids = parcels.process_regrid(parcels_gdf)
#     assert(len(parcels_gdf)==len(actual_centroids))
#     assert(len(actual_centroids[actual_centroids['geometry'].geom_type == 'Point'])==len(parcels_gdf))
#     assert(len(actual_centroids[actual_centroids['geometry'].geom_type == 'Polygon'])==0)