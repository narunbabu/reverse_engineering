# utils/logger.py

import logging
from datetime import datetime
from pathlib import Path

class CustomFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        ct = datetime.fromtimestamp(record.created)
        if datefmt:
            s = ct.strftime(datefmt)
        else:
            s = ct.isoformat()
        return s

def setup_logger(project_folder: Path) -> logging.Logger:
    log_folder = project_folder / 'logs'
    log_folder.mkdir(parents=True, exist_ok=True)
    log_file = log_folder / 'project_creation.log'
    
    logger = logging.getLogger(f'project_creation_{project_folder.name}')
    logger.setLevel(logging.DEBUG)
    
    # Prevent adding multiple handlers to the logger
    if not logger.hasHandlers():
        # Create handlers
        f_handler = logging.FileHandler(log_file, encoding='utf-8')
        f_handler.setLevel(logging.DEBUG)
        
        c_handler = logging.StreamHandler()
        c_handler.setLevel(logging.INFO)
        
        # Create formatters and add to handlers
        formatter = CustomFormatter('%(asctime)s | %(levelname)s | %(message)s', "%Y-%m-%d %H:%M:%S.%f")
        f_handler.setFormatter(formatter)
        c_handler.setFormatter(formatter)
        
        # Add handlers to the logger
        logger.addHandler(f_handler)
        logger.addHandler(c_handler)
    
    return logger
