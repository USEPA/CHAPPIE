# -*- coding: utf-8 -*-
"""
Retrieve all data for a given AOI

@author: jbousqui
"""
import os

import geopandas
import pandas

from CHAPPIE.assets import (
    cultural,
    education,
    emergency,
    food,
    hazard_infrastructure,
    health,
)
from CHAPPIE.endpoints import hazard_losses
from CHAPPIE.hazards import flood, technological, tornadoes, tropical_cyclones, weather
from CHAPPIE.household import svi

main_dir = r"L:\lab\SHC_1012\Pensacola Model\PPBEP"
out_dir = os.path.join(main_dir, "auto_download")
in_dir = os.path.join(main_dir, "WatershedBoundaries_Blockgroups")
in_dir = os.path.join(in_dir, "WatershedBoundaries_Blockgroups_Merged")
in_dir = os.path.join(in_dir, "BothWatershedsMerged")
aoi = os.path.join(in_dir, "tl_2023_12_01_bg_FL_AL_BothMerged.shp")
aoi_gdf = geopandas.read_file(aoi)

assets_dict = {}
hazards_dict = {}
house_dict = {}

# API Key handling
usda_API = os.environ['usda_API']

# Get cultural assets
assets_dict["historic_sites"] = cultural.get_historic(aoi_gdf)
assets_dict["libraries"] = cultural.get_library(aoi_gdf)
assets_dict["museums"] = cultural.get_museums(aoi_gdf)
assets_dict["worship"] = cultural.get_worship(aoi_gdf)

# Get educational assets
assets_dict["schools_public"] = education.get_schools_public(aoi_gdf)
assets_dict["schools_private"] = education.get_schools_private(aoi_gdf)
assets_dict["child_care"] = education.get_child_care(aoi_gdf)
assets_dict["colleges_uni"] = education.get_colleges_universities(aoi_gdf)
assets_dict["colleges_sup"] = education.get_supplemental_colleges(aoi_gdf)

# Get emergency assets
assets_dict["fire_ems"] = emergency.get_fire_ems(aoi_gdf)
assets_dict["police"] = emergency.get_police(aoi_gdf)

# Get food assets
assets_dict["agritourism"] = food.get_agritourism(aoi_gdf, usda_API)
assets_dict["csa"] = food.get_CSA(aoi_gdf, usda_API)
assets_dict["farmers_market"] = food.get_farmers_market(aoi_gdf, usda_API)
assets_dict["food_hub"] = food.get_food_hub(aoi_gdf, usda_API)
assets_dict["farm_store"] = food.get_farm_store(aoi_gdf, usda_API)

# Get health assets
assets_dict["hospitals"] = health.get_hospitals(aoi_gdf)
#assets_dict["urgent_care"] = health.get_urgent_care(aoi_gdf)
#providers = health.get_providers(aoi_gdf)
#assets_dict["providers"] = health.provider_address(providers)

# Get hazard infrastructure assets
assets_dict["dams"] = hazard_infrastructure.get_dams(aoi_gdf)
assets_dict["levees"] = hazard_infrastructure.get_levee(aoi_gdf)

# Get flood hazard
hazards_dict["flood_FEMA"] = flood.get_fema_nfhl(aoi_gdf)
#TODO: requires parcels first
# flood.get_flood()

# Get hazards
in_crs = 'ESRI:102005'
tornadoes_gdf = tornadoes.get_tornadoes(aoi_gdf.to_crs(in_crs))
hazards_dict["tornadoes"] = tornadoes.process_tornadoes(tornadoes_gdf,
                                                        aoi_gdf.to_crs(in_crs))
cyclones = tropical_cyclones.get_cyclones(aoi_gdf.to_crs('ESRI:102005'))
hazards_dict["tropical_cyclones"] = tropical_cyclones.process_cyclones(cyclones,
                                                                       aoi_gdf.to_crs(in_crs))

# Get weather hazards
hazards_dict["heat"] = weather.get_heat_events(aoi_gdf)

# Get tech hazards
hazards_dict["superfund"] = technological.get_superfund_npl(aoi_gdf)
hazards_dict["brownfields"] = technological.get_FRS_ACRES(aoi_gdf)
hazards_dict["landfills"] = technological.get_landfills(aoi_gdf)
hazards_dict["tri"] = technological.get_tri(aoi_gdf)

# Get hazard endpoints
#hazards_dict["losses"] = hazard_losses.get_hazard_losses

# Get svi metrics
house_dict["svi"] = svi.get_SVI('12033',
                                        level='block group',
                                        year=2022)

#TODO: write QA txt
cols = ["Table", "Column", "data_type", "min", "max", "mean/mode", "NaN_Count"]
df = pandas.DataFrame(columns=cols)
for key, val in assets_dict.items():
    if len(val)==0:
        # Catch empty datsets where /0 will error
        df.loc[len(df)] = [key, "NODATA", "NODATA", "NODATA", "NODATA", "NODATA", "NODATA"]
    else:
        for col in val.columns:
            col_series = val[col]
            col_type = col_series.dtype
            try:
                mean = sum(col_series)/len(col_series)
            except TypeError:
                mean = col_series.mode()
            na = sum(col_series.isna())
            try:
                col_min = min(col_series.dropna())
                col_max = max(col_series.dropna())
            except TypeError:
                col_min = "TYPE_ERROR"
                col_max = "TYPE_ERROR"
            except ValueError:
                col_min = "VALUE_ERROR"
                col_max = "VALUE_ERROR"
            # Table, Column, dtype, min, max, mean, NaN
            row = [key, col, col_type, col_min, col_max, mean, na]
            df.loc[len(df)] = row
# Write QAQC
df.to_csv(os.path.join(out_dir, "assets2.csv"))

# Write results
for key, val in assets_dict.items():
    if val.shape==(0,0):
        # Skip empty
        continue
    if not os.path.exists(os.path.join(out_dir, key)):
        os.makedirs(os.path.join(out_dir, key))
    val.to_parquet(os.path.join(out_dir, key, f"{key}.parquet"))
for key, val in hazards_dict.items():
    if not os.path.exists(os.path.join(out_dir, key)):
        os.makedirs(os.path.join(out_dir, key))
    val.to_parquet(os.path.join(out_dir, key, f"{key}.parquet"))
for key, val in house_dict.items():
    if not os.path.exists(os.path.join(out_dir, key)):
        os.makedirs(os.path.join(out_dir, key))
    val.to_parquet(os.path.join(out_dir, key, f"{key}.parquet"))
