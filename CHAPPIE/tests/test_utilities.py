import os
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock, patch

import pygris
import pytest
from geopandas import read_parquet
from pyarrow.parquet import ParquetFile
from requests.exceptions import ConnectionError, HTTPError

from CHAPPIE import utils

# CI inputs/expected
DIRPATH = os.path.dirname(os.path.realpath(__file__))
#DIRPATH = r"L:\lab\GitHub\CHAPPIE\CHAPPIE\tests"

EXPECTED_DIR = os.path.join(DIRPATH, 'expected')  # Expected


# Make sure pygris imports/functions as expected
@pytest.mark.unit
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


@pytest.mark.unit
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


@pytest.mark.unit
def test_write_results_dict(assets_results_dict: dict):
  with TemporaryDirectory() as temp_dir:
    utils.write_results_dict(assets_results_dict, temp_dir)
    # Check for files
    sub_dirs = os.listdir(temp_dir)
    assert len(sub_dirs)==3, "Wrong number of sub-directories"
    for i, fld in enumerate(sub_dirs):
      f = os.path.join(temp_dir,fld, f"{fld}.parquet")
      assert os.path.isfile(f), f"'{f}' file not found"
      # Check file columns
      expected_cols = [36, 205, 60]
      actual = ParquetFile(f).metadata.num_columns
      assert actual==expected_cols[i], f"Parquet cols mismatch: {actual}"
      # Check file rows
      expected_rows = [9, 0, 0]
      actual = ParquetFile(f).metadata.num_rows
      assert actual==expected_rows[i], f"Parquet cols mismatch: {actual}"


@pytest.mark.unit
#Test how Connection error is handled, but patch the post_request call
@patch('CHAPPIE.utils.requests.post')
@pytest.mark.unit
def test_post_request_connection_error(mock_post):
    mock_resp = MagicMock()
    mock_resp.raise_for_status.side_effect = ConnectionError
    mock_post.return_value = mock_resp
    url = "https://fake.epa.gov/GeocodeServer"
    data = {}

    result = utils.post_request(url=url, data=data)
    #assert mock_resp.raise_for_status.called
    assert mock_resp.raise_for_status.called == True
    # Ensures the mocked method was called twice (one plus a retry)
    assert mock_post.call_count == 2
    assert result == {"url": url,
                      "status": "error",
                      "reason": "Connection error, 2 attempts",
                      "text": ""
                      }


@pytest.mark.unit
# Test other exception branch of post_request function, which has no retry
@patch('CHAPPIE.utils.requests.post')
@pytest.mark.unit
def test_post_request_502_error(mock_post):
    mock_resp = MagicMock()
    mock_resp.status_code = 502
    mock_resp.raise_for_status.side_effect = HTTPError
    mock_post.return_value = mock_resp
    url = "https://fake.epa.gov/GeocodeServer"
    data = {}

    result = utils.post_request(url=url, data=data)
    #assert mock_resp.raise_for_status.called
    assert mock_resp.raise_for_status.called == True
    # Ensures the mocked method was called once, no retries
    assert mock_post.call_count == 1
    assert result == {"url": url, "data": data, "status": 502}
