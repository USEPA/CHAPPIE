# -*- coding: utf-8 -*-
"""
Test food assets. 

@author: jbousqui
"""
import os
import geopandas
from shapely import Point
from geopandas.testing import assert_geodataframe_equal
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
    assert pnt == Point(30.23698502049977, -85.64365604143532)

def test_get_agritourism():
    actual = food.get_agritourism(aoi_gdf, usda_API)
    assert isinstance(actual, geopandas.GeoDataFrame)
