"""Clone and manage target repositories."""

from __future__ import annotations

import logging
import re
from pathlib import Path
from urllib.parse import urlparse

from git import Repo

from utils.errors import CloneError
from utils.files import ensure_directory

LOGGER = logging.getLogger(__name__)


class RepositoryCloner:
    """Clone Git repositories into the configured workspace directory."""

    def __init__(self, repository_root: Path) -> None:
        self.repository_root = repository_root
        ensure_directory(repository_root)

    def clone(self, repository_url: str, branch: str | None = None) -> Path:
        """Clone or reuse a repository checkout."""

        repository_name = self._derive_repository_name(repository_url)
        target_path = self.repository_root / repository_name

        try:
            if target_path.exists() and (target_path / ".git").exists():
                LOGGER.info("Reusing existing repository checkout at %s", target_path)
                return target_path

            LOGGER.info("Cloning repository %s into %s", repository_url, target_path)
            if branch:
                Repo.clone_from(repository_url, target_path, branch=branch)
            else:
                Repo.clone_from(repository_url, target_path)
            return target_path
        except Exception as exc:  # pragma: no cover - network and git operations are environment dependent
            raise CloneError(f"Failed to clone repository {repository_url}: {exc}") from exc

    def _derive_repository_name(self, repository_url: str) -> str:
        parsed = urlparse(repository_url)
        if parsed.scheme in {"http", "https", "git", "ssh", "file"}:
            raw_name = Path(parsed.path).name
        else:
            raw_name = Path(repository_url).name

        slug = raw_name.rstrip("/")
        slug = re.sub(r"\.git$", "", slug)
        slug = re.sub(r"[^A-Za-z0-9._-]+", "_", slug)
        return slug or "repository"
