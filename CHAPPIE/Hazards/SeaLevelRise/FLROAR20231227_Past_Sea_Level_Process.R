
# Load the pipe %>% -----
library(magrittr)




# Functions required for processing -----
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


# get_stn_orig(): this function retrieves the installation date of the specified CO-OPS station -----
# # stn: CO-OPS station ID
get_stn_orig <- function(stn) {
  # Create the API URL to retrieve the station installation metadata
  url <- paste0("https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations/", stn, "/details.xml")
  # Read the station intallation metadata xml
  api_xml <- suppressMessages(XML::xmlInternalTreeParse(httr::content(httr::GET(url), type = "text")))
  # Convert the metadata xml to a list and keep only the information regarding the station establishment
  XML::xmlToList(api_xml)$established
}


# get_stn_wl(): this function retrieves water level data between the start and end dates for the specified CO-OPS station and datum -----
# # stn: CO-OPS station ID
# # start: start date as a character string in the form YYYYMMDD
# # end: end date as a character string in the form YYYYMMDD
# # datum: datum to which the water level data should be corrected (e.g. MSL, MHHW, etc.)
# # # # #  The full list of accepted datum arguments can be found here: https://api.tidesandcurrents.noaa.gov/api/prod/#datum
get_stn_wl <- function(stn, start, end, datum) {
  # Create the API URL to retrieve water level data
  url <- paste0("https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?begin_date=",
                start, "&end_date=", end, "&station=", stn, "&product=monthly_mean&datum=", datum, "&time_zone=gmt&units=english&format=csv")
  # Read the csv retrieved by the API and create a Date column from the Year and Month columns
  readr::read_csv(url) |>
    dplyr::mutate(Date = lubridate::ym(paste(Year, Month, sep = "-")))
}


# adj_stn_seas(): this function will detect and remove the average seasonal cycle signature from water level trends -----
# # stn_wl: water level data for the station
# # wl_col: column containing the water level data for the chosen datum
adj_stn_seas <- function(stn_wl, wl_col) {
  # Create a vector of water level values from the specified water level measurement
  wl <- stn_wl[[wl_col]]
  # Convert the water level values to a time series object with monthly measurements from the minimum to the maximum dates in the water level data
  stn_ts <- ts(data = wl, frequency = 12, start = c(lubridate::year(min(stn_wl$Date)), lubridate::month(min(stn_wl$Date))),
               end = c(lubridate::year(max(stn_wl$Date)), lubridate::month(max(stn_wl$Date))))
  # Apply a 12-point (monthly) moving average linear filter to extract the overall trend from the data
  stn_trend <- filter(stn_ts, filter = c(1/2, rep(1, 11), 1/2) / 12, method = "convo", sides = 2)
  # Remove the overall trend from the time series to get the seasonal signature
  stn_seas <- stn_ts - stn_trend
  # Calculate the overall seasonal effect in the time series by averaging monthly over all years
  mm <- numeric(frequency(stn_seas))
  for(i in 1:frequency(stn_seas)) {
    mm[i] <- mean(stn_seas[(seq(1, length(stn_seas), by = frequency(stn_seas)) - 1) + i], na.rm = TRUE)
  }
  # Zero
  mm <- mm - mean(mm)
  # Create a data frame representing the seasonal effect by month
  dplyr::tibble(Month = seq(1:12), Seasonal = mm)
}


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


# get_rsl(): this function retrieves the relative sea level trend published by NOAA for all COOPS stations within the extent of the input raster
# extent: raster with the desired extent
get_rsl <- function(extent) {
    # Create a bounding box for the raster
  rast_bbox <- dplyr::tibble(lon = c(terra::ext(extent)[1][[1]], terra::ext(extent)[1][[1]], terra::ext(extent)[2][[1]], terra::ext(extent)[2][[1]], terra::ext(extent)[1][[1]]),
                             lat = c(terra::ext(extent)[3][[1]], terra::ext(extent)[4][[1]], terra::ext(extent)[4][[1]], terra::ext(extent)[3][[1]], terra::ext(extent)[3][[1]])) %>%
    # Convert latitude and longitude to points
    sf::st_as_sf(., coords = c("lon", "lat")) %>%
    # Match the bounding box crs to the r
    sf::st_set_crs(., terra::crs(extent)) |>
    # Combine bounding box points into one object
    dplyr::summarise() %>%
    # Convert points to a polygon
    sf::st_cast("POLYGON") |>
    # Convert polygon from "bowtie" to rectangle
    sf::st_convex_hull() %>%
    # Transform to NAD83 Albers North America - planar units (m)
    sf::st_transform(., "+proj=aea +lat_1=20 +lat_2=60 +lat_0=40 +lon_0=-96 +x_0=0 +y_0=0 +ellps=GRS80 +datum=NAD83 +units=m +no_defs")
  
  stns <- suppressWarnings(sf::st_intersection(coops_stns, rast_bbox))
  
  dplyr::filter(rsl, `Station ID` %in% stns$id)
}




# Input data required for processing -----
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




