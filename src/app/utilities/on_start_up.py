"""
Startup utilities for database checks.
"""

from __future__ import annotations

from loguru import logger
from sqlmodel import text

from src.app.models.database import create_db_and_tables, engine


def check_database() -> None:
    """Ensure PostgreSQL is reachable and tables exist."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        create_db_and_tables()
        logger.info("Database check passed")
    except Exception as exc:
        logger.critical(f"Database check failed; application startup aborted: {exc}")
        raise
