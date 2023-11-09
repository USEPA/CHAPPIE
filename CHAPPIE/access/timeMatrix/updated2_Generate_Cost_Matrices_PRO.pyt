# -*- coding: utf-8 -*-
"""
Created on Thu Nov  8 18:32:55 2018

@author: jbousqui
This tool creates a table of travel time for origins and destination using
ArcGIS Online routing services
Function adapted from http://esriurl.com/uc16napy
Date: 8/23/2016
Version 0.1.1
Notes: Major updates 1/12/2023
"""
import arcpy
import os
import time
import numpy


def message(msg, severity=0):
    """standard message printing for .py or .pyt"""
    print(msg)
    if severity == 0: arcpy.AddMessage(msg)
    elif severity == 1: arcpy.AddWarning(msg)
    elif severity == 2: arcpy.AddError(msg)


def exec_time(start, msg):
    """Global Timer
    Funct Notes: used during testing to compare efficiency of each step
    """
    end = time.process_time()
    elapsed = end - start
    elapsed_min = "{} min".format(int(elapsed/60))
    elapsed_sec = "{} sec".format(int(round(elapsed % 60)))
    message("Run time for {}: {}, {}".format(msg, elapsed_min, elapsed_sec))

    return time.process_time()


def field2list(table, field):
    """Return list read from field in table"""
    return [row[0] for row in arcpy.da.SearchCursor(table, [field])]


def setParam(str1, str2, str3, str4, str5):
    """Set Input Parameter
    Purpose: returns arcpy.Parameter for provided string, setting defaults for missing."""
    lst = [str1, str2, str3, str4, str5]
    defLst = ["Input", "name", "GpFeatureLayer", "Required", "Input"]
    i = 0
    for str_ in lst:
        if str_ =="":
            lst[i]=defLst[i]
        i+=1
    return arcpy.Parameter(
        displayName=lst[0],
        name=lst[1],
        datatype=lst[2],
        parameterType=lst[3],
        direction=lst[4])


def main(params):
    """Program entry point"""
    start = time.process_time() #start the clock

    # Define inputs
    origin_in = params[0].valueAsText
    destination_in = params[1].valueAsText
    # Optional inputs
    travel_modes = params[2].valueAsText
    #time_of_day = params[3].valueAsText
    #time_zone = params[4].valueAsText
    limit = params[3].valueAsText
    path = params[4].valueAsText  # Output GDB

    # Derived params
    travel_modes = [x.replace("'", "") for x in travel_modes.split(';')]
    st = int(params[5].valueAsText)  # Start at run #

    # Hard coded params
    maxPnts = int(1000)
    # WALKING TIME only available for <27miles (50miles in documentation)
    if travel_modes[0] == 'Walking Time':
        cutoff = '360 Minutes'
    else:
        cutoff = ''

    # Get the credentials from the signed in user (check that it works)
    # NOTE: Sign in through catalog- "ready to use services"
    credentials = arcpy.GetSigninToken()
    if not credentials:
        raise message("Please sign into ArcGIS Online", 2)
    token = credentials["token"]
    referer = credentials["referer"]

    # Create output gbd if it doesn't exist
    if not os.path.exists(path):
        arcpy.management.CreateFileGDB(os.path.dirname(path), os.path.basename(path))

    # Copy FC inputs into GBD to make sure OBJECTID are sequential
    origin_FC = os.path.join(path, "Origins_A")
    arcpy.CopyFeatures_management(origin_in, origin_FC)
    message("origin_in: {} -> origin_FC: {}".format(origin_in, origin_FC))
    arcpy.MakeFeatureLayer_management(origin_FC, "Origin")

    destination_FC = os.path.join(path, "Destinations_A")
    arcpy.CopyFeatures_management(destination_in, destination_FC)
    message("{0}in: {1} -> {0}FC: {2}".format("destination_", destination_in, destination_FC))
    arcpy.MakeFeatureLayer_management(destination_FC, "Destination")

    # ObjectID field name for whereClause
    o_oid_name = arcpy.Describe(origin_FC).OIDFieldName
    d_oid_name = arcpy.Describe(destination_FC).OIDFieldName

    # Get list of OIDs
    o_oid_list = field2list(origin_FC, o_oid_name)
    message("There are {} Origins".format(len(o_oid_list)))
    d_oid_list = field2list(destination_FC, d_oid_name)
    message("There are {} Destinations".format(len(d_oid_list)))

    # List of all possible combinations
    pairs = len([(o, d) for o in o_oid_list for d in d_oid_list])

    # To simplify we limit each set to maxPnts
    n_origins = numpy.ceil(len(o_oid_list) / maxPnts)
    n_destins = numpy.ceil(len(d_oid_list) / maxPnts)

    runs = int(n_origins) * int(n_destins)

    # OID run chunks
    o_run_list = []
    d_run_list = []
    for o_chunk in numpy.array_split(o_oid_list, n_origins):
        for d_chunk in numpy.array_split(d_oid_list, n_destins):
            o_run_list += [[min(o_chunk), max(o_chunk)]]
            d_run_list += [[min(d_chunk), max(d_chunk)]]

    # Limit converted to distance to do selection of destinations
    rate = 5.0  # Default walk speed is 5 km/hr)
    max_dist = str(((rate*1000)/60)*float(limit)) + ' meters'  # meters
    message("Max {} O-D pairs will be calculated over {} requests. Max {} credits.".format(pairs, runs, pairs*0.0005))

    start = exec_time(start, "Parameters Initialized")
    crd = 0

    for run in range(st+1, runs+1):
        message('Run {} of {}'.format(run, runs))
        # Select subset of points from each layer for this run
        o_min, o_max = min(o_run_list[run-1]), max(o_run_list[run-1])
        #d_min, d_max = min(d_run_list[run-1]), max(d_run_list[run-1])
        o_whereClause = '{0} >= {1} AND {0} <= {2}'.format('"' + o_oid_name + '"', o_min, o_max)
        #d_whereClause = '{0} >= {1} AND {0} <= {2}'.format('"'+ d_oid_name + '"', d_min, d_max)
        message("Origins: {} {} to {}".format(o_oid_name, o_min, o_max))

        #select origin
        arcpy.SelectLayerByAttribute_management("Origin", "NEW_SELECTION", o_whereClause)
        #arcpy.SelectLayerByAttribute_management("Destination", "NEW_SELECTION", d_whereClause)

        # Select destination based on range (max_dist in meters)
        arcpy.SelectLayerByLocation_management("Destination",
                                               'WITHIN_A_DISTANCE',
                                               "Origin",
                                               max_dist,
                                               "NEW_SELECTION")

        message("Destinations: " + arcpy.GetCount_management("Destination")[0])

        params = {'Origins': "Origin",
                  'Destinations': "Destination",
                  'Travel_Mode': travel_modes[0],
                  'Cutoff': cutoff}
        # Call the service for each travel mode, with the selection
        #for mode in travel_modes:
            #params['Travel_Mode'] = mode

        result = arcpy.agolservices.GenerateOriginDestinationCostMatrix(**params)

        #Check the status of the result object every second until it has a value of 4(succeeded) or greater
        while result.status < 4:
            time.sleep(1) # Wait one second

        #print any warning or error messages returned from the tool
        result_severity = result.maxSeverity
        if result_severity in [1, 2]:
            message(result.getMessages(result_severity), result_severity)

        # Get the output matrix table name
        output_FC_name = u"Online_{}_{}".format(arcpy.ValidateTableName(travel_modes[0], path), str(run))
        output_service_table = os.path.join(path, output_FC_name)

        if result_severity not in [2]:
            # If no error get the result and save to geodatabase feature class
            if arcpy.Exists(output_service_table):
                arcpy.management.Delete(output_service_table)
            result.getOutput(1).save(output_service_table)
            crd += int(arcpy.GetCount_management(output_service_table)[0])
        else:
            message('No result from for this run')
        start = exec_time(start, "run #" + str(run))

    message('Ran to compleation')
    message('Estimated credits used:{}'.format(crd*0.0005))


