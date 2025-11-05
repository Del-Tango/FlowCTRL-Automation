"""
Logging configuration and utilities
"""

import logging
import logging.handlers
import sys

from pathlib import Path
from typing import Optional


def setup_logging(
    log_file: Path,
    log_name: str = "FlowCTRL",
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    timestamp_format: str = "%H:%M:%S",
    debug_mode: bool = False,
) -> logging.Logger:
    """Setup logging configuration"""

    # Create log directory if it doesn't exist
    log_file.parent.mkdir(parents=True, exist_ok=True)

    # Get logger
    logger = logging.getLogger(log_name)

    # Set log level
    if debug_mode:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    # Clear existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Create formatter
    formatter = logging.Formatter(log_format, timestamp_format)

    # File handler - always create this
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB per file
        backupCount=5  # 5 backups
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console handler - only add if not in silence mode
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Prevent propagation to root logger
    logger.propagate = False

    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance"""
    return logging.getLogger(name)


class ConsoleOutput:
    """Console output utilities with formatting"""

    @staticmethod
    def info(message: str):
        """Print info message"""
        print(f"[ INFO ]: {message}")

    @staticmethod
    def error(message: str):
        """Print error message"""
        print(f"[ ERROR ]: {message}")

    @staticmethod
    def warning(message: str):
        """Print warning message"""
        print(f"[ WARNING ]: {message}")

    @staticmethod
    def debug(message: str):
        """Print debug message"""
        print(f"[ DEBUG ]: {message}")

    @staticmethod
    def ok(message: str):
        """Print success message"""
        print(f"[ OK ]: {message}")

    @staticmethod
    def nok(message: str):
        """Print failure message"""
        print(f"[ NOK ]: {message}")

    @staticmethod
    def banner(message: str):
        """Print banner message"""
        print(message)


# CODE DUMP

#       print(f"\n{'='*60}")
#       print(f"{'='*60}\n")

#   def setup_logging(
#       log_file: Path,
#       log_name: str = "FlowCTRL",
#       log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
#       timestamp_format: str = "%H:%M:%S",
#       debug_mode: bool = False,
#   ) -> logging.Logger:
#       """Setup logging configuration"""

#       # Create log directory if it doesn't exist
#       log_file.parent.mkdir(parents=True, exist_ok=True)

#       # Get logger
#       logger = logging.getLogger(log_name)

#       # Set log level
#       if debug_mode:
#           logger.setLevel(logging.DEBUG)
#       else:
#           logger.setLevel(logging.INFO)

#       # Clear existing handlers
#       for handler in logger.handlers[:]:
#           logger.removeHandler(handler)

#       # Create formatter
#       formatter = logging.Formatter(log_format, timestamp_format)

#       # File handler
#       file_handler = logging.handlers.RotatingFileHandler(
#           log_file, maxBytes=10 * 1024 * 1024, backupCount=5  # 10MB per file, 5 backups
#       )
#       file_handler.setFormatter(formatter)
#       logger.addHandler(file_handler)

#       # Console handler
#       console_handler = logging.StreamHandler()
#       console_handler.setFormatter(formatter)
#       logger.addHandler(console_handler)

#       return logger

