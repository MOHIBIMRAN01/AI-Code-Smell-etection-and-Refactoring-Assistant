"""Database connection settings using SQLAlchemy."""

import logging
import os
from typing import Generator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker, Session

LOGGER = logging.getLogger(__name__)

# Fetch from environment. We default to sqlite if no DB url is provided (useful for offline testing)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

# For SQLite, we need to disable same_thread check
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args=connect_args
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """Dependency generator for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def migrate_database() -> None:
    """Add new columns to existing tables when the schema evolves."""
    inspector = inspect(engine)
    if not inspector.has_table("analyses"):
        return

    existing = {column["name"] for column in inspector.get_columns("analyses")}
    blob_type = "BYTEA" if engine.dialect.name == "postgresql" else "BLOB"
    additions = {
        "repo_archive_blob": blob_type,
        "json_report_blob": blob_type,
        "repo_expires_at": "TIMESTAMP" if engine.dialect.name == "postgresql" else "DATETIME",
    }

    with engine.begin() as connection:
        for column_name, column_type in additions.items():
            if column_name not in existing:
                connection.execute(
                    text(f"ALTER TABLE analyses ADD COLUMN {column_name} {column_type}")
                )
                LOGGER.info("Added analyses.%s column", column_name)
