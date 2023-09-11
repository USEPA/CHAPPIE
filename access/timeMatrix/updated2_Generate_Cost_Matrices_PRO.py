# -*- coding: utf-8 -*-
"""
Created on Thu Nov  8 18:32:55 2018

@author: jbousqui
This tool creates a table of travel time for origins and destination using
ArcGIS Online routing services
Function adapted from http://esriurl.com/uc16napy
Date: 8/23/2016
Version 0.0.13
Notes: Trying to not break it. Added Param for start position.
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


# def exceed_200_warn(num, string, maxPnts):
#     """Exceeds 200 Warning
#     Purpose: provide message and how many runs it will take when an input has more than 200 points"""
#     message("There were {} {}. They must be separated into {} tables.".format(str(num), string, str(math.ceil(int(num)/float(maxPnts)))))
#     print("There were {} {}. They must be separated into {} tables.".format(str(num), string, str(math.ceil(int(num)/float(maxPnts)))))

#     return int(math.ceil(int(num)/float(maxPnts)))


# def import_service(service_name, username="", password="", ags_connection_file="", token="", referer=""):
#     """Import Service
#     Purpose: Imports the service toolbox based on the specified credentials and returns the toolbox object"""

#     #Construct the connection string to import the service toolbox
#     if username and password:
#         tbx = "https://logistics.arcgis.com/arcgis/rest/services;{0};{1};{2}".format(service_name, username, password)
#     elif ags_connection_file:
#         tbx = "{0};{1}".format(ags_connection_file, service_name)
#     elif token and referer:
#         tbx = "https://logistics.arcgis.com/arcgis/rest/services;{0};token={1};{2}".format(service_name, token, referer)
#     else:
#         raise arcpy.ExecuteError("No valid option specified to connect to the {0} service".format(service_name))

#     #Import the service toolbox
#     tbx_alias = "agol"
#     #return arcpy.ImportToolbox(tbx, tbx_alias)
#     arcpy.ImportToolbox(tbx, tbx_alias)

#     return getattr(arcpy, tbx_alias)


# def close_service(service_name, username="", password="", ags_connection_file="", token="", referer=""):
#     #Construct the connection string to import the service toolbox
#     if username and password:
#         tbx = "https://logistics.arcgis.com/arcgis/rest/services;{0};{1};{2}".format(service_name, username, password)
#     elif ags_connection_file:
#         tbx = "{0};{1}".format(ags_connection_file, service_name)
#     elif token and referer:
#         tbx = "https://logistics.arcgis.com/arcgis/rest/services;{0};token={1};{2}".format(service_name, token, referer)
#     else:
#         raise arcpy.ExecuteError("No valid option specified to connect to the {0} service".format(service_name))

#     #Remove the service toolbox
#     arcpy.RemoveToolbox(tbx)

#     return None


#def query_service(service_name, O, D, mode, time_of_day, time_zone, retries = 3):
#    for attempt in range(retries):
#        try:
#            service = import_service(service_name, token=token, referer=referer)
#            return service.GenerateOriginDestinationCostMatrix(O, D, Travel_Mode = mode, Time_of_Day = time_of_day, Time_Zone_for_Time_of_Day = time_zone)
#            #(Origins, Destinations, {Travel_Mode}, {Time_Units}, {Distance_Units}, {Analysis_Region},
#            #{Number_of_Destinations_to_Find}, {Cutoff}, {Time_of_Day}, {Time_Zone_for_Time_of_Day},
#            #{Point_Barriers}, {Line_Barriers}, {Polygon_Barriers}, {UTurn_at_Junctions}, {Use_Hierarchy},
#            #{Restrictions;Restrictions...}, {Attribute_Parameter_Values}, {Impedance}, {Origin_Destination_Line_Shape})
#        except:
#            service = close_service(service_name, token=token, referer=referer)
#            if attempt < retries - 1:
#                message("Attempt: " + str(attempt))
#                continue
#            else:
#                raise


def main(params):
    """Program entry point"""
    start = time.process_time() #start the clock
    #script params:
    #origin_in = 'blockpoints3_cape'
    #destination_in ='Cape_Cod_Merged2'
    #travel_modes = "'Driving Time';'Walking Time"
    #time_of_day = "9/17/2016"
    #time_zone = "Geographically Local"
    #path = r"L:\Public\jbousqui\AED\GIS\Cape\TestResults.gdb"

    # Define inputs
    origin_in = params[0].valueAsText
    destination_in = params[1].valueAsText
    # Optional inputs
    travel_modes = params[2].valueAsText
    #time_of_day = params[3].valueAsText
    #time_zone = params[4].valueAsText
    limit = params[3].valueAsText
    # Output GDB
    path = params[4].valueAsText
    #derived
    #travel_modes = map(lambda a: a.replace("'",""), travel_modes.split(';'))
    travel_modes = [x.replace("'", "") for x in travel_modes.split(';')]
    st = int(params[5].valueAsText) #start at run #
    #other (not yet inputs)
    maxPnts = int(1000)

    # WALKING TIME only available for <27miles (50miles in documentation)
    if travel_modes[0] == 'Walking Time':
        cutoff = '360 Minutes'
    else:
        cutoff = ''
##    #Get the name and version of the product used to run the script
##    install_info = arcpy.GetInstallInfo()
##    product_version = "{0} {1}".format(install_info["ProductName"], install_info["Version"])

    #Get the credentials from the signed in user (check that it works)
    #NOTE: Sign in through catalog- "ready to use services"
    credentials = arcpy.GetSigninToken()
    if not credentials:
        raise message("Please sign into ArcGIS Online", 2)
    token = credentials["token"]
    referer = credentials["referer"]

    # Get service for first time (check that it works)
    #service_name = "World/OriginDestinationCostMatrix"
    #service = import_service(service_name, token=token, referer=referer)

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

    #objectid field name for whereClause
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

        #result = service.GenerateOriginDestinationCostMatrix(**params)
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

        #time_of_day = setParam("Travel Date & Time", "time_of_day", "GPDate", "Opttional", "")
        #time_zone = setParam("Time Zone", "time_zone", "GPString", "Optional", "")
        #cutoff = setParam("Cutoff", "cutoff", "GPTimeUnit", "Optional", "")
        limit = setParam("Limit (min)", "limit", "GPDouble", "Optional", "")
        st = setParam("Start Run", "start_run", "GPString", "Optional", "")
        outTbl = setParam("Results", "outTbl", "DEWorkspace", "", "Output")

        travel_modes =arcpy.Parameter(
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

        #default values to make debugging faster
        #origin_in.value = 'blockpoints3_cape'
        #destination_in.value ='Cape_Cod_Merged2'
        #time_of_day.value = "9/17/2016"
        #outTbl.value = r"L:\Public\jbousqui\AED\GIS\Cape\TestResults.gdb"

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
