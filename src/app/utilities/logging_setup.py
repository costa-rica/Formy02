"""
Loguru configuration for Formy02.
"""

from __future__ import annotations

import atexit
import os
import sys
from datetime import datetime
from pathlib import Path

from loguru import logger

from src.app.utilities import config


def make_daily_or_size_rotation(size_mb: int):
    """Rotate on local-midnight rollover or size overflow."""
    size_bytes = size_mb * 1024 * 1024

    def should_rotate(message, file):
        if file.tell() + len(message) > size_bytes:
            return True
        try:
            file_local_date = datetime.fromtimestamp(os.path.getmtime(file.name)).date()
        except OSError:
            return False
        return message.record["time"].date() > file_local_date

    return should_rotate


def _fatal(message: str) -> None:
    logger.critical(message)
    print(message, file=sys.stderr)
    logger.complete()
    raise RuntimeError(message)


def configure_logging() -> None:
    """Remove default Loguru sink and set up sinks per RUN_ENVIRONMENT."""
    logger.remove()

    env = config.RUN_ENVIRONMENT
    if not config.NAME_APP:
        logger.add(sys.stderr, level="ERROR", backtrace=True, diagnose=True)
        _fatal("FATAL: NAME_APP is missing or empty.")
    if env not in {"development", "testing", "production"}:
        logger.add(sys.stderr, level="ERROR", backtrace=True, diagnose=True)
        _fatal("FATAL: RUN_ENVIRONMENT is missing or invalid.")

    console_format = (
        "<green>{time:HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{module}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    file_format = (
        "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
        "{level: <8} | "
        "{module}:{function}:{line} | "
        "{message}"
    )

    if env in {"development", "testing"}:
        logger.add(
            sys.stdout,
            format=console_format,
            level="DEBUG" if env == "development" else "INFO",
            colorize=True,
            backtrace=True,
            diagnose=True,
            enqueue=env != "development",
        )

    if env in {"testing", "production"}:
        if not config.PATH_TO_LOGS:
            logger.add(sys.stderr, level="ERROR", backtrace=True, diagnose=True)
            _fatal("FATAL: PATH_TO_LOGS is required in testing and production.")

        log_dir = Path(config.PATH_TO_LOGS)
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / f"{config.NAME_APP}-{{time:YYYY-MM-DD}}.log"

        logger.add(
            str(log_file),
            format=file_format,
            level="INFO",
            rotation=make_daily_or_size_rotation(config.LOG_MAX_SIZE_IN_MB),
            retention=config.LOG_MAX_FILES,
            backtrace=True,
            diagnose=True,
            enqueue=True,
        )

    def _handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        logger.opt(exception=(exc_type, exc_value, exc_traceback)).critical(
            "Uncaught exception"
        )

    sys.excepthook = _handle_exception
    atexit.register(logger.complete)
    logger.info(f"{config.NAME_APP} logging initialised | environment={env}")
