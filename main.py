import logging
import sys

from utils import get_opps
from utils.predict import Predict 
from utils.db.db_utils import get_db_url, session_scope, DataAccessLayer, insert_data

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

conn_string = get_db_url()
dal = DataAccessLayer(conn_string)
dal.connect()

def main():    

    logger.info("Smartie is fetching opportunties from SAM...")
    data = get_opps.main()
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
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh = logging.FileHandler(r'smartie-logger.log')
    fh.setFormatter( logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(fh)
    main()
