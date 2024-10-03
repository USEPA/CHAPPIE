
library(magrittr)

# Example AOI: Little Pine Island service area
little_pine <- sf::read_sf("L:/Priv/SHC_1012/Florida ROAR/Data/Boundary Shapefiles/Updated ROAR MB Boundaries", "LittlePineIsland_ServiceArea")




# Example: Tornado damages 2000 to present in the Little Pine Island service area
# Filter tornadoes for needed years and project to CRS of Little Pine Island service area boundary
torn_path_proj <- sf::st_transform(sf::read_sf("L:/Priv/SHC_1012/Florida ROAR/Data/Hazards/Tornadoes/1950-2022-torn-aspath/1950-2022-torn-aspath", "1950-2022-torn-aspath") |>
                                     dplyr::filter(yr >= 2000), terra::crs(little_pine)) |>
  # Calculate the storm radius in meters
  dplyr::mutate(radM = (wid / 2) / 1.094)

# Buffer projected tornado paths by storm radius in meters
torn_path_buffer <- sf::st_buffer(torn_path_proj, dist = torn_path_proj$radM)

# Determine which tornadoes intersect Little Pine Island service area boundary
intersection_torn_aoi <- function(paths, aoi, name) {
  # Check for multiple AOI boundaries
  if("list" %in% class(aoi)) {
    # Determine which tornadoes intersect AOI boundaries
    lapply(aoi, function(x) paths[sf::st_transform(x, terra::crs(paths)), op = sf::st_intersects]) %>%
      # Add a new column to each list item for the AOI boundary names
      purrr::map2(., names(.), ~dplyr::mutate(.x, Location = .y)) %>%
      # Combine all list items into one spatial data frame
      dplyr::bind_rows()
  } else {
    # Determine which tornadoes intersect AOI boundary
    paths[sf::st_transform(aoi, terra::crs(paths)), op = sf::st_intersects] |>
      # Add a new column for the boundary name
      dplyr::mutate(Location = name)
  }
}
torn_path_buffer_int <- intersection_torn_aoi(torn_path_buffer, little_pine, "Little Pine Island")

# Determine damages from selected tornadoes
get_tornado_losses <- function(tornadoes) {
  # Result of tornado intersection with AOI
  tornadoes |>
    # Losses from 1996-pres (property) and 2007-pres (crops) are in millions of dollars - convert to actual numbers and convert 0 to NA (unknown losses)
    dplyr::mutate(loss = ifelse(yr >= 1996, loss * 1000000, loss),
                  loss = ifelse(loss == 0, NA, loss),
                  closs = ifelse(yr < 2007, NA, closs * 1000000)) %>%
    # Property losses prior to 1996 were categorized - assign values to the categories
    dplyr::left_join(., dplyr::tibble(loss = seq(1:9),
                                      val = c("0-50", "50-500", "500-5000", "5000-50000",
                                              "50000-500000", "500000-5000000", "5000000-50000000",
                                              "50000000-500000000", "5000000000"))) |>
    # For categorized property losses, determine the minimum and maximum potential loss values
    dplyr::mutate(val = ifelse(yr >= 1996, NA, val),
                  minloss = as.numeric(stringr::str_split_i(val, "-", 1)),
                  maxloss = as.numeric(stringr::str_split_i(val, "-", 2)),
                  loss = ifelse(yr >= 1996, loss, maxloss)) |>
    # Keep only needed columns
    dplyr::select(om:mag, inj, fat, loss, closs)
}
get_tornado_losses(torn_path_buffer_int)




# Example: Tropical cyclone damages 2000 to present in the Little Pine Island service area
# Filter tropical cyclones for needed years and project to CRS of Little Pine Island service area boundary
hurr_pts_proj <- sf::st_transform(sf::read_sf("L:/Priv/SHC_1012/Florida ROAR/Data/Hazards/TropicalCyclones/IBTrACS.NA.list.v04r00.points", "IBTrACS.NA.list.v04r00.points") |>
                                       # Create an appropriately formatted Date column
                                       dplyr::mutate(Date = lubridate::ymd_hms(ISO_TIME)) |>
                                       dplyr::filter(SEASON >= 2000), terra::crs(little_pine))

