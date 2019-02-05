
import sys
import datetime
import json
import os
import logging
from utils import fbo_nightly_scraper, get_fbo_attachments, train
from utils.predict import Predict 
from utils.db.db_utils import get_db_url, session_scope, DataAccessLayer, \
                              insert_updated_nightly_file, retrain_check, \
                              fetch_validated_attachments, insert_model, \
                              fetch_last_score

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

conn_string = get_db_url()
dal = DataAccessLayer(conn_string)
dal.connect()

def get_nightly_data(notice_types = ['MOD','PRESOL','COMBINE', 'AMDCSS'],
                     naics = ['334111', '334118', '3343', '33451', '334516', '334614', 
                              '5112', '518', '54169', '54121', '5415', '54169', '61142']):
    '''
    Exectures methods in fbo_nightly_scraper module.

    Parameters:
        notice_types (list): notice types to scrape from fbo.
        naics (list): NAICS numbers to include. Default value is IT-related NAICS.

    Returns:
        nightly_data (list): list of dicts in JSON format.
    '''
    #get day before yesterday to give FBO time to update their FTP
    now_minus_two = datetime.datetime.now() - datetime.timedelta(2)
    date = now_minus_two.strftime("%Y%m%d")
    nfbo = fbo_nightly_scraper.NightlyFBONotices(date = date, 
                                                 notice_types = notice_types, 
                                                 naics = naics)
    file_lines = nfbo.download_from_ftp()
    if not file_lines:
        #exit program if download_from_ftp() failed (this is logged by the module)
        sys.exit(1)
    json_str = nfbo.pseudo_xml_to_json(file_lines)
    filtered_json_str = nfbo.filter_json(json_str)
    nightly_data = json.loads(filtered_json_str)
    
    return nightly_data

def retrain(session):
    '''
    Retrains a model using validated samples and original training data if retrain_check() evaluates
    to True.
    '''
    retrain = retrain_check(session)
    if retrain:
        logger.info("Smartie is retraining a model!")
        attachments = fetch_validated_attachments(session)
        X, y = train.prepare_samples(attachments)
        results, score, best_estimator, params = train.train(X,
                                                             y, 
                                                             weight_classes = True,
                                                             n_iter_search = 150,
                                                             score='roc_auc',
                                                             random_state = 123)
        logger.info("Smartie is done retraining a model!")
        last_score = fetch_last_score(session)
        better_model = True if last_score < score else False
        if better_model:
            train.pickle_model(best_estimator)
            logger.info("Smartie has pickled the new model!")
        else:
            pass
        insert_model(session, results, params, score)
    else:
        logger.info("Smartie decided not to retrain a new model!")


def main():   
    '''
    Run all of the scripts together.
    '''    
    logger.info("Smartie is downloading the most recent nightly FBO file...")
    nightly_data = get_nightly_data()
    logger.info("Smartie is done downloading the most recent nightly FBO file!")

    logger.info("Smartie is getting the attachments and their text from each FBO notice...")
    fboa = get_fbo_attachments.FboAttachments(nightly_data)
    updated_nightly_data = fboa.update_nightly_data()
    logger.info("Smartie is done getting the attachments and their text from each FBO notice!")

    logger.info("Smartie is making predictions for each notice attachment...")
    predict = Predict(updated_nightly_data)
    updated_nightly_data_with_predictions = predict.insert_predictions()
    logger.info("Smartie is done making predictions for each notice attachment!")
    
    logger.info("Smartie is inserting data into the database...")
    with session_scope(dal) as session:
        insert_updated_nightly_file(session, updated_nightly_data_with_predictions)
    logger.info("Smartie is done inserting data into database!")
    
    logger.info("Smartie is performing the retrain check...")
    with session_scope(dal) as session:
        retrain(session)
    logger.info("*"*80)

if __name__ == '__main__':
    logging.basicConfig(filename='fbo.log',
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s') 
    main()

