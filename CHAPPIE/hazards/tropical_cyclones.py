import geopandas
import os
import urllib.request
import zipfile



def get_tropical_cyclones(out_dir, dataset=['lines', 'points']):
    base_url = "https://www.ncei.noaa.gov/data/international-best-track-archive-for-climate-stewardship-ibtracs/v04r00/access/shapefile/"
    results = []  # use named tuple instead?
    for data in dataset:
        url = f'{base_url}IBTrACS.ALL.list.v04r00.{data}.zip'       
        temp = os.path.join(out_dir, f"{data}_temp.zip")  # temp zip out_file
        urllib.request.urlretrieve(url, temp)  # Download zip
        # Extract shp components
        with zipfile.ZipFile(temp, 'r') as zip_ref:
            zip_ref.extractall(out_dir)
        shp = os.path.join(out_dir, f"IBTrACS.ALL.list.v04r00.{data}.shp")
        results.append(geopandas.read_file(shp))
        
    return results

def process_tropical_cyclones(tropical_cyclones_gdf, aoi_gdf, distance=160934):
    """ Get buffered (based on 'wid' column) hurricane paths for AOI

    Parameters
    ----------
    tropical_cyclones_gdf : geopandas.geodataframe.GeoDataFrame
        All tropical cyclone paths (points).
    aoi_gdf : geopandas.geodataframe.GeoDataFrame
        Area of Interest. CRS must be in meters.
    distance : int, optional
        Distance from the aoi in aoi units (meters).
        The default is 160934 (meters), ~100 miles.


    Returns
    -------
    cyclone_path_aoi : geopandas.geodataframe.GeoDataFrame
        Buffered tornadoe paths for AOI.
    """

    # step 1: Find tropical cyclone track points that fall within a specified
    # distance of the AOI boundary(ies).
    
    # project to aoi CRS
    tropical_cyclones_gdf = tropical_cyclones_gdf.to_crs(aoi_gdf.crs)
    
    # Filter on aoi bbox
    xmin, ymin, xmax, ymax = aoi_gdf.total_bounds
    # index on bbox
    cyclone_aoi = tropical_cyclones_gdf.cx[xmin-distance:xmax+distance,
                                           ymin-distance:ymax+distance]
    # Reduce the columns
    cols = ["Name", "SID", "SEASON", "NAME", "Date", "USA_WIND", "USA_PRES"]
    cyclone_aoi = cyclone_aoi[cols]
            
    # step 2: determine which point is the closest. If multiple points for the
    # same storm have the same distance, keep only the earliest
    
    # step 3: storm level ('USA_WIND' col)
    #gdf[gdf.USA_WIND < 34]['StormLevel'] = "Tropical Depression"
    #gdf[gdf.USA_WIND < 64]['StormLevel'] = "Tropical Storm"
    #gdf[gdf.USA_WIND < 83]['StormLevel'] = "Category 1"
    #gdf[gdf.USA_WIND < 96]['StormLevel'] = "Category 2"
    #gdf[gdf.USA_WIND < 113]['StormLevel'] = "Category 3"
    #gdf[gdf.USA_WIND < 137]['StormLevel'] = "Category 4"
    #else "Category 5")))))),
    
    # This is a placeholder function
    print('process_tropical_cyclones')