"""Logging utilities for the automation framework."""

from functools import cache
import logging
import os

from features.utils.config_manager import get_config

_LOGGER_NAME = "{{PROJECT_NAME}}_logger"


@cache
def get_logger() -> logging.Logger:
    """
    Return the shared, fully-configured application logger.

    The logger writes to both console and a log file.
    """
    logger = logging.getLogger(_LOGGER_NAME)
    logger.setLevel(logging.INFO)

    if logger.hasHandlers():
        return logger

    config = get_config()
    log_file = config.get("log_file_location") or "features/logs/app.log"
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    log_format = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    # File handler
    file_handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")
    file_handler.setFormatter(log_format)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_format)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
