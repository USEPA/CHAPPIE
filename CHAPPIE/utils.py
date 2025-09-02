# -*- coding: utf-8 -*-
"""Module with utility functions

@author: jbousquin
"""
import os
import time
import urllib.request
import zipfile
from io import BytesIO
from tempfile import TemporaryDirectory
from warnings import warn

import pandas
import py7zr
import requests
from geopandas import read_file


def get_zip(url, temp_file):
    """Download and extract contants of zip file from url to specified directory

    Note: this is used for download of full datasets (tornadoes and cyclones)

    Parameters
    ----------
    url : str
        url for zipfile download
    temp_file : str
        Directory to write contents of zip file to
    """
    out_dir = os.path.dirname(temp_file)
    urllib.request.urlretrieve(url, temp_file)  # Download zip

    # Extract
    with zipfile.ZipFile(temp_file, "r") as zip_ref:
        zip_ref.extractall(out_dir)


def get_from_zip(url, expected_csvs, encoding="utf-8"):
    """Get csvs from zip as pandas.DataFrame.

    Note: this doesn't seem to be implemented anywhere

    Parameters
    ----------
        url : str
            Uniform Resource Locator (URL) for the zip file.
        expected_csvs : list | str
            csv file(s) to retrieve from zip.
        encoding : str, optional
            Encoding for pandas to use. Defaults to "utf-8".

    Returns
    -------
        df : pandas.DataFrame
            Combined table of results from expected csv file(s).
    """
    # TODO: try except encoding instead?
    if isinstance(expected_csvs, str):
        expected_csvs = list(expected_csvs)
    res = requests.get(url)
    res.raise_for_status()  # exception if not OK
    with zipfile.ZipFile(BytesIO(res.content)) as zip_file:
        dfs = []
        for filename in expected_csvs:
            with zip_file.open(filename) as extracted_file:
                content = extracted_file.read()
                dfs.append(pandas.read_csv(BytesIO(content), encoding=encoding))
    df = pandas.concat(dfs, ignore_index=True)

    return df


def download_unzip_lyrpkg(url, save_path=None):
    """Download and unzip recreation area layer packages from URL

    Parameters
    ----------
    url : str
        The layer package download url
    save_path : str, optional
        Folder path for download, by default None uses tempfile.TemporaryDirectory

    Returns
    -------
    geopandas.GeoDataFrame
        GeoDataFrame for recreation areas.
    """
    #Download the file from `url` and save it as tempfile
    response = requests.get(url)  # Send GET request to the URL
    response.raise_for_status()  # Assert request was successful

    gdb_file = "recareas.gdb"

    with TemporaryDirectory() as temp_dir:
        with py7zr.SevenZipFile(BytesIO(response.content), mode='r') as z:
                # List all archived file names from the zip
                file_list = z.namelist()
                # List all top level folders (unique). NOTE: no sort/order
                folders = list(set([f.split('/')[0] for f in file_list]))
                # List folder version suffix
                v_sufs = ["".join(c for c in x if c.isdigit()) for x in folders]
                # Folder name with largest version suffix
                folder = [x for x in folders if x.endswith(max(v_sufs))][0]
                # Get files in desired folder
                # Note: this excludes ~/0000USA Recreational Areas.lyr')
                select_files = [f for f in file_list if f.startswith(f'{folder}/{gdb_file}')]
                # Extract the selected files to a temp directory
                z.extract(path=temp_dir, targets=select_files)
                #extract the selected files using the custom factory
                gdf = read_file(os.path.join(temp_dir, f'{folder}', gdb_file))

    return gdf


def write_QA(results_dict, out_csv_file):
    """Create CSv with Quality Assurance metrics from results dictionary

    Parameters
    ----------
    results_dict : dict
        dictionary where each key is the table name and value is the dataframe
    out_csv_file : str
        Path and file to save QA csv
    """
    cols = ["Table", "Column", "data_type", "min", "max", "mean/mode", "NaN_Count"]
    df = pandas.DataFrame(columns=cols)
    for key, val in results_dict.items():
        if len(val)==0:
            # Catch empty datsets where /0 will error
            df.loc[len(df)] = [key] + 6*["NODATA"]
        else:
            for col in val.columns:
                col_series = val[col]
                col_type = col_series.dtype
                try:
                    mean = sum(col_series)/len(col_series)
                except TypeError:
                    mean = col_series.mode()
                na = sum(col_series.isna())
                try:
                    col_min = min(col_series.dropna())
                    col_max = max(col_series.dropna())
                except TypeError:
                    col_min = "TYPE_ERROR"
                    col_max = "TYPE_ERROR"
                except ValueError:
                    col_min = "VALUE_ERROR"
                    col_max = "VALUE_ERROR"
                # Table, Column, dtype, min, max, mean, NaN
                row = [key, col, col_type, col_min, col_max, mean, na]
                df.loc[len(df)] = row
    # Write QAQC
    df.to_csv(out_csv_file)


def write_results_dict(results_dict, out_dir):
    """Write multiple dataframe results as parquet to a folder

    Parameters
    ----------
    results_dict : dict
        dictionary where each key is the table name and value is the dataframe
    out_dir : str
        Folder to save results in
    """
    for key, val in results_dict.items():
        if val.shape==(0,0):
            # Skip empty
            continue
        # Generating a folder for each because esri wanted it that way...
        if not os.path.exists(os.path.join(out_dir, key)):
            os.makedirs(os.path.join(out_dir, key))
        val.to_parquet(os.path.join(out_dir, key, f"{key}.parquet"))


def post_request(url, data):
    """ Generate post request from url and data.

    Parameters
    ----------
    url : str
        URL for post request.
    data : dict
        Data dictionary for post request body.

    Returns
    -------
    json
        Post request response json.

    """
    count = 0

    while True:
        try:
            r = requests.post(url, data=data)
            r.raise_for_status()
            r_json = r.json()
            return r_json
        except requests.exceptions.ConnectionError as e:
            count += 1
            if count < 2:
                warn(f"Connection error, count is {count}. Error: {e}")
                time.sleep(5)
                continue
            else:
                return {"url": url,
                        "status": "error",
                        "reason": f"Connection error, {count} attempts",
                        "text": ""}
        except Exception as e:
            warn(f"Response: {r}, Error: {e}")
            return {"url": url, "data": data, "status": r.status_code}
