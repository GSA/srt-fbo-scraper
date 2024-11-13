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
    """Configure logger with both JSON and standard formatting"""
    logger.handlers = []  # Clear existing handlers
    logger.setLevel(logging.INFO)
    
    # Create logs directory if it doesn't exist
    log_dir = Path("/var/log/fbo_scraper")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Standard log file handler
    standard_log_path = log_dir / "fbo_scraper.log"
    standard_file_handler = TimedRotatingFileHandler(
        standard_log_path,
        when="midnight",
        interval=1,
        backupCount=30
    )
    standard_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    standard_file_handler.setFormatter(standard_formatter)
    standard_file_handler.setLevel(stdout_level)
    logger.addHandler(standard_file_handler)
    
    # 2. JSON log file handler
    json_log_path = log_dir / "fbo_scraper.json.log"
    json_file_handler = TimedRotatingFileHandler(
        json_log_path,
        when="midnight",
        interval=1,
        backupCount=30
    )
    json_formatter = CustomJsonFormatter()
    json_file_handler.setFormatter(json_formatter)
    json_file_handler.setLevel(stdout_level)
    logger.addHandler(json_file_handler)
    
    # 3. Console handler (using standard formatting)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(standard_formatter)
    console_handler.setLevel(stdout_level)
    logger.addHandler(console_handler)
    
    return logger