
# Load the pipe %>% -----
library(magrittr)




# Functions required for processing -----
# match_ss_proj(): to avoid transforming raster layers, this function transforms the CRS of the AOI boundary(ies), hurricane paths, etc. to match that of the storm surge
# # # # # # # # #  raster layers
# # shp: AOI boundary(ies), hurricane paths, etc
# # # #  Can be one or multiple - if multiple, resulting spatial data frames are stored in a list
# # crs: coordinate reference system of the storm surge raster layer
match_ss_proj <- function(shp, crs) {
  # Check for multiple shapefiles
  if("list" %in% class(shp)) {
    # Transform shapefiles to match the CRS of storm surge raster layers (all are the same CRS)
    purrr::map(.x = shp,
               .f = sf::st_transform,
               crs = crs)
  } else {
    # Transform the shapefile to match the CRS of storm surge raster layers (all are the same CRS)
    sf::st_transform(shp, crs)
  }
}

# crop_ss_aoi(): this function crops and masks a storm surge raster layer by the AOI boundary(ies) extent to decrease the size of the storm surge raster layer
# # ss: storm surge raster layer
# # aoi: transformed AOI boundary(ies)
# # # #  Can be one or multiple - if multiple, resulting spatial data frames are stored in a list
crop_ss_aoi <- function(ss, aoi) {
  # Check for multiple AOI boundaries
  if("list" %in% class(aoi)) {
    lapply(aoi, function(x) terra::mask(terra::crop(ss, terra::ext(x)), x)) %>%
      purrr::set_names(paste(names(aoi), gsub("y", "y-", stringr::str_split_i(basename(terra::sources(ss)), "_", 2)), sep = "-"))
  } else {
    terra::mask(terra::crop(ss, terra::ext(aoi)), aoi)
  }
}

# crop_ss_hurr(): this function crops and masks storm surge raster layers by buffered hurricane paths
# # paths: buffered hurricane paths spatial data frame
# # ss: storm surge raster layer(s)
# # # # Can be one or multiple - if multiple, resulting cropped and masked rasters are stored in a list
crop_ss_hurr <- function(paths, ss) {
  if("list" %in% class(ss)) {
    # Create an empty list to store results
    l <- list()
    for(n in 1:nrow(paths)) {
      # Subset hurricane paths
      hurr_sub <- paths[n,]
      name <- paste(hurr_sub$Location, gsub(" ", "-", hurr_sub$StormLevel), sep = "-")
      # Mask cropped storm surge by the hurricane's buffered path
      msk <- terra::mask(terra::crop(ss[name][[1]], terra::ext(hurr_sub)), hurr_sub)
      # Save the cropped raster to a list
      suppressWarnings(l[paste(hurr_sub$Location, hurr_sub$SID, sep = "-")] <- msk)
    }
    l
  } else {
    for(n in 1:nrow(paths)) {
      # Subset hurricane paths
      hurr_sub <- paths[n,]
      # Mask cropped storm surge by the hurricane's buffered path
      terra::mask(ss, hurr_sub)
    }
  }
}

# cell_freq_hurr(): this function calculates cell frequencies for each storm surge depth
# # ss: storm surge raster layer(s) cropped and masked by buffered hurricane paths
# # # # Can be one or multiple, but the function produces one resulting data frame regardless of the number of storm surge raster layers
cell_freq_hurr <- function(ss) {
  if("list" %in% class(ss)) {
    # Calculate cell frequency
    hurr_cells <- lapply(ss, terra::freq) %>%
      # Add a new column to each list item for the storm surge raster layer identifier
      purrr::map2(., names(.), ~dplyr::mutate(.x, Name = .y)) |>
      # Combine into one data frame
      dplyr::bind_rows() |>
      dplyr::as_tibble()
  } else {
    # Calculate cell frequency
    dplyr::as_tibble(terra::freq(ss))
  }
}

