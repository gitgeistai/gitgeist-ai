# gitgeist/utils/logger.py
import logging
import sys
from pathlib import Path
from typing import Optional

def setup_logger(log_file: Optional[Path] = None, level: str = "INFO") -> logging.Logger:
    """Setup application-wide logging"""
    
    # Create logger
    logger = logging.getLogger("gitgeist")
    logger.setLevel(getattr(logging, level.upper()))
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """Get a logger for a specific module"""
    return logging.getLogger(f"gitgeist.{name}")

def set_log_level(level: str) -> None:
    """Set logging level for all gitgeist loggers"""
    logger = logging.getLogger("gitgeist")
    logger.setLevel(getattr(logging, level.upper()))
    
    # Update console handler level for INFO and above
    for handler in logger.handlers:
        if isinstance(handler, logging.StreamHandler) and handler.stream == sys.stdout:
            if level.upper() in ['DEBUG']:
                handler.setLevel(logging.DEBUG)
            else:
                handler.setLevel(logging.INFO)


