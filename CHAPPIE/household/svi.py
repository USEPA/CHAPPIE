# -*- coding: utf-8 -*-
"""
Lookups for SVI

NOTE: imports are all for last function

Created on Mon Sep 25 14:41:17 2023

@author: jbousqui
"""
import pygris
from pygris.data import get_census


# SVI dict
def variables(subset=None):
        x = {
        "FIPS": [],
        "Area": [],
        "TotPop": ["B01003_001E"],
        "HousUnits": ["B25001_001E"],
        "Household": ["B11001_001E"],
        "Poverty150": ["B29003_001E", "B29003_002E"],
        "Unemploy": ["B23025_003E", "B23025_005E"],
        "HouseBurd": [
            "B25074_001E",
            "B25074_006E",
            "B25074_007E",
            "B25074_008E",
            "B25074_009E",
            "B25074_015E",
            "B25074_016E",
            "B25074_017E",
            "B25074_018E",
            "B25074_024E",
            "B25074_025E",
            "B25074_026E",
            "B25074_027E",
            "B25074_033E",
            "B25074_034E",
            "B25074_035E",
            "B25074_036E",
            "B25074_042E",
            "B25074_043E",
            "B25074_044E",
            "B25074_045E",
            "B25074_051E",
            "B25074_052E",
            "B25074_053E",
            "B25074_054E",
            "B25074_060E",
            "B25074_061E",
            "B25074_062E",
            "B25074_063E",
            "B25091_001E",
            "B25091_008E",
            "B25091_009E",
            "B25091_010E",
            "B25091_011E",
            "B25091_019E",
            "B25091_020E",
            "B25091_021E",
            "B25091_022E",
        ],
        "NoHSDiplo": [
            "B15003_001E",
            "B15003_017E",
            "B15003_018E",
            "B15003_019E",
            "B15003_020E",
            "B15003_021E",
            "B15003_022E",
            "B15003_023E",
            "B15003_024E",
            "B15003_025E",
        ],
        "NoHlthIns": [
            "B27010_001E",
            "B27010_017E",
            "B27010_033E",
            "B27010_050E",
            "B27010_066E",
        ],
        "65andover": [
            "B01001_001E",
            "B01001_020E",
            "B01001_021E",
            "B01001_022E",
            "B01001_023E",
            "B01001_024E",
            "B01001_025E",
            "B01001_044E",
            "B01001_045E",
            "B01001_046E",
            "B01001_047E",
            "B01001_048E",
            "B01001_049E",
        ],
        "17andbelow": [
            "B01001_001E",
            "B01001_003E",
            "B01001_004E",
            "B01001_005E",
            "B01001_006E",
            "B01001_027E",
            "B01001_028E",
            "B01001_029E",
            "B01001_030E",
        ],
        "DisableCiv": [
            "C21007_001E",
            "C21007_005E",
            "C21007_008E",
            "C21007_012E",
            "C21007_015E",
            "C21007_020E",
            "C21007_023E",
            "C21007_027E",
            "C21007_030E",
        ],
        "SPH": ["B11001_002E", "B11001_005E", "B11001_006E"],
        "ELP": [
            "B16004_001E",
            "B16004_007E",
            "B16004_008E",
            "B16004_012E",
            "B16004_013E",
            "B16004_017E",
            "B16004_018E",
            "B16004_022E",
            "B16004_023E",
            "B16004_029E",
            "B16004_030E",
            "B16004_034E",
            "B16004_035E",
            "B16004_039E",
            "B16004_040E",
            "B16004_044E",
            "B16004_045E",
            "B16004_051E",
            "B16004_052E",
            "B16004_056E",
            "B16004_057E",
            "B16004_061E",
            "B16004_062E",
            "B16004_066E",
            "B16004_067E",
        ],
        "Hisp": ["B03002_001E", "B03002_012E"],
        "Black": ["B03002_001E", "B03002_004E"],
        "Asian": ["B03002_001E", "B03002_006E"],
        "AIAN": ["B03002_001E", "B03002_005E"],
        "NHPI": ["B03002_001E", "B03002_007E"],
        "TwoRace": ["B03002_001E", "B03002_009E"],
        "OtherRace": ["B03002_001E", "B03002_008E"],
        "MUStruct": ["B25024_001E", "B25024_007E", "B25024_008E", "B25024_009E"],
        "MobHome": ["B25024_001E", "B25024_010E"],
        "Crowd": [
            "B25014_001E",
            "B25014_005E",
            "B25014_006E",
            "B25014_007E",
            "B25014_011E",
            "B25014_012E",
            "B25014_013E",
        ],
        "NoVeh": ["B25044_001E", "B25044_003E", "B25044_010E"],
        "GrpQuarter": ["B09019_002E", "B09019_026E"],
    }

    if subset:
        if subset in ['keys', 'indicators']:
            return list(x.keys())
        else:
            return x[subset]
    else:
        # Flatten
        return list(set([val for sublst in list(x.values()) for val in sublst]))


