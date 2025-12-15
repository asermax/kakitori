"""Logging configuration for kakitori."""

import logging
import sys


logger = logging.getLogger("kakitori")


def setup_logging(verbose: bool = False) -> None:
    """Configure logging for the kakitori CLI.

    Args:
        verbose: If True, enable DEBUG level logging. Otherwise use INFO level.
    """
    level = logging.DEBUG if verbose else logging.INFO

    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))

    logger.setLevel(level)
    logger.addHandler(handler)
    logger.propagate = False
