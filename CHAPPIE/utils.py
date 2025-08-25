
# -*- coding: utf-8 -*-
"""Module with utility functions

@author: jbousquin
"""
import os

import pandas


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
    """Write mutliple dataframe results as parquet to a folder

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
        if not os.path.exists(os.path.join(out_dir, key)):
            os.makedirs(os.path.join(out_dir, key))
        val.to_parquet(os.path.join(out_dir, key, f"{key}.parquet"))
