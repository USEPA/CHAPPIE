
# Load the pipe %>% -----
library(magrittr)



# Step 1: Read tropical cyclone track points -----
# # Read the shapefile "IBTrACS.NA.list.v04r00.points" from the path
hurr_pts <- sf::read_sf("L:\\Priv\\SHC_1012\\Florida ROAR\\Data\\Hazards\\TropicalCyclones\\IBTrACS.NA.list.v04r00.points", "IBTrACS.NA.list.v04r00.points") |>
  # Create an appropriately formatted Date column
  dplyr::mutate(Date = lubridate::ymd_hms(ISO_TIME))



# Step 2: Project the tropical cyclone track points to the correct NAD83 UTM zone(s) -----
# # project_hurr_pts(): tropical cyclone track points geometries need to be planar for buffering, so this function transforms them to the specified NAD83 UTM zone
# # # pts: tropical cyclone track points spatial data frame
# # # zone: NAD83 UTM zone number to which the tropical cyclone track points data should be converted (from WGS84)
# # # # # # Can be one or multiple - if multiple, resulting spatial data frames are stored in a list
project_hurr_pts <- function(pts, zone) {
  # Check for multiple UTM zones
  if(length(zone) > 1) {
    # Transform the tornado paths spatial data frame to each UTM zone
    purrr::map(.x = unlist(lapply(zone, function(x) paste0("+proj=utm +zone=", x, " +ellps=GRS80 +units=m +no_defs"))),
               .f = sf::st_transform,
               x = pts) %>%
      # Set the names of each list item to their UTM zone projection
      purrr::set_names(unlist(lapply(zone, function(x) paste0("hurr_proj_", x))))
  } else {
    # Transform the tornado paths spatial data frame to the specified UTM zone
    sf::st_transform(pts, paste0("+proj=utm +zone=", zone, " +ellps=GRS80 +units=m +no_defs"))
  }
}



# Step 3: Find tropical cyclone track points that fall within a specified distance of the AOI boundary(ies) and determine which is the closest by storm -----
# # find_hurr_pts(): this function finds all tropical cyclone track points that fall within the specified distance of the AOI boundary(ies)
# # # pts: projected tropical cyclone track points spatial data frame
# # # aoi: the AOI boundary(ies) spatial data frame(s)
# # # # #  Can be one or multiple, but the function produces one resulting spatial data frame regardless of the number of AOI boundaries
# # # dist: within distance in meters
# # # # # # The default distance is 100 miles (160934 m)
# # # name: if only one AOI boundary is supplied, provide a name to serve as an identifier in the resulting spatial data frame
find_hurr_pts <- function(pts, aoi, dist = 160934, name) {
  # Check for multiple AOI boundaries
  if("list" %in% class(aoi)) {
    # Subset tropical cyclone points that are within the specified distance of AOI boundaries
    lapply(aoi, function(x) pts[sf::st_transform(x, terra::crs(pts)), op = sf::st_is_within_distance, dist = dist]) %>%
      # Add a new column to each list item for the AOI boundary names
      purrr::map2(., names(.), ~dplyr::mutate(.x, Name = .y)) %>%
      # Keep only needed columns
      lapply(., "[", c("Name", "SID", "SEASON", "NAME", "Date", "USA_WIND", "USA_PRES")) |>
      # Combine into one data frame
      dplyr::bind_rows()
  } else {
    # Subset tropical cyclone points that are within the specified distance of the AOI boundary
    pts[sf::st_transform(aoi, terra::crs(pts)), op = sf::st_is_within_distance, dist = dist] %>%
      # Add a new column to for the AOI boundary name
      dplyr::mutate(Name = name) |>
      # Keep only needed columns
      dplyr::select(Name, SID, SEASON, NAME, Date, USA_WIND, USA_PRES)
  }
}

# # closest_hurr_pt(): of the tropical cyclone track points within the specified distance of the AOI boundary(ies), this function finds the closest point to the AOI
# # # # # # # # # # #  boundary(ies) for each tropical cyclone
# # # pts: spatial data frame of tropical cyclone track points that fall within the specified distance of AOI boundary(ies)
# # # aoi: AOI boundary(ies)
closest_hurr_pt <- function(pts, aoi) {
  # Check for multiple AOI boundaries
  if("list" %in% class(aoi)) {
    tmp <- lapply(aoi, function(x) cbind(pts, Distance = units::drop_units(sf::st_distance(pts, sf::st_transform(x, terra::crs(pts)))))) %>%
      # Add a new column to each list item for the AOI boundary names
      purrr::map2(., names(.), ~dplyr::mutate(.x, AOI = .y)) |>
      # Combine into one data frame
      dplyr::bind_rows() |>
      # Create a column indicating if the points AOI and distance calculation AOI match
      dplyr::mutate(Match = ifelse(Name == AOI, "Yes", "No")) |>
      # Remove points that don't match
      dplyr::filter(Match != "No")
  } else {
    tmp <- pts %>%
      dplyr::mutate(Distance = units::drop_units(sf::st_distance(., sf::st_transform(aoi, terra::crs(pts)))))
  }
  tmp |>
    # Determine closest point of tropical cyclones to boundaries
    dplyr::group_by(Name, SID) |>
    dplyr::slice_min(Distance) |>
    # Remove grouping
    dplyr::ungroup() |>
    # If multiple points for the same storm have the same distance, keep only the earliest
    dplyr::group_by(Name, SID) |>
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
                  StormLevel = factor(StormLevel, levels = c("Tropical Depression", "Tropical Storm", "Category 1", "Category 2", "Category 3", "Category 4", "Category 5"))) |>
    # Keep only needed columns
    dplyr::select(Name, SID, Year = SEASON, StormName = NAME, Date, WindSpdKts = USA_WIND, PressureMb = USA_PRES, StormLevel) |>
    # Remove grouping
    dplyr::ungroup()
}