# cell_freq_aoi(): this function calculates the total number of cells in the AOI boundary(ies)
# # ss: storm surge raster layer(s) cropped and masked by AOI boundary(ies)
# # # # Can be one or multiple, but the function produces one resulting data frame regardless of the number of storm surge raster layers
# # aoi: the AOI boundary(ies) spatial data frame(s)
# # # #  Can be one or multiple, but the function produces one resulting data frame regardless of the number of AOI boundaries
cell_freq_aoi <- function(ss, aoi) {
  res <- dplyr::tibble()
  if("list" %in% class(aoi)) {
    for(s in 1:length(ss)) {
      b <- gsub(paste0("-Category-", sub(".*\\-", "", names(ss[s]))), "", names(ss[s]))
      tmp <- terra::mask(!is.na(ss[[s]]), aoi[[b]]) %>%
        terra::freq(.) |>
        dplyr::mutate(Location = b) |>
        dplyr::group_by(Location) |>
        dplyr::summarise(Total = sum(count)) |>
        dplyr::ungroup()
      res <- rbind(res, tmp)
    }
  } else {
    for(s in 1:length(ss)) {
      b <- gsub(paste0("-Category-", sub(".*\\-", "", names(ss[s]))), "", names(ss[s]))
      tmp <- terra::mask(!is.na(ss[[s]]), aoi) %>%
        terra::freq(.) |>
        dplyr::mutate(Location = b) |>
        dplyr::group_by(Location) |>
        dplyr::summarise(Total = sum(count)) |>
        dplyr::ungroup()
      res <- rbind(res, tmp)
    }
  }
  res
}




# Example with multiple boundaries: FL ROAR -----
# Input data required for processing
# Apply the read_sf() function to all AOI boundary shapefiles in the folder
fl_roar_aoi_upd <- purrr::map(.x = tools::file_path_sans_ext(list.files("L:/Priv/SHC_1012/Florida ROAR/Data/Hazards/Processing/Boundaries", pattern = "OWRem.shp$")),
                              .f = sf::read_sf, dsn = "L:/Priv/SHC_1012/Florida ROAR/Data/Hazards/Processing/Boundaries") %>%
  # Transform each AOI to NAD83 Albers North America projection
  purrr::map(.x = ., .f = sf::st_transform, crs = "+proj=aea +lat_1=20 +lat_2=60 +lat_0=40 +lon_0=-96 +x_0=0 +y_0=0 +ellps=GRS80 +datum=NAD83 +units=m +no_defs") |>
  # Set the names of each list item to the AOI name and type (mitigation bank or service area)
  purrr::set_names(gsub(" Service", "-Service",
                        gsub(" Mitigation", "-Mitigation",
                             gsub("_", " ",
                                  gsub("_Boundary_OWRem.shp", "",
                                       gsub("FLROAR20231227_", "",
                                            list.files("L:/Priv/SHC_1012/Florida ROAR/Data/Hazards/Processing/Boundaries", pattern = "OWRem.shp$")))))))

# Load tropical cyclones processing data
load("L:/Priv/SHC_1012/Florida ROAR/Data/Hazards/Processing/TropicalCyclones/FLROAR20231227_Tropical_Cyclones.rda")

# Create a list of storm surge for all hurricane categories
ss_cat <- purrr::map(.x = list.files("L:/Priv/SHC_1012/Florida ROAR/Data/Hazards/StormSurge/US_SLOSH_MOM_Inundation_v3/US_SLOSH_MOM_Inundation_v3/",
                                     pattern = ".tif$", full.names = TRUE),
                     .f = terra::rast) |>
  # Set the names of each list item to the AOI name and type (mitigation bank or service area)
  purrr::set_names(
    stringr::str_split_i(list.files("L:/Priv/SHC_1012/Florida ROAR/Data/Hazards/StormSurge/US_SLOSH_MOM_Inundation_v3/US_SLOSH_MOM_Inundation_v3/",
                                    pattern = ".tif$"), "_", 2))


# Step 1: Transform AOI boundaries to match the CRS of storm surge raster layers
fl_roar_aoi_proj <- match_ss_proj(fl_roar_aoi_upd, unique(unlist(lapply(ss_cat, terra::crs))))

