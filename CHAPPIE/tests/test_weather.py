"""
Test natural hazards weather

@author: jbousqui
"""
import os

import geopandas
import pandas
from pandas.testing import assert_frame_equal

from CHAPPIE import layer_query
from CHAPPIE.hazards import weather

# CI inputs/expected
DIRPATH = os.path.dirname(os.path.realpath(__file__))

EXPECTED_DIR = os.path.join(DIRPATH, 'expected')  # Expected
DATA_DIR = os.path.join(DIRPATH, 'data')  # inputs

AOI = os.path.join(DATA_DIR, "BreakfastPoint_ServiceArea.shp")
aoi_gdf = geopandas.read_file(AOI)

def test_tracts():
    actual = layer_query.getTract(aoi_gdf)["GEOID"].to_list()
    expected = ['12005002607', '12005000806', '12005002604', '12005002500',
                '12005001402', '12013010200', '12045960102', '12005002606',
                '12005001800', '12005001700', '12005001301', '12005000805',
                '12005000302', '12005002605', '12005002400', '12005001502',
                '12005001501', '12005001000', '12005000803', '12005000401',
                '12005002609', '12005001600', '12005000700', '12005000600',
                '12005002707', '12005002709', '12131950501', '12005002711',
                '12005002710', '12005002300', '12005001403', '12005990000',
                '12005002712', '12005002608', '12005002200', '12005001100',
                '12005000900', '12005000500', '12005001900', '12005001200',
                '12005000203', '12005000204', '12005002706', '12005002708',
                '12005002703', '12005002713', '12005002000', '12005001404',
                '12005001302', '12133970302', '12005000201', '12005000804',
                '12005000402']
    assert actual == expected

def test_get_heat_events():
    actual = weather.get_heat_events(aoi_gdf)
    expected_file = os.path.join(EXPECTED_DIR, "heat.csv")
    expected = pandas.read_csv(expected_file)
    assert_frame_equal(actual, expected)
