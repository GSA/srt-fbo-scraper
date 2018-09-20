# -*- coding: utf-8 -*-

import os, json
from fbo_weekly_scraper import FBONotices


elem_json = FBONotices().xml_to_json(os.getcwd()+"/tests/test_data.xml")

a = json.loads(elem_json)



