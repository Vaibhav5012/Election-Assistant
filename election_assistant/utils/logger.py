"""Centralized logging configuration for the Election Assistant app.

Provides a factory function that returns a consistently configured
logger with both console and file output.
"""

import logging
import sys
from pathlib import Path


# --- Log File Path ---
_LOG_DIR: Path = Path(__file__).resolve().parent.parent / "logs"
_LOG_FILE: str = "election_assistant.log"

# --- Log Format ---
_LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
_DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"


def get_logger(name: str) -> logging.Logger:
    """Return a configured logger with file and console handlers.

    Args:
        name: The name for the logger, typically ``__name__``.

    Returns:
        A ``logging.Logger`` instance with console and file handlers attached.
    """
    logger = logging.getLogger(name)

    # Avoid adding duplicate handlers on repeated calls
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # --- Console handler (INFO and above) ---
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(
        logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT)
    )
    logger.addHandler(console_handler)

    # --- File handler (DEBUG and above) ---
    _LOG_DIR.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(
        _LOG_DIR / _LOG_FILE, encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(
        logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT)
    )
    logger.addHandler(file_handler)

    return logger
