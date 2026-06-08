"""
Database engine and session management using SQLModel / PostgreSQL.
"""

from __future__ import annotations

from typing import Generator

from sqlmodel import SQLModel, Session, create_engine

from src.app.utilities import config

# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------
DATABASE_URL = (
    "postgresql+psycopg://"
    f"{config.DB_USER}:{config.DB_PASSWORD}"
    f"@{config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}"
)

engine = create_engine(
    DATABASE_URL,
    echo=config.DEBUG,
)


def get_engine():
    """Return the process-wide SQLAlchemy engine."""
    return engine


# ---------------------------------------------------------------------------
# Table creation (called once at startup)
# ---------------------------------------------------------------------------
def create_db_and_tables() -> None:
    """Create all tables defined via SQLModel metadata."""
    # Import models here so their metadata is registered before create_all
    import src.app.models.user  # noqa: F401
    import src.app.models.surveyed_person  # noqa: F401
    import src.app.models.question  # noqa: F401
    import src.app.models.response  # noqa: F401
    import src.app.models.junction  # noqa: F401

    SQLModel.metadata.create_all(engine)


# ---------------------------------------------------------------------------
# Session dependency (use with FastAPI Depends)
# ---------------------------------------------------------------------------
def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
