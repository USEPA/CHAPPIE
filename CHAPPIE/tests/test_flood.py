# -*- coding: utf-8 -*-
"""
Test flood 

@author: tlomba01
"""
import os
import geopandas
import pandas
from pandas.testing import assert_frame_equal
from geopandas.testing import assert_geodataframe_equal
from CHAPPIE.hazards import flood

# CI inputs/expected
DIRPATH = os.path.dirname(os.path.realpath(__file__))

EXPECTED_DIR = os.path.join(DIRPATH, 'expected')  # Expected
DATA_DIR = os.path.join(DIRPATH, 'data')  # inputs
PARCEL_DIR = os.path.join(EXPECTED_DIR, 'parcels')

AOI = os.path.join(DATA_DIR, "BreakfastPoint_ServiceArea.shp")
PARCELS = os.path.join(PARCEL_DIR, "BP_Regrid.shp")
aoi_gdf = geopandas.read_file(AOI)
parcels_gdf = geopandas.read_file(PARCELS)

def test_get_fema_nfhl():
    actual = flood.get_fema_nfhl(aoi_gdf)
    actual.drop(columns=['OBJECTID', 'VERSION_ID', 'STUDY_TYP', 'SFHA_TF', 
                         'STATIC_BFE', 'V_DATUM', 'DEPTH', 'LEN_UNIT', 
                         'VELOCITY', 'VEL_UNIT', 'DUAL_ZONE', 'SOURCE_CIT', 
                         'GFID', 'esri_symbology', 'GlobalID', 'Shape__Area', 
                         'Shape__Length'], inplace=True)
    actual.sort_values(by=['DFIRM_ID', 'FLD_AR_ID', 'geometry'], inplace=True, ignore_index=True)
    #actual.to_parquet(os.path.join(EXPECTED_DIR, 'get_fema_nfhl.parquet'))

    # assert no changes
    expected_file = os.path.join(EXPECTED_DIR, 'get_fema_nfhl.parquet')
    expected = geopandas.read_parquet(expected_file)
 
    assert_geodataframe_equal(actual, 
                              expected,
                              check_like=True,
                              check_less_precise=True)
    
def test_get_flood_no_overlap():
    test_parcels = ['07533-450-090',
                    '26487-000-000',
                    '26484-030-000',
                    '26470-000-000',
                    '07533-450-090',
                    '26509-020-000',
                    '26567-000-000',
                    '26551-005-000',
                    '38324-000-000',
                    '36617-000-000']
    # Get subset of parcels with no known overlap with flood areas
    no_overlap_parcels = parcels_gdf[parcels_gdf['parcelnumb'].isin(test_parcels)].reset_index()
    actual = flood.get_flood(no_overlap_parcels)

    expected_file = os.path.join(EXPECTED_DIR, 'get_flood_no_overlap.csv')
    expected = pandas.read_csv(expected_file)
    assert_frame_equal(actual, expected)

def test_get_flood_complete_overlap():
    test_parcels = ['36630-000-000',
                    '32736-000-000',
                    '32736-015-000',
                    '32734-010-000',
                    '32728-000-000',
                    '26630-000-000',
                    '26631-000-000',
                    '26509-010-000',
                    '03623-050-000',
                    '26593-533-000']
    # Get subset of parcels with complete known overlap with flood areas
    complete_overlap_parcels = parcels_gdf[parcels_gdf['parcelnumb'].isin(test_parcels)].reset_index()
    #actual_file = os.path.join(EXPECTED_DIR, 'get_flood_complete_overlap.csv')
    actual = flood.get_flood(complete_overlap_parcels, 
                             #actual_file
                            )

    expected_file = os.path.join(EXPECTED_DIR, 'get_flood_complete_overlap.csv')
    expected = pandas.read_csv(expected_file)
    assert_frame_equal(actual, expected)