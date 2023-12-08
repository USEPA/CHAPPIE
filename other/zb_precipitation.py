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

for fc in fc_in:
    for hour in fc:
        print('run IDW')
        