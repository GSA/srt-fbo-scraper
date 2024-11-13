""" 
Command line tool to generate users that need to be removed from out User db.
"""


import logging
from pathlib import Path
import sys, traceback
from datetime import datetime
from typing import Any
from addict import Addict
from fbo_scraper.options import pre_main
from .ebuy_csv import db_forwarding, parse_csv
from tqdm import tqdm
from argparse import BooleanOptionalAction

import functools
from copy import deepcopy
from fbo_scraper.json_log_formatter import configure_logger
from fbo_scraper.options.parser import make_parser
from fbo_scraper.db.connection import DataAccessLayer, get_db_url, DALException

from fbo_scraper.db.db import Users
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = sys.prefix

BASE_PKG_DIR = Path(__file__).parent.parent.parent.parent
connection_params = {'connect_timeout': 30}

logger = logging.getLogger()

def setup_logging(options):
    """Initialize logging configuration"""
    global logger
    logger = configure_logger(
        logger,
        options,
        stdout_level=logging.DEBUG
    )

    return logger

def setup_db():
    conn_string = get_db_url()
    dal = DataAccessLayer(conn_string, connection_params)
    dal.connect()
    return dal

def separation_parser():

    parser = make_parser()

    parser.add_argument(
        "-n",
        "--not-government",
        dest="not_government_file",
        required=False,
        help="Full Path to Not Government employees Separation Report",
    )

    parser.add_argument(
        "-g",
        "--government",
        dest="government_file",
        required=False,
        help="Full Path to Government employees Separation Report",
    )

    parser.add_argument(
        "-e",
        "--environment",
        dest="environment",
        required=False,
        default="local",
        help="Define the cloud.gov environment for data insertion",
    )

    return parser

def process_not_government(file_path: str, session):
    employees_listed = parse_csv(file_path)

    try:
        logger.info("Progress on Not Government Separation Report")
        for employee in tqdm(employees_listed):
            user = session.query(Users).filter(
                Users.firstName == employee.get('First name'),
                Users.lastName == employee.get('Last name')).first()
            if user:
                logger.info(f"User {user.firstName} {user.lastName} is marked as Rejected")
                user.isRejected = True
                user.isAccepted = False

    except Exception as e:
        logger.error("Error with Not Government Separation Report User Query")
        raise e
    

def process_government(file_path: str, session):
    employees_listed = parse_csv(file_path)

    try:
        logger.info("Progress on Government Separation Report")
        for employee in tqdm(employees_listed):
            user = session.query(Users).filter(
                Users.email == employee.get('email')).first()
            if user:
                logger.info(f"User {user.firstName} {user.lastName} is marked as Rejected")
                user.isRejected = True
                user.isAccepted = False

    except Exception as e:
        logger.error("Error with Not Government Separation Report User Query")
        raise e


def process_separation_report(options):

    logger.info("Starting Separation Report Processing")

    db_child = db_forwarding(options.environment)

    logger.info("Connecting to Database...")
    dal = setup_db()

    with dal.Session.begin() as session:
        if options.not_government_file:
            process_not_government(options.not_government_file, session)
        
        if options.government_file:
            process_government(options.government_file, session)


    if db_child:
        db_child.close()


def main():
    options = pre_main(
        app_name="Separation Report Tool",
        app_version="0.0.1",
        _make_parser=separation_parser,
    )

    setup_logging(options)

    try:
        process_separation_report(options)
    except KeyboardInterrupt:
        logger.exception("Keyboard Interrupt")
    except Exception as e:
        logger.exception("Error processing Separation Reports")
        traceback.print_exc(file=sys.stdout)



    
