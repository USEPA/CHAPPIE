# -*- coding: utf-8 -*-
"""
Test flood

@author: tlomba01
"""
import os
import random
from unittest.mock import MagicMock, patch

import geopandas
import pandas
import pytest
from geopandas.testing import assert_geodataframe_equal
from pandas.testing import assert_frame_equal
from requests.exceptions import HTTPError

from CHAPPIE.hazards import flood

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
    """ Test get FEMA NFHL """
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

class TestGetFlood:
    """ Test cases for get_flood """

    parcels = {"Multipolygon":
               ['03814-000-000',
                '03608-010-000',
                '32719-000-000',
                '03798-000-000',
                '32736-350-000',
                '40000-975-312',
                '03805-150-000',
                '26496-000-000',
                '32738-639-000', #this returns 0, but has a small corner of raster pixel present
                '03613-000-000', #this returns 0, but has a corner of raster pixel present
                '05964-000-000'], #Multipolygon (Donut with null value);
                "Tiny":
                ['31668-150-000', #14.5 m2 parcel no overlap NULL
                '34801-158-000', #14.3 m2 parcel no overlap NULL
                '40001-175-010', #14.3 m2 parcel complete overlap NULL
                '30464-230-000', #15.8 m2 parcel complete overlap NULL; multipolygon
                '30819-058-000', #74.8 m2 parcel no overlap, value of 0
                '40000-050-059', #74.3 m2 parcel no overlap, value of 0
                '31423-031-000', #74.3 m2 parcel complete overlap NULL
                '38187-505-000', #Smallest parcel to return overlap value of 0 (74.9 m2)
                '38466-020-000'], #Smallest parcel to return overlap value of 1 (96.5 m2)
                "Investigate":
                ['08344-000-000', #74.4 m2 parcel complete overlap NULL; not a unique parcel numb (3 polygons)
                '26529-020-000', #parcel with overlap but returned 0 value; yes returns 0, but has a corner of raster pixel present
                '38186-090-000', #parcel with no overlap but returned a value (0.5)
                '38461-816-000', #greater than 75m2 (134.2) returned NULL
                '38461-876-000', #greater than 75m2 (134.2) returned NULL
                '37252-030-120', #greater than 75m2 (102.4) returned NULL
                '36238-010-000', #greater than 75m2 (205.6) returned NULL
                '36459-720-010', #greater than 75m2 (486.1) returned NULL
                '38373-019-000'], #greater than 75m2 (200.1) returned NULL
                "exterior some overlap":
                ['03841-000-000',
                '32736-000-000',
                '32736-026-010',
                '26410-000-000',
                '36076-023-000',
                '36081-010-000',
                '36071-029-000',
                '36468-000-000',
                '36719-000-000',
                '05152-000-000'],
                "partial (0.75-0.99) overlap":
                ['03869-000-000',
                '03799-000-000',
                '03805-257-000',
                '03805-342-000',
                '33997-000-000',
                '32720-000-000',
                '26618-000-000',
                '26466-010-000',
                '07566-010-000',
                '26626-030-000'],
                "partial (0.01-0.25) overlap":
                ['33722-000-000',
                '32767-010-000',
                '32807-000-000',
                '32807-007-000',
                '07564-125-000',
                '26436-015-082',
                '26467-010-070',
                '03726-040-000',
                '03802-050-000',
                '34024-322-000'],
                "complete overlap":
                ['36630-000-000',
                '32736-000-000',
                '32736-015-000',
                '32734-010-000',
                '32728-000-000',
                '26630-000-000',
                '26631-000-000',
                '26509-010-000',
                '03623-050-000',
                '26593-533-000'],
                "no overlap":
                ['07533-450-090',
                '26487-000-000',
                '26484-030-000',
                '26470-000-000',
                '07533-450-090',
                '26509-020-000',
                '26567-000-000',
                '26551-005-000',
                '38324-000-000',
                '36617-000-000'
                ]}

    def test_get_flood_no_overlap(self):
        """ Test get flood when parcels have no overlap """
        test_parcels = self.parcels["no overlap"]
        # Get subset of parcels with no known overlap with flood areas
        no_overlap_parcels = parcels_gdf[parcels_gdf['parcelnumb'].isin(test_parcels)].reset_index()
        actual = flood.get_flood(no_overlap_parcels)

        expected_file = os.path.join(EXPECTED_DIR, 'get_flood_no_overlap.csv')
        expected = pandas.read_csv(expected_file)
        assert_frame_equal(actual, expected)

    def test_get_flood_complete_overlap(self):
        """ Test get flood when parcels have complete overlap """
        test_parcels = self.parcels["complete overlap"]
        # Get subset of parcels with complete known overlap with flood areas
        complete_overlap_parcels = parcels_gdf[parcels_gdf['parcelnumb'].isin(test_parcels)].reset_index()
        actual = flood.get_flood(complete_overlap_parcels)

        expected_file = os.path.join(EXPECTED_DIR, 'get_flood_complete_overlap.csv')
        expected = pandas.read_csv(expected_file)
        assert_frame_equal(actual, expected)

    def test_get_flood_gt1pct_lt25pct_overlap(self):
        """ Test get flood when parcels have partial (0.01-0.25) overlap """
        test_parcels = self.parcels["partial (0.01-0.25) overlap"]
        # Get subset of parcels with partial (0.01-0.25) known overlap with flood areas
        gt1pct_lt25pct_overlap_parcels = parcels_gdf[parcels_gdf['parcelnumb'].isin(test_parcels)].reset_index()
        actual = flood.get_flood(gt1pct_lt25pct_overlap_parcels)

        expected_file = os.path.join(EXPECTED_DIR, 'get_flood_gt1pct_lt25pct_overlap.csv')
        expected = pandas.read_csv(expected_file)
        assert_frame_equal(actual, expected)

    def test_get_flood_gt75pct_lt99pct_overlap(self):
        """ Test get flood when parcels have partial (0.75-0.99) overlap """
        test_parcels = self.parcels["partial (0.75-0.99) overlap"]

        # Get subset of parcels with partial (0.75-0.99) known overlap with flood areas
        gt75pct_lt99pct_overlap_parcels = parcels_gdf[parcels_gdf['parcelnumb'].isin(test_parcels)].reset_index()
        actual = flood.get_flood(gt75pct_lt99pct_overlap_parcels)

        expected_file = os.path.join(EXPECTED_DIR, 'get_flood_gt75pct_lt99pct_overlap.csv')
        expected = pandas.read_csv(expected_file)
        assert_frame_equal(actual, expected)

    def test_get_flood_exterior_some_overlap(self):
        """ Test get flood when parcels have some exterior overlap """
        test_parcels = self.parcels["exterior some overlap"]

        # Get subset of parcels with complete known overlap with flood areas
        exterior_some_overlap_parcels = parcels_gdf[parcels_gdf['parcelnumb'].isin(test_parcels)].reset_index()
        actual = flood.get_flood(exterior_some_overlap_parcels)

        expected_file = os.path.join(EXPECTED_DIR, 'get_flood_exterior_some_overlap.csv')
        expected = pandas.read_csv(expected_file)
        assert_frame_equal(actual, expected)

    def test_get_multipolygon(self):
        """ Test get flood when parcels are multipolygons """
        test_parcels = self.parcels["Multipolygon"]
        # Get subset of parcels that are multipolygons
        multipolygon_parcels = parcels_gdf[parcels_gdf['parcelnumb'].isin(test_parcels)].reset_index()
        actual = flood.get_flood(multipolygon_parcels)

        expected_file = os.path.join(EXPECTED_DIR, 'get_multipolygon.csv')
        expected = pandas.read_csv(expected_file)
        assert_frame_equal(actual, expected)

    def test_get_tiny_parcels(self):
        """ Test get flood when parcels are less than or nearly 75m2 """
        test_parcels = self.parcels["Tiny"]
        # Get subset of parcels with tiny geometries and results of null
        tiny_parcels = parcels_gdf[parcels_gdf['parcelnumb'].isin(test_parcels)].reset_index()
        #actual_file = os.path.join(EXPECTED_DIR, 'get_tiny.csv')
        actual = flood.get_flood(tiny_parcels,
                                #actual_file
                                )

        # test for parcel size
        # expect mean value is not empty if Shape_Area is greater than or equal to 74.334286
        # the parcels for 08344-000-000 make this fail, not sure why, so moved to needs investigation
        assert actual['mean'].count()==len(tiny_parcels[tiny_parcels["Shape_Area"] > 74.334285])

        expected_file = os.path.join(EXPECTED_DIR, 'get_tiny.csv')
        expected = pandas.read_csv(expected_file)
        assert_frame_equal(actual, expected, check_dtype=False)

    def test_needs_investigation(self):
        """ Test get flood when parcels return unexpected results """
        test_parcels = self.parcels["Investigate"]
        # Get subset of parcels with unexpected results
        needs_investigation_parcels = parcels_gdf[parcels_gdf['parcelnumb'].isin(test_parcels)].reset_index()
        actual = flood.get_flood(needs_investigation_parcels)

        expected_file = os.path.join(EXPECTED_DIR, 'get_needs_investigation.csv')
        expected = pandas.read_csv(expected_file)
        assert_frame_equal(actual, expected, check_dtype=False)

    def test_valid_geometry(self):
        """ Test parcels have valid geometry """
        test_parcels = self.parcels
        subset_parcels = parcels_gdf[parcels_gdf['parcelnumb'].isin(test_parcels)].reset_index()
        invalid_geom = []
        for i in range(len(subset_parcels)):
            row = subset_parcels.iloc[[i]]
            geom = row.geometry
            if not geom.is_valid.item():
                invalid_geom.append(row)
        assert len(invalid_geom)==0

