# Update expected results
import os

import geopandas
import pandas
from geopandas.testing import assert_geodataframe_equal
from pandas.testing import assert_frame_equal

#DIRPATH =r"L:\lab\GitHub\CHAPPIE\CHAPPIE\tests"
DIRPATH = os.path.dirname(os.path.realpath(__file__))

EXPECTED_DIR = os.path.join(DIRPATH, 'expected')  # Expected
DATA_DIR = os.path.join(DIRPATH, 'data')  # inputs

AOI = os.path.join(DATA_DIR, "BreakfastPoint_ServiceArea.shp")
AOI_BANK = os.path.join(DATA_DIR, "BreakfastPoint_RIBITS2020.shp")
aoi_gdf = geopandas.read_file(AOI)
aoi_bank_gdf = geopandas.read_file(AOI_BANK)

# assets
## Cultural
from CHAPPIE.assets import cultural

### test_get_worship()
actual = cultural.get_worship(aoi_gdf)
actual.drop(columns=['FID'], inplace=True)
actual.sort_values(by=['EIN', 'NAME'], inplace=True, ignore_index=True)

expected_file = os.path.join(EXPECTED_DIR, 'cultural_worship.parquet')
expected = geopandas.read_parquet(expected_file)
try:
    assert_geodataframe_equal(actual, expected)
except AssertionError as ae:
    print(ae)
    actual.to_parquet(expected_file)

## Emergency
from CHAPPIE.assets import emergency

### test_get_fire_ems()
actual = emergency.get_fire_ems(aoi_gdf)
int_cols = ["DATA_SECURITY", "LOADDATE", "FTYPE", "FCODE", "ISLANDMARK",
            "POINTLOCATIONTYPE"]
actual.drop(columns=['OBJECTID']+int_cols, inplace=True)

actual.sort_values(by=['PERMANENT_IDENTIFIER', 'geometry', 'NAME'],
                   inplace=True,
                   ignore_index=True)

expected_file = os.path.join(EXPECTED_DIR, 'fire_ems.parquet')
expected = geopandas.read_parquet(expected_file)
try:
    assert_geodataframe_equal(actual, expected)
except AssertionError as ae:
    print(ae)
    actual.to_parquet(expected_file)


###test_get_police()
actual = emergency.get_police(aoi_gdf)

# Drop columns that are not needed and int (32 vs 64)
int_cols = ["DATA_SECURITY", "LOADDATE", "FTYPE", "FCODE", "ISLANDMARK",
            "POINTLOCATIONTYPE"]
actual.drop(columns=['OBJECTID']+int_cols, inplace=True)

actual.sort_values(by=['PERMANENT_IDENTIFIER', 'geometry', 'NAME'],
                    inplace=True,
                    ignore_index=True)

expected_file = os.path.join(EXPECTED_DIR, 'get_police.parquet')
expected = geopandas.read_parquet(expected_file)
try:
    assert_geodataframe_equal(actual, expected)
except AssertionError as ae:
    print(ae)
    actual.to_parquet(expected_file)

## Food
from CHAPPIE.assets import food

# get key from env
usda_API = os.environ['usda_API']

###test_get_farmers_market()
actual = food.get_farmers_market(aoi_gdf, usda_API)

# Old file
expected_file = os.path.join(EXPECTED_DIR, 'get_farmers_markets.parquet')
expected = geopandas.read_parquet(expected_file)
try:
    assert_geodataframe_equal(actual, expected)
except AssertionError as ae:
    print(ae)
    actual.to_parquet(expected_file)

###test_get_farm_store()
actual = food.get_farm_store(aoi_gdf, usda_API)

expected_file = os.path.join(EXPECTED_DIR, 'get_farm_store.parquet')
expected = geopandas.read_parquet(expected_file)
try:
    assert_geodataframe_equal(actual, expected)
except AssertionError as ae:
    print(ae)
    actual.to_parquet(expected_file)

##Health
from CHAPPIE.assets import health

###test_get_providers()
actual = health.get_providers(aoi_gdf)

expected_file = os.path.join(EXPECTED_DIR, 'get_providers.parquet')
expected = pandas.read_parquet(expected_file)  # No geo (addresses only)
# NOTE: dict are not ordered, drop all columns where it contains a dict
# 'addresses', 'practiceLocations', 'basic', 'endpoints', 'other_names',
# 'taxonomies',
cols = ['created_epoch', 'enumeration_type', 'last_updated_epoch', 'number',
        'identifiers', 'zip5']
