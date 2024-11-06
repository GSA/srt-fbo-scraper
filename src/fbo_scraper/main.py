import logging
from pathlib import Path
from fbo_scraper import get_opps
from fbo_scraper.get_opps import SamApiError
from fbo_scraper.binaries import binary_path
from fbo_scraper.predict import Predict, PredictException
from fbo_scraper.db.db_utils import (
    session_scope,
    insert_data_into_solicitations_table,
    insert_notice_types,
)
from fbo_scraper.json_log_formatter import configure_logger
from fbo_scraper.sam_utils import update_old_solicitations, opportunity_filter_function
import sys
import os
from fbo_scraper.db.connection import DataAccessLayer, get_db_url, DALException
from fbo_scraper.options import pre_main
from fbo_scraper.options.parser import make_parser
from fbo_scraper import name, version
from fbo_scraper.json_log_formatter import configure_logger, configureLogger

# Initialize logger with specific name
logger = logging.getLogger('scraper')

def setup_logging(options):
    """Initialize logging configuration"""
    global logger
    logger = configure_logger(
        logger,
        options,
        stdout_level=logging.INFO
    )
    return logger

def setup_db():
    """Setup database connection"""
    conn_string = get_db_url()
    dal = DataAccessLayer(conn_string)
    dal.connect()
    return dal

def scraper_parser():
    """
    Allows to accept command line arguments for the scraper.
    """
    from argparse import BooleanOptionalAction

    parser = make_parser()

    client = parser.add_argument_group("Client Options")
    
    client.add_argument(
        "--solicitation-types",
        dest="client.target_sol_types",
        required=False,
        help="Define the solicitation types to be fetched from SAM."
    )

    client.add_argument(
        "--skip-attachments",
        dest="client.skip_attachments",
        required=False,
        help="Define whether to skip attachments."
    )

    client.add_argument(
        "--from-date",
        dest="client.from_date",
        required=False,
        help="Define the start date for the search. Format: mm/dd/yyyy"
    )

    client.add_argument(
        "--to-date",
        dest="client.to_date",
        required=False,
        help="Define the end date for the search. Format: mm/dd/yyyy"
    )

    client.add_argument(
        "--limit",
        dest="client.limit",
        required=False,
        help="Define the limit for the number of opportunities to be fetched from SAM."
    )

    client.add_argument(
        "--json-logging",
        dest="client.json_logging",
        action="store_true",
        required=False,
        default=False,
        help="Enable JSON-formatted logging output."
    )

    database = parser.add_argument_group("Database Options")
    database.add_argument(
        "--update-old",
        dest="database.update_old",
        action=BooleanOptionalAction,
        required=False,
        help="Define whether to update old solicitations."
    )

    prediction_model = parser.add_argument_group("Prediction Model Options")
    prediction_model.add_argument(
        "--model-name",
        dest="prediction.model_name",
        required=False,
        help="Define the name to the prediction model in binaries folder."
    )

    prediction_model.add_argument(
        "--model-path",
        dest="prediction.model_path",
        required=False,
        help="Define the absolute path to the prediction model."
    )

    return parser

def grab_model_path(options):
    """
    Returns the path to the prediction model.
    """
    model_name = options.prediction.model_name
    model_path = options.prediction.model_path
    if model_name:
        model_path = Path(binary_path, model_name)
    elif model_path:
        model_path = Path(model_path)
    else:
        model_path = Path(binary_path, "atc_estimator.pkl")
    return model_path

def check_environment():
    """
    Tests to make sure any needed env vars have been set
    """
    if not os.getenv("SAM_API_URI"):
        os.environ["SAM_API_URI"] = "https://api.sam.gov/opportunities/v2/search"
        logger.warning(
            f"SAM_API_URI environment variable not set, using default {os.getenv('SAM_API_URI')}"
        )
    else:
        logger.info(
            f"Found SAM_API_URI in the environment: {os.environ['SAM_API_URI']}"
        )

    if not os.getenv("SAM_API_KEY"):
        logger.error("SAM_API_KEY not found in the environment.")
        logger.critical("Exiting")
        exit(7)
    else:
        logger.info(
            f"Found SAM_API_KEY in the environment: {os.environ['SAM_API_KEY'][:4]}...{os.environ['SAM_API_KEY'][-4:]}"
        )

def main(
    limit=None,
    updateOld=True,
    opportunity_filter_function=None,
    target_sol_types="o,k",
    skip_attachments=False,
    from_date="yesterday",
    to_date="yesterday",
    options=None,
):
    """
    Main execution function for the scraper
    """
    opps_data = None
    predict_data = None

    try:
        dal = setup_db()

        model_path = grab_model_path(options)
        predict = Predict(best_model_path=model_path)

        if limit:
            logger.warning(
                f"Artificial limit of {limit} placed on the number of opportunities processed. "
                "Should not happen in production."
            )

        if not updateOld:
            logger.warning(
                "Set to NOT update old solicitations. Should not happen in production."
            )

        with dal.Session.begin() as session:
            # make sure notice types are configured and committed
            insert_notice_types(session)

        logger.info("Smartie is fetching opportunities from SAM...")

        opps_data = get_opps.main(
            limit,
            opportunity_filter_function=opportunity_filter_function,
            target_sol_types=target_sol_types,
            skip_attachments=skip_attachments,
            from_date=from_date,
            to_date=to_date,
        )

        if not opps_data:
            logger.info("Smartie didn't find any opportunities!")
        else:
            logger.info("Smartie is done fetching opportunities from SAM!")
            logger.info("Smartie is making predictions for each notice attachment...")

            predict_data = predict.insert_predictions(opps_data)
            logger.info("Smartie is done making predictions for each notice attachment!")

            with dal.Session.begin() as session:
                if predict_data:
                    logger.info("Smartie is inserting data into the database...")
                    insert_data_into_solicitations_table(session, predict_data)
                    logger.info("Smartie is done inserting data into database!")
                else:
                    if opps_data and not predict_data:
                        logger.error("No prediction data to insert. Something went wrong.")

                if updateOld:
                    update_old_solicitations(session, max_tests=10)

            logger.info("Run complete without major errors.")
    
    except SamApiError as e:
        logger.error(f"API Error - {e}", exc_info=True)
    except PredictException as e:
        logger.error(f"Prediction Error - {e}", exc_info=True)
    except DALException as e:
        logger.error(f"Database Error - {e}", exc_info=True)
    except Exception as e:
        logger.error("Unhandled error. Data for the day may be lost.")
        logger.error(f"Exception: {e}", exc_info=True)
        logger.error(f"Unexpected error: {str(sys.exc_info()[0])}")

def actual_main():
    """
    Entry point for the application when run directly
    """
    # Get options
    options = pre_main(
        app_name=name,
        app_version=version,
        _make_parser=scraper_parser,
    )
    
    # Setup logging with options
    setup_logging(options)
    
    # Check environment after logging is configured
    check_environment()

    # Run main with parsed options
    main(
        limit=options.client.limit,
        updateOld=options.database.update_old,
        opportunity_filter_function=opportunity_filter_function,
        target_sol_types=options.client.target_sol_types,
        skip_attachments=options.client.skip_attachments,
        from_date=options.client.from_date,
        to_date=options.client.to_date,
        options=options,
    )

if __name__ == "__main__":
    actual_main()