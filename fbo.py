#!/usr/bin/env python3
import sys
import datetime
import json
import os
from utils import fbo_nightly_scraper as fbo, get_fbo_attachments
from utils.predict import Predict 
from utils.db import db

def get_nightly_data(notice_types, naics):
    now = datetime.datetime.now() - datetime.timedelta(1)
    current_date = now.strftime("%Y%m%d")
    nfbo = fbo.NightlyFBONotices(date = current_date, notice_types = notice_types, naics = naics)
    file_lines = nfbo.download_from_ftp()
    json_str = nfbo.pseudo_xml_to_json(file_lines)
    filtered_json_str = nfbo.filter_json(json_str)
    nightly_data = json.loads(filtered_json_str)
    return nightly_data, current_date


def main(notice_types= ['MOD','PRESOL','COMBINE'], naics = {'336411','334419'}):
    '''
    Main function that returns JSON representing a nightly file along with the date of that file
    '''
    
    print("-"*80)
    print("Downloading most recent nightly FBO file from FTP...")
    nightly_data, current_date = get_nightly_data(notice_types, naics)
    print("Done downloading most recent nightly FBO file from FTP!")

    print("-"*80)
    print("Getting attachments and their text from each FBO notice...")
    fboa = get_fbo_attachments.FboAttachments(nightly_data)
    updated_nightly_data = fboa.update_nightly_data()
    print("Done getting attachments and their text from each FBO notice!")

    print("-"*80)
    print("Making predictions for each notice attachment...")
    predict = Predict(updated_nightly_data)
    updated_nightly_data = predict.insert_predictions()
    print("Done making predictions for each notice attachment!")
    db.temp_remove_data_in_postgres()
    db.DataAccessLayer().add_json_nightly_file_to_postgres(updated_nightly_data)  
    return updated_nightly_data, current_date

if __name__ == '__main__':
    updated_nightly_data, current_date = main()
    print(current_date)
    print(type(updated_nightly_data))
    #with open('result.json', 'w') as fp:
        #json.dump(updated_nightly_data, fp)
        