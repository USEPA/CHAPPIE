"""
Module for National Landcover Dataset (nlcd) metrics

@author: jbousquin
"""
import os
from datetime import datetime
from tempfile import TemporaryDirectory

#import rioxarray
import rasterio
import requests

from CHAPPIE import layer_query

TIMEOUT = 100


def get_NLCD(aoi, year, dataset="Land_Cover"):
    """Download NLCD raster tiles by polygon extent.

    If not lower 48 only run one state at a time

    Parameters
    ----------
    aoi : geopandas.GeoDataframe
        Area of interest geometries.
    year : integer or string
        Year being retrieved.
    dataset : string
        Valid datasets include Land_Cover, Tree_Canopy, Impervious, or
        roads. The default is "Land_Cover".

    Returns
    -------
    geopandas.GeoDataFrame or array
        Depends on dataset type, array from rasterio
    """
    out_crs = 5070  # Service native(mrlc_display/3857, mrlc_download/5070)
    # Make sure dataset parameter is usable
    datasets = ["Land_Cover", "Impervious", "Tree_Canopy"]
    assert dataset in datasets, f"'{dataset}' not in NLCD datasets"
    # Make sure year parameter is usable
    year = check_year_NLCD(year, dataset)

    # Check if we can work in the aoi.crs or have to change it
    if aoi.crs.to_authority()[0]!='EPSG':
        # TODO: why does web-mercator work but not 4326 or 5070?!
        gdf = aoi.to_crs(3857)
        query_crs = 3857
    else:
        query_crs = aoi.crs.to_epsg()  # CRS for query
        gdf = aoi.copy()

    # Get geo info for query
    bbox = gdf.total_bounds
    # Create subset X and Y string from extent (minx, miny, maxx, maxy)
    subset = [
        f'X("{bbox[0]}","{bbox[2]}")',
        f'Y("{bbox[1]}","{bbox[3]}")',
    ]

    # Determine landmass (based on FIPs state)
    st_df = layer_query.get_state_by_aoi(gdf)
    if not set(st_df.STUSAB).isdisjoint(["AK", "HI", "PR"]):
        # TODO: not robust for multi: e.g., non-conus, or conus + non-conus
        landmass = set(st_df.STUSAB).intersection(["AK", "HI", "PR"]).pop()
    else:
        landmass = "L48"
    # Determine serviceName
    if dataset == "Tree_Canopy" and landmass == "L48":
        serviceName = f"nlcd_tcc_conus_{year}_v2021-4"
        coverage = "mrlc_download__" + serviceName
    else:
        serviceName = f"NLCD_{year}_{dataset}_{landmass}"
        coverage = serviceName

    # Source url (to use mrlc_display change outCRS to 3857)
    # url = f"https://www.mrlc.gov/geoserver/mrlc_display/{coverage}/ows"
    url = f"https://www.mrlc.gov/geoserver/mrlc_download/{serviceName}/ows"
    epsg_url = "http://www.opengis.net/def/crs/EPSG/0/"

    # Create params dict
    params = {
        "service": "WCS",
        "version": "2.0.1",
        "request": "GetCoverage",
        "coverageid": coverage,
        "subset": subset,
        "SubsettingCRS": f"{epsg_url}{query_crs}",
        "format": "image/geotiff",
        "OutputCRS": f"{epsg_url}{out_crs}",
    }

    # Get response
    res = get_url(url, params)
    res.raise_for_status()  # Check response

    # # Save result to TempDir
    with TemporaryDirectory() as temp_dir:
        out_file = os.path.join(temp_dir, f"NLCD_{year}_{dataset}.tif")
        with open(out_file, "wb") as f:
            f.write(res.content)
        # Read in raster using rioxarray
        #rds = rioxarray.open_rasterio(out_file)
        # Read in raster using rasterio
        with rasterio.open(out_file) as src:
            if src.crs:
                raster_crs = src.crs
            else:
                raster_crs = out_crs  # From query
            # clip by aoi
            #geos = aoi.geometry.to_crs(raster_crs, invert=False
            #out_image, out_transform = rasterio.mask.mask(src, geos, crop=True))
            image = src.read(1)  # Read first band as array
    return image


def check_year_NLCD(year, dataset):
    """
    Check a given year is available from different datasets

    Parameters
    ----------
    year : integer or string
        Year being checked.
    dataset : string
        Valid datasets include Land_Cover, Tree_Canopy, Impervious, or roads.

    Returns
    -------
    year : integer
        Valid year.

    """
    year = int(year)  # Ensure year is expected format
    # Make sure year is in dataset
    latest = datetime.now().year
    if dataset in ["Land_Cover", "Impervious"]:
        years = [2001, 2004, 2006, 2008, 2011, 2013, 2016, 2019, 2021]
    elif dataset == "Tree_Canopy":
        years = list(range(2011, 2021))
    elif dataset == "roads":
        years = [1992, 1999, 2002, 2003] + list(range(2008, latest))
    else:
        years = "Problem"
    assert year < latest, f"Only available through {max(years)}"
    assert year in years, f"Year {year} is not in {years}"
    return year


def get_url(url, data=None):
    """
    Standard get request from url

    Parameters
    ----------
    url : string
        url to send request to.
    data : dict, optional
        The payload of data to request. The default is None.

    Returns
    -------
    res : string or json
        Response, type depends on service and data.

    """
    if data:
        res = requests.get(url, data, timeout=TIMEOUT)
    else:
        res = requests.get(url, timeout=TIMEOUT)
    # TODO: watch out for res.url vs url (added back, possibly removed it once)
    assert res.ok, f"Problem with {res.url}"
    return res
