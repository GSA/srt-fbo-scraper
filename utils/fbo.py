# -*- coding: utf-8 -*-
"""
Created on Thu Oct 11 13:16:44 2018

@author: AustinPeel
"""
import datetime
from utils import fbo_nightly_scraper as fbo , get_fbo_attachments
import json


def get_nightly_data_and_append_attachements():
    nightly_data = json.loads(_run_nightly_scraper())
    get_fbo_attachments.append_attachments(nightly_data)
    return nightly_data

def _get_server_date():
    now = datetime.datetime.now() - datetime.timedelta(3)
    currentDate = now.strftime("%Y%m%d")
    return currentDate

def _run_nightly_scraper():
    currentDate = _get_server_date()
    nfbo = fbo.NightlyFBONotices(date=currentDate)
    file_name = nfbo.get_and_write_file()
    json_str = nfbo.pseudo_xml_to_json(file_name)
    return json_str



if __name__ == '__main__':
    #doesnt save yet, because we need to push postgres anyhow 
    get_nightly_data_and_append_attachements()