# Step 2: Crop and mask storm surge raster layers by AOI boundaries
# Check hurricane intensities
unique(hurr_path_buffer$StormLevel)
# From 1996-2016, only Category 1, 3, and 4 hurricanes impacted the FL ROAR AOI boundaries
ss_crop_aoi <- c(crop_ss_aoi(ss_cat$Category1, fl_roar_aoi_proj), crop_ss_aoi(ss_cat$Category3, fl_roar_aoi_proj), crop_ss_aoi(ss_cat$Category4, fl_roar_aoi_proj))

# Step 3: Transform buffered hurricane paths to storm surge CRS
hurr_buffer_ss_proj <- match_ss_proj(hurr_path_buffer, unique(unlist(lapply(ss_cat, terra::crs)))) |>
  # Combine into one spatial data frame with the same CRS
  dplyr::bind_rows() |>
  # Keep only hurricanes
  dplyr::filter(!StormLevel %in% c("Tropical Depression", "Tropical Storm"))

# Step 4: Transform hurricane paths to match the CRS of storm surge raster layers
hurr_path_ss_proj <- match_ss_proj(hurr_path_proj, unique(unlist(lapply(ss_cat, terra::crs)))) |>
  # Combine into one spatial data frame with the same CRS
  dplyr::bind_rows() |>
  # Keep only hurricanes
  dplyr::filter(!StormLevel %in% c("Tropical Depression", "Tropical Storm"))

# Step 5: Crop and mask storm surge rasters by buffered hurricane paths
ss_crop_hurr <- crop_ss_hurr(hurr_buffer_ss_proj, ss_crop_aoi)

# Step 6: Calculate the number of cells in each storm surge depth category for each individual hurricane and AOI
hurr_cells <- cell_freq_hurr(ss_crop_hurr) |>
  # Add columns for storm ID and location name
  dplyr::mutate(SID = stringr::str_split_i(Name, pattern = "-", 3),
                Location = paste(stringr::str_split_i(Name, pattern = "-", 1), stringr::str_split_i(Name, pattern = "-", 2), sep = "-")) %>%
  # Combine with hurricane paths
  dplyr::left_join(., sf::st_drop_geometry(hurr_path_ss_proj)) |>
  # Create Bank and Category columns from the Name column
  dplyr::mutate(Bank = stringr::str_split_i(Name, pattern = "-", 1),
                Category = stringr::str_split_i(Name, pattern = "-", 2)) |>
  # Keep only needed columns
  dplyr::select(Bank, Category, SID, Year, StormName, StormLevel, SSDepth = value, HurrCells = count)

# Step 7: Calculate the total number of cells in the AOI boundaries
aoi_cells <- cell_freq_aoi(ss_crop_aoi, fl_roar_aoi_proj) |>
  # Create Bank and Category columns from the Name column
  dplyr::mutate(Bank = stringr::str_split_i(Location, pattern = "-", 1),
                Category = stringr::str_split_i(Location, pattern = "-", 2)) |>
  # Keep only needed columns
  dplyr::select(Bank, Category, AOICells = Total) |>
  # Keep only distinct rows
  dplyr::distinct()

# Step 8: Calculate the total number of cells with no data (above storm surge)
na_cells <- hurr_cells |>
  # Calculate total cells by location and storm
  dplyr::group_by(Bank, Category, SID, StormLevel, StormName, Year) |>
  dplyr::summarise(HurrTotal = sum(HurrCells)) |>
  # Remove grouping
  dplyr::ungroup() %>%
  # Combine with total cells in AOI
  dplyr::left_join(., aoi_cells) |>
  # Calculate cells above water
  dplyr::mutate(HurrCells = AOICells - HurrTotal,
                SSDepth = "Unaffected") |>
  # Keep only needed columns
  dplyr::select(Bank, Category, SID, Year, StormName, StormLevel, SSDepth, HurrCells)

