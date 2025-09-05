# -*- coding: utf-8 -*-
"""
Retrieve all data for a given AOI

@author: jbousqui
"""

import os

import geopandas
import pandas

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
from CHAPPIE.layer_query import get_county

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
# Get intersecting county
county_FIPS = get_county(parcel_gdf)["GEOID"].to_list()
# Get svi metrics
dfs = []
for geoid in county_FIPS:
    dfs.append(svi.get_SVI(geoid, level="block group", year=2023))
house_dict["svi"] = pandas.concat(dfs)

# There are a couple ways to associate metrics from house_dict to houesholds,
# i.e., parcel polygons or parcel centroids. Here we ensure a one-to-one
# household to block group by joining the parcel centroids and svi polygons.
svi_gdf = house_dict["svi"].to_crs(parcel_centroids.crs)  # CRS must match
households = parcel_centroids.sjoin(svi_gdf,
                                    how="left",  # Keep all points
                                    rsuffix="svi",
                                    )
# TODO: can likely drop the index, rsuffix took care of the rename
#households = households.rename(columns={"index_right": "svi_index"})

# Get flood hazard
hazards_dict["flood_FEMA"] = flood.get_fema_nfhl(parcel_gdf)
hazards_dict["flood_EA"] = flood.get_flood(parcel_gdf)

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
tornadoes_gdf = tornadoes.get_tornadoes(parcel_gdf.to_crs(in_crs))
hazards_dict["tornadoes"] = tornadoes.process_tornadoes(
    tornadoes_gdf, parcel_gdf.to_crs(in_crs)
)
cyclones = tropical_cyclones.get_cyclones(parcel_gdf.to_crs("ESRI:102005"))
hazards_dict["tropical_cyclones"] = tropical_cyclones.process_cyclones(
    cyclones, parcel_gdf.to_crs(in_crs)
)

# Wind event hazards cover large areas and likely impact a household when
# the parcel is in their path. Here we used the parcel, but because the path is
# buffered based on wind speed, using centroids shouldn't impact most results.
parcel_results = parcel_gdf.sjon(hazards_dict["tropical_cyclones"], how="left")
parcel_results = parcel_results.sjon(hazards_dict["tornadoes"], how="left")

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

# TODO: aggregate?
# NOTE: superfund result wasn't in range (ACCOMACK county, VA)
# NOTE:some 5700 parcel points fall in range of multiple brownfields,
# REGISTRY_ID '110038762416' & '110002476614'
# Multiple tech hazards can be in range of each parcel centroid
# NOTE: landfills didnt generate more duplicate parcel points (all one-to-one)
# NOTE: TRI didn't generate more duplciate parcel points, OBJECTID_left warning
len(households)

# Get community level characteristics
# Note: these will be accessed by networks
# Get cultural assets
assets_dict["historic_sites"] = cultural.get_historic(parcel_gdf)
assets_dict["libraries"] = cultural.get_library(parcel_gdf)
assets_dict["museums"] = cultural.get_museums(parcel_gdf)
assets_dict["worship"] = cultural.get_worship(parcel_gdf)

# Get educational assets
assets_dict["schools_public"] = education.get_schools_public(parcel_gdf)
assets_dict["schools_private"] = education.get_schools_private(parcel_gdf)
assets_dict["child_care"] = education.get_child_care(parcel_gdf)
assets_dict["colleges_uni"] = education.get_colleges_universities(parcel_gdf)
assets_dict["colleges_sup"] = education.get_supplemental_colleges(parcel_gdf)

# Get emergency assets
assets_dict["fire_ems"] = emergency.get_fire_ems(parcel_gdf)
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

#for key, df in assets_dict.items():
#    #route?


# NOTE: Ecosystem services characteristics may be access by other networks
# Get hazard infrastructure assets
assets_dict["dams"] = hazard_infrastructure.get_dams(parcel_gdf)
assets_dict["levees"] = hazard_infrastructure.get_levee(parcel_gdf)


utils.write_QA(assets_dict, os.path.join(out_dir, "assets2.csv"))
utils.write_results_dict(assets_dict, out_dir)
