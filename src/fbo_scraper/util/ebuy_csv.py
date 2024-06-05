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
from datetime import datetime
from typing import Any
from addict import Addict
from fbo_scraper.predict import Predict
from fbo_scraper.options import pre_main
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.safari.options import Options as SafariOptions

import functools
from copy import deepcopy
from fbo_scraper.options.parser import make_parser
from fbo_scraper.json_log_formatter import configureLogger
from fbo_scraper.db.connection import DataAccessLayer, get_db_url, DALException
from fbo_scraper.main import grab_model_path
from fbo_scraper.get_opps import get_docs, get_attachment_data
from fbo_scraper.db.db_utils import (
    insert_data_into_solicitations_table,
)
from fbo_scraper.db.db import Attachment, NoticeType, Solicitation, Base


BASE_DIR = sys.prefix

BASE_PKG_DIR = Path(__file__).parent.parent.parent.parent

EBUY_DEFAULT_DIR = Path(BASE_PKG_DIR, "ebuy")
ATTACHMENTS_DIR = Path(BASE_PKG_DIR, "attachments")

SOLICITATION_COLUMNS = Solicitation.__table__.columns.keys()
ATTACHMENT_COLUMNS = Attachment.__table__.columns.keys()

SOLICITATION_JSON_FIELDS = ('category_list', 'history', 'action', 'contactInfo', 'parseStatus', 'predictions', 'noticeData')

now = datetime.now()
now_sft = now.strftime("%Y_%m_%d_%H-%M-%S")
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
            d["numDocs"] = d["AttachmentCount"]
            d["notice type"] = "RFQ" # Specific eBuy notice type
            d["solnbr"] = d["RFQID"]
            d["agency"] = d["BuyerAgency"]
            d["subject"] = d["Title"]
            d["postedDate"] = parse(d["IssueDate"])
            d["emails"] = [d["BuyerEmail"]]
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

def none_to_null(row: dict):
    from sqlalchemy import null

    for k, v in row.items():
        if v is None:
            row[k] = 'NULL'
    return row 

def make_sql_statment(row_values: list[dict], table):
    from sqlalchemy.sql import text
    
    table_name = table.__tablename__

    columns = ", ".join([f'"{col}"' for col in table.__table__.columns.keys()])

    statements = []
    #print(row_values)
    for row in row_values:
        value_keys = row.keys()

        row = none_to_null(row)

        update_values = ', '.join([f'"{key}" = EXCLUDED."{key}"' for key in value_keys]).replace("'NULL'", "NULL")
            #stmt = f"UPDATE {table_name} SET {update_values} WHERE id = '{row['id']}'"
        insert_values = ', '.join([f"'{row[key]}'" for key in value_keys]).replace("'NULL'", "NULL")
            #stmt = f"INSERT INTO {table_name} ({columns}) VALUES ({insert_values})"


        stmt = f"INSERT INTO {table_name} ({columns}) VALUES ({insert_values}) ON CONFLICT (id) DO UPDATE SET {update_values};"

        statements.append(stmt)

    return '\n'.join(statements)


def models_to_sql_insert(sols):
    # Convert the models to dictionaries

    import json
    from sqlalchemy import func
    sol_data = []
    attachment_data = []

    for sol in sols:
        sol.updatedAt = func.now()
        sol_dict = deepcopy(sol.__dict__)
        attachments = sol_dict.pop("attachments")
        
        if "noticeData" in sol_dict and '\ufeffS.No' in sol_dict["noticeData"]:
            sol_dict["noticeData"].pop('\ufeffS.No', None)

        for key, value in sol_dict.items():
            if isinstance(value, (dict, list)) or key in SOLICITATION_JSON_FIELDS:
                sol_dict[key] =json.dumps(value, ensure_ascii=False).replace("'", "''")

        if "_sa_instance_state" in sol_dict:
            sol_dict.pop("_sa_instance_state")


        sol_dict = {col: sol_dict.get(col, None) for col in SOLICITATION_COLUMNS}

        for attachment in attachments:
            attachment_dict = deepcopy(attachment.__dict__)
            
            if "_sa_instance_state" in attachment_dict:
                attachment_dict.pop("_sa_instance_state")
            if "attachment_text" in attachment_dict:
                attachment_dict.pop("attachment_text")

            attachment_dict = {col: attachment_dict.get(col, None) for col in ATTACHMENT_COLUMNS}

            attachment_data.append(attachment_dict)
        
        sol_data.append(sol_dict)

    # Compile the statement to get the SQL
    logger.info('Compiling insert statements....')
    attachment_stmt = make_sql_statment(attachment_data, Attachment)

    
    sol_stmt = make_sql_statment(sol_data, Solicitation)

    # Get the SQL and the parameters
    sql_stmt = str(attachment_stmt) + "\n" + str(sol_stmt) 

    return sql_stmt

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
            solicitation_inserted = insert_data_into_solicitations_table(session, predicted_data)
            logger.info("Smartie is done inserting data into database!")

        if solicitation_inserted:
            sql = models_to_sql_insert(solicitation_inserted)
            logger.debug(f"SQL: {sql}")

            if sql:
                with open(Path(EBUY_DEFAULT_DIR, f"ebuy_insert_{now_sft}.sql"), "w") as f:
                    f.write(sql)
                    logger.info("SQL Insert file created!")



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