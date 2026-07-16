"""
This module configures the application-wide logging utility.
"""

import logging
import os
import sys

def get_logger(name: str = "ai_task_manager") -> logging.Logger:
    """
    Creates and returns a configured logger instance with both console and file handlers.
    
    Args:
        name (str): Name of the logger.
        
    Returns:
        logging.Logger: The configured Logger object.
    """
    logger = logging.getLogger(name)
    
    # Avoid adding multiple handlers if they are already configured on this logger
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 1. Console (Stream) Handler - logs to stderr
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # 2. File Handler - logs to logs/app.log
        log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logs"))
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "app.log")
        
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
    return logger

# Reusable default logger object
logger = get_logger()
