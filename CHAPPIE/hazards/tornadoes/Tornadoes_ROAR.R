# Tornadoes -----
# Download tornado path, initial starting points, and corresponding .csv files from the NOAA National Weather Service Storm Prediction Center to the directory specified by "dir"
# Data is for the entire US
download_tornados_noaa_nws <- function(dir) {
  # Set working directory to dir argument
  setwd(dir)
  # Create a vector of download URLs
  # Update URL as needed from: https://www.spc.noaa.gov/gis/svrgis/
  URLS <- c("https://www.spc.noaa.gov/gis/svrgis/zipped/1950-2022-torn-aspath.zip",
            "https://www.spc.noaa.gov/gis/svrgis/zipped/1950-2022-torn-initpoint.zip",
            "https://www.spc.noaa.gov/wcm/data/1950-2022_torn.csv.zip")
  # Run a loop to download .zip files from URLs
  for(u in URLS) {
    # Create temporary .zip file
    temp <- tempfile(fileext = ".zip")
    # Download .zip file to temporary .zip file
    downloader::download(u, temp)
    # Unzip .zip file
    unzip(temp)
  }
}