try:
    assert_frame_equal(actual[cols].sort_values(by=['number', 'zip5']).reset_index(drop=True),
                    expected[cols].sort_values(by=['number', 'zip5']).reset_index(drop=True))
except AssertionError as ae:
    print(ae)
    actual.to_parquet(expected_file)

##Infrastructure
from CHAPPIE.assets import hazard_infrastructure

###test_get_dams()
actual = hazard_infrastructure.get_dams(aoi_gdf)
actual.drop(columns=['OBJECTID', "primaryPurposeId"], inplace=True)
# Note: "primaryPurposeId"==None is problematic
actual.sort_values(by=['id', 'name'], inplace=True, ignore_index=True)

expected_file = os.path.join(EXPECTED_DIR, 'dams.parquet')
expected = geopandas.read_parquet(expected_file)
try:
    assert_geodataframe_equal(actual, expected, check_less_precise=True)
except AssertionError as ae:
    print(ae)
    actual.to_parquet(expected_file)


##Recreation
from CHAPPIE.assets import recreation

###test_get_padus()
actual = recreation.get_padus(aoi_bank_gdf)
actual.drop(columns=['OBJECTID'], inplace=True)
actual.sort_values(by=['Unit_Nm', 'geometry'], inplace=True, ignore_index=True)

# old file
expected_file = os.path.join(EXPECTED_DIR, 'padus.parquet')
expected = geopandas.read_parquet(expected_file)

try:
    assert_geodataframe_equal(actual,
                              expected,
                              check_less_precise=True)
except AssertionError as ae:
    print(ae)
    actual.to_parquet(expected_file)


###test_get_trails()
actual = recreation.get_trails(aoi_gdf)
actual.drop(columns=['objectid'], inplace=True)
actual.sort_values(by=['permanentidentifier', 'geometry'],
                    inplace=True,
                    ignore_index=True)
actual.rename(columns={'GEOMETRY': 'geometry'}, inplace=True)

expected_file = os.path.join(EXPECTED_DIR, 'trails.parquet')
expected = geopandas.read_parquet(expected_file)
try:
    assert_geodataframe_equal(actual,
                              expected,
                              check_less_precise=True)
except AssertionError as ae:
    print(ae)
    actual.to_parquet(expected_file)


##Transit
from CHAPPIE.assets import transit

#test_get_air()
actual = transit.get_air(aoi_gdf)
drop_cols = ["OBJECTID", "EFF_DATE", "LAST_INFO_RESPONSE"]
actual.drop(columns=drop_cols, inplace=True)
# Drop geometry redundant columns that cause trouble
actual.drop(columns=["LAT_DEG", "LONG_DEG", 'LAT_MIN', 'LONG_MIN'],
            inplace=True)
actual.rename(columns={'GEOMETRY': 'geometry'}, inplace=True)
actual.sort_values(by=['ARPT_ID'], inplace=True, ignore_index=True)

expected_file = os.path.join(EXPECTED_DIR, 'get_air.parquet')
expected = geopandas.read_parquet(expected_file)
try:
    assert_geodataframe_equal(actual, expected, check_less_precise=True)
except AssertionError as ae:
    print(ae)
    actual.to_parquet(expected_file)

#test_get_bus()
actual = transit.get_bus(aoi_gdf)
actual.drop(columns=['OBJECTID'], inplace=True)
actual.rename(columns={'GEOMETRY': 'geometry'}, inplace=True)
sort_list = ["ntd_id","stop_id","stop_name", 'geometry']
actual.sort_values(by=sort_list,
                    inplace=True,
                    ignore_index=True)

expected_file = os.path.join(EXPECTED_DIR, 'get_bus.parquet')
expected = geopandas.read_parquet(expected_file)
try:
    assert_geodataframe_equal(actual,
                              expected,
                              check_less_precise=True)
except AssertionError as ae:
    print(ae)
    actual.to_parquet(expected_file)


# eco_services
# hazards
## Technological
import CHAPPIE.tests.test_technological as test_tech
from CHAPPIE.hazards import technological

###test_get_FRS_ACRES()
actual = technological.get_FRS_ACRES(aoi_gdf)
actual.drop(columns=['OBJECTID'], inplace=True)
actual.sort_values(by=['KEY_FIELD', 'geometry', 'REGISTRY_ID'],
                   inplace=True,
                   ignore_index=True)

