import sys  # Necessary for sys.stdout
import logging
from pythonjsonlogger import jsonlogger
from datetime import datetime
from dateutil import parser
from pathlib import Path
from logging.handlers import TimedRotatingFileHandler

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        
        if not log_record.get('timestamp'):
            now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            log_record['timestamp'] = now
        
        log_record['level'] = record.levelname.lower()
        self.process_log_record(log_record)
    
    def process_log_record(self, log_record):
        meta = {}
        to_remove = []
        
        for key in log_record:
            if key not in ['message', 'level', 'timestamp', 'meta']:
                meta[key] = log_record[key]
                to_remove.append(key)
        
        if meta:
            log_record['meta'] = meta
            
        for key in to_remove:
            del log_record[key]
            
        if 'timestamp' in log_record:
            t = parser.parse(log_record['timestamp'])
            log_record['timestamp'] = t.strftime('%Y-%m-%dT%H:%M:%SZ')
            
        return log_record

def configure_logger(logger, options, stdout_level=logging.INFO):
    """Configure logger with either JSON or standard formatting"""
    logger.handlers = []
    
    # Choose the formatter
    if options.client.json_logging:
        formatter = CustomJsonFormatter()
    else:
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    # Configure handler for the named logger
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    handler.setLevel(stdout_level)
    logger.addHandler(handler)
    
    # Add this section to configure the root logger
    root_logger = logging.getLogger()
    if not root_logger.handlers:
        root_handler = logging.StreamHandler(sys.stdout)
        root_handler.setFormatter(formatter)
        root_handler.setLevel(stdout_level)
        root_logger.addHandler(root_handler)
    
    return logger