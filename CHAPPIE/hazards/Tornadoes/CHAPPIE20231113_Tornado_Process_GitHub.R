
# Load the pipe %>% -----
library(magrittr)


# Step 1: Read tornado paths -----
# # Read the shapefile "1950-2022-torn-aspath" from the path
torn_path <- sf::read_sf("L:\\Priv\\SHC_1012\\Florida ROAR\\Data\\Hazards\\Tornadoes\\1950-2022-torn-aspath\\1950-2022-torn-aspath", "1950-2022-torn-aspath")



# Step 2: Project the tornado paths to the correct NAD83 UTM zone(s) and calculate storm radius in meters -----
# # project_torn_path(): tornado path geometries need to be planar for buffering, so this function transforms them to the specified NAD83 UTM zone
# # # paths: tornado paths spatial data frame
# # # zone: NAD83 UTM zone to which the tornado paths data should be converted (from WGS84)
# # # # # # Can be one or multiple - if multiple, resulting spatial data frames are stored in a list
project_torn_path <- function(paths, zone) {
  # Check for multiple UTM zones
  if(length(zone) > 1) {
    # Transform the tornado paths spatial data frame to each UTM zone
    purrr::map(.x = unlist(lapply(zone, function(x) paste0("+proj=utm +zone=", x, " +ellps=GRS80 +units=m +no_defs"))),
               .f = sf::st_transform,
               x = paths) %>%
      # Set the names of each list item to their UTM zone projection
      purrr::set_names(unlist(lapply(zone, function(x) paste0("torn_proj_", x)))) %>%
      # Add a new column to each list item that calculates the storm radius in meters
      lapply(., function(x) {cbind(x, radM = (x$wid / 2) / 1.094)})
  } else {
    # Transform the tornado paths spatial data frame to the specified UTM zone
    sf::st_transform(paths, paste0("+proj=utm +zone=", zone, " +ellps=GRS80 +units=m +no_defs")) |>
      # Calculate the storm radius in meters
      dplyr::mutate(radM = (wid / 2) / 1.094)
  }
}


# Step 3: Buffer projected tornado paths by storm radius in meters -----
# # buffer_torn_path(): this function applies a buffer of equivalent to each storm's radius in meters
# # # paths: projected tornado paths spatial data frame(s)
# # # # # #  Can be one or multiple - if multiple, resulting spatial data frames are stored in a list
buffer_torn_path <- function(paths) {
  # Check for multiple projections of the tornado paths data
  if("list" %in% class(paths)) {
    # Apply a buffer equivalent to each storm's radius in meters
    lapply(paths, function(x) sf::st_buffer(x, dist = x$radM)) %>%
      # Set the name of each list item to their UTM zone projection
      purrr::set_names(gsub("proj", "buffer", names(paths)))
  } else {
    # Apply a buffer equivalent to each storm's radius in meters
    sf::st_buffer(paths, dist = paths$radM)
  }
}


# Step 4: Determine which tornadoes intersect AOI boundary(ies) -----
# # intersection_torn_aoi(): this function determines which AOI boundary(ies) buffered tornado paths intersect
# # # paths: buffered tornado paths spatial data frame
# # # aoi: AOI boundary(ies)
# # # # #  Can be one or multiple, but the function produces one resulting spatial data frame regardless of the number of AOI boundaries
# # # name: if only one AOI boundary is supplied, provide a name to serve as an identifier in the resulting spatial data frame
intersection_torn_aoi <- function(paths, aoi, name) {
  # Check for multiple AOI boundaries
  if("list" %in% class(aoi)) {
    # Determine which tornadoes intersect AOI boundaries
    lapply(aoi, function(x) paths[sf::st_transform(x, terra::crs(paths)), op = sf::st_intersects]) %>%
      # Add a new column to each list item for the AOI boundary names
      purrr::map2(., names(.), ~dplyr::mutate(.x, Name = .y)) %>%
      # Combine all list items into one spatial data frame
      dplyr::bind_rows()
  } else {
    # Determine which tornadoes intersect AOI boundary
    paths[sf::st_transform(aoi, terra::crs(paths)), op = sf::st_intersects] |>
      # Add a new column for the boundary name
      dplyr::mutate(Name = name)
  }
}





