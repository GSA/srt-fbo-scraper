# -*- coding: utf-8 -*-
"""
Created on Thu Oct 11 13:16:44 2018

@author: AustinPeel
"""
import sys, os
if os.name == 'nt':
    sys.path.append("H:/fbo-scraper")
    
import datetime, json
from utils import fbo_nightly_scraper as fbo , get_fbo_attachments



def get_nightly_data_and_append_attachements(save=True):
    nightly_data = json.loads(_run_nightly_scraper())
    get_fbo_attachments.append_attachments(nightly_data)
    if save:
        _save_json(nightly_data)
    return nightly_data

def _get_server_date():
    now = datetime.datetime.now() - datetime.timedelta(1)
    currentDate = now.strftime("%Y%m%d")
    return currentDate

def _run_nightly_scraper():
    currentDate = _get_server_date()
    nfbo = fbo.NightlyFBONotices(date=currentDate)
    file_name = nfbo.get_and_write_file()
    json_str = nfbo.pseudo_xml_to_json(file_name)
    return json_str

def _save_json(json_file):
    out_path = os.path.join(os.getcwd(),"temp/nightly_files")
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    json_file_path = os.path.join(out_path, "temp.json")
    with open(json_file_path, 'w') as f:
        json.dump(json_file, f)


if __name__ == '__main__':
    a = get_nightly_data_and_append_attachements(save=True)
    