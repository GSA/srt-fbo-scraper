import logging

from utils import get_opps
from utils.predict import Predict
from utils.db.db_utils import get_db_url, session_scope, DataAccessLayer, insert_data_into_solicitations_table, insert_notice_types
from utils.json_log_formatter import CustomJsonFormatter, configureLogger
from utils.sam_utils import update_old_solicitations, opportunity_filter_function, set_psc_code_download_list
import sys
import datetime
import os

logger = logging.getLogger()
configureLogger(logger, stdout_level=logging.INFO)

conn_string = get_db_url()
dal = DataAccessLayer(conn_string)
dal.connect()


def main(limit=None, updateOld=True, opportunity_filter_function=None, target_sol_types="o,k", skip_attachments=False, from_date = 'yesterday', to_date='yesterday'):
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


        data = get_opps.main(limit, opportunity_filter_function=opportunity_filter_function, target_sol_types=target_sol_types, skip_attachments=skip_attachments, from_date=from_date, to_date=to_date)
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


def check_environment():
    '''
    Tests to make sure any needed env vars have been set
    Exits application with error if anything isn't found.
    Returns:
    '''

    if not os.getenv('SAM_API_URI'):
        os.environ['SAM_API_URI'] = "https://api.sam.gov/opportunities/v2/search"
        logger.warning(f"SAM_API_URI environment variable not set, using default {os.getenv('SAM_API_URI')}")
    else:
        logger.info(f"Found SAM_API_URI in the environment: {os.environ['SAM_API_URI']}")

    if not os.getenv('SAM_API_KEY'):
        logger.error("SAM_API_KEY not found in the environment.")
        logger.critical("Exiting")
        exit(7)
    else:
        logger.info(f"Found SAM_API_KEY in the environment: { os.environ['SAM_API_KEY'][:4] }...{ os.environ['SAM_API_KEY'][-4:] }")


if __name__ == '__main__':
    # set defaults
    limit = None
    updateOld = True
    target_sol_types = "o,k"
    skip_attachemnts = False
    from_date = "yesterday"
    to_date = "yesterday"


    # set these PSC codes for EPA demo mode
    # set_psc_code_download_list(["61", "6117", "6125", "6130", "6135", "6140", "6150", "7", "7A", "7A20", "7A21", "7B", "7B20", "7B21", "7B22", "7C", "7C20", "7C21", "7D", "7D20", "7E", "7E20", "7E21", "7F", "7F20", "7G", "7G20", "7G21", "7G22", "7H", "7H20", "7J", "7J20", "7K" "7K20", "7730", "D", "DA", "DA01", "DA10", "DB", "DB01", "DB02", "DB10", "DC", "DC01", "DC10", "DD", "DD01", "DE", "DE01", "DE02", "DE10", "DE11", "DF", "DF01", "DF10", "DG", "DG01", "DG10", "DG11", "DH", "DH01", "DH10", "DJ", "DJ01", "DJ10", "DK", "DK01", "DK10"] )


    # fast mode
    # limit=40
    updateOld=False
    # skip_attachemnts=True

    #db reload for last week
    #from_date = datetime.date.today() - datetime.timedelta(days=8)
    #to_date = datetime.date.today() - datetime.timedelta(days=1)
    # updateOld=False

    
    check_environment()
    main(limit=limit, updateOld=updateOld, opportunity_filter_function=opportunity_filter_function, target_sol_types=target_sol_types, skip_attachments=skip_attachemnts, from_date=from_date, to_date=to_date)
