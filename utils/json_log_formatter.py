import logging
from pythonjsonlogger import jsonlogger
from datetime import datetime
import re

class CustomJsonFormatter(jsonlogger.JsonFormatter):

    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        if not log_record.get('timestamp'):
            # this doesn't use record.created, so it is slightly off
            now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            log_record['timestamp'] = now
        if log_record.get('level'):
            log_record['level'] = log_record['level'].lower()
            if (log_record['level'] == 'level 12'):
                log_record['level'] = 'found it top'
        else:
            log_record['level'] = record.levelname.lower()

        # did we set the level numerically?
        matches = re.match("level ([0-9]*)", log_record['level'])
        if matches:
            l_int = int( matches.group(1) )
            if (l_int >=10) and (l_int < 20): # greater than DEBUG but less then INFO gets marked as debug for log searching
                log_record['level'] = 'debug'



def configureLogger(logger, log_file_level = logging.INFO, stdout_level = 11):

    # stdout_level defaults to 11 so we get everything even a tiny bit more critical than DEBUG in the cloud.gov logs
    logger.setLevel(stdout_level)

    # json output setup
    logHandler = logging.StreamHandler()
    formatter = CustomJsonFormatter('(timestamp) (level) (name) (message) (filename) (funcName) (lineno)') # jsonlogger.JsonFormatter()
    logHandler.setFormatter(formatter)
    logHandler.setLevel(stdout_level)
    logger.addHandler(logHandler)

    # file handler
    fh = logging.FileHandler(r'smartie-logger.log')
    fh.setFormatter( logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    fh.setLevel(log_file_level)
    logger.addHandler(fh)

    logger.info('set log levels to {} and {}'.format(log_file_level, stdout_level))

    return logger