expected_file = os.path.join(EXPECTED_DIR, 'get_FRS_ACRES.parquet')
expected = geopandas.read_parquet(expected_file)
expected['ACCURACY_VALUE'] = expected['ACCURACY_VALUE'].astype('int32')
try:
    assert_geodataframe_equal(actual, expected)
except AssertionError as ae:
    print(ae)
    actual.to_parquet(expected_file)

###test_get_tri()
actual = technological.get_tri(aoi_gdf)
actual.drop(columns=['OBJECTID'], inplace=True)
actual.sort_values(by=['EPA_REGISTRY_ID', 'geometry', 'FACILITY_NAME'],
                   inplace=True,
                   ignore_index=True)

expected = test_tech.expected_32('get_tri.parquet')
try:
    assert_geodataframe_equal(actual, expected, normalize=True)
except AssertionError as ae:
    print(ae)
    expected_file = os.path.join(EXPECTED_DIR, 'get_tri.parquet')
    actual.to_parquet(expected_file)


##Tornadoes
from CHAPPIE.hazards import tornadoes

###test_get_tornadoes()
actual = tornadoes.get_tornadoes(aoi_gdf)

# Sorted so expeccted doesn't have to be
actual = actual.sort_values(by=['geometry', 'date'], ignore_index=True)

expected_file = os.path.join(EXPECTED_DIR, 'get_tornaodes_aoi.parquet')
expected = geopandas.read_parquet(expected_file)
try:
    assert_geodataframe_equal(actual, expected)
except AssertionError as ae:
    print(ae)
    actual.to_parquet(expected_file)

###test_process_tornadoes_aoi()
actual = tornadoes.process_tornadoes(actual, aoi_gdf)

# Sorted so expeccted doesn't have to be
actual = actual.sort_values(by=['TornNo', 'Date'], ignore_index=True)

# check columns
expected_cols = ['Year', 'Date', 'TornNo', 'Magnitude', 'geometry']
missing_cols = set(expected_cols) - set(actual.columns)
assert not missing_cols, f"Columns missing: {', '.join(missing_cols)}"

expected_file = os.path.join(EXPECTED_DIR, 'process_tornaodes_aoi.parquet')
expected = geopandas.read_parquet(expected_file)
expected = expected.sort_values(by=['TornNo', 'Date'], ignore_index=True)
expected['Date'] = expected['Date'].astype('datetime64[ms]')
field_list = ['Year', 'TornNo', 'Magnitude', 'wid']
for i in range(len(field_list)):
    expected[field_list[i]] = expected[field_list[i]].astype('int32')
try:
    assert_geodataframe_equal(actual,
                                expected,
                                check_like=True,
                                check_less_precise=True)
except AssertionError as ae:
    print(ae)
    actual.to_parquet(expected_file)

#tropical_cyclones
from CHAPPIE.hazards import tropical_cyclones

###test_get_cyclones()
actual = tropical_cyclones.get_cyclones(aoi_gdf)
actual = actual.sort_values(by=["SID", "day", "USA_WIND", "geometry"],
                            ignore_index=True)
actual.reset_index(drop=True, inplace=True)

expected_file = os.path.join(EXPECTED_DIR, 'cyclones_aoi.parquet')
expected = geopandas.read_parquet(expected_file)
try:
    assert_geodataframe_equal(actual, expected)
except AssertionError as ae:
    print(ae)
    actual.to_parquet(expected_file)
###test_process_cyclones()

## Flood
from CHAPPIE.hazards import flood

### test_get_fema_nfhl()
actual = flood.get_fema_nfhl(aoi_gdf)
actual.drop(columns=['OBJECTID', 'VERSION_ID', 'STUDY_TYP', 'SFHA_TF',
                        'STATIC_BFE', 'V_DATUM', 'DEPTH', 'LEN_UNIT',
                        'VELOCITY', 'VEL_UNIT', 'DUAL_ZONE', 'SOURCE_CIT',
                        'GFID', 'esri_symbology', 'GlobalID', 'Shape__Area',
                        'Shape__Length'], inplace=True)
actual.sort_values(by=['DFIRM_ID', 'FLD_AR_ID', 'geometry'],
                   inplace=True,
                   ignore_index=True)

expected_file = os.path.join(EXPECTED_DIR, 'get_fema_nfhl.parquet')
expected = geopandas.read_parquet(expected_file)

try:
    assert_geodataframe_equal(actual,
                              expected,
                              check_like=True,
                              check_less_precise=True)
except AssertionError as ae:
    print(ae)
    actual.to_parquet(expected_file)
