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
    
    # Cleaner options check using DotDict
    if options.client.json_logging:
        formatter = CustomJsonFormatter()
    else:
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    handler.setLevel(stdout_level)
    logger.addHandler(handler)
    
    return logger