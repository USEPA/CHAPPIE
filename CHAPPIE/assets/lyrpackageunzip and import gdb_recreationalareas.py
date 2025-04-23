import os
import py7zr
import re
import geopandas
lyrPackage = r"C:\Users\EDamico\Work\Chappie\originals\USA_Recreational_Areas.lpk"
zip7file = lyrPackage.replace(".lpk", ".7z")
if lyrPackage.endswith(".lpk"):
    os.rename(lyrPackage, zip7file)


archive = py7zr.SevenZipFile(zip7file, mode='r')


filter_pattern = re.compile(r'v107/recareas.gdb')
with py7zr.SevenZipFile(zip7file, 'r') as archive:
    allfiles = archive.getnames()
    selective_files = [f for f in allfiles if filter_pattern.match(f)]
    archive.extract(targets=selective_files)



gdf = geopandas.read_file(r'v107/recareas.gdb', layer="recareas", driver='OpenFileGDB')