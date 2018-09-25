# -*- coding: utf-8 -*-
import os
import json
import sys
import random

cwd = os.getcwd()
base = os.path.split(cwd)[0]
utils_path = os.path.join(base,'utils')
sys.path.insert(0, utils_path)
from fbo_weekly_scraper import FBONotices

def create_test_json():
    xml_path = os.path.join(base,'weekly_files','fbo_weekly_09-19-18.xml')
    try:
        json_str = FBONotices().xml_to_json(xml_path)
    except FileNotFoundError:
        print("You haven't downloaded the xml data yet. Exiting test...")
        sys.exit(0)

    fbo_json = json.loads(json_str)
    notices_json = fbo_json['NOTICES']
    test_data_dict = {k:[] for k in notices_json}
    for k in notices_json:
        records = notices_json[k]

        max_n = len(records)
        if max_n < 10:
            # Get a list of max_n/2 random indices from the records (no duplicates)
            random_indices = random.sample(range(len(records)), int(max_n/2))
        else:
            # Get a list of 10 random indices from the records (no duplicates)
            random_indices = random.sample(range(len(records)), 10)
        for i in random_indices:
            test_data_dict[k].append(records[i])
    test_json_str = json.dumps(test_data_dict)
    test_json = json.loads(test_json_str)

    with open ('test.json','w') as f:
        json.dump(test_json,f)

if __name__=='__main__':
    create_test_json()
