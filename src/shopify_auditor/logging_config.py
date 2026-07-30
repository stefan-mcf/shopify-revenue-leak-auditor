"""Logging configuration placeholder."""

from __future__ import annotations

import logging


def configure_logging(level: int = logging.INFO) -> None:
    logging.basicConfig(level=level, format="%(levelname)s:%(name)s:%(message)s")
