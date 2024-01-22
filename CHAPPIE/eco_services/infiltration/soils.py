# functions from H2O_databaser

def soil_rounding(val):
    """
    Rounds a soil N value to nearest integer

    Parameters
    ----------
    val : float

    Returns
    -------
    integer
    """
    if val <1:
        return int(numpy.ceil(val))
    return int(val+0.5)

def get_county_surveys(SSA):
    """
    Create SQL query for survey areasymbol (SSA) based on formated FIP

    Parameters
    ----------
    SSA : string
        Soil Survey Areasymbol (SSA).

    Returns
    -------
    list
        List of soil surveys.

    """
    tblA = "legend"  # Legend table
    tblB = "laoverlap"  # Legend Area Overlap Table
    a_symbol = "areasymbol"  # Area symbol field name used in both tables
    cond1 = "{}.lkey = {}.lkey".format(tblA, tblB)  # lkey = lkey
    cond2 = "{}.{} = '{}'".format(tblB, a_symbol, SSA)  # areasymbol = SSA
    s_join = "INNER JOIN {} ON {} AND {}".format(tblB, cond1, cond2)
    query = "SELECT {0}.{1} FROM {0} {2}".format(tblA, a_symbol, s_join)
    response = query_SSA(query)  # Query server
    # Get list of SSA from response
    if len(response) > 0:
        # Will sometimes return duplicates
        return list(set([survey[0] for survey in response['Table']]))
    #else:
    #TODO: warn louder?
    print("WARNING: No Soil Survey Area for {}".format(SSA))
    return None


def get_survey_date(SSA):
    """
    Create SQL query for survey save date (saverest) using areasymbol (SSA)

    Parameters
    ----------
    SSA : string
        Soil Survey Areasymbol (SSA).

    Returns
    -------
    tuple
        Date in year month day (yyyy, mm, dd) format for latest survey.

    """
    where = "WHERE sacatalog.areasymbol = '{}'".format(SSA)
    query = "SELECT saverest FROM sacatalog {}".format(where)
    res = query_SSA(query)
    # Get date
    if len(res) > 0:
        #print(res['Table'])
        # Return date tuple in desired format (year, mo, da)
        date = res['Table'][0][0].split(" ")[0].split("/")
        return date[2], date[0].zfill(2), date[1].zfill(2)
    #else:
    #TODO: warn louder?
    print("WARNING: No {} for {}".format("survey", SSA))
    return None


def getMUKEY_val(mukey, col, table="Component"):
    """
    SQl query to get a value from a column in a table based on a mukey

    Parameters
    ----------
    mukey : string
        Map Unit Key for identifying soils information.
    col : string
        Column of table to look within.
    table : string, optional
        Table being queried. The default is "Component".

    Returns
    -------
    list
        List of values for the mukey.

    """

    where = "WHERE {}.mukey = '{}'".format(table, mukey)
    query = "SELECT {} FROM {} {}".format(col, table, where)
    res = query_SSA(query)

    # Get value
    if len(res) > 0:
        # Return list of values
        return [value[0] for value in res['Table']]
        #return list(set([value[0] for value in res['Table']])) #unique
    #else:
    print("WARNING: No {} for {}".format(col, mukey))
    # Must return list to subscript (can't be None[0])
    return [None]


def query_SSA(query_str):
    """
    Get results from Soil Data Access Query Services

    Parameters
    ----------
    query_str : string
        SQL query
    Returns
    -------
    json string
        Result of query.

    """
    data = {'query': query_str,
            'format': 'JSON'}
    url = "https://sdmdataaccess.nrcs.usda.gov/Tabular/SDMTabularService/post.rest"
    res = requests.post(url, data, timeout=TIMEOUT)
    assert res.ok, 'Problem with {}, {}'.format(url, data)
    return loads(res.content)

    def get_Soils(self):
        """
        Get soils data from web soil survey by latest soil survey year

        Returns
        -------
        gdf : geopandas.GeoDataFrame
            GeoDataFrame of soils results

        """
        if self.FIPs is None:
            self.set_FIPs()

        # Source url (WSS)
        url = "https://websoilsurvey.sc.egov.usda.gov/DSD/Download/Cache/SSA/"

        # Build WSS query, download, and unpack to out_shapefile
        FIP_df = self.FIPs
        FIP_df['SSA'] = FIP_df['ST_ABBR'] + [x[2:5] for x in FIP_df['GEOID']]

        # TODO: presumably done because FIP_SSA != SSA, but seems to be same?
        SSA_list = []
        unique_SSA_list = list(set(FIP_df['SSA']))
        unique_SSA_list.sort()
        for SSA in unique_SSA_list:
            SSA_list += get_county_surveys(SSA)

        soils_list = []  # To keep track of GDFs
        for SSA in SSA_list:
            # Get latest saverest
            year, mo, da = get_survey_date(SSA)

            # Download SSURGO by SSA, e.g. url + wss_SSA_FL113_[2017-10-06].zip
            download = "wss_SSA_{}_[{}-{}-{}].zip".format(SSA, year, mo, da)
            # temp to check dates
            print(download)
            res = get_url(url + download)
            soils_zip = os.path.join(self.D1, download)
            with open(soils_zip, "wb") as f:
                f.write(res.content)
            # Check archive is valid and extract downloaded files to D2 folder
            if check_archive(soils_zip):
                z = soils_zip  # shorthand for zip filename
                # soilmu_a shapefiles has multiple component files (e.g. .prj)
                shp_root = "{}/spatial/soilmu_a_".format(SSA)
                # List shp component files in archive
                shp_list = [f for f in archive_list(z) if shp_root in f]
                for f in shp_list:
                    archive_extract(z, f, self.D2)  # Extract each component
                    if f.endswith('.shp'):
                        # List shapefiles
                        shp = os.path.join(self.D2, f.replace('/', os.sep))
                gdf_temp = as_gdf(shp)
                # Append geodataframe to list
                soils_list+=[gdf_temp]
        # append soils gdfs together
        gdf = pandas.concat(soils_list)
        # Save gdf here before any pre-processing?

        # Start processing GDF
        # Get "hydgrp" by mukey to populate "Max_Type_N" field
        mukey_list = list(set(gdf["MUKEY"]))  # Unique mukey list

        # Create dictionary where mukey:first hydrgrps
        soil_dict = {key: getMUKEY_val(key, "hydgrp")[0] for key in mukey_list}
        # Reduce dual soil hydrgrps to first, leaving None as None
        soil_dict = {k:None if v is None else v[0] for (k,v) in  soil_dict.items()}

        # Dictionary lookup for soil class -> Max_Type_N
        max_n_lookup = {"A": 1, "B": 2, "C": 3, "D": 4, None: 0}

        # Update Max_Type_N field using soil dictionary
        gdf["Max_Type_N"] = [max_n_lookup[soil_dict[k]] for k in gdf["MUKEY"]]

        # Drop extra cols
        gdf = gdf.drop(columns=["AREASYMBOL", "SPATIALVER", "MUSYM"])
        gdf = gdf.to_crs(3857)  # re-project
        self.set_Soils(gdf)  # Set on database

        gdf.to_file(os.path.join(self.D2, "AOI_Soils.shp"))

        return gdf