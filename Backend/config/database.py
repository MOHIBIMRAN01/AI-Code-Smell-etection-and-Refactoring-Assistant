"""Database connection settings using SQLAlchemy."""

import logging
import os
from typing import Generator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker, Session

LOGGER = logging.getLogger(__name__)

# Force SQLite if DATABASE_URL tries to connect to Neon (quota exceeded)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

# If Neon connection string detected, use SQLite instead
if "neon.tech" in DATABASE_URL or "psycopg2" in DATABASE_URL:
    LOGGER.warning("Neon database detected, switching to SQLite")
    DATABASE_URL = "sqlite:///./app.db"

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
    
    # Determine column types based on database dialect
    if engine.dialect.name == "postgresql":
        blob_type = "BYTEA"
        timestamp_type = "TIMESTAMP"
    else:  # SQLite or other databases
        blob_type = "BLOB"
        timestamp_type = "DATETIME"
    
    additions = {
        "repo_archive_blob": blob_type,
        "json_report_blob": blob_type,
        "repo_expires_at": timestamp_type,
    }

    with engine.begin() as connection:
        for column_name, column_type in additions.items():
            if column_name not in existing:
                try:
                    connection.execute(
                        text(f"ALTER TABLE analyses ADD COLUMN {column_name} {column_type}")
                    )
                    LOGGER.info("Added analyses.%s column", column_name)
                except Exception as e:
                    LOGGER.warning("Could not add column %s: %s", column_name, str(e))