# Determine which tropical cyclones pass within 100 miles of the Little Pine Island service area boundary
find_hurr_pts <- function(pts, aoi, dist = 160934, name) {
  # Check for multiple AOI boundaries
  if("list" %in% class(aoi)) {
    # Subset tropical cyclone points that are within the specified distance of AOI boundaries
    lapply(aoi, function(x) pts[sf::st_transform(x, terra::crs(pts)), op = sf::st_is_within_distance, dist = dist]) %>%
      # Add a new column to each list item for the AOI boundary names
      purrr::map2(., names(.), ~dplyr::mutate(.x, Location = .y)) %>%
      # Keep only needed columns
      lapply(., "[", c("Location", "SID", "SEASON", "NAME", "Date", "USA_WIND", "USA_PRES")) |>
      # Combine into one data frame
      dplyr::bind_rows()
  } else {
    # Subset tropical cyclone points that are within the specified distance of the AOI boundary
    pts[sf::st_transform(aoi, terra::crs(pts)), op = sf::st_is_within_distance, dist = dist] %>%
      # Add a new column to for the AOI boundary name
      dplyr::mutate(Location = name) |>
      # Keep only needed columns
      dplyr::select(Location, SID, SEASON, NAME, Date, USA_WIND, USA_PRES)
  }
}
closest_hurr_pt <- function(pts, aoi) {
  # Check for multiple AOI boundaries
  if("list" %in% class(aoi)) {
    tmp <- lapply(aoi, function(x) cbind(pts, Distance = units::drop_units(sf::st_distance(pts, sf::st_transform(x, terra::crs(pts)))))) %>%
      # Add a new column to each list item for the AOI boundary names
      purrr::map2(., names(.), ~dplyr::mutate(.x, AOI = .y)) |>
      # Combine into one data frame
      dplyr::bind_rows() |>
      # Create a column indicating if the points AOI and distance calculation AOI match
      dplyr::mutate(Match = ifelse(Location == AOI, "Yes", "No")) |>
      # Remove points that don't match
      dplyr::filter(Match != "No")
  } else {
    tmp <- pts %>%
      dplyr::mutate(Distance = units::drop_units(sf::st_distance(., sf::st_transform(aoi, terra::crs(pts)))))
  }
  tmp |>
    # Determine closest point of tropical cyclones to boundaries
    dplyr::group_by(Location, SID) |>
    dplyr::slice_min(Distance) |>
    # Remove grouping
    dplyr::ungroup() |>
    # If multiple points for the same storm have the same distance, keep only the earliest
    dplyr::group_by(Location, SID) |>
    dplyr::slice_min(Date) |>
    # Remove grouping
    dplyr::ungroup() |>
    # Add storm intensity
    dplyr::mutate(StormLevel = ifelse(USA_WIND < 34, "Tropical Depression",
                                      ifelse(USA_WIND < 64, "Tropical Storm",
                                             ifelse(USA_WIND < 83, "Category 1",
                                                    ifelse(USA_WIND < 96, "Category 2",
                                                           ifelse(USA_WIND < 113, "Category 3",
                                                                  ifelse(USA_WIND < 137, "Category 4", "Category 5")))))),
                  StormLevel = factor(StormLevel, levels = c("Tropical Depression", "Tropical Storm", "Category 1", "Category 2",
                                                             "Category 3", "Category 4", "Category 5"))) |>
    # Keep only needed columns
    dplyr::select(Location, SID, Year = SEASON, StormName = NAME, Date, WindSpdKts = USA_WIND, PressureMb = USA_PRES, StormLevel) |>
    # Remove grouping
    dplyr::ungroup()
}
hurr_pts_aoi_int <- closest_hurr_pt(find_hurr_pts(hurr_pts_proj, little_pine, name = "Little Pine Island"), little_pine)

