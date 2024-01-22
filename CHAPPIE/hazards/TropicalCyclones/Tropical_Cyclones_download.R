# Tropical cyclones -----
# Download tropical cyclone wind exposure data from the NOAA Office of Coastal Management to the directory specified by "dir"
# Data is for the North Atlantic and Eastern Pacific basins
download_cyclones_noaa_ocm <- function(dir) {
  # Set working directory to dir argument
  setwd(dir)
  # Create temporary .zip file
  temp <- tempfile(fileext = ".zip")
  # Download .zip file to temporary .zip file
  # Update URL as needed from: https://data.noaa.gov/onestop
  downloader::download("https://marinecadastre.gov/downloads/data/mc/TropicalCycloneWindExposure.zip", temp)
  # Unzip .zip file
  unzip(temp)
}

# Download tropical cyclone best tracks and points from the NOAA National Centers for Environmental Information to the directory specified by "dir"
# Data is for all cyclones in all basins
download_cyclones_noaa_ncei <- function(dir) {
  # Set working directory to dir argument
  setwd(dir)
  # Create download header
  UA <- paste('Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0)', 'Gecko/20100101 Firefox/98.0')
  # Create a vector of download URLs
  # Update URL as needed from: https://www.ncei.noaa.gov/products/international-best-track-archive
  URLS <- c("https://www.ncei.noaa.gov/data/international-best-track-archive-for-climate-stewardship-ibtracs/v04r00/access/shapefile/IBTrACS.ALL.list.v04r00.lines.zip",
            "https://www.ncei.noaa.gov/data/international-best-track-archive-for-climate-stewardship-ibtracs/v04r00/access/shapefile/IBTrACS.ALL.list.v04r00.points.zip")
  # Run a loop to download .zip files from URLs
  for(u in URLS) {
    # Create temporary .zip file
    temp <- tempfile(fileext = ".zip")
    # Download .zip file
    dl <- httr::GET(u, httr::add_headers(`User-Agent` = UA, Connection = 'keep-alive'))
    # Save .zip file to temporary file
    writeBin(dl$content, temp)
    # Unzip .zip file
    unzip(temp)
  }
}