# Step 4: Convert tropical cyclone track points of storms passing within 100 miles of the AOI boundary(ies) to paths -----
# # convert_hurr_pts: this function converts tropical cyclone track points of storms passing closest to the AOI boundary(ies) to lines
# # # pts: projected tropical cyclone track points spatial data frame
# # # closest: data frame containing attribute information for storms at the point they are closest to the AOI boundary(ies)
convert_hurr_pts <- function(pts, closest) {
  pts |>
    # Remove tropical cyclones with no storm intensity and keep only storm IDs for tropical cyclone track points closest to the AOI boundary(ies)
    dplyr::filter(SID %in% dplyr::filter(closest, !is.na(StormLevel))$SID) |>
    # Combine tropical cyclone track points based on storm ID
    dplyr::group_by(SID) |>
    dplyr::summarise(do_union = FALSE) |>
    # Convert series of tropical cyclone track points to tropical cyclone paths
    sf::st_cast("LINESTRING") %>%
    # Combine tropical cyclone path lines with tropical cyclone attributes
    dplyr::left_join(., closest) |>
    # Keep only needed columns
    dplyr::select(Name, SID, Year, StormName, Date, WindSpdKts, PressureMb, StormLevel)
}



# Step 5: Buffer projected tropical cyclone paths by distance specified -----
# # buffer_hurr_path(): this function applies a buffer of equivalent to each storm's radius in meters
# # # paths: projected tropical cyclone paths spatial data frame(s)
# # # # # #  Can be one or multiple - if multiple, resulting spatial data frames are stored in a list
# # # dist: within distance in meters
# # # # # # The default distance is 100 miles (160934 m)
buffer_hurr_path <- function(paths, dist = 160934) {
  # Check for multiple projections of the tropical cyclones path data
  if("list" %in% class(paths)) {
    # Apply a buffer equivalent to the specified distance
    lapply(paths, function(x) sf::st_buffer(x, dist = dist)) %>%
      # Set the name of each list item to their UTM zone projection
      purrr::set_names(gsub("proj", "buffer", names(paths)))
  } else {
    # Apply a buffer equivalent to the specified distance
    sf::st_buffer(paths, dist = dist)
  }
}



# Example with multiple AOI boundaries: FL ROAR Tropical Cyclone Process -----
# # Read the shapefile "IBTrACS.NA.list.v04r00.points" from the path
hurr_pts <- sf::read_sf("L:\\Priv\\SHC_1012\\Florida ROAR\\Data\\Hazards\\TropicalCyclones\\IBTrACS.NA.list.v04r00.points", "IBTrACS.NA.list.v04r00.points") |>
  # Filter for needed years
  dplyr::filter(SEASON > 1995, SEASON < 2016) |>
  # Create an appropriately formatted Date column
  dplyr::mutate(Date = lubridate::ymd_hms(ISO_TIME))

# # Project to UTM zones 16 (Breakfast Point) & 17 (Fl Gulf Coast, Little Pine Island, Mangrove Point)
hurr_pts_proj <- project_hurr_pts(hurr_pts, c(16, 17))

# # Load AOI data
# # Apply the read_sf() function to all shapefiles in the folder
fl_roar_aoi <- purrr::map(.x = tools::file_path_sans_ext(list.files("L:\\Priv\\SHC_1012\\Florida ROAR\\Data\\Boundary Shapefiles\\Updated ROAR MB Boundaries\\",
                                                                    pattern = ".shp$")),
                          .f = sf::read_sf,
                          dsn = "L:\\Priv\\SHC_1012\\Florida ROAR\\Data\\Boundary Shapefiles\\Updated ROAR MB Boundaries") |>
  # Set the names of each list item to the AOI name and type (mitigation bank or service area)
  purrr::set_names(
    paste(stringr::str_trim(
      stringr::str_replace_all(
        stringr::str_split_i(
          tools::file_path_sans_ext(
            list.files("L:\\Priv\\SHC_1012\\Florida ROAR\\Data\\Boundary Shapefiles\\Updated ROAR MB Boundaries\\", pattern = ".shp$")), "_", 1), "([[:upper:]])", " \\1")),
      ifelse(
        grepl("RIBITS",
              stringr::str_split_i(
                tools::file_path_sans_ext(
                  list.files("L:\\Priv\\SHC_1012\\Florida ROAR\\Data\\Boundary Shapefiles\\Updated ROAR MB Boundaries\\", pattern = ".shp$")), "_", 2)) == TRUE,
        "Mitigation Bank", "Service Area"),
      sep = "-"))

