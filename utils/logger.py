# logger.py
# agentic_ai_framework/utils/logger.py
import logging
from config import LOG_FILE
import os

def setup_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO) # Set default logging level

    # Create logs directory if it doesn't exist
    logs_dir = os.path.dirname(LOG_FILE)
    if logs_dir and not os.path.exists(logs_dir):
        os.makedirs(logs_dir)

    # Create handlers
    c_handler = logging.StreamHandler()
    f_handler = logging.FileHandler(LOG_FILE)

    # Set levels for handlers
    c_handler.setLevel(logging.INFO)
    f_handler.setLevel(logging.INFO)

    # Create formatters and add to handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    c_handler.setFormatter(formatter)
    f_handler.setFormatter(formatter)

    # Add handlers to the logger
    # Prevent adding duplicate handlers if re-called
    if not logger.handlers:
        logger.addHandler(c_handler)
        logger.addHandler(f_handler)
        logger.propagate = False # Prevent messages from being duplicated in parent loggers

    return logger