# Part 1 - Relative sea level change -----
# OPTION 1 - CALCULATE RELATIVE SEA LEVEL CHANGE (MHHW) FROM DATA AVAILABLE FROM NOAA
# Step 1: Get COOPS stations closest to AOI boundaries
stn_dist <- purrr::map(.x = fl_roar_aoi_upd, .f = get_coops_dist, stn = coops_stns) %>%
  # Add a new column to each list item for the AOI boundary names
  purrr::map2(., names(.), ~dplyr::mutate(.x, Location = .y)) %>%
  # Combine all list items into one spatial data frame
  dplyr::bind_rows() |>
  # Create Bank and Category columns from the Name column
  dplyr::mutate(Bank = stringr::str_split_i(Location, pattern = "-", 1),
                Category = stringr::str_split_i(Location, pattern = "-", 2)) |>
  # Keep needed columns
  dplyr::select(Bank, Category, StationID = id, StationName = name, State = state, Affil = affil, DistM) |>
  # Get the closest station for each AOI
  dplyr::group_by(Bank, Category) |>
  dplyr::slice_min(DistM)


# Step 2: Get the installation date for each station
stn_dist <- stn_dist |>
  dplyr::mutate(Install = lubridate::ymd_hms(get_stn_orig(StationID)))


# Step 3: Retrieve water level data for each station
stn_mhhw <- dplyr::tibble()
for(i in unique(stn_dist$StationID)) {
  sub <- dplyr::distinct(dplyr::select(dplyr::filter(stn_dist, StationID == i), StationID, StationName, Install))
  tmp <- get_stn_wl(sub$StationID, paste0(lubridate::year(sub$Install),
                                          ifelse(lubridate::month(sub$Install) < 10, paste0("0", lubridate::month(sub$Install)), lubridate::month(sub$Install)),
                                          ifelse(lubridate::day(sub$Install) < 10, paste0("0", lubridate::day(sub$Install)), lubridate::day(sub$Install))),
                    "20231130", "MHHW") |>
    dplyr::mutate(StationID = sub$StationID,
                  StationName = sub$StationName) |>
    dplyr::filter(!is.na(MHHW)) |>
    dplyr::mutate(MHHWm = measurements::conv_unit(MHHW, "ft", "m"))
  stn_mhhw <- rbind(stn_mhhw, tmp)
}


# Step 4: Remove the seasonal signature from the water level data -----
seas_avg <- dplyr::tibble()
for(i in unique(stn_mhhw$StationID)) {
  tmp <- adj_stn_seas(dplyr::filter(stn_mhhw, StationID == i), "MHHWm") |>
    dplyr::mutate(StationID = i)
  seas_avg <- rbind(seas_avg, tmp)
}


# Step 5: Remove the seasonal effect with the water level data -----
stn_no_seas <- dplyr::left_join(stn_mhhw, seas_avg) |>
  # Adjust the water level data by removing the seasonal effect
  dplyr::mutate(Adjusted = MHHWm - Seasonal)


# Step 6: Calculate the relative sea level trend -----
rel_sl_trend <- dplyr::tibble()
for(i in unique(stn_no_seas$StationID)) {
  tmp_lm <- lm(Adjusted ~ Year, data = dplyr::filter(stn_no_seas, StationID == i))
  tmp <- dplyr::tibble(StationID = i, RelSLTrendMMYr = measurements::conv_unit(tmp_lm$coefficients[[2]], "m", "mm"))
  rel_sl_trend <- rbind(rel_sl_trend, tmp)
}


# Step 7: Add the relative sea level trend with seasonality removed to the station information -----
stn_aoi <- dplyr::left_join(stn_dist, rel_sl_trend) |>
  # Keep only needed columns
  dplyr::select(Bank, Category, StationID, StationName, RelSLTrendMMYr) |>
  # Remove grouping
  dplyr::ungroup()


# OPTION 2 - DOWNLOAD RELATIVE SEA LEVEL CHANGE (MSL) FROM NOAA FOR STATIONS WITHIN THE DESIRED EXTENT
# Step 1: Retrieve relative sea level change for all COOPS stations within the desired extent
rsl_chng <- purrr::map(.x = fl_dem, .f = get_rsl) %>%
  # Add a new column to each list item for the AOI boundary names
  purrr::map2(., names(.), ~dplyr::mutate(.x, Location = .y)) %>%
  # Combine into one data frame
  dplyr::bind_rows() |>
  # Keep only needed columns
  dplyr::select(Location, `Station ID`:`MSL Trends (mm/yr)`) |>
  # Calculate the average relative sea level trend by DEM location
  dplyr::group_by(Location) |>
  dplyr::summarise(AvgMMYr = mean(`MSL Trends (mm/yr)`))




# Part 2 - Create a grid of points to convert to a tidal surface using VDatum and ArcPro -----
# Step 1: Create a grid of points spaced 500m over the extent of each DEM
dem_pts <- purrr::map(fl_dem, dem_to_pts, res = 500)


# Step 2: Save results
# Save each grid of points as a text file
purrr::map(x. = dem_pts, .f = write.table,
           file = paste0("L:/Priv/SHC_1012/Florida ROAR/Data/Hazards/Processing/SeaLevelRise/VDatum/", names(.x), ".txt"), sep = ",", row.names = FALSE)