# Example with multiple AOI boundaries: FL ROAR Tornado Process -----
# # Read the shapefile "1950-2022-torn-aspath" from the path
torn_path <- sf::read_sf("L:\\Priv\\SHC_1012\\Florida ROAR\\Data\\Hazards\\Tornadoes\\1950-2022-torn-aspath\\1950-2022-torn-aspath", "1950-2022-torn-aspath") |>
  # Filter for only the years needed
  dplyr::filter(yr > 1995, yr < 2016)

# # Project to UTM zones 16 (Breakfast Point) & 17 (Fl Gulf Coast, Little Pine Island, Mangrove Point)
torn_path_proj <- project_torn_path(torn_path, c(16, 17))

# # Apply buffer equivalent to each storm's radius in meters
torn_path_buffer <- buffer_torn_path(torn_path_proj)

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

# # Determine which tornadoes intersect each AOI boundary and save results in list
torn_path_buffer_int <- list(intersection_torn_aoi(torn_path_buffer$torn_buffer_16, fl_roar_aoi[1:2]),
                             intersection_torn_aoi(torn_path_buffer$torn_buffer_17, fl_roar_aoi[3:8])) |>
  # Set the names of each list item to the UTM zone
  purrr::set_names(c("torn_path_buffer_int_16", "torn_path_buffer_int_17"))

# # Transform each list item to WGS84, combine into one data frame, and format
torn_path_buffer_int_comb <- purrr::map(.x = torn_path_buffer_int,
                                        .f = sf::st_transform,
                                        crs = "epsg:4326") |>
  # Combine all list items into one spatial data frame
  dplyr::bind_rows() |>
  # Create Bank and Category columns from the Name column, correctly format the date column, and format the mag column then convert to a factor
  dplyr::mutate(Bank = stringr::str_split_i(Name, pattern = "-", 1),
                Category = stringr::str_split_i(Name, pattern = "-", 2),
                date = lubridate::ymd(date),
                mag = factor(ifelse(mag < 0, NA, mag), levels = c(NA, 0, 1, 2, 3, 4))) |>
  # Keep only needed columns
  dplyr::select(Bank, Category, Year = yr, Date = date, TornNo = om, Magnitude = mag)

# # Remove the intersecting buffered tornado paths' geometry and save the results as a csv
readr::write_csv(sf::st_drop_geometry(torn_path_buffer_int_comb),
                 "L:\\Priv\\SHC_1012\\Florida ROAR\\Data\\Hazards\\Processing\\Tornadoes\\FLROAR20231108_Torn_Buffer_AOI_Intersection_1996_2016.csv")
# # Save the intersecting buffered tornado paths results as a new shapefile
sf::st_write(torn_path_buffer_int_comb, "L:\\Priv\\SHC_1012\\Florida ROAR\\Data\\Hazards\\Processing\\Tornadoes\\FLROAR20231108_Torn_Buffer_AOI_Intersection_1996_2016.shp")





# Example with one AOI boundary: Determine which tornadoes ocurred in the state of Alabama from 2000 to 2010 -----
torn_path_al <- sf::read_sf("L:\\Priv\\SHC_1012\\Florida ROAR\\Data\\Hazards\\Tornadoes\\1950-2022-torn-aspath\\1950-2022-torn-aspath", "1950-2022-torn-aspath") |>
  dplyr::filter(yr > 2000, yr < 2010)
torn_proj_al <- project_torn_path(torn_path_al, 16)
torn_buffer_al <- buffer_torn_path(torn_proj_al)
aoi_al <- dplyr::filter(spData::us_states, NAME == "Alabama")
torn_buffer_aoi_int_al <- intersection_torn_aoi(torn_buffer_al, aoi_al, "State of AL")
plot(sf::st_transform(aoi_al$geometry, "epsg:4326"), axes = TRUE)
plot(sf::st_transform(torn_buffer_aoi_int_al$geometry, "epsg:4326"), add = TRUE, col = "red")
