"""
Module for flood hazards

@author: tlomba01
"""

import warnings

import pandas
from numpy import nan

from CHAPPIE import layer_query


def get_fema_nfhl(aoi):
    """Get FEMA NFHL sites within AOI.

    Parameters
    ----------
    aoi : geopandas.GeoDataFrame
        Spatial definition for Area Of Interest (AOI).

    Returns
    -------
    geopandas.GeoDataFrame
        GeoDataFrame for FEMA NFHL.

    """

    url = "https://services.arcgis.com/P3ePLMYs2RVChkJx/ArcGIS/rest/services/USA_Flood_Hazard_Reduced_Set_gdb/FeatureServer"
    xmin, ymin, xmax, ymax = aoi.total_bounds
    bbox = [xmin, ymin, xmax, ymax]
    # out_fields = ['geometry', 'DFIRM_ID', 'FLD_AR_ID', 'FLD_ZONE', 'ZONE_SUBTY']

    return layer_query.get_bbox(
        aoi=bbox,
        url=url,
        # out_fields=out_fields,
        layer=0,
        in_crs=aoi.crs.to_epsg(),
    )


def get_flood(aoi, output=None):
    """Get flood imagery statistics and histogram for polygon within AOI.

    Parameters
    ----------
    aoi : geopandas.GeoDataFrame
        Parcel polygons to be summarized for Area Of Interest (AOI).

    output : str, optional
        csv file path to Append data to. The default is None and does not write to csv.

    Returns
    -------
    pandas.DataFrame
        Table of results with Mean statistic, and parcel number (id).

    """
    url = "https://enviroatlas.epa.gov/arcgis/rest/services/Supplemental/Estimated_floodplain_CONUS_WM/ImageServer"
    parcel_id = "parcelnumb"  # unique id column name for parcel data

    df = pandas.DataFrame(columns=[parcel_id, "mean"])
    # Add headers to the csv at beginning once, since the rows are appended to csv one by one hereafter
    if output:
        df.to_csv(output, mode="a", index=False, header=True)

    for i in range(len(aoi)):  # TODO: use iterrows instead?
        data = []
        data.append(aoi[parcel_id][i])
        row = aoi.iloc[[i]]
        datadict = layer_query.get_image_by_poly(aoi=aoi, url=url, row=row)
        try:
            actual = datadict["statistics"][0]["mean"]
        except IndexError as e:
            warnings.warn(f"Response does not contain mean value: {datadict}")
            actual = nan
        data.append(actual)
        df.loc[i] = data
        # This probably could be improved by using iterrows.
        # Iterrows may obscure the geometry somewhat, but is worth revisiting.
        if output:
            df.to_csv(output, mode="a", index=False, header=False)
            df.drop(df.index, inplace=True)
    return df
