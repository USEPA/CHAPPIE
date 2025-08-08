# Update expected results
import os

import geopandas
import pandas
from pandas.testing import assert_frame_equal
from geopandas.testing import assert_geodataframe_equal

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
# assert no changes
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

# open up old
expected_file = os.path.join(EXPECTED_DIR, 'get_police.parquet')
expected = geopandas.read_parquet(expected_file)

# assert no changes
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

#assert no changes
try:
    assert_geodataframe_equal(actual, expected)
except AssertionError as ae:
    print(ae)
    actual.to_parquet(expected_file)

###test_get_farm_store()
actual = food.get_farm_store(aoi_gdf, usda_API)
# Old file
expected_file = os.path.join(EXPECTED_DIR, 'get_farm_store.parquet')
expected = geopandas.read_parquet(expected_file)
#assert no changes
try:
    assert_geodataframe_equal(actual, expected)
except AssertionError as ae:
    print(ae)
    actual.to_parquet(expected_file)

##Health
from CHAPPIE.assets import health

###test_get_providers()
actual = health.get_providers(aoi_gdf)
# Test result dataframes
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
# actual.to_parquet(os.path.join(EXPECTED_DIR, 'trails.parquet'))

#assert no changes
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
#test_get_air()
#test_get_bus()
# eco_services
# hazards
## Technological
###test_get_FRS_ACRES()
###test_get_tri()
##Tornadoes
###test_get_tornadoes()
###test_process_tornadoes_aoi()
#tropical_cyclones
###test_get_cyclones()
###test_process_cyclones()
## Flood