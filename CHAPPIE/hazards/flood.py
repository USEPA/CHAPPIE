"""
Module for flood hazards

@author: tlomba01
"""
from CHAPPIE import layer_query
import pandas

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

    url = 'https://services.arcgis.com/P3ePLMYs2RVChkJx/ArcGIS/rest/services/USA_Flood_Hazard_Reduced_Set_gdb/FeatureServer'
    xmin, ymin, xmax, ymax = aoi.total_bounds
    bbox = [xmin, ymin, xmax, ymax]
    # out_fields = ['geometry', 'DFIRM_ID', 'FLD_AR_ID', 'FLD_ZONE', 'ZONE_SUBTY']

    return layer_query.get_bbox(aoi=bbox,
                                url=url,
                                # out_fields=out_fields,
                                layer=0,
                                in_crs=aoi.crs.to_epsg())

def get_flood(aoi, output=None):
    """Get flood imagery statistics and histogram for polygon within AOI.

    Parameters
    ----------
    aoi : geopandas.GeoDataFrame
        Parcel polygons to be summarized for Area Of Interest (AOI).

    output : str, optional 
        csv file path to Append data to.

    Returns
    -------
    pandas.DataFrame
        Table of results with Mean statistic, and parcel number (id).

    """
    url = 'https://enviroatlas.epa.gov/arcgis/rest/services/Supplemental/Estimated_floodplain_CONUS_WM/ImageServer'
    parcel_id = 'parcelnumb' # unique id column name for parcel data

    df = pandas.DataFrame(columns=[parcel_id, 'mean'])
    if output:
        df.to_csv(output, mode='a', index=False, header=True)
    #aoi = aoi[:1000] #TODO: remove this when tests are written to call only certain parcelnumb's
    for i in range(len(aoi)): #TODO: use iterrows instead?
        data = []
        data.append(aoi[parcel_id][i])
        row = aoi.iloc[[i]]
        actual = layer_query.get_image_by_poly(aoi=aoi, url=url, row=row)
        data.append(actual)
        df.loc[i] = data
        if output:
            df.to_csv(output, mode='a', index=False, header=False)
            df.drop(df.index, inplace=True)
    return df