def indicators(subset=None):
    x = {'Base_Data': ['FIPS', 'Area', 'TotPop', 'HousUnits', 'Household'],
         'Socioeconomic_Status': ['Poverty150', 'Unemploy', 'HouseBurd',
                                  'NoHSDiplo', 'NoHlthIns'],
         'Household Characteristics': ['65andover', '17andbelow', 'DisableCiv',
                                       'SPH', 'ELP'],
         'Racial_and_Ethnic_Minority Status': ['Hisp', 'Black', 'Asian',
                                               'AIAN', 'NHPI', 'TwoRace',
                                               'OtherRace',],
         'Housing_Type_and_Transportation': ['MUStruct', 'MobHome', 'Crowd',
                                             'NoVeh', 'GrpQuarter'],
         }
    if subset:
        return x[subset]
    return x


def preprocess(df_in):
    # Deep copy table
    df = df_in.copy()
    # List new column names
    #indicators = SVI_variables('keys')

    # cols maths: just rename, percents where col2/col1,
    # and difs where col2-col1/col1
    renames = ["TotPop", "HousUnits", "Household"]

    # Percent of population ([0] is TotPop)
    pct_pop = [
        "Poverty150",
        "65andover",
        "17andbelow",
        "Hisp",
        "Black",
        "Asian",
        "AIAN",
        "NHPI",
        "TwoRace",
        "OtherRace",
        "ELP",
    ]
    # sum/[0] but not over pop
    pct = [
        "Unemploy",
        "NoHSDiplo",
        "NoHlthIns",
        "DisableCiv",
        "SPH",
        "MUStruct",
        "MobHome",
        "Crowd",
        "NoVeh",
        "GrpQuarter",
    ]
    pct += pct_pop  # Combine for now

    for col in variables("keys"):
        metric_cols = variables(col)

        if col in renames:
            df = df.rename(columns={metric_cols[0]: col})
        elif col in pct:
            if len(metric_cols) > 2:
                # Numerator is sum of list (excluding denominator)
                df[col] = (
                    df[metric_cols[1:]].sum(axis=1).divide(df[metric_cols[0]]) * 100.0
                )
                if col == "NoHSDiplo":
                    df[col] = [100.0 - x for x in df[col]]  # Invert
            else:
                # Numerator is last in list
                num_col = metric_cols[1]  # Numerator column
                dem_col = metric_cols[0]  # Denominator column
                try:
                    df[col] = df[num_col].divide(df[dem_col]) * 100.0
                except TypeError as e:
                    # TODO: move to function if needed for any other cols
                    # Meant to catch when some or all of the 2 values are None
                    numerators = df[num_col].to_list()
                    denominators = df[dem_col].to_list()

                    if None in numerators or denominators:
                        metrics = []  # Build list of metrics to infer
                        if None in numerators:
                            metrics += [num_col]
                        if None in denominators:
                            metrics += [dem_col]
                        for metric in metrics:
                            # geoids where na
                            bad_ids = df[df[metric].isna()]["GEOID"].to_list()
                            for fip in bad_ids:
                                # TODO: currently assumes missing bg not tract
                                assert len(fip)>11, 'Meant for block-group'
                                val = infer_bg_from_tract(fip, metric, year=year)[0]
                                mask = df["GEOID"] == fip
                                df.loc[mask, metric] = val
                            # Warning what metrics were infered at what ids
                            warn(
                                f'"{metric}" infered at {bad_ids} block-groups from tract'
                            )
                        # Re-try
                        df[col] = df[num_col].divide(df[dem_col]) * 100.0
                    else:
                        # Something else went awry
                        raise e
        elif col == "HouseBurd":
            renter = df[metric_cols[1:29]].sum(axis=1).divide(df[metric_cols[0]])
            owner = df[metric_cols[30:]].sum(axis=1).divide(df[metric_cols[29]])
            df[col] = (renter + owner) * 100.0
        else:
            # TODO: throw error
            print(f"{col} has no preprocessing assigned")
    # TODO: drop original cols?

    return df


def get_SVI(geo, level="block group", year=2020):
    """Get geograhpies and a table of SVI indicators for a given geoid

    Parameters
    ----------
    geo : str
        GEOID/FIPs code representing an area. Must be 5 or more digits.
    level : str, optional
        Census level to calculate SVI (default "block group" or "tract")
    year : int, optional
        5-year ACS vintage year, by default 2020

    Returns
    -------
    geopandas.GeoDataFrame
        Table of SVI results and associated polygons
    """
    assert level in ['tract', 'block group'], f'{level} not a recognized level'
    #format params from geo (query census BGs) or id?
    if len(geo)==5:
        state, county = geo[:2], geo[2:5]
        geo_id_str = f'state:{geo[:2]};county:{geo[2:5]}'

    SVI_tract_data = get_census(dataset = "acs/acs5",
                                variables = variables(),
                                year=year,
                                params = {"for": f"{level}:*",
                                          "in": geo_id_str},
                                return_geoid = True,
                                guess_dtypes = True,
                                )
    SVI_tract_results = preprocess(SVI_tract_data)

    if level == 'tract':
        # Get track geos (2020)
        tract_geos = pygris.tracts(state=state, county=county, year=year)
        # Combine with geos
        SVI_results_gdf = tract_geos.merge(SVI_tract_results, on='GEOID')
    elif level == 'block group':
        # Get block group geos (2020)
        bg_geos = pygris.block_groups(state=state, county=county, year=year)
        # Combine with geos
        SVI_results_gdf = bg_geos.merge(SVI_tract_results, on='GEOID')
    return SVI_results_gdf
