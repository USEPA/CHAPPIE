
# Load the pipe operator
library(magrittr)


# Step 1: Read tornado paths
# dir: folder directory containing the shapefile
# file: name of the shapefile without the extension (.shp)
# years: OPTIONAL vector of minimum and maximum years (inclusive) for which the data should be filtered (if omitted all years are included)
read_tornadoes <- function(dir, file, years) {
  # Check if the years parameter is included
  if(missing(years)) {
    # If years is not included, read the whole dataset
    sf::read_sf(dir, file)
  } else {
    # If years is included, read the dataset and filter for the years indicated
    sf::read_sf(dir, file) |>
      dplyr::filter(yr >= min(years), yr <= max(years))
  }
}

torn_path <- read_tornadoes("L:\\Priv\\SHC_1012\\Florida ROAR\\Data\\Hazards\\Tornadoes\\1950-2022-torn-aspath\\1950-2022-torn-aspath", "1950-2022-torn-aspath")


# Step 2: Transform tornado paths to the appropriate UTM zone and calculate storm radius in meters
# Data need to be planar for buffering - UTM Zones 16 (Breakfast Point) & 17 (Fl Gulf Coast, Little Pine Island, Mangrove Point)
torn_proj <- purrr::map(.x = c("+proj=utm +zone=16 +ellps=GRS80 +units=m +no_defs", "+proj=utm +zone=17 +ellps=GRS80 +units=m +no_defs"),
                        .f = sf::st_transform,
                        x = torn_path) %>%
  # Set the names of each list item  to their UTM projection
  purrr::set_names(c("torn_proj_16", "torn_proj_17")) %>%
  # Add a new column to each list item that calculates the storm radius in meters
  lapply(., function(x) {cbind(x, radM = (x$wid / 2) / 1.094)})


# Step 3: Buffer transformed tornado paths by storm radius in meters
torn_buffer <- lapply(torn_proj, function(x) sf::st_buffer(x, dist = x$radM))


# Step 4: Select lines where intersecting AOI
# Apply the read_sf() function to all shapefiles in the folder
boundaries <- purrr::map(.x = tools::file_path_sans_ext(list.files("L:\\Priv\\SHC_1012\\Florida ROAR\\Data\\Boundary Shapefiles\\Updated ROAR MB Boundaries\\",
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

# Determine which buffered tornado paths intersect AOI in UTM Zone 16
torn_aoi_16 <- lapply(boundaries[1:2], function(x) torn_buffer$torn_proj_16[sf::st_transform(x, terra::crs(torn_buffer$torn_proj_16)), op = sf::st_intersects]) %>%
  # Add a new column to each list item for the item's name
  purrr::map2(., names(.), ~dplyr::mutate(.x, Name = .y)) %>%
  # Combine all list items into one
  dplyr::bind_rows() |>
  # Create Bank and Category columns from the Name column, correctly format the date column, and format the mag column then convert to a factor
  dplyr::mutate(Bank = stringr::str_split_i(Name, pattern = "-", 1),
                Category = stringr::str_split_i(Name, pattern = "-", 2),
                date = lubridate::ymd(date),
                mag = factor(ifelse(mag < 0, NA, mag), levels = c(NA, 0, 1, 2, 3, 4))) |>
  # Keep only needed columns
  dplyr::select(Bank, Category, Year = yr, Date = date, TornNo = om, Magnitude = mag)

# Determine which buffered tornado paths intersect AOI in UTM Zone 17
torn_aoi_17 <- lapply(boundaries[3:8], function(x) torn_buffer$torn_proj_17[sf::st_transform(x, terra::crs(torn_buffer$torn_proj_17)), op = sf::st_intersects]) %>%
  # Add a new column to each list item for the item's name
  purrr::map2(., names(.), ~dplyr::mutate(.x, Name = .y)) %>%
  # Combine all list items into one
  dplyr::bind_rows() |>
  # Create Bank and Category columns from the Name column, correctly format the date column, and format the mag column then convert to a factor
  dplyr::mutate(Bank = stringr::str_split_i(Name, pattern = "-", 1),
                Category = stringr::str_split_i(Name, pattern = "-", 2),
                date = lubridate::ymd(date),
                mag = factor(ifelse(mag < 0, NA, mag), levels = c(NA, 0, 1, 2, 3, 4))) |>
  # Keep only needed columns
  dplyr::select(Bank, Category, Year = yr, Date = date, TornNo = om, Magnitude = mag)

# Combine results and transform to WGS84
torn_aoi <- rbind(sf::st_transform(torn_aoi_16, "epsg:4326"), sf::st_transform(torn_aoi_17, "epsg:4326"))

# Remove the geometry and save the results as a csv
readr::write_csv(sf::st_drop_geometry(torn_aoi), "L:\\Priv\\SHC_1012\\Florida ROAR\\Data\\Hazards\\Processing\\Tornadoes\\FLROAR20231108_Tornadoes_AOI_Intersection.csv")
# Save the results as a new shapefile
sf::st_write(torn_aoi, "L:\\Priv\\SHC_1012\\Florida ROAR\\Data\\Hazards\\Processing\\Tornadoes\\FLROAR20231108_Tornadoes_AOI_Intersection.shp")



# Simplified example - Determine tornadoes that intersect the state of Alabama (UTM Zone 16) from 2000-2010 -----
# Read the Alabama state boundary from the built in US States data set
bound_al <- dplyr::filter(spData::us_states, NAME == "Alabama")
# Read the tornado path data and calculate storm radius in meters
torn_path <- read_tornadoes("L:\\Priv\\SHC_1012\\Florida ROAR\\Data\\Hazards\\Tornadoes\\1950-2022-torn-aspath\\1950-2022-torn-aspath",
                            "1950-2022-torn-aspath", c(2000,2010)) %>%
  sf::st_transform(., paste0("+proj=utm +zone=16 +ellps=GRS80 +units=m +no_defs")) |>
  dplyr::mutate(radM = (wid / 2) / 1.094)
# Buffer the tornado paths by the radius in meters
torn_buffer <- sf::st_buffer(torn_path, torn_path$radM)
# Determine which tornadoes intersect the state lines of Arkansas
torn_al <- torn_buffer[sf::st_transform(bound_al, terra::crs(torn_buffer)), op = sf::st_intersects]
# Examine results
plot(sf::st_transform(bound_al$geometry, "epsg:4326"), axes = TRUE)
plot(sf::st_transform(torn_al$geometry, "epsg:4326"), add = TRUE)
