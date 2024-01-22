
# Load the pipe %>% -----
library(magrittr)




# Functions required for processing -----
# dem_to_pts(): this function converts the input DEM to a grid of points
# dem: DEM with elevation in NAVD88 for the AOI
# res: point spacing in meters
dem_to_pts <- function(dem, res) {
  # Set the resolution of the DEM grid cells to the desired resolution
  dem_grid <- terra::aggregate(dem, fact = round(res/3))
  # Set the value of the grid cells to 0 (MHHW height in m)
  terra::values(dem_grid) <- 0
  # Convert the cells to xy coordinates and z height
  as.data.frame(dem_grid, xy = TRUE) |>
    dplyr::rename(z = Layer_1)
}

# dem_to_bbox(): this function converts the input DEM to a bounding box
# dem: DEM with elevation in NAVD88 for the AOI
dem_to_bbox <- function(dem) {
  # Create a bounding box for the raster
  dplyr::tibble(lon = c(terra::ext(dem)[1][[1]], terra::ext(dem)[1][[1]], terra::ext(dem)[2][[1]], terra::ext(dem)[2][[1]], terra::ext(dem)[1][[1]]),
                lat = c(terra::ext(dem)[3][[1]], terra::ext(dem)[4][[1]], terra::ext(dem)[4][[1]], terra::ext(dem)[3][[1]], terra::ext(dem)[3][[1]])) %>%
    # Convert latitude and longitude to points
    sf::st_as_sf(., coords = c("lon", "lat")) %>%
    # Match the bounding box crs to the r
    sf::st_set_crs(., terra::crs(dem)) |>
    # Combine bounding box points into one object
    dplyr::summarise() %>%
    # Convert points to a polygon
    sf::st_cast("POLYGON") |>
    # Convert polygon from "bowtie" to rectangle
    sf::st_convex_hull() %>%
    # Transform to NAD83 Albers North America - planar units (m)
    sf::st_transform(., "+proj=aea +lat_1=20 +lat_2=60 +lat_0=40 +lon_0=-96 +x_0=0 +y_0=0 +ellps=GRS80 +datum=NAD83 +units=m +no_defs")
}


# get_coops_dist(): this function calculates distance from an AOI to all CO-OPS stations -----
# # stn: data frame of CO-OPS station locations
# # aoi: AOI boundary
get_coops_dist <- function(stn, aoi) {
  stn %>%
    # Calculate the distance from the AOI to each CO-OPS station
    dplyr::mutate(DistM = units::drop_units(sf::st_distance(., sf::st_transform(aoi, crs = terra::crs(.))))) |>
    # Order from closest to furthest
    dplyr::arrange(DistM)
}




# Input data required for processing -----
# Apply the read_sf() function to all AOI boundary shapefiles in the folder
fl_roar_mb_upd <- purrr::map(.x = tools::file_path_sans_ext(list.files("L:/Priv/SHC_1012/Florida ROAR/Data/Hazards/Processing/Boundaries/FLROAR_Boundary_Update",
                                                                       pattern = "MitigationBank_Upd_RemOW.shp$")),
                             .f = sf::read_sf, dsn = "L:/Priv/SHC_1012/Florida ROAR/Data/Hazards/Processing/Boundaries/FLROAR_Boundary_Update") %>%
  # Transform each AOI to NAD83 Albers North America projection
  purrr::map(.x = ., .f = sf::st_transform, crs = "+proj=aea +lat_1=20 +lat_2=60 +lat_0=40 +lon_0=-96 +x_0=0 +y_0=0 +ellps=GRS80 +datum=NAD83 +units=m +no_defs") |>
  # Set the names of each list item to the AOI name and type (mitigation bank or service area)
  purrr::set_names(gsub("_", "-",
                        gsub("_Upd_Rem OW.shp", "",
                             gsub("([a-z])([A-Z])", "\\1 \\2",
                                  list.files("L:/Priv/SHC_1012/Florida ROAR/Data/Hazards/Processing/Boundaries/FLROAR_Boundary_Update", pattern = "MitigationBank_Upd_RemOW.shp$")))))


# Read CO-OPS station location information and convert latitude/longitude to points
# Station information reads as polygons when points are needed
coops_stns <- sf::st_drop_geometry(sf::read_sf("L:/Priv/SHC_1012/Florida ROAR/Data/Hazards/Processing/SeaLevelRise/NWLON_coverage/NWLON_coverage", "NWLON_Coverages")) %>%
  # Convert the latitude and longitude listed to points
  sf::st_as_sf(., coords = c("longitude", "latitude"), crs = "epsg:4326") |>
  # Transform to NAD83 Albers North America
  sf::st_transform("+proj=aea +lat_1=20 +lat_2=60 +lat_0=40 +lon_0=-96 +x_0=0 +y_0=0 +ellps=GRS80 +datum=NAD83 +units=m +no_defs") |>
  # Keep only needed columns
  dplyr::select(id, name, state, affil)


