import logging
from pythonjsonlogger import jsonlogger
from datetime import datetime
from dateutil import parser
from sys import stdout

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


    def process_log_record(self, log_record):
        '''
        Use this to move everything besides message, level, and timestamp into
        a 'meta' dict to be compatable with cloud.gov loggerator
        :param log_record:
        :return:
        '''
        log_record['meta'] = dict()
        to_be_removed = []
        for key in log_record:
            if not key in ['message', 'level', 'timestamp', 'meta']:
                log_record['meta'][key] = log_record[key]
                to_be_removed.append(key)

        if 'timestamp' in log_record:
            t = parser.parse(log_record['timestamp'])
            log_record['timestamp'] = t.strftime('%Y-%m-%dT%H:%M:%SZ')

        for key in to_be_removed:
            del log_record[key]

        # TODO: we *should* be able to get this to work as a dict, but cloud.gov doesn't do it for me.
        extra = ""
        for key in log_record['meta']:
            extra = "{} {}:{} |".format(extra, key, log_record['meta'][key])
        if not extra == "":
            extra = " [{} ]".format(extra)
        log_record['message'] = "{}{}".format(log_record['message'], extra)

        del log_record['meta']


        return log_record



def configureLogger(logger, log_file_level = logging.INFO, stdout_level = 11):

    # stdout_level defaults to 11 so we get everything even a tiny bit more critical than DEBUG in the cloud.gov logs
    logger.setLevel(stdout_level)

    # json output setup
    logHandler = logging.StreamHandler(stdout)
    formatter = CustomJsonFormatter('(timestamp) (level) (message) (filename) (lineno)') # jsonlogger.JsonFormatter()
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

