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
import pytest

# CI inputs/expected
DIRPATH = os.path.dirname(os.path.realpath(__file__))

EXPECTED_DIR = os.path.join(DIRPATH, 'expected')  # Expected
DATA_DIR = os.path.join(DIRPATH, 'data')  # inputs
TEST_DIR = os.path.join(DIRPATH, 'results')  # test results (have to create)
PARCEL_DIR = os.path.join(EXPECTED_DIR, 'parcels')

AOI = os.path.join(DATA_DIR, "BreakfastPoint_ServiceArea.shp")
PARCELS = os.path.join(PARCEL_DIR, "BP_Regrid.shp")
aoi_gdf = geopandas.read_file(AOI)
parcels_gdf = geopandas.read_file(PARCELS)

def test_get_fema_nfhl():
    """ Test get FEMA HFHL """
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
    """ Test get flood when parcels have no overlap """
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
    """ Test get flood when parcels have complete overlap """
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

def test_get_flood_gt1pct_lt25pct_overlap():
    """ Test get flood when parcels have partial (0.01-0.25) overlap """
    test_parcels = ['33722-000-000',
                    '32767-010-000',
                    '32807-000-000',
                    '32807-007-000',
                    '07564-125-000',
                    '26436-015-082',
                    '26467-010-070',
                    '03726-040-000',
                    '03802-050-000',
                    '34024-322-000']
    # Get subset of parcels with partial (0.01-0.25) known overlap with flood areas
    gt1pct_lt25pct_overlap_parcels = parcels_gdf[parcels_gdf['parcelnumb'].isin(test_parcels)].reset_index()
    actual = flood.get_flood(gt1pct_lt25pct_overlap_parcels)

    expected_file = os.path.join(EXPECTED_DIR, 'get_flood_gt1pct_lt25pct_overlap.csv')
    expected = pandas.read_csv(expected_file)
    assert_frame_equal(actual, expected)

def test_get_flood_gt75pct_lt99pct_overlap():
    """ Test get flood when parcels have partial (0.75-0.99) overlap """
    test_parcels = ['03869-000-000',
                    '03799-000-000',
                    '03805-257-000',
                    '03805-342-000',
                    '33997-000-000',
                    '32720-000-000',
                    '26618-000-000',
                    '26466-010-000',
                    '07566-010-000',
                    '26626-030-000',
                    ]
    # Get subset of parcels with partial (0.75-0.99) known overlap with flood areas
    gt75pct_lt99pct_overlap_parcels = parcels_gdf[parcels_gdf['parcelnumb'].isin(test_parcels)].reset_index()
    actual = flood.get_flood(gt75pct_lt99pct_overlap_parcels)

    expected_file = os.path.join(EXPECTED_DIR, 'get_flood_gt75pct_lt99pct_overlap.csv')
    expected = pandas.read_csv(expected_file)
    assert_frame_equal(actual, expected)

def test_get_flood_exterior_some_overlap():
    """ Test get flood when parcels have some exterior overlap """
    test_parcels = ['03841-000-000',
                    '32736-000-000',
                    '32736-026-010',
                    '26410-000-000',
                    '36076-023-000',
                    '36081-010-000',
                    '36071-029-000',
                    '36468-000-000',
                    '36719-000-000',
                    '05152-000-000']
    # Get subset of parcels with complete known overlap with flood areas
    exterior_some_overlap_parcels = parcels_gdf[parcels_gdf['parcelnumb'].isin(test_parcels)].reset_index()
    #actual_file = os.path.join(EXPECTED_DIR, 'get_flood_exterior_some_overlap.csv')
    actual = flood.get_flood(exterior_some_overlap_parcels, 
                             #actual_file
                            )

    expected_file = os.path.join(EXPECTED_DIR, 'get_flood_exterior_some_overlap.csv')
    expected = pandas.read_csv(expected_file)
    assert_frame_equal(actual, expected)

def test_get_multipolygon():
    """ Test get flood when parcels are multipolygons """
    test_parcels = ['03814-000-000', 
                    '03608-010-000',
                    '32719-000-000',
                    '03798-000-000',
                    '32736-350-000',
                    '40000-975-312',
                    '03805-150-000',
                    '26496-000-000',
                    '32738-639-000', #this returns 0, but has a small corner of raster pixel present
                    '03613-000-000', #this returns 0, but has a corner of raster pixel present
                    '05964-000-000', #Multipolygon (Donut with null value); Result looks valid (not null)	
                    ]
    # Get subset of parcels that are multipolygons
    multipolygon_parcels = parcels_gdf[parcels_gdf['parcelnumb'].isin(test_parcels)].reset_index()
    actual = flood.get_flood(multipolygon_parcels
                            )

    expected_file = os.path.join(EXPECTED_DIR, 'get_multipolygon.csv')
    expected = pandas.read_csv(expected_file)
    assert_frame_equal(actual, expected)

