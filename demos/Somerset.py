# -*- coding: utf-8 -*-
"""
Retrieve all data for a given AOI

@author: jbousqui
"""

import os

import geopandas

from CHAPPIE import parcels, utils
from CHAPPIE.assets import (
    cultural,
    education,
    emergency,
    food,
    hazard_infrastructure,
    health,
)

# from CHAPPIE.endpoints import hazard_losses
from CHAPPIE.hazards import flood, technological, tornadoes, tropical_cyclones, weather
from CHAPPIE.household import svi

main_dir = r"L:\lab\SHC_1012\Crisfield, Maryland\Data"
out_dir = os.path.join(main_dir, "auto_download")
in_dir = os.path.join(out_dir, "aoi")
aoi = os.path.join(in_dir, "Somerset_30mBuffer.shp")
aoi_gdf = geopandas.read_file(aoi)

assets_dict = {}
hazards_dict = {}
house_dict = {}

# API Key handling (other users may way to switch these out here)
usda_API = os.environ["usda_API"]

# Start by getting intersecting parcels to relate all characteristics to
parcel_gdf = parcels.get_regrid(aoi_gdf)
parcel_gdf.drop_duplicates(inplace=True)  # Drop duplicates
parcel_gdf.reset_index(inplace=True, drop=True)  # Fix index
# Get a generalized representation to join results to
parcel_centroids = parcels.process_regrid(parcel_gdf)

# Get household level characteristics
house_dict["svi"] = svi.get_SVI_by_aoi(parcel_gdf, year=2023)

# There are a couple ways to associate metrics from house_dict to houesholds,
# i.e., parcel polygons or parcel centroids. Here we ensure a one-to-one
# household to block group by joining the parcel centroids and svi polygons.
svi_gdf = house_dict["svi"].to_crs(parcel_centroids.crs)  # CRS must match
households = parcel_centroids.sjoin(svi_gdf,
                                    how="left",  # Keep all points
                                    rsuffix="svi",
                                    )

# Get flood hazard
hazards_dict["flood_FEMA"] = flood.get_fema_nfhl(parcel_gdf)
# above currently hits failure:
#pyogrio.errors.DataSourceError: Failed to read GeoJSON data; At line 1,
#character 1024001: Unterminated object; Range downloading not supported by this server!
hazards_dict["flood_EA"] = flood.get_flood(parcel_gdf)
# above hits KeyError: 'statistics'

# Some hazards are attributed to households, like household characteristics
# either as those that intersect the parcel polygon or centroid. We use centroid
# to avoid one-to-many relationships, but the most relevant relationship is if
# the building footprint itself intersects the flood zone.
for key, gdf in hazards_dict.items():
    # TODO: faster/better join on parcelID?
    households = households.sjoin(gdf, how="left")
    # TODO: can likely drop the index but may be useful for one vs many
    households = households.rename(columns={"index_right": f"{key}_index"})

# Get event hazards
in_crs = "ESRI:102005"
parcel_gdf = parcel_gdf.to_crs(in_crs)
tornadoes_gdf = tornadoes.get_tornadoes(parcel_gdf)
hazards_dict["tornadoes"] = tornadoes.process_tornadoes(tornadoes_gdf,
                                                        parcel_gdf)
cyclones = tropical_cyclones.get_cyclones(parcel_gdf)
hazards_dict["cyclones"] = tropical_cyclones.process_cyclones(cyclones,
                                                              parcel_gdf)

# Wind event hazards cover large areas and likely impact a household when
# the parcel is in their path. Here we used the parcel, but because the path is
# buffered based on wind speed, using centroids shouldn't impact most results.
parcel_results = parcel_gdf.sjoin(hazards_dict["tornadoes"], how="left")
parcel_results = parcel_results.sjoin(hazards_dict["cyclones"], how="left")

# Back to original GCS for queries
parcel_gdf = parcel_gdf.to_crs(4326)

# Get weather hazards
hazards_dict["heat"] = weather.get_heat_events(parcel_gdf)

