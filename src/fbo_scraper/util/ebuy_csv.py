"""
Important Note: Need to have a cookies.json file stored in the conf directory.
This file is used to authenticate the user to the eBuy site to download the attachments.
Here's a step-by-step guide:

- Manually log into eBuy through Max.gov  website in your browser.
- Use EditThisCookie chrome extension to export your cookies. 
- Copy the exported values into a cookies.json file.

"""

import logging
from pathlib import Path
import sys, traceback
import http.cookiejar
import json
from addict import Addict
from fbo_scraper.predict import Predict
from fbo_scraper.options import pre_main
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.safari.options import Options as SafariOptions

import functools

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

def get_default_browser():
    """Grabbing the default browser based on operating system"""
    import platform
    browser = None

    # Determine the operating system
    os_name = platform.system()

    # Choose the appropriate driver based on the operating system
    match os_name:
        case "Windows":
            browser = webdriver.Edge(options=EdgeOptions())
        case "Darwin":
            browser = webdriver.Safari(options=SafariOptions())
        case _:
            browser = webdriver.Firefox(options=FirefoxOptions())

    return browser

def grab_cookies(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        driver = get_default_browser()
        try:
            driver.get("https://login.max.gov/cas/login?service=https%3A%2F%2Fwww.ebuy.gsa.gov%2Febuyopen%2F")
        except Exception as e:
            logger.error(f"Error loading the eBuy site: {e}")
            driver.quit()
            raise e
        # Wait for the user to manually log in
        input("Press Enter after you have logged in...")
        cookies = driver.get_cookies()
        
        f = func(cookies, *args, **kwargs)
        driver.quit()
        return f
    return wrapper


@grab_cookies
def create_ebuy_headers(cookies):

    """
    cookies_path = Path(BASE_DIR, "conf", "cookies.json") 
    # Load the cookies from the file
    with open(cookies_path, 'r') as f:
        cookies = json.load(f)
    """

    # Add the cookies to the cookie jar
    cookie_jar = [Addict(cookie) for cookie in cookies]

    # Get the cookies as a string
    cookie_string = '; '.join(f'{c.name}={c.value}' for c in cookie_jar)

    # Add the cookies to the headers
    headers = {
        'Cookie': cookie_string,
    }

    return headers
    

def grab_attachment_texts(data) -> list[dict]:
    """
    Calling the document url listed in the resourceLinks key to grab the text
    to use for predictions. 
    """

    prediction_ready = []
    headers = create_ebuy_headers()
    for opp in data:
        file_list = get_docs(opp, out_path=ATTACHMENTS_DIR, headers=headers)
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
    logger.debug(options)

    predict = Predict(best_model_path=options.model_path)
    
    rfq_data = parse_csv(options.file_path)
    logger.debug("After Parse: ", rfq_data[0])
    
    rfq_data = filter_out_no_attachments(rfq_data)
    logger.debug("After Filter: ", rfq_data[0])
    
    rfq_data = rfq_relabeling(rfq_data)
    logger.debug("After Labeling: ", rfq_data[0])

    rfq_data = grab_attachment_texts(rfq_data)

    predicted_data = predict.insert_predictions(rfq_data)
    logger.debug(predicted_data[0])

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