def test_get_tiny_parcels():
    """ Test get flood when parcels are less than or nearly 75m2 """
    test_parcels = ['31668-150-000', #14.5 m2 parcel no overlap NULL
                    '34801-158-000', #14.3 m2 parcel no overlap NULL
                    '40001-175-010', #14.3 m2 parcel complete overlap NULL
                    '30464-230-000', #15.8 m2 parcel complete overlap NULL; multipolygon
                    '30819-058-000', #74.8 m2 parcel no overlap, value of 0
                    '40000-050-059', #74.3 m2 parcel no overlap, value of 0
                    '31423-031-000', #74.3 m2 parcel complete overlap NULL
                    '08344-000-000', #74.4 m2 parcel complete overlap NULL; not a unique parcel numb (3 polygons)
                    '38187-505-000', #Smallest parcel to return overlap value of 0 (74.9 m2)
                    '38466-020-000', #Smallest parcel to return overlap value of 1 (96.5 m2)
                    ]
    # Get subset of parcels with tiny geometries and results of null
    tiny_parcels = parcels_gdf[parcels_gdf['parcelnumb'].isin(test_parcels)].reset_index()
    #actual_file = os.path.join(EXPECTED_DIR, 'get_tiny.csv')
    actual = flood.get_flood(tiny_parcels,
                             #actual_file
                             )

    expected_file = os.path.join(EXPECTED_DIR, 'get_tiny.csv')
    expected = pandas.read_csv(expected_file)
    assert_frame_equal(actual, expected)

def test_needs_investigation():
    """ Test get flood when parcels return unexpected results """
    test_parcels = ['26529-020-000', #parcel with overlap but returned 0 value; yes returns 0, but has a corner of raster pixel present
                    '38186-090-000', #parcel with no overlap but returned a value (0.5)
                    '38461-816-000', #greater than 75m2 (134.2) returned NULL
                    '38461-876-000', #greater than 75m2 (134.2) returned NULL
                    '37252-030-120', #greater than 75m2 (102.4) returned NULL
                    '36238-010-000', #greater than 75m2 (205.6) returned NULL
                    '36459-720-010', #greater than 75m2 (486.1) returned NULL
                    '38373-019-000' #greater than 75m2 (200.1) returned NULL
    ]
    # Get subset of parcels with tiny geometries and results of null
    needs_investigation_parcels = parcels_gdf[parcels_gdf['parcelnumb'].isin(test_parcels)].reset_index()
    actual = flood.get_flood(needs_investigation_parcels)
    
    expected_file = os.path.join(EXPECTED_DIR, 'get_needs_investigation.csv')
    expected = pandas.read_csv(expected_file)
    assert_frame_equal(actual, expected)

def test_valid_geometry():
    """ Test parcels have valid geometry """
    test_parcels = ['03814-000-000', #Multipolygon
                    '03608-010-000', #Multipolygon
                    '32719-000-000', #Multipolygon
                    '03798-000-000', #Multipolygon
                    '32736-350-000', #Multipolygon
                    '40000-975-312', #Multipolygon
                    '03805-150-000', #Multipolygon
                    '26496-000-000', #Multipolygon
                    '32738-639-000', #this returns 0, but has a small corner of raster pixel present
                    '03613-000-000', #this returns 0, but has a corner of raster pixel present
                    '05964-000-000', #Multipolygon (Donut with null value); Result looks valid (not null)	
                    '31668-150-000', #14.5 m2 parcel no overlap NULL
                    '34801-158-000', #14.3 m2 parcel no overlap NULL
                    '40001-175-010', #14.3 m2 parcel complete overlap NULL
                    '30464-230-000', #15.8 m2 parcel complete overlap NULL; multipolygon
                    '30819-058-000', #74.8 m2 parcel no overlap, value of 0
                    '40000-050-059', #74.3 m2 parcel no overlap, value of 0
                    '31423-031-000', #74.3 m2 parcel complete overlap NULL
                    '08344-000-000', #74.4 m2 parcel complete overlap NULL; not a unique parcel numb (3 polygons)
                    '38187-505-000', #Smallest parcel to return overlap value of 0 (74.9 m2)
                    '38466-020-000', #Smallest parcel to return overlap value of 1 (96.5 m2)'26529-020-000', #parcel with overlap but returned 0 value; yes returns 0, but has a corner of raster pixel present
                    '38186-090-000', #parcel with no overlap but returned a value (0.5)
                    '38461-816-000', #greater than 75m2 (134.2) returned NULL
                    '38461-876-000', #greater than 75m2 (134.2) returned NULL
                    '37252-030-120', #greater than 75m2 (102.4) returned NULL
                    '36238-010-000', #greater than 75m2 (205.6) returned NULL
                    '36459-720-010', #greater than 75m2 (486.1) returned NULL
                    '38373-019-000' #greater than 75m2 (200.1) returned NULL
    ]
    subset_parcels = parcels_gdf[parcels_gdf['parcelnumb'].isin(test_parcels)].reset_index()
    invalid_geom = []
    for i in range(len(subset_parcels)):
        row = subset_parcels.iloc[[i]]
        geom = row.geometry
        if geom.is_valid.item() == False:
            invalid_geom.append(row)
    assert len(invalid_geom)==0       

    #TODO: test for url character length?

    #TODO: test for winding order? is_ccw method available in GeoPandas v1.0.0 

    #TODO: test for parcel size?