# Determine damages from selected tropical cyclones
get_cyclone_losses <- function(storm, aoi) {
  # Determine which counties are in the AOI
  target_counties <- tigris::counties()[sf::st_transform(aoi, terra::crs(tigris::counties())), op = sf::st_intersects] |>
    # Create a state-county FIPS identifier
    dplyr::mutate(STCZFP = paste(as.numeric(STATEFP), as.numeric(COUNTYFP), sep = "-"))
  
  # Read the compiled NOAA Storm Events database (1950-2022)
  readr::read_csv("L:/Priv/SHC_1012/Florida ROAR/Data/Hazards/StormEvents/StormEvents_details_d1950-2022.csv") |>
    # Add columns for month and state-county FIPS identifier
    dplyr::mutate(MONTH = as.numeric(stringr::str_sub(BEGIN_YEARMONTH, start = -2)),
                  STCZFP = paste(STATE_FIPS, CZ_FIPS, sep = "-")) |>
    # Keep only counties in the AOI
    dplyr::filter(STCZFP %in% unique(target_counties$STCZFP)) |>
    # Search episode narratives for the storm names by row
    dplyr::rowwise() |>
    # Assign STORM as the first storm name that appears in the narrative
    dplyr::mutate(STORM = stringr::str_to_upper(stringr::str_split(EPISODE_NARRATIVE, pattern = " ")[[1]][stringr::str_split(EPISODE_NARRATIVE, pattern = " ")[[1]]
                                                                                                          %in% stringr::str_to_title(unique(storm$StormName))][1])) |>
    # Create a storm identifier assigning matched storms to a season
    dplyr::mutate(ID = paste(YEAR, STORM, sep = "-")) |>
    # Keep only storms that occurred in the correct season
    dplyr::filter(ID %in% unique(dplyr::mutate(storm, ID = paste(Year, StormName, sep = "-"))$ID)) |>
    # Keep only needed columns
    dplyr::select(YEAR, MONTH, DAY = BEGIN_DAY, TIME = BEGIN_TIME, TZ = CZ_TIMEZONE, STATE, CZ_NAME, EVENT_TYPE, STORM, INJURIES_DIRECT:SOURCE, EPISODE_NARRATIVE, EVENT_NARRATIVE) |>
    # Remove storm events that did not match with any storm names (not tropical cyclone related)
    dplyr::filter(!is.na(STORM)) |>
    # Sort by date of event, state, and county
    dplyr::arrange(YEAR, MONTH, DAY, STATE, CZ_NAME)
}
get_cyclone_losses(hurr_pts_aoi_int, little_pine)




# Example: Miscellaneous hazard damages 2000 to present in the Little Pine Island service area
# Determine damages from selected tropical cyclones
get_hazard_losses <- function(event, aoi) {
  # Determine which counties are in the AOI
  target_counties <- tigris::counties()[sf::st_transform(aoi, terra::crs(tigris::counties())), op = sf::st_intersects] |>
    # Create a state-county FIPS identifier
    dplyr::mutate(STCZFP = paste(as.numeric(STATEFP), as.numeric(COUNTYFP), sep = "-"))
  
  # Read the compiled NOAA Storm Events database (1950-2022)
  events <- readr::read_csv("L:/Priv/SHC_1012/Florida ROAR/Data/Hazards/StormEvents/StormEvents_details_d1950-2022.csv") |>
    # Add columns for month and state-county FIPS identifier
    dplyr::mutate(STCZFP = paste(STATE_FIPS, CZ_FIPS, sep = "-")) |>
    # Keep only counties in the AOI
    dplyr::filter(STCZFP %in% unique(target_counties$STCZFP))
  
  # Search for natural hazard keywords
  if(length(event) > 1) {
    events |>
      # Search for multiple natural hazard keywords in the event types
      dplyr::filter(grepl(stringr::str_c(event, collapse = "|"), EVENT_TYPE, ignore.case = TRUE)) |>
      # Create a column for month
      dplyr::mutate(MONTH = as.numeric(stringr::str_sub(BEGIN_YEARMONTH, start = -2))) |>
      # Keep only needed columns
      dplyr::select(YEAR, MONTH, DAY = BEGIN_DAY, TIME = BEGIN_TIME, TZ = CZ_TIMEZONE, STATE, CZ_NAME, EVENT_TYPE, INJURIES_DIRECT:SOURCE, EPISODE_NARRATIVE, EVENT_NARRATIVE)
  } else {
    events |>
      # Search for the natural hazard keyword in the event types
      dplyr::filter(grepl(event, EVENT_TYPE, ignore.case = TRUE)) |>
      # Create a column for month
      dplyr::mutate(MONTH = as.numeric(stringr::str_sub(BEGIN_YEARMONTH, start = -2))) |>
      # Keep only needed columns
      dplyr::select(YEAR, MONTH, DAY = BEGIN_DAY, TIME = BEGIN_TIME, TZ = CZ_TIMEZONE, STATE, CZ_NAME, EVENT_TYPE, INJURIES_DIRECT:SOURCE, EPISODE_NARRATIVE, EVENT_NARRATIVE)
  }
}
get_hazard_losses("rain", little_pine)
get_hazard_losses(c("flood", "storm surge"), little_pine)
