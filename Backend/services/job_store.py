"""In-memory async job store for long-running analysis tasks."""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class AnalysisJob:
    job_id: str
    status: JobStatus = JobStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    result: Any = None          # AnalysisResponse dict when completed
    error: str | None = None    # Error message when failed
    repository_url: str = ""


class JobStore:
    """Thread-safe in-memory store for analysis jobs."""

    def __init__(self) -> None:
        self._jobs: dict[str, AnalysisJob] = {}
        self._lock = threading.Lock()

    def create(self, job_id: str, repository_url: str) -> AnalysisJob:
        job = AnalysisJob(job_id=job_id, repository_url=repository_url)
        with self._lock:
            self._jobs[job_id] = job
        return job

    def get(self, job_id: str) -> AnalysisJob | None:
        with self._lock:
            return self._jobs.get(job_id)

    def set_running(self, job_id: str) -> None:
        with self._lock:
            job = self._jobs.get(job_id)
            if job:
                job.status = JobStatus.RUNNING
                job.updated_at = datetime.utcnow()

    def set_completed(self, job_id: str, result: Any) -> None:
        with self._lock:
            job = self._jobs.get(job_id)
            if job:
                job.status = JobStatus.COMPLETED
                job.result = result
                job.updated_at = datetime.utcnow()

    def set_failed(self, job_id: str, error: str) -> None:
        with self._lock:
            job = self._jobs.get(job_id)
            if job:
                job.status = JobStatus.FAILED
                job.error = error
                job.updated_at = datetime.utcnow()

    def cleanup_old_jobs(self, max_age_seconds: int = 3600) -> None:
        """Remove jobs older than max_age_seconds to prevent memory leaks."""
        cutoff = (datetime.utcnow().timestamp() - max_age_seconds)
        with self._lock:
            to_delete = [
                jid for jid, job in self._jobs.items()
                if job.created_at.timestamp() < cutoff
            ]
            for jid in to_delete:
                del self._jobs[jid]


# Singleton shared across the app
_job_store: JobStore | None = None
_store_lock = threading.Lock()


def get_job_store() -> JobStore:
    global _job_store
    if _job_store is None:
        with _store_lock:
            if _job_store is None:
                _job_store = JobStore()
    return _job_store