# Load NOAA NAVD88 DEMs
fl_dem <- list(pan_east_dem = terra::rast("L:/Priv/SHC_1012/Florida ROAR/Data/Hazards/SeaLevelRise/FL_slr_dem/FL_Pan_East_dem/FL_Pan_East_GCS_3m_NAVDm.tif"),
               west_1_dem = terra::rast("L:/Priv/SHC_1012/Florida ROAR/Data/Hazards/SeaLevelRise/FL_slr_dem/FL_West_1_dem/FL_West_1_GCS_3m_NAVDm.tif"),
               west_2_dem = terra::rast("L:/Priv/SHC_1012/Florida ROAR/Data/Hazards/SeaLevelRise/FL_slr_dem/FL_West_2_dem/FL_West_2_GCS_3m_NAVDm.tif"),
               west_3_dem = terra::rast("L:/Priv/SHC_1012/Florida ROAR/Data/Hazards/SeaLevelRise/FL_slr_dem/FL_West_3_dem/FL_West_3_GCS_3m_NAVDm.tif"),
               sw_dem = terra::rast("L:/Priv/SHC_1012/Florida ROAR/Data/Hazards/SeaLevelRise/FL_slr_dem/FL_SW_dem/FL_SW_GCS_3m_NAVDm.tif"))


# Read table of relative sea level change (MSL)
rsl <- readr::read_csv("L:/Priv/SHC_1012/Florida ROAR/Data/Hazards/SeaLevelRise/USStationsLinearSeaLevelTrends.csv")




# Processing steps -----
# Step 1: Create a grid of points spaced 500m over the extent of each DEM
dem_pts <- purrr::map(fl_dem, dem_to_pts, res = 500)


# Step 2: Save grid results as a text file
purrr::map(x. = dem_pts, .f = write.table,
           file = paste0("L:/Priv/SHC_1012/Florida ROAR/Data/Hazards/Processing/SeaLevelRise/VDatum/", names(.x), ".txt"), sep = ",", row.names = FALSE)


# Step 3: Convert grid points from height relative to MHHW to height relative to NAVD88 using VDatum
# This step is done outside R using the VDatum software


# Step 4: Create a tidal surface representing MHHW in NAVD88 using IDW interpolation
# This step is done outside R using ArcPro and follows the steps outline in the NOAA SLR inundation modeling methods


# Step 5: Create bounding boxes that represent the extent of the DEMs
fl_dem_bbox <- purrr::map(.x = fl_dem, .f = dem_to_bbox)


# Step 6: Determine which CO-OPS stations are closest to or within the extent of the DEMs
fl_dem_stns <- purrr::map(.x = fl_dem_bbox, .f = get_coops_dist, stn = coops_stns) %>%
  # Add a new column to each list item for the DEM names
  purrr::map2(., names(.), ~dplyr::mutate(.x, DEM = .y)) |>
  # Combine into one data frame
  dplyr::bind_rows() |>
  # Determine the closest CO-OPS stations to each DEM
  dplyr::group_by(DEM) |>
  dplyr::slice_min(DistM) |>
  # Remove grouping
  dplyr::ungroup() |>
  # Keep only needed columns
  dplyr::select(DEM, id, name, DistM)


# Step 7: Determine which CO-OPS stations are closest to each AOI
fl_roar_mb_stns <- purrr::map(.x = fl_roar_mb_upd, .f = get_coops_dist, stn = coops_stns) %>%
  # Add a new column to each list item for the DEM names
  purrr::map2(., names(.), ~dplyr::mutate(.x, Location = .y)) |>
  # Combine into one data frame
  dplyr::bind_rows() |>
  # Determine the closest CO-OPS stations to each DEM
  dplyr::group_by(Location) |>
  dplyr::slice_min(DistM) |>
  # Remove grouping
  dplyr::ungroup() |>
  # Keep only needed columns
  dplyr::select(Location, id, name, DistM)


# Step 8: Get the relative sea level trend for each CO-OPS stations closest to or within the DEM extents and determine the total change in sea level from present
rsl_chng <- dplyr::left_join(sf::st_drop_geometry(fl_dem_stns), dplyr::select(dplyr::mutate(rsl, `Station ID` = as.character(`Station ID`)),
                                                                              c(`Station ID`, `First Year`:`+/- 95% CI (mm/yr)`)),
                 by = c("id" = "Station ID")) |>
  dplyr::filter(name %in% fl_roar_mb_stns$name) %>%
  dplyr::left_join(., dplyr::select(sf::st_drop_geometry(fl_roar_mb_stns), id, name, Location)) |>
  # Calculate the total change in sea level per year range
  dplyr::mutate(`1996ChngM` = ((2023 - 1996) * `MSL Trends (mm/yr)`) / 1000,
                `2001ChngM` = ((2023 - 2001) * `MSL Trends (mm/yr)`) / 1000,
                `2006ChngM` = ((2023 - 2006) * `MSL Trends (mm/yr)`) / 1000,
                `2011ChngM` = ((2023 - 2011) * `MSL Trends (mm/yr)`) / 1000,
                `2016ChngM` = ((2023 - 2016) * `MSL Trends (mm/yr)`) / 1000) |>
  # Keep only needed columns
  dplyr::select(DEM, Location, name, `MSL Trends (mm/yr)`, `1996ChngM`:`2016ChngM`)
