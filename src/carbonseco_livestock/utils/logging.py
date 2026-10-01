"""Structured logging helpers for operational diagnostics."""

from __future__ import annotations

import logging
import os


def get_logger(name: str = "carbonseco_livestock") -> logging.Logger:
    """Return a module logger configured once for console output."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        level_name = os.environ.get("CARBONSECO_LOG_LEVEL", "INFO").upper()
        level = getattr(logging, level_name, logging.INFO)
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
        )
        logger.addHandler(handler)
        logger.setLevel(level)
        logger.propagate = False
    return logger