# # Find which tropical cyclone track points fall within 100 miles of AOI boundaries then subset the closest point for each storm and boundary
hurr_pts_aoi_int <- rbind(sf::st_drop_geometry(closest_hurr_pt(find_hurr_pts(hurr_pts_proj$hurr_proj_16, fl_roar_aoi[1:2]), fl_roar_aoi[1:2])),
                          sf::st_drop_geometry(closest_hurr_pt(find_hurr_pts(hurr_pts_proj$hurr_proj_17, fl_roar_aoi[3:8]), fl_roar_aoi[3:8])))

# # Save the results as a .csv
hurr_pts_aoi_int |>
  # Create Bank and Category columns from the Name column
  dplyr::mutate(Bank = stringr::str_split_i(Name, pattern = "-", 1),
                Category = stringr::str_split_i(Name, pattern = "-", 2)) |>
  # Keep only needed columns
  dplyr::select(Bank, Category, SID, Year, StormName, Date, WindSpdKts, PressureMb, StormLevel) %>%
  readr::write_csv(., "L:\\Priv\\SHC_1012\\Florida ROAR\\Data\\Hazards\\Processing\\TropicalCyclones\\FLROAR20231109_Hurr_Pts_AOI_Closest_1996_2016.csv")

# # Convert tropical cyclone track points for storms passing within 100 miles of AOI boundaries to tropical cyclone paths
hurr_path_proj <- list("hurr_path_proj_16" = dplyr::filter(convert_hurr_pts(hurr_pts_proj$hurr_proj_16, hurr_pts_aoi_int),
                                                           Name %in% c("Breakfast Point-Mitigation Bank", "Breakfast Point-Service Area")),
                       "hurr_path_proj_17" = dplyr::filter(convert_hurr_pts(hurr_pts_proj$hurr_proj_17, hurr_pts_aoi_int),
                                                           !Name %in% c("Breakfast Point-Mitigation Bank", "Breakfast Point-Service Area")))

# # Apply buffer of 100 miles
hurr_path_buffer <- buffer_hurr_path(hurr_path_proj)

# # Transform each list item to WGS84, combine into one data frame, and format
hurr_path_buffer_comb <- purrr::map(.x = hurr_path_buffer,
                                    .f = sf::st_transform,
                                    crs = "epsg:4326") |>
  # Combine all list items into one spatial data frame
  dplyr::bind_rows() |>
  # Create Bank and Category columns from the Name column
  dplyr::mutate(Bank = stringr::str_split_i(Name, pattern = "-", 1),
                Category = stringr::str_split_i(Name, pattern = "-", 2)) |>
  # Keep only needed columns
  dplyr::select(Bank, Category, SID, Year, StormName, Date, WindSpdKts, PressureMb, StormLevel)

# # Save results as new shapefile
sf::st_write(hurr_path_buffer_comb, "L:\\Priv\\SHC_1012\\Florida ROAR\\Data\\Hazards\\Processing\\TropicalCyclones\\FLROAR20231109_Hurr_Buffer_AOI_Intersection_1996_2016.shp")



# Example with one AOI boundary: Determine which tropical cyclones impacted the state of Alabama from 2000 to 2010 -----
hurr_pts_al <- hurr_pts <- sf::read_sf("L:\\Priv\\SHC_1012\\Florida ROAR\\Data\\Hazards\\TropicalCyclones\\IBTrACS.NA.list.v04r00.points", "IBTrACS.NA.list.v04r00.points") |>
  dplyr::filter(SEASON > 2000, SEASON < 2010) |>
  dplyr::mutate(Date = lubridate::ymd_hms(ISO_TIME))
hurr_pts_proj_al <- project_hurr_pts(hurr_pts_al, 16)
aoi_al <- dplyr::filter(spData::us_states, NAME == "Alabama")
hurr_pts_al_int <- sf::st_drop_geometry(closest_hurr_pt(find_hurr_pts(hurr_pts_proj_al, aoi_al, name = "State of AL"), aoi_al))
hurr_path_proj_al <- convert_hurr_pts(hurr_pts_proj_al, hurr_pts_al_int)
hurr_path_buffer_al <- buffer_hurr_path(hurr_path_proj_al)
plot(sf::st_transform(hurr_path_buffer_al$geometry, "epsg:4326"))
plot(sf::st_transform(aoi_al$geometry, "epsg:4326"), axes = TRUE, add = TRUE, col = "red")
