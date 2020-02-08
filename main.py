import logging

from utils import get_opps
from utils.predict import Predict 
from utils.db.db_utils import get_db_url, session_scope, DataAccessLayer, insert_data
from utils.json_log_formatter import CustomJsonFormatter, configureLogger

logger = logging.getLogger()
configureLogger(logger)

conn_string = get_db_url()
dal = DataAccessLayer(conn_string)
dal.connect()

def main(limit = None):

    logger.info("Connecting with database at {}".format(conn_string))
    logger.info("Smartie is fetching opportunties from SAM...")
    if limit:
        logger.warning("Artifical limit of {} placed on the number of opportunities processed".format(limit))

    data = get_opps.main(limit)
    if not data:
        logger.info("Smartie didn't find any opportunities!")
        return
    logger.info("Smartie is done fetching opportunties from SAM!")


    logger.info("Smartie is making predictions for each notice attachment...")
    predict = Predict(data)
    data = predict.insert_predictions()
    logger.info("Smartie is done making predictions for each notice attachment!")
    
    logger.info("Smartie is inserting data into the database...")
    with session_scope(dal) as session:
        insert_data(session, data)
    logger.info("Smartie is done inserting data into database!")
    

if __name__ == '__main__':
    main()
