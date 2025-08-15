# -*- coding: utf-8 -*-
"""
Test food assets.

@author: jbousqui
"""
import os

import geopandas
from geopandas.testing import assert_geodataframe_equal
from shapely import Point

from CHAPPIE.assets import food

# get key from env
usda_API = os.environ['usda_API']

# CI inputs/expected
DIRPATH = os.path.dirname(os.path.realpath(__file__))

EXPECTED_DIR = os.path.join(DIRPATH, 'expected')  # Expected
DATA_DIR = os.path.join(DIRPATH, 'data')  # inputs

AOI = os.path.join(DATA_DIR, "BreakfastPoint_ServiceArea.shp")
aoi_gdf = geopandas.read_file(AOI)


def test_radius():
    pnt, radius = food.search_pnt_radius(aoi_gdf)
    assert radius == 25
    assert isinstance(radius, int)
    assert isinstance(pnt, Point)  # shapely.Point
    # Can't check epsg off point, but we can confirm values
    assert pnt == Point(-85.64365604143532, 30.23698502049977)

def test_get_agritourism():
    actual = food.get_agritourism(aoi_gdf, usda_API)
    assert isinstance(actual, geopandas.geodataframe.GeoDataFrame)
    # Expect this one not to be empty
    assert len(actual)==2
    # assert no changes
    expected_file = os.path.join(EXPECTED_DIR, 'get_agritourism.parquet')
    expected = geopandas.read_parquet(expected_file)

    assert_geodataframe_equal(actual, expected)

def test_get_CSA():
    actual = food.get_CSA(aoi_gdf, usda_API)
    assert isinstance(actual, geopandas.geodataframe.GeoDataFrame)
    assert len(actual)==0

def test_get_farmers_market():
    actual = food.get_farmers_market(aoi_gdf, usda_API)
    assert isinstance(actual, geopandas.geodataframe.GeoDataFrame)
    # Expect this one not to be empty
    #assert len(actual)==2
    # assert no changes
    expected_file = os.path.join(EXPECTED_DIR, 'get_farmers_markets.parquet')
    expected = geopandas.read_parquet(expected_file)

    assert_geodataframe_equal(actual, expected)

def test_get_food_hub():
    actual = food.get_food_hub(aoi_gdf, usda_API)
    assert isinstance(actual, geopandas.geodataframe.GeoDataFrame)
    assert len(actual)==0

def test_get_farm_store():
    actual = food.get_farm_store(aoi_gdf, usda_API)
    assert isinstance(actual, geopandas.geodataframe.GeoDataFrame)
    # Expect this one not to be empty
    assert len(actual)==1
    # assert no changes
    expected_file = os.path.join(EXPECTED_DIR, 'get_farm_store.parquet')
    expected = geopandas.read_parquet(expected_file)

    assert_geodataframe_equal(actual, expected)