# Heat hazards are gatherd by census tract (11 digit ID)
# This allows them to be joined (many parcels to one heat vale) on SVI geoid
hazards_dict["heat"] = hazards_dict["heat"].rename(columns={"id": "heat_id"})
households["tract_id"] = [id[:11] for id in households["GEOID"]]  # Add tract_id
households = households.set_index("tract_id").join(
    hazards_dict["heat"].set_index("geoId")
)
households.reset_index(inplace=True)  # Fix it after the join

# Get hazard endpoints
# hazards_dict["losses"] = hazard_losses.get_hazard_losses


# Note: these may have spatial relations other than overlap (e.g., range)
# Get tech hazards
hazards_dict["superfund"] = technological.get_superfund_npl(parcel_gdf)  #n=1
hazards_dict["brownfields"] = technological.get_FRS_ACRES(parcel_gdf)  #n=8
hazards_dict["landfills"] = technological.get_landfills(parcel_gdf)  #n=5
hazards_dict["tri"] = technological.get_tri(parcel_gdf)  #n=8

# For demonstration purposes we used a 5 km buffer around centroids
# Note index_right is added in first sjoin, not the pandas.join and then each
# subsequent sjoin TODO: figure out if it is needed?
households = households.to_crs("ESRI:102005")  # Use CONUS equidistant conic
for key in ["superfund", "brownfields", "landfills", "tri"]:
    join_params = {
        "df": hazards_dict[key].to_crs(households.crs),
        "how": "left",
        "predicate": "dwithin",
        "distance": "5000",
        "rsuffix": f"{key}",
    }
    households = households.sjoin(**join_params)
    #households = households.rename(columns={"index_right": f"{key}_index"})

# Aggregating - of the results above we expect:
# NOTE: superfund result wasn't in range (ACCOMACK county, VA)
# NOTE: landfills didnt generate more duplicate parcel points (all one-to-one)
# NOTE: TRI didn't generate more duplciate parcel points, OBJECTID_left warning
# NOTE: 5700 parcel points fall in range of multiple brownfields,
# REGISTRY_ID '110038762416' & '110002476614'
# Multiple tech hazards can be in range of each parcel centroid, ideally some
# aggregation method would be used for each field. Luckily it's just the one
# dataset that isn't one-to-one and we can use duplicated index to groupby.
# the demonstrated agg method concats values into a list.
# List fields from joined
cols = hazards_dict["brownfields"].columns

suf = "_brownfields"  # Imitate rsuffix
cols = [f"{col}{suf}" if f"{col}{suf}" in households else col for col in cols]
cols.pop(cols.index('geometry'))  # drop geometry (not joined)

for col in cols:
    households[col] = households.groupby(households.index)[col].apply(list)

# drop duplicates beyond first occurance (based on index)
households = households[~households.index.duplicated()]

# Get community level characteristics
# Note: these will be accessed by networks, for now just get nearest
# Get cultural assets
assets_dict["historic_sites"] = cultural.get_historic(parcel_gdf)
assets_dict["libraries"] = cultural.get_library(parcel_gdf)
assets_dict["museums"] = cultural.get_museums(parcel_gdf)
assets_dict["worship"] = cultural.get_worship(parcel_gdf)

# Get educational assets (currently down - skip)
#assets_dict["schools_public"] = education.get_schools_public(parcel_gdf)
#assets_dict["schools_private"] = education.get_schools_private(parcel_gdf)
#assets_dict["child_care"] = education.get_child_care(parcel_gdf)
#assets_dict["colleges_uni"] = education.get_colleges_universities(parcel_gdf)
#assets_dict["colleges_sup"] = education.get_supplemental_colleges(parcel_gdf)

# Get emergency assets
assets_dict["fire_ems"] = emergency.get_fire_ems(parcel_gdf)  # check url
assets_dict["police"] = emergency.get_police(parcel_gdf)

# Get food assets
assets_dict["agritourism"] = food.get_agritourism(parcel_gdf, usda_API)
assets_dict["csa"] = food.get_CSA(parcel_gdf, usda_API)
assets_dict["farmers_market"] = food.get_farmers_market(parcel_gdf, usda_API)
assets_dict["food_hub"] = food.get_food_hub(parcel_gdf, usda_API)
assets_dict["farm_store"] = food.get_farm_store(parcel_gdf, usda_API)