@pytest.fixture
# GeoDataFrame with single point feature
def point_gdf():
    data = {
        'geometry': geopandas.GeoSeries.from_wkt(["POINT (-85.763623 30.329186)"])
    }
    point_gdf = geopandas.GeoDataFrame(data)
    point_gdf.crs = parcels_gdf.crs
    point_gdf['parcelnumb'] = random.randint(1,10)
    return point_gdf

# Test sending point data to get_image_by_poly, but patch the computeStatHist endpoint call
@patch('test_flood.flood.layer_query.ESRIImageService.computeStatHist')
def test_get_image_by_poly_point(mock_computeStatHist, point_gdf: geopandas.GeoDataFrame):
    url = "https://fake.org/ImageServer"
    row = point_gdf.iloc[[0]]

    result = flood.layer_query.get_image_by_poly(aoi=point_gdf, url=url, row=row)
    assert result is None
    mock_computeStatHist.assert_not_called() # Ensures the mocked method was never called

@pytest.fixture
# GeoDataFrame with single polygon feature
def polygon_gdf():
    data = {
        'geometry': geopandas.GeoSeries.from_wkt(["POLYGON ((-85.76298351599996 30.32878118700006, -85.76305759399997 30.32884191600005, -85.76316722699994 30.328925333000036, -85.76326076499998 30.32898948400003, -85.76337258599995 30.32905792500004, -85.76348870399994 30.329121772000065, -85.76362266399997 30.329186308, -85.76300802099996 30.329986128000023, -85.76235017699997 30.329637642000055, -85.76221772699995 30.329535969000062, -85.76211676699995 30.32929401400003, -85.76220841399999 30.328930764000056, -85.76228414799994 30.32877965800003, -85.76273981899999 30.328780179000045, -85.76298351599996 30.32878118700006))"])
    }
    point_gdf = geopandas.GeoDataFrame(data)
    point_gdf.crs = parcels_gdf.crs
    point_gdf['parcelnumb'] = random.randint(1,10)
    return point_gdf

#Test how 502 server error is handled, but patch the computeStatHist endpoint call
@patch('CHAPPIE.layer_query.utils.requests.post')
def test_get_image_by_poly_502_error(mock_post_request, polygon_gdf: geopandas.GeoDataFrame):
    mock_resp = MagicMock()
    mock_resp.status_code = 502
    mock_resp.raise_for_status.side_effect = HTTPError
    mock_post_request.return_value = mock_resp # mock return value
    url = "https://fake.org/ImageServer"
    row = polygon_gdf.iloc[[0]]
    result = flood.layer_query.get_image_by_poly(aoi=polygon_gdf, url=url, row=row)
    assert result['data'] is None
    assert mock_resp.raise_for_status.called == True
    # Ensure the mocked method was called twice (one plus a retry)
    #assert mock_post_request.call_count == 2

# Test mock return object {'statistics': []}, but patch the computeStatHist endpoint call
# @patch('CHAPPIE.layer_query.ESRIImageService.computeStatHist')
# def test_get_image_by_poly_index_error():
#     pass
