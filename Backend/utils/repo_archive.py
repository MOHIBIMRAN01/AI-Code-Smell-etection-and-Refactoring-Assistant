"""Archive and extract repository clones as compressed tar.gz bytes."""

from __future__ import annotations

import io
import tarfile
from pathlib import Path


def archive_repository(repository_path: Path) -> bytes:
    """Pack a cloned repository directory into gzip-compressed tar bytes."""
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w:gz") as archive:
        archive.add(repository_path, arcname=repository_path.name)
    return buffer.getvalue()


def extract_repository(archive_bytes: bytes, target_dir: Path) -> Path:
    """Extract a repository archive into *target_dir* and return the repo root path."""
    buffer = io.BytesIO(archive_bytes)
    with tarfile.open(fileobj=buffer, mode="r:gz") as archive:
        archive.extractall(path=target_dir)

    extracted = sorted(target_dir.iterdir())
    if not extracted:
        raise ValueError("Repository archive did not contain any files.")
    return extracted[0]