# Step 9: Calculate the percent area underwater for each individual hurricane and AOI
ss_hurr_per_under <- rbind(hurr_cells, na_cells) %>%
  dplyr::left_join(., aoi_cells) |>
  dplyr::mutate(PerUnder = (HurrCells / AOICells) * 100,
                SSDepth = factor(SSDepth, levels = unique(SSDepth)))

# Check results - should return and empty data frame if all cells are accounted for
ss_hurr_per_under |>
  dplyr::group_by(Bank, Category, StormName, Year) |>
  dplyr::summarise(Total = sum(PerUnder, na.rm = TRUE)) |>
  dplyr::filter(!dplyr::near(Total, 100), !dplyr::near(Total, 0))

# Step 10: Save results
# Save new storm surge per hurricane raster files
for(i in 1:length(ss_crop_hurr)) {
  terra::writeRaster(ss_crop_hurr[[i]],
                     paste0("L:/Priv/SHC_1012/Florida ROAR/Data/Hazards/Processing/StormSurge/FLROAR20231227_Storm_Surge_",
                            gsub("-", "_", gsub(" ", "_", names(ss_crop_hurr)[i])), ".tif"), overwrite = TRUE)
}

# Save percent area underwater
readr::write_csv(ss_hurr_per_under, "L:/Priv/SHC_1012/Florida ROAR/Data/Hazards/Processing/StormSurge/FLROAR20231227_Storm_Surge_AOI_Per_Area_Underwater_1996_2016.csv")

# Save objects produced
save(ss_cat, fl_roar_aoi_proj, ss_crop_aoi, hurr_buffer_ss_proj, hurr_path_ss_proj, ss_crop_hurr, hurr_cells, aoi_cells, na_cells, ss_hurr_per_under,
     file = "L:/Priv/SHC_1012/Florida ROAR/Data/Hazards/Processing/StormSurge/FLROAR20231227_Storm_Surge.rda")




# Example with one boundary: 2020 in Baldwin County, AL -----
# Input data required for processing
# Load updated AOI boundaries
load("L:/Priv/SHC_1012/Florida ROAR/Data/Hazards/Processing/Boundaries/CHAPPIE20231227_Boundaries_Baldwin_County_example.rda")

# Load tropical cyclones processing data
load("L:/Priv/SHC_1012/Florida ROAR/Data/Hazards/Processing/TropicalCyclones/CHAPPIE20231227_Tropical_Cyclones_Baldwin_County_example.rda")

# Create a list of storm surge for all hurricane categories
ss_cat <- purrr::map(.x = list.files("L:/Priv/SHC_1012/Florida ROAR/Data/Hazards/StormSurge/US_SLOSH_MOM_Inundation_v3/US_SLOSH_MOM_Inundation_v3/",
                                     pattern = ".tif$", full.names = TRUE),
                     .f = terra::rast) |>
  # Set the names of each list item to the AOI name and type (mitigation bank or service area)
  purrr::set_names(
    stringr::str_split_i(list.files("L:/Priv/SHC_1012/Florida ROAR/Data/Hazards/StormSurge/US_SLOSH_MOM_Inundation_v3/US_SLOSH_MOM_Inundation_v3/",
                                    pattern = ".tif$"), "_", 2))


# Step 1: Transform the AOI boundary to match the CRS of storm surge raster layers
aoi_al_upd_proj <- match_ss_proj(aoi_al_upd, unique(unlist(lapply(ss_cat, terra::crs))))

# Step 2: Crop and mask storm surge raster layers by the AOI boundary
# Check hurricane intensities
unique(hurr_path_buffer_al$StormLevel)
# In 2020, only Category 1 and 2 hurricanes impacted the AOI boundary
ss_crop_aoi_al <- list(`Baldwin County-Category-1` = crop_ss_aoi(ss_cat$Category1, aoi_al_upd_proj),
                       `Baldwin County-Category-2` = crop_ss_aoi(ss_cat$Category2, aoi_al_upd_proj))

