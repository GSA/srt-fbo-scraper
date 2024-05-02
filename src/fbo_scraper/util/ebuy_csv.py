import logging
from pathlib import Path
import sys, traceback

from fbo_scraper.predict import Predict
from fbo_scraper.options import pre_main
from fbo_scraper.options.parser import make_parser
from fbo_scraper.json_log_formatter import configureLogger
from fbo_scraper.db.connection import DataAccessLayer, get_db_url, DALException
from fbo_scraper.main import grab_model_path
from fbo_scraper.get_opps import get_docs, get_attachment_data
from fbo_scraper.db.db_utils import (
    insert_data_into_solicitations_table,
)


BASE_DIR = sys.prefix

BASE_PKG_DIR = Path(__file__).parent.parent.parent.parent

EBUY_DEFAULT_DIR = Path(BASE_PKG_DIR, "ebuy")
ATTACHMENTS_DIR = Path(BASE_PKG_DIR, "attachments")

logger = logging.getLogger()
configureLogger(logger, stdout_level=logging.INFO)

def setup_db():
    conn_string = get_db_url()
    dal = DataAccessLayer(conn_string)
    dal.connect()
    return dal

def ebuy_parser():

    
    ebuy_config = Path(BASE_DIR, "conf", "ebuy.yml")

    parser = make_parser(ebuy_config)

    parser.add_argument(
        "-f",
        "--file",
        dest="file",
        required=True,
        help="eBuy CSV file to process",
    )

    prediction_model = parser.add_argument_group("Prediction Model Options")
    prediction_model.add_argument(
        "--model-name",
        dest="prediction.model_name",
        required=False,
        help="Define the name to the prediction model in binaries folder.",

    )

    prediction_model.add_argument(
        "--model-path",
        dest="prediction.model_path",
        required=False,
        help="Define the absolute path to the prediction model.",
    )

    return parser

def grab_ebuy_csv(options):
    """Placing the Path to the eBuy CSV file in the options object"""
    options.file_path = Path(EBUY_DEFAULT_DIR, options.file)

def parse_csv(file_path) -> list:
    import csv

    with open(file_path, "r", newline='') as csv_file:
        dict_reader = csv.DictReader(csv_file, delimiter=",", quotechar='"')
        return list(dict_reader)
    

def filter_out_no_attachments(data) -> list[dict]:
    return [d for d in data if d["Attachments"] and len(d) == 13] 
    # Length of 13 is to mitigate the csv deliminter issue from export
    # Hopefully eBuy Open will adjust

def rfq_relabeling(data) -> list[dict]:
    """ 
    Relabeling data to match the SAM labeling for the model
    """
    from dateutil.parser import parse

    for d in data:
        try:
            d["resourceLinks"] = d["Attachments"].split("\n")
            d["notice type"] = "RFQ" # Specific eBuy notice type
            d["solnbr"] = d["RFQID"]
            d["agency"] = d["BuyerAgency"]
            d["subject"] = d["Title"]
            d["postedDate"] = parse(d["IssueDate"])
            d["emails"] = d["BuyerEmail"]
            d["office"] = ""
        except KeyError:
            logger.error(f"Not all data present for {d.get('RFQID')}")
            continue
    return data

def grab_attachment_texts(data) -> list[dict]:
    """
    Calling the document url listed in the resourceLinks key to grab the text
    to use for predictions. 
    """

    prediction_ready = []
    for opp in data:
        file_list = get_docs(opp, out_path=ATTACHMENTS_DIR)
        opp["attachments"] = []

        if file_list:
            attachment_data = [
                get_attachment_data(file_and_url_tuple[0], file_and_url_tuple[1])
                for file_and_url_tuple in file_list
            ]
            opp["attachments"].extend(attachment_data)

        prediction_ready.append(opp)

    return prediction_ready

def clear_attachments():
    try:
        for path in ATTACHMENTS_DIR.glob("**/*"):
            if path.is_file():
                path.unlink()
    except Exception as e:
        logger.error(f"Error clearing attachments: {e}")

def ebuy_process(options):
    dal = setup_db()

    grab_ebuy_csv(options)
    options.model_path = grab_model_path(options)
    print(options)

    predict = Predict(best_model_path=options.model_path)
    
    rfq_data = parse_csv(options.file_path)
    print("After Parse: ", rfq_data[0])
    rfq_data = filter_out_no_attachments(rfq_data)
    print("After Filter: ", rfq_data[0])
    rfq_data = rfq_relabeling(rfq_data)
    print("After Labeling: ", rfq_data[0])

    rfq_data = grab_attachment_texts(rfq_data)

    predicted_data = predict.insert_predictions(rfq_data)
    print(predicted_data[0])

    with dal.Session.begin() as session:
        if predicted_data:
            # insert_data(session, data)
            logger.info("Smartie is inserting data into the database...")
            insert_data_into_solicitations_table(session, predicted_data)
            logger.info("Smartie is done inserting data into database!")

def main():
    options = pre_main(
        app_name="ebuy parser",
        app_version="0.0.1",
        _make_parser=ebuy_parser,
    )
    
    try:
        ebuy_process(options)
    except KeyboardInterrupt:
        logger.exception("Keyboard Interrupt")
        clear_attachments()
    except Exception as e:
        logger.exception("Error processing eBuy CSV")
        traceback.print_exc(file=sys.stdout)
    
    clear_attachments()

    sys.exit(0)