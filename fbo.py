
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

logging.basicConfig(level=logging.INFO,
                    format='[%(levelname)s] %(message)s')

conn_string = get_db_url()
dal = DataAccessLayer(conn_string)
dal.connect()

def get_nightly_data(notice_types, naics):
    now_minus_two = datetime.datetime.now() - datetime.timedelta(2)
    date = now_minus_two.strftime("%Y%m%d")
    nfbo = fbo_nightly_scraper.NightlyFBONotices(date = date, notice_types = notice_types, naics = naics)
    file_lines = nfbo.download_from_ftp()
    if not file_lines:
        #exit program if download_from_ftp() failed
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
        logging.info("Smartie is retraining a model!")
        attachments = fetch_validated_attachments(session)
        X, y = train.prepare_samples(attachments)
        results, score, best_estimator, params = train.train(X,
                                                             y, 
                                                             weight_classes = True,
                                                             n_iter_search = 150,
                                                             score='roc_auc',
                                                             random_state = 123)
        logging.info("Smartie is done retraining a model!")
        last_score = fetch_last_score(session)
        better_model = True if last_score < score else False
        if better_model:
            train.pickle_model(best_estimator)
            logging.info("Smartie has pickled the new model!")
        else:
            pass
        insert_model(session, results, params, score)
    else:
        logging.info("Smartie decided not to retrain a new model!")


def main():    
    notice_types= ['MOD','PRESOL','COMBINE', 'AMDCSS']
    naics = ['334111', '334118', '3343', '33451', '334516', '334614', '5112', '518', 
             '54169', '54121', '5415', '54169', '61142']
    logging.info("Smartie is downloading the most recent nightly FBO file...")
    nightly_data = get_nightly_data(notice_types, naics)
    logging.info("Smartie is done downloading the most recent nightly FBO file!")

    logging.info("Smartie is getting the attachments and their text from each FBO notice...")
    fboa = get_fbo_attachments.FboAttachments(nightly_data)
    updated_nightly_data = fboa.update_nightly_data()
    logging.info("Smartie is done getting the attachments and their text from each FBO notice!")

    logging.info("Smartie is making predictions for each notice attachment...")
    predict = Predict(updated_nightly_data)
    updated_nightly_data_with_predictions = predict.insert_predictions()
    logging.info("Smartie is done making predictions for each notice attachment!")
    
    logging.info("Smartie is inserting data into the database...")
    with session_scope(dal) as session:
        insert_updated_nightly_file(session, updated_nightly_data_with_predictions)
    logging.info("Smartie is done inserting data into database!")
    
    logging.info("Smartie is performing the retrain check...")
    with session_scope(dal) as session:
        retrain(session)

if __name__ == '__main__':
    main()

