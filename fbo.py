
import sys
import datetime
import json
import os
import logging
from utils import fbo_nightly_scraper as fbo, get_fbo_attachments
from utils.predict import Predict 
from utils.db.db_utils import get_db_url, session_scope, DataAccessLayer, insert_updated_nightly_file

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

conn_string = get_db_url()
dal = DataAccessLayer(conn_string)
dal.connect()

def get_nightly_data(notice_types, naics):
    now = datetime.datetime.now() - datetime.timedelta(1)
    current_date = now.strftime("%Y%m%d")
    nfbo = fbo.NightlyFBONotices(date = current_date, notice_types = notice_types, naics = naics)
    file_lines = nfbo.download_from_ftp()
    if not file_lines:
        #exit program if download_from_ftp() failed
        sys.exit(1)
    json_str = nfbo.pseudo_xml_to_json(file_lines)
    filtered_json_str = nfbo.filter_json(json_str)
    nightly_data = json.loads(filtered_json_str)
    return nightly_data


def main():
    '''
    Main function that returns JSON representing a nightly file along with the date of that file
    '''
    
    notice_types= ['MOD','PRESOL','COMBINE', 'AMDCSS']
    naics = ['334111', '334118', '3343', '33451', '334516', '334614', '5112', '518', 
             '54169', '54121', '5415', '54169', '61142']
    logging.info("Downloading most recent nightly FBO file from FTP...")
    nightly_data = get_nightly_data(notice_types, naics)
    logging.info("Done downloading most recent nightly FBO file from FTP!")

    logging.info("Getting attachments and their text from each FBO notice...")
    fboa = get_fbo_attachments.FboAttachments(nightly_data)
    updated_nightly_data = fboa.update_nightly_data()
    logging.info("Done getting attachments and their text from each FBO notice!")

    logging.info("Making predictions for each notice attachment...")
    predict = Predict(updated_nightly_data)
    updated_nightly_data = predict.insert_predictions()
    logging.info("Done making predictions for each notice attachment!")
    
    logging.info("Inserting into database...")
    insert_updated_nightly_file(dal, updated_nightly_data)
    logging.info("Done inserting into database!")
    

if __name__ == '__main__':
    main()

