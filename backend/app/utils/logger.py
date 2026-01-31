"""Logging utility module."""

import logging
import sys
from typing import Literal

from app.config import get_settings


def setup_logging(
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] | None = None,
) -> None:
    """Setup application logging configuration.

    Args:
        level: Log level. If None, uses setting from config.
    """
    settings = get_settings()
    log_level = level or settings.log_level

    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level),
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )

    # Reduce noise from third-party libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("playwright").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name.

    Args:
        name: Logger name, typically __name__ of the module.

    Returns:
        Configured logger instance.
    """
    return logging.getLogger(name)