# Step 3: Transform buffered hurricane paths to storm surge CRS
hurr_buffer_ss_proj_al <- match_ss_proj(hurr_path_buffer_al, unique(unlist(lapply(ss_cat, terra::crs)))) |>
  # Combine into one spatial data frame with the same CRS
  dplyr::bind_rows() |>
  # Keep only hurricanes
  dplyr::filter(!StormLevel %in% c("Tropical Depression", "Tropical Storm"))

# Step 4: Transform hurricane paths to match the CRS of storm surge raster layers
hurr_path_ss_proj_al <- match_ss_proj(hurr_path_proj_al, unique(unlist(lapply(ss_cat, terra::crs)))) |>
  # Combine into one spatial data frame with the same CRS
  dplyr::bind_rows() |>
  # Keep only hurricanes
  dplyr::filter(!StormLevel %in% c("Tropical Depression", "Tropical Storm"))

# Step 5: Crop and mask storm surge rasters by buffered hurricane paths
ss_crop_hurr_al <- crop_ss_hurr(hurr_buffer_ss_proj_al, ss_crop_aoi_al)

# Step 6: Calculate the number of cells in each storm surge depth category for each individual hurricane
hurr_cells_al <- cell_freq_hurr(ss_crop_hurr_al) |>
  # Add columns for storm ID and location name
  dplyr::mutate(SID = stringr::str_split_i(Name, pattern = "-", 2),
                Location = stringr::str_split_i(Name, pattern = "-", 1)) %>%
  # Combine with hurricane paths
  dplyr::left_join(., sf::st_drop_geometry(hurr_path_ss_proj_al)) |>
  # Keep only needed columns
  dplyr::select(Location, SID, Year, StormName, StormLevel, SSDepth = value, HurrCells = count)

# Step 7: Calculate the total number of cells in the AOI boundaries
aoi_cells_al <- cell_freq_aoi(ss_crop_aoi_al, aoi_al_upd_proj) |>
  # Keep only needed columns
  dplyr::select(Location, AOICells = Total) |>
  # Keep only distinct rows
  dplyr::distinct()

# Step 8: Calculate the total number of cells with no data (above storm surge)
na_cells_al <- hurr_cells_al |>
  # Calculate total cells by location and storm
  dplyr::group_by(Location, SID, StormLevel, StormName, Year) |>
  dplyr::summarise(HurrTotal = sum(HurrCells)) |>
  # Remove grouping
  dplyr::ungroup() %>%
  # Combine with total cells in AOI
  dplyr::left_join(., aoi_cells_al) |>
  # Calculate cells above water
  dplyr::mutate(HurrCells = AOICells - HurrTotal,
                SSDepth = "Unaffected") |>
  # Keep only needed columns
  dplyr::select(Location, SID, Year, StormName, StormLevel, SSDepth, HurrCells)

# Step 9: Calculate the percent area underwater for each individual hurricane and AOI
ss_hurr_per_under_al <- rbind(hurr_cells_al, na_cells_al) %>%
  dplyr::left_join(., aoi_cells_al) |>
  dplyr::mutate(PerUnder = (HurrCells / AOICells) * 100,
                SSDepth = factor(SSDepth, levels = unique(SSDepth)))

# Check results - should return and empty data frame if all cells are accounted for
ss_hurr_per_under_al |>
  dplyr::group_by(Location, StormName, Year) |>
  dplyr::summarise(Total = sum(PerUnder, na.rm = TRUE)) |>
  dplyr::filter(!dplyr::near(Total, 100), !dplyr::near(Total, 0))

# Step 10: Save results
# Save objects produced
save(ss_cat, aoi_al_upd_proj, ss_crop_aoi_al, hurr_buffer_ss_proj_al, hurr_path_ss_proj_al, ss_crop_hurr_al, hurr_cells_al, aoi_cells_al, na_cells_al, ss_hurr_per_under_al,
     file = "L:/Priv/SHC_1012/Florida ROAR/Data/Hazards/Processing/StormSurge/CHAPPIE20231227_Storm_Surge_Baldwin_County_example.rda")
