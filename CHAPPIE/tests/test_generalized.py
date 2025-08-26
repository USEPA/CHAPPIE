import os
from tempfile import TemporaryDirectory

import pygris
import pytest
from geopandas import read_parquet

from CHAPPIE import utils

# CI inputs/expected
DIRPATH = os.path.dirname(os.path.realpath(__file__))
#DIRPATH = r"L:\lab\GitHub\CHAPPIE\CHAPPIE\tests"

EXPECTED_DIR = os.path.join(DIRPATH, 'expected')  # Expected

# Make sure pygris imports/functions as expected
def test_bg():
  g_geos = pygris.block_groups(state='12', county='033', year='2021')
  assert 'GEOID' in g_geos.columns, 'Missing expected column'

# results_dict fixture from assets in expected to use in tests
@pytest.fixture(scope='session')
def assets_results_dict():
    results_dict = {}
    expected_file = os.path.join(EXPECTED_DIR, 'cultural_historic.parquet')
    results_dict["historic_sites"] = read_parquet(expected_file)
    expected_file = os.path.join(EXPECTED_DIR, 'cultural_lib.parquet')
    results_dict["libraries"] = read_parquet(expected_file)
    expected_file = os.path.join(EXPECTED_DIR, 'cultural_museum.parquet')
    results_dict["museums"] = read_parquet(expected_file)
    return results_dict

def test_write_QA(assets_results_dict: dict):
  with TemporaryDirectory() as temp_dir:
    qa_csv = os.path.join(temp_dir, "assets_qa.csv")
    utils.write_QA(assets_results_dict, qa_csv)
    # Check for file
    assert os.path.isfile(qa_csv), f"'{qa_csv}' file not found"
    assert len(os.listdir(temp_dir))==1, "Wrong number of files"
    # Check for file contents
    with open(qa_csv, 'r') as csv:
      contents = csv.read()
    assert len(contents)==7723, f'File content length mismatch: {len(contents)}'

def test_write_results_dict(assets_results_dict: dict):
  with TemporaryDirectory() as temp_dir:
    utils.write_results_dict(assets_results_dict, temp_dir)
    # Check for files
    sub_dirs = os.listdir(temp_dir)
    assert len(sub_dirs)==3, "Wrong number of sub-directories"
    for i, fld in enumerate(sub_dirs):
      f = os.path.join(temp_dir,fld, f"{fld}.parquet")
      assert os.path.isfile(f), f"'{f}' file not found"
      # Check file sizes
      expected = [34601, 98953, 32359]
      actual = os.path.getsize(f)
      assert actual==expected[i], f"Parquet size mismatch: {actual}"
