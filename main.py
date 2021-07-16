import logging

from utils import get_opps
from utils.predict import Predict
from utils.db.db_utils import get_db_url, session_scope, DataAccessLayer, insert_data, insert_data_into_solicitations_table
from utils.json_log_formatter import CustomJsonFormatter, configureLogger
from utils.sam_utils import update_old_solicitations
import sys

logger = logging.getLogger()
configureLogger(logger, stdout_level=0)

conn_string = get_db_url()
dal = DataAccessLayer(conn_string)
dal.connect()


def main(limit=None, updateOld=True, filter_naics = True, target_sol_types=("Combined Synopsis/Solicitation", "Solicitation")):
    try:
        if limit:
            logger.error("Artifical limit of {} placed on the number of opportunities processed.  Should not happen in production.".format(limit))

        if not updateOld:
            logger.error("Set to NOT update old solicitations. Should not happen in production.".format(limit))



        logger.info("Connecting with database at {}".format(conn_string))
        logger.info("Smartie is fetching opportunties from SAM...")


        data = get_opps.main(limit, filter_naics=filter_naics, target_sol_types=target_sol_types)
        if not data:
            logger.info("Smartie didn't find any opportunities!")
        else:
            logger.info("Smartie is done fetching opportunties from SAM!")

            logger.info("Smartie is making predictions for each notice attachment...")
            predict = Predict(data)
            data = predict.insert_predictions()
            logger.info("Smartie is done making predictions for each notice attachment!")

            logger.info("Smartie is inserting data into the database...")

        with session_scope(dal) as session:
            if data:
                # insert_data(session, data)
                insert_data_into_solicitations_table(session, data)
                logger.info("Smartie is done inserting data into database!")

            if updateOld:
                update_old_solicitations(session)

        logger.info("Run complete without major errors.")

    except Exception as e:
        logger.error("Unhandled error. Data for the day may be lost.")
        logger.error(f"Exception: {e}", exc_info=True)
        logger.error("Unexpected error: {}".format(str(sys.exc_info()[0])))


if __name__ == '__main__':
    main(limit=None, updateOld=True, filter_naics = True, target_sol_types=("Combined Synopsis/Solicitation", "Solicitation"))
