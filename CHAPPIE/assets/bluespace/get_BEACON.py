import pandas
import requests


def by_bbox(beachids, year=2023):
    return None

def by_id(beachids, year=2023):
    """ Get table of BEACON beach information for beach id.

    Parameters
    ----------
    beachids : [str] | str
        BEACON Beach ID.
    year : int | str, optional
        Year to get BEACON information for. The default is 2023.

    Returns
    -------
    pandas.DataFrame
        Table with row(s) containing beach information.

    """
    #TODO: replace 2023 with current?
    if isinstance(beachids, (str, int)):
        beachids = [str(beachids)]
    else:
        beachids = [str(b_id) for b_id in beachids]

    # Static variables in query
    base_url = 'https://beacon.epa.gov/ords/beacon2/f?'
    param = 'p=137:37:::::P37_BEACH_ID,P37_EFFECTIVE_YEAR_PARAM'
    dfs = []
    
    for beachid in beachids:
        url = f'{base_url}{param}:{beachid},{year}'
        res = requests.get(url)  # Get html
        res_table = pandas.read_html(res.text)  # Read into table
        # General info
        row = res_table[2][1].to_list()  # Values to row
        cols = res_table[2][0].to_list()  # Column names
        # Location info
        row += res_table[11][1].to_list()  # Values to row
        cols += res_table[11][0].to_list()  # Extract column names
        # Renames (drop colon)
        cols = [col.strip(':') for col in cols]
        # Build df from lists
        df = pandas.DataFrame([row])
        df.columns = cols
        dfs+=[df]  # Add to list of resulting tables
    return pandas.concat(dfs)