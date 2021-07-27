import logging

from utils import get_opps
from utils.predict import Predict
from utils.db.db_utils import get_db_url, session_scope, DataAccessLayer, insert_data_into_solicitations_table, insert_notice_types
from utils.json_log_formatter import CustomJsonFormatter, configureLogger
from utils.sam_utils import update_old_solicitations
import sys
import datetime

logger = logging.getLogger()
configureLogger(logger, stdout_level=logging.INFO)

conn_string = get_db_url()
dal = DataAccessLayer(conn_string)
dal.connect()


def main(limit=None, updateOld=True, filter_naics = True, target_sol_types="o,k", skip_attachments=False, from_date = 'yesterday', to_date='yesterday'):
    try:
        if limit:
            logger.error("Artifical limit of {} placed on the number of opportunities processed.  Should not happen in production.".format(limit))

        if not updateOld:
            logger.error("Set to NOT update old solicitations. Should not happen in production.".format(limit))

        with session_scope(dal) as session:
            # make sure that the notice types are configured and committed before going further
            insert_notice_types(session)

        logger.info("Connecting with database at {}".format(conn_string))
        logger.info("Smartie is fetching opportunties from SAM...")


        data = get_opps.main(limit, filter_naics=filter_naics, target_sol_types=target_sol_types, skip_attachments=skip_attachments, from_date=from_date, to_date=to_date)
        if not data:
            logger.info("Smartie didn't find any opportunities!")
        else:
            logger.info("Smartie is done fetching opportunties from SAM!")

            logger.info("Smartie is making predictions for each notice attachment...")
            predict = Predict(data)
            data = predict.insert_predictions()
            logger.info("Smartie is done making predictions for each notice attachment!")


        with session_scope(dal) as session:
            if data:
                # insert_data(session, data)
                logger.info("Smartie is inserting data into the database...")
                insert_data_into_solicitations_table(session, data)
                logger.info("Smartie is done inserting data into database!")
            else:
                logger.error("No data to insert. Something went wrong.")

            if updateOld:
                update_old_solicitations(session, max_tests=10)

        logger.info("Run complete without major errors.")

    except Exception as e:
        logger.error("Unhandled error. Data for the day may be lost.")
        logger.error(f"Exception: {e}", exc_info=True)
        logger.error("Unexpected error: {}".format(str(sys.exc_info()[0])))


if __name__ == '__main__':
    # set defaults
    limit = None
    updateOld = True
    filter_naics = True
    target_sol_types = "o,k"
    skip_attachemnts = False


    # fast mode
    # limit=40
    updateOld=False
    # skip_attachemnts=True

    #db reload for last week
    # from_date = datetime.date.today() - datetime.timedelta(days=8)
    # to_date = datetime.date.today() - datetime.timedelta(days=1)
    # updateOld=False


    main(limit=limit, updateOld=updateOld, filter_naics = filter_naics, target_sol_types=target_sol_types, skip_attachments=skip_attachemnts)
