# -*- coding: utf-8 -*-
"""
Created on Mon Sep 25 16:33:15 2023

@author: jbousqui
"""

import os

import geopandas
import pandas
import pytest
from geopandas.testing import assert_geodataframe_equal

from CHAPPIE.household import svi

# CI inputs/expected
DIRPATH = os.path.dirname(os.path.realpath(__file__))
#DIRPATH = r'D:\code\CHAPPIE\CHAPPIE\tests'

EXPECTED_DIR = os.path.join(DIRPATH, 'expected')  # Expected

def test_get_SVI_by_county_all_tracts():
    gdf = svi.get_SVI('12033', level='tract', year=2020)
    # check for columns
    check_cols = ['Poverty150', 'Unemploy', 'HouseBurd', 'NoHSDiplo', 'NoHlthIns',
                  '65andover', '17andbelow', 'DisableCiv', 'SPH', 'ELP', 'Hisp',
                  'Black', 'Asian', 'AIAN', 'NHPI', 'TwoRace', 'OtherRace',
                  'MUStruct', 'MobHome', 'Crowd', 'NoVeh', 'GrpQuarter']
    for col in check_cols:
        assert col in gdf.columns, f'Missing Column: {col}'
    # Test against Tract 1
    actual_tract = gdf[gdf['GEOID']=='12033000100']
    actual_df = actual_tract[check_cols].reset_index(drop=True)
    # Setup expected df
    expected_vals = [16.07565011820331,
                     2.9769959404600814,
                     76.77215189873418,
                     20.84388185654008,
                     13.740458015267176,
                     24.699176694110196,
                     19.632678910702978,
                     33.914421553090335,
                     29.599999999999998,
                     1.0570824524312896,
                     2.8499050031665614,
                     28.24572514249525,
                     1.013299556681444,
                     0.253324889170361,
                     4.749841671944269,
                     10.639645345155161,
                     0.0,
                     24.654622741764083,
                     0.4250797024442083,
                     0.7032348804500703,
                     26.160337552742618,
                     4.500330906684315]
    expected_dict = {key:[val] for key, val in zip(check_cols, expected_vals)}
    expected_df = pandas.DataFrame.from_dict(expected_dict)

    pandas.testing.assert_frame_equal(actual_df, expected_df)


def test_get_SVI_by_county_all_BG():
    actual = svi.get_SVI('12033', level='block group', year=2021)
    #actual.to_parquet(os.path.join(EXPECTED_DIR, 'bg_12033_2021.parquet'))

    expected_file = os.path.join(EXPECTED_DIR, 'bg_12033_2021.parquet')
    expected = geopandas.read_parquet(expected_file)
    #assert len(gdf_bg)==199
    assert_geodataframe_equal(actual, expected, check_like=True)

pytest.mark("unit")
def test_infer_bg_from_tract():
    #infer_BG_from_tract(bg_geoid, metric_col, year=2020, method='uniform')
    bg_id = "510010901011"
    metric_col = "B09019_002E"
    actual = svi.infer_bg_from_tract("510010901011", "B09019_002E", year=2023)
    expected = (bg_id, pandas.Series(data=[1864], name=metric_col))
    assert actual[0] == expected[0], "Mismatched block group ID"
    assert actual[1].all() == expected[1].all(), "Mismatched tract-level result"

#pytest.mark("integration")
# def test_infer_bg_from_tract_from_preprocess()
#     df_in = 
#     actual = svi.preprocess(df_in, 2023)
#     asster actual[metric]==expected[metric]
