import geopandas
import os
from CHAPPIE import layer_query


def get_tropical_cyclones_aoi(aoi):
    baseurl = 'https://services2.arcgis.com/FiaPA4ga0iQKduv3/ArcGIS/rest/services/'
    # starting w/ lines only
    url = f'{baseurl}IBTrACS_ALL_list_v04r00_lines_1/FeatureServer'
    #url_pnts = f'{baseurl}Tornado_Tracks_1950_2017_1/FeatureServer'
    max_buff = 160934
    # NOTE: assumes aoi_gdf in meters
    # TODO: assert aoi.crs in meters
    xmin, ymin, xmax, ymax = aoi.total_bounds
    #bbox = [xmin-max_buff, xmax+max_buff, ymin-max_buff, ymax+max_buff]
    #bbox = [xmin, xmax, ymin, ymax]
    bbox = [xmin, ymin, xmax,  ymax]
    out_fields = ['SID', 'NAME', 'USA_WIND', 'USA_PRES', 'year', 'month', 'day']
    
    return layer_query.get_bbox(bbox,
                                url,
                                0,
                                out_fields,
                                aoi.crs.to_epsg(),
                                buff_dist_m = max_buff)


def process_tropical_cyclones_aoi(cyclones_gdf, aoi):
    # project to aoi CRS
    #TODO: must be in meters?
    cyclones_gdf = cyclones_gdf.to_crs(aoi.crs)  # match crs for clip
    # Fix up geometries
    #combine segments with the same SID
    #SID_list = list(set(cyclones_gdf.SID))
    #Note this uses default first for groupby
    cyclones_gdf = cyclones_gdf.dissolve(by='SID', aggfunc='max')
    # TODO: assert aoi.crs is in meters 
    cyclones_gdf['geometry'] = cyclones_gdf.buffer(160934)  # Buffer track
    # clip buffered paths to aoi extent
    cyclones_gdf = cyclones_gdf.clip(aoi.total_bounds)
    
    # Fix up fields
    # Add storm level
    cyclones_gdf['StormLevel'] = "Category 5"
    cyclones_gdf.loc[cyclones_gdf.USA_WIND < 137, 'StormLevel'] = "Category 4"
    cyclones_gdf.loc[cyclones_gdf.USA_WIND < 113, 'StormLevel'] = "Category 3"
    cyclones_gdf.loc[cyclones_gdf.USA_WIND < 96, 'StormLevel'] = "Category 2"
    cyclones_gdf.loc[cyclones_gdf.USA_WIND < 83, 'StormLevel'] = "Category 1"
    cyclones_gdf.loc[cyclones_gdf.USA_WIND < 64, 'StormLevel'] = "Tropical Storm"
    cyclones_gdf.loc[cyclones_gdf.USA_WIND < 34, 'StormLevel'] = "Tropical Depression"
    # Date
    cyclones_gdf['Date'] = [f'{row.year}-{row.month}-{row.day}' for i, row in cyclones_gdf.iterrows()]
    # Rename cols
    update_cols = {'SID': 'SID', 
                   'year': 'Year',
                   'NAME': 'StormName',
                   'USA_WIND': 'WindSpdKts',
                   'USA_PRES': 'PressureMb',
                   }
    return cyclones_gdf.rename(columns=update_cols)
                              
    
def get_tropical_cyclones(out_dir, dataset=['lines', 'points']):
    base_url = "https://www.ncei.noaa.gov/data/international-best-track-archive-for-climate-stewardship-ibtracs/v04r00/access/shapefile/"
    results = []  # use named tuple instead?
    for data in dataset:
        url = f'{base_url}IBTrACS.ALL.list.v04r00.{data}.zip'       
        temp = os.path.join(out_dir, f"{data}_temp.zip")  # temp zip out_file
        layer_query.get_zip(url, temp)  # Download & extract zip
        shp = os.path.join(out_dir, f"IBTrACS.ALL.list.v04r00.{data}.shp")
        results.append(geopandas.read_file(shp))
    
    if len(results)==1:
        return results[0]
    
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