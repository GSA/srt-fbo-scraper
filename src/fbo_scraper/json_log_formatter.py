import logging
from pythonjsonlogger import jsonlogger
from datetime import datetime
from dateutil import parser
from sys import stdout
from logging.handlers import TimedRotatingFileHandler
import re
from pathlib import Path
from fbo_scraper import log_path

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        
        # Add timestamp if not present
        if not log_record.get("timestamp"):
            now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            log_record["timestamp"] = now
        
        # Safely handle level using .get() to avoid KeyError
        level = log_record.get("level")
        if level:
            log_record["level"] = level.lower()
            if level == "level 12":
                log_record["level"] = "found it top"
        else:
            log_record["level"] = record.levelname.lower()
        
        # Level number matching - moved outside the else block as per review
        matches = re.match("level ([0-9]*)", log_record.get("level", ""))
        if matches:
            l_int = int(matches.group(1))
            if (l_int >= 10) and (l_int < 20):
                log_record["level"] = "debug"

    def process_log_record(self, log_record):
        """
        Use this to move everything besides message, level, and timestamp into
        a 'meta' dict to be compatible with cloud.gov loggerator
        """
        log_record["meta"] = dict()
        to_be_removed = []
        for key in log_record:
            if key not in ["message", "level", "timestamp", "meta"]:
                log_record["meta"][key] = log_record[key]
                to_be_removed.append(key)

        if "timestamp" in log_record:
            t = parser.parse(log_record["timestamp"])
            log_record["timestamp"] = t.strftime("%Y-%m-%dT%H:%M:%SZ")

        for key in to_be_removed:
            del log_record[key]
        return log_record

def configureLogger(logger, log_file_level=logging.INFO, stdout_level=11):
    # stdout_level defaults to 11 so we get everything even a tiny bit more critical than DEBUG in the cloud.gov logs
    logger.setLevel(stdout_level)

    # Add JSON handler
    json_handler = logging.StreamHandler(stdout)
    json_formatter = CustomJsonFormatter(
        "%(timestamp)s %(level)s %(message)s %(filename)s %(lineno)s"
    )
    json_handler.setFormatter(json_formatter)
    json_handler.setLevel(stdout_level)
    logger.addHandler(json_handler)

    # Standard formatter output
    standard_handler = logging.StreamHandler(stdout)
    standard_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%dT%H:%M:%SZ'
    )
    standard_handler.setFormatter(standard_formatter)
    standard_handler.setLevel(stdout_level)
    logger.addHandler(standard_handler)

    # File handler
    fh = TimedRotatingFileHandler(
        Path(log_path, "smartie-logger.log"), when="midnight", backupCount=14
    )
    fh.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    fh.setLevel(log_file_level)
    logger.addHandler(fh)
    
    logger.info("Set log levels to {} and {}".format(log_file_level, stdout_level))
    return logger