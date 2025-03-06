# -*- coding: utf-8 -*-
"""Module to query regrid API.

@author: tlomba01
"""
import os

_regrid_base_url = "https://fs.regrid.com/"

# get key from env
_regrid_api_key = os.environ['REGRID_API_KEY']
_regrid_fs_path = "/rest/services/premium/FeatureServer/0"