# Get health assets
assets_dict["hospitals"] = health.get_hospitals(parcel_gdf)
# assets_dict["urgent_care"] = health.get_urgent_care(parcel_gdf)
# providers = health.get_providers(parcel_gdf)
# assets_dict["providers"] = health.provider_address(providers)

households = households.to_crs("ESRI:102005")

# When two points are nearest it results in multiple rows, we can check for
# these by getting len() of results
for key, df in assets_dict.items():
    x = households.sjoin_nearest(df.to_crs(households.crs),
                                 how="left",
                                 rsuffix=f"{key}",
                                 distance_col=f"{key}_dist"
                                 )
    print(f'{key}: {len(x)}')
# We can then explore each (historic_sites, worship) to see why this happened
key, df = "historic_sites", assets_dict["historic_sites"]
test_join = households.sjoin_nearest(df.to_crs(households.crs),
                                     how="left",
                                     rsuffix=f"{key}",
                                     distance_col=f"{key}_dist"
                                     )
test_join[test_join.index.duplicated()]  # Examine duplicates (e.g., 1304)
test_prop_ids = test_join.loc[1304]['PROPERTY_ID'].to_list()
# Look at original geometry for the duplicates
df[df['PROPERTY_ID'].isin(test_prop_ids)]['geometry']
# In a full evaluation the best row/point should be chosen, arbitrary here
# assets_dict["historic_sites0"] = assets_dict["historic_sites"]  # Retain OG
assets_dict["historic_sites"] = df.drop_duplicates(subset=['geometry'])

# Now look at worship
key, df = "worship", assets_dict["worship"]
test_join = households.sjoin_nearest(df.to_crs(households.crs),
                                     how="left",
                                     rsuffix=f"{key}",
                                     distance_col=f"{key}_dist"
                                     )
test_join[test_join.index.duplicated()]  # Examine duplicates (e.g., 1024)
test_join.loc[1024, "NAME"] # Unique places
test_join.loc[1024, ["STREET", "MATCH_ADDR"]]  # PO Box -> address used
test_ids = test_join.loc[1024, "GlobalID_worship"].to_list()
# Look at original geometry for the duplicates
df[df['GlobalID'].isin(test_ids)]['geometry']
# assets_dict["worship0"] = assets_dict["worship"]  # Retain OG
assets_dict["worship"] = df.drop_duplicates(subset=['geometry'])  # 104 -> 83

for key, df in assets_dict.items():
    #route?
    households = households.sjoin_nearest(df.to_crs(households.crs),
                                          how="left",
                                          rsuffix=f"{key}",
                                          distance_col=f"{key}_dist"
                                          )

# Get hazard infrastructure assets (floods were assessed to households)
assets_dict["dams"] = hazard_infrastructure.get_dams(parcel_gdf)
# assets_dict["levees"] = hazard_infrastructure.get_levee(parcel_gdf)  #500 error

# NOTE: Ecosystem services characteristics may be accessed by other networks,
# e.g., downstream from dams along stream networks, but here we'll keep distance
#for key in ["dams", "levees"]:
key = 'dams'
join_params = {
    "df": assets_dict[key].to_crs(households.crs),
    "how": "left",
    "predicate": "dwithin",
    "distance": "5000",
    "rsuffix": f"{key}",
}
households = households.sjoin(**join_params)

# Intermediate query results from the dictionary can be QA-ed/saved
utils.write_QA(assets_dict, os.path.join(out_dir, "assets2.csv"))
utils.write_results_dict(assets_dict, out_dir)

# Results aggregated to parcels can be joined to households
households = households.rename(columns={"id_left": "id"})
 # Drop cols in parcels duplicated in households
cols = ['geometry', 'geoid', 'parcelnumb', 'fema_flood_zone']
parcel_results = parcel_results.drop(columns=cols)
households = households.join(parcel_results, on='id', rsuffix='parcel')

# Results aggregated to households can be saved, e.g., as parquet
households.to_parquet(os.path.join(out_dir, "parcels.parquet"))
