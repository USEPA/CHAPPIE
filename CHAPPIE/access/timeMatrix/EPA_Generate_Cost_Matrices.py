import arcpy
import os
import time
import pandas
from json import loads


def field2list(table, field):
    """Return list read from field in table"""
    return [row[0] for row in arcpy.da.SearchCursor(table, [field])]


def extendFileName(fName, extend):
    """Insert text at end of filename without changing extension"""
    name, ext = os.path.splitext(fName)
    return name + extend + ext


def message(msg, severity = 0):
    """Standard message printing for .py or .pyt"""
    print(msg)
    if severity == 0: arcpy.AddMessage(msg)
    elif severity == 1: arcpy.AddWarning(msg)
    elif severity == 2: arcpy.AddError(msg)


def exec_time(start, msg):
    """Global Timer
    Funct Notes: used during testing to compare efficiency of each step
    """
    end = time.clock()
    elapsed = end - start
    elapsed_min = "{} min".format(int(elapsed/60))
    elapsed_sec = "{} sec".format(int(round(elapsed % 60)))
    message("Run time for {}: {}, {}".format(msg, elapsed_min, elapsed_sec))

    return time.clock()


def split_by(lst, length):
    """ Generator that returns chunks, of 'length' size, from lst
    """
    iterable = iter(lst)
    def yield_length():
        for i in range(length):
            yield iterable.next()
    while True:
        res = list(yield_length())
        if not res:
            return
        yield res


def runLayerSelection(layer, oid_name, run_id_list):
    """Make selection of layer for run"""
    r_min, r_max = min(run_id_list), max(run_id_list)
    whereClause = '{0} >= {1} AND {0} <= {2}'.format('"'+ oid_name + '"', r_min, r_max)
    return arcpy.SelectLayerByAttribute_management(layer, "NEW_SELECTION", whereClause)


def import_GP_service(server="", service_name=""):
    """Imports the Geoprocessing service as a toolbox and returns the
    the toolbox object"""
    if server == "":
        server = "https://igeo.epa.gov/arcgis/services"
    if service_name == "":
        service_name = "OEI_IGD/GenerateOriginDestinationCostMatrix"
    tbx = "{};{}".format(server, service_name)
    return arcpy.ImportToolbox(tbx)


def main(params):
    # Start timer
    start = time.clock()

    # Assign size limit
    maxPnts = 200

    # Assign start run
    if params[2].valueAsText is None:
        startRun = 0
    else:
        startRun = int(params[2].valueAsText) - 1
        
    # Create run_dict with default params
    run_dict = {'Origin_Destination_Line_Shape': "NO_LINES"}
##    run_dict = {'Analysis_Region': "NorthAmerica"}
##    run_dict['Time_Zone_for_Time_of_Day'] = "Geographically Local"
    
    # Define inputs from params
    origin_in = params[0].valueAsText
    destination_in = params[1].valueAsText

    # Define outputs from params
    out_csv = params[3].valueAsText

##    # Travel modes may need to be formatted
##    travel_modes = params[2].valueAsText
##    #travel_modes = "'Driving Time';'Walking Time"
##    travel_modes = map(lambda a: a.replace("'",""), travel_modes.split(';'))
##
##    run_dict['Travel_Mode'] = travel_modes[0]

    # Create layers from origin/destinaiton
    origin_lyr, destination_lyr = "origins1", "destinations1"
    arcpy.MakeFeatureLayer_management(origin_in, origin_lyr)
    arcpy.MakeFeatureLayer_management(destination_in, destination_lyr)
    run_dict['Origins'] = origin_lyr
    run_dict['Destinations'] = destination_lyr

    # Objectid field name for whereClause
    o_oid_name = arcpy.Describe(origin_lyr).OIDFieldName
    d_oid_name = arcpy.Describe(destination_lyr).OIDFieldName

    # Get list of OIDs
    o_oid_list = field2list(origin_lyr, o_oid_name)
    message("There are {} Origins".format(len(o_oid_list)))
    d_oid_list = field2list(destination_lyr, d_oid_name)
    message("There are {} Destinations".format(len(d_oid_list)))
    
    # Split O/D lists into maxPnts segments
    o_run_list = list(split_by(o_oid_list, maxPnts))
    d_run_list = list(split_by(d_oid_list, maxPnts))
    runs = len(d_run_list) * len(o_run_list)

    # Repeat the outside list, e.g. [[a,b],[c,d],[a,b],[c,d]]
    o_runs = o_run_list*len(d_run_list)
    # Repeat the inside list, e.g. [[a,b],[a,b],[c,d],[c,d]]
    d_runs = [d_run for d_run in d_run_list for i in range(len(o_run_list))]
    
    # Number of possible combinations
    #pairs = len([(o,d) for o in o_oid_list for d in d_oid_list])
    pairs = len(o_oid_list) * len(d_oid_list)
    message("{} O-D pairs will be calculated over {} requests.".format(pairs, runs))
    #message("Estimated credits: {}".format(math.ceil(pairs * 0.0005)))

    #Import service as toolbox
    #arcpy.GenerateOriginDestinationCostMatrix_GenerateOriginDestinationCostMatrix()
    service = import_GP_service()

    # Message with run time for setup
    start = exec_time(start, 'setup')
    
    for run in range(startRun, runs):
        message("\nGenerating Matrix Table for Run {} of {}".format(run +1, runs))
        # The subset of points from each layer for this run
        o_run, d_run = o_runs[run], d_runs[run]

        # Select origin/destination
        runLayerSelection(run_dict['Origins'], o_oid_name, o_run)
        runLayerSelection(run_dict['Destinations'], d_oid_name, d_run)

        # Run with set params
        result = service.GenerateOriginDestinationCostMatrix(**run_dict)

        # Wait until results status is complete
        while result.status < 4:
            time.sleep(0.2)

	try:
            # Save results as shapefile/feature class
            #result[1].save(outFC)

            # Save results as csv
            results_features_json = loads(result[1].JSON)['features']
            # Flatten feature attribute list
            results_list = [x['attributes'] for x in results_features_json]
            # Convert to pandas dataframe
            df = pandas.DataFrame(results_list)

            # Reduce to desired fields
            fields = ['Total_Time', 'Total_Distance',
                      'OriginOID', 'DestinationOID']
            df = df.loc[:, fields]

            # Save as csv
            out_csv_run = extendFileName(out_csv, '_run{}'.format(run +1))
            df.to_csv(out_csv_run)
        except:
            message("Problem encountered")
            message(result.getMessages())
        # Message with run time for that run
        start = exec_time(start, 'run {}'.format(run + 1))
