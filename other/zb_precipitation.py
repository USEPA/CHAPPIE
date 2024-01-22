# -*- coding: utf-8 -*-
"""
Created on Fri Dec  8 14:37:05 2023

@author: jbousqui
"""
import arcpy
from pathlib import Path

wksp = r'L:\Priv\SHC_1012\Pensacola Model\Water Pollution Work\Coliphage Study'
path = Path(wksp).joinpath('Data\D2')
gdb_in = path.joinpath('HourlyPrecipTableJoins.gdb')
gdb_out = path.joinpath('HourlyPrecipRasters.gdb')

arcpy.env.workspace = str(gdb_in)
fc_in = arcpy.ListFeatureClasses()
arcpy.env.workspace = str(gdb_out)

# env settings
crs = 'GEOGCS["GCS_North_American_1983",DATUM["D_North_American_1983",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]]'
extent = "-87.6346429484369 30.2799079916928 -86.9192989554438 30.9990560422155"

for fc in fc_in:
    fc_file = f'{gdb_in}\{fc}'
    fields = [x.name for x in arcpy.ListFields(fc_file)]
    hours = [field for field in fields if field.startswith('F')]
    for hour in hours:
        with arcpy.EnvManager(outputCoordinateSystem=crs, extent=extent):
            out_raster = arcpy.sa.Idw(fc_file,
                                      hour,
                                      0.00286137510990375,
                                      2,
                                      "VARIABLE 12",
                                      None)
            out_raster.save(f'auto_IDW_Hour_{hour[1:]}'))
