"""Clone and manage target repositories."""

from __future__ import annotations

import logging
import os
import re
import shutil
import stat
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

try:
    from git import InvalidGitRepositoryError, Repo
except ImportError as exc:
    LOGGER = logging.getLogger(__name__)
    LOGGER.error(
        "GitPython is not available or git executable not found in PATH. "
        "Repository cloning will not work: %s", exc
    )
    raise

from utils.errors import CloneError

LOGGER = logging.getLogger(__name__)


def _force_remove_readonly(func, path, excinfo):
    """Error handler for shutil.rmtree on Windows read-only / locked files."""
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception:
        pass


def _kill_git_processes() -> None:
    """Terminate any lingering git.exe processes on Windows."""
    if sys.platform != "win32":
        return
    try:
        subprocess.run(
            ["taskkill", "/F", "/IM", "git.exe"],
            capture_output=True,
            timeout=5,
        )
        time.sleep(0.5)
    except Exception as exc:
        LOGGER.debug("Could not kill git processes: %s", exc)


def _safe_rmtree(target_path: Path, retries: int = 3, delay: float = 1.0) -> bool:
    """Remove a directory tree robustly on Windows with retry logic."""
    for attempt in range(retries):
        try:
            shutil.rmtree(target_path, onerror=_force_remove_readonly)
            if not target_path.exists():
                return True
        except Exception as exc:
            LOGGER.debug("rmtree attempt %d failed: %s", attempt + 1, exc)

        if attempt == 0:
            _kill_git_processes()
        time.sleep(delay)

    # Last-resort: Windows rd /s /q
    if sys.platform == "win32":
        try:
            subprocess.run(
                ["cmd", "/c", "rd", "/s", "/q", str(target_path)],
                capture_output=True,
                timeout=30,
            )
            if not target_path.exists():
                return True
        except Exception as exc:
            LOGGER.debug("rd /s /q fallback failed: %s", exc)

    return not target_path.exists()


def _is_valid_repo(path: Path) -> bool:
    """Return True if *path* contains a usable (non-corrupted) git repository."""
    if not path.exists() or not (path / ".git").exists():
        return False
    try:
        repo = Repo(path)
        _ = repo.head.commit
        files = [p for p in path.iterdir() if p.name != ".git"]
        return len(files) > 0
    except (InvalidGitRepositoryError, Exception):
        return False


class RepositoryCloner:
    """Clone Git repositories into caller-supplied directories.

    The class no longer manages a persistent on-disk repositories cache —
    callers are responsible for providing (and cleaning up) the target
    directory.  Use ``clone_into`` to clone directly into a given path.
    """

    def clone_into(
        self, repository_url: str, target_dir: Path, branch: str | None = None
    ) -> Path:
        """Clone *repository_url* into *target_dir* and return the checkout path.

        The repository is placed in a sub-directory named after the repo slug
        inside *target_dir*, e.g. ``target_dir/guava``.
        """
        repository_name = self._derive_repository_name(repository_url)
        target_path = target_dir / repository_name

        # Remove any leftover partial clone at this location.
        if target_path.exists() and not _is_valid_repo(target_path):
            LOGGER.info("Removing incomplete clone at %s", target_path)
            _safe_rmtree(target_path)

        LOGGER.info("Cloning repository %s into %s", repository_url, target_path)
        try:
            clone_kwargs: dict = {}
            if branch:
                clone_kwargs["branch"] = branch
            Repo.clone_from(repository_url, target_path, **clone_kwargs)
            return target_path
        except Exception as exc:
            if target_path.exists():
                _safe_rmtree(target_path)
            raise CloneError(
                f"Failed to clone repository {repository_url}: {exc}"
            ) from exc

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
