"""Background cleanup for expired repository clones stored in the database."""

from __future__ import annotations

import logging
import threading
from datetime import datetime

from sqlalchemy.orm import Session

from config.database import SessionLocal
from config.settings import Settings
from models.db_models import Analysis

LOGGER = logging.getLogger(__name__)


def purge_expired_repo_clones(db: Session) -> int:
    """Remove expired repository archive blobs from the database."""
    now = datetime.utcnow()
    expired = (
        db.query(Analysis)
        .filter(
            Analysis.repo_archive_blob.isnot(None),
            Analysis.repo_expires_at.isnot(None),
            Analysis.repo_expires_at <= now,
        )
        .all()
    )

    for analysis in expired:
        analysis.repo_archive_blob = None
        analysis.repo_expires_at = None
        if analysis.repository_path.startswith("db://"):
            analysis.repository_path = f"db://purged/{analysis.id}"

    if expired:
        db.commit()
    return len(expired)


class RepoCloneCleanupService:
    """Periodically purge repository clone blobs that exceeded their TTL."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, name="repo-clone-cleanup", daemon=True)
        self._thread.start()
        LOGGER.info(
            "Repository clone cleanup started (TTL=%s min, interval=%s s)",
            self.settings.repo_clone_ttl_minutes,
            self.settings.repo_cleanup_interval_seconds,
        )

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5)

    def _run(self) -> None:
        while not self._stop_event.wait(self.settings.repo_cleanup_interval_seconds):
            db = SessionLocal()
            try:
                purged = purge_expired_repo_clones(db)
                if purged:
                    LOGGER.info("Purged %s expired repository clone(s) from database", purged)
            except Exception:
                LOGGER.exception("Repository clone cleanup failed")
                db.rollback()
            finally:
                db.close()