###########TOOLBOX############
class Toolbox(object):
    def __init__(self):
        self.label = "Generate Cost Matrices"
        self.alias = "Generate Cost Matrix"
        # List of tool classes associated with this toolbox
        self.tools= [Cost_Matrix]
class Cost_Matrix (object):
    def __init__(self):
        self.label = "Cost Matrix"
        self.description = "This tool generates a travel network cost matrix given two sets of points"

    def getParameterInfo(self):
        origin_in = setParam("Origin", "origin_FC", "", "", "")
        destination_in = setParam("Destination", "dest_in", "", "", "")

        #time_of_day = setParam("Travel Date & Time", "time_of_day", "GPDate", "Optional", "")
        #time_zone = setParam("Time Zone", "time_zone", "GPString", "Optional", "")
        #cutoff = setParam("Cutoff", "cutoff", "GPTimeUnit", "Optional", "")
        limit = setParam("Limit (min)", "limit", "GPDouble", "Optional", "")
        st = setParam("Start Run", "start_run", "GPString", "Optional", "")
        outTbl = setParam("Results", "outTbl", "DEWorkspace", "", "Output")

        travel_modes = arcpy.Parameter(
            displayName = "Travel Modes",
            name = "travel_mode_lst",
            datatype = "GPString",
            parameterType = "Required",
            direction = "Input",
            multiValue = True)

        #value list
        travel_modes.filter.type = "ValueList"
        travel_modes.filter.list = ["Driving Time", "Walking Time", "Trucking Time", "Rural Driving Time"]
        #defaults
        travel_modes.value = "Walking Time"
        #time_zone.value = "Geographically Local"
        st.value = "0"

        params = [origin_in, destination_in, travel_modes, limit, outTbl, st]
        return params
    def isLicensed(self):
        return True
    def updateParameters(self, params):
        return
    def updateMessages(self, params):
        return
    def execute(self, params, messages):
        #main(params)
        try:
            main(params)
        except Exception as ex:
            arcpy.AddMessage(ex.message)
            print(ex.message)
