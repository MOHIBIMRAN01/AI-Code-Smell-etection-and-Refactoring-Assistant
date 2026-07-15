"""Git commit history analysis utilities for evolution-aware code smell detection."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError

LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class CommitInfo:
    """Normalized representation of a repository commit."""

    hash: str
    author: str
    message: str
    date: datetime | None
    modified_files: list[str] = field(default_factory=list)
    diff: str = ""
    lines_added: int = 0
    lines_deleted: int = 0


class CommitAnalyzer:
    """Inspect Git history for a repository and expose structured commit details."""

    def __init__(self, repository_path: str | Path, max_commits: int | None = None) -> None:
        self.repository_path = Path(repository_path).resolve()
        self.max_commits = max_commits
        self._repo: Repo | None = None

    def analyze_repository(self, target_file: str | None = None) -> list[CommitInfo]:
        """Analyze the repository history, optionally filtering to a specific Java file."""

        repo = self._load_repository()
        commits: list[CommitInfo] = []

        if target_file is not None:
            target_file = self._normalize_path(target_file)

        try:
            if target_file is not None:
                commit_iter = repo.iter_commits(paths=target_file, all=True)
            else:
                commit_iter = repo.iter_commits(all=True)

            for commit in commit_iter:
                if self.max_commits is not None and len(commits) >= self.max_commits:
                    break

                commits.append(self._build_commit_info(repo, commit))
        except GitCommandError as exc:
            LOGGER.warning("Unable to read commit history from %s: %s", self.repository_path, exc)
            return []

        return commits

    def get_commits_for_file(self, java_file: str) -> list[CommitInfo]:
        """Return commits that modified the given Java file."""

        return self.analyze_repository(target_file=java_file)

    def _load_repository(self) -> Repo:
        if self._repo is not None:
            return self._repo

        if not self.repository_path.exists():
            raise ValueError(f"Repository path does not exist: {self.repository_path}")

        try:
            self._repo = Repo(self.repository_path)
            return self._repo
        except InvalidGitRepositoryError as exc:
            raise ValueError(f"{self.repository_path} is not a valid Git repository") from exc

    def _commit_touches_file(self, commit: Any, repo: Repo, target_file: str) -> bool:
        normalized_target = self._normalize_path(target_file)
        if not normalized_target:
            return True

        try:
            file_names = list(getattr(commit.stats, "files", {}).keys())
        except Exception:
            file_names = []

        if not file_names:
            try:
                diff_names = repo.git.diff_tree(commit.hexsha, name_only=True).splitlines()
                file_names = [self._normalize_path(path) for path in diff_names if path]
            except GitCommandError:
                file_names = []

        return any(self._normalize_path(path) == normalized_target for path in file_names)

    def _build_commit_info(self, repo: Repo, commit: Any) -> CommitInfo:
        modified_files = self._collect_modified_files(commit)
        diff = ""
        stats = getattr(commit, "stats", None)
        insertions = 0
        deletions = 0

        if stats is not None:
            totals = getattr(stats, "total", {}) or {}
            insertions = int(totals.get("insertions", 0) or 0)
            deletions = int(totals.get("deletions", 0) or 0)

        return CommitInfo(
            hash=commit.hexsha,
            author=self._extract_author(commit),
            message=commit.message.strip(),
            date=commit.committed_datetime,
            modified_files=modified_files,
            diff=diff,
            lines_added=insertions,
            lines_deleted=deletions,
        )

    def _collect_modified_files(self, commit: Any) -> list[str]:
        try:
            files = getattr(commit.stats, "files", None)
            if files:
                return [self._normalize_path(path) for path in files.keys()]
        except Exception:
            LOGGER.debug("Unable to read modified files from commit %s", getattr(commit, "hexsha", "unknown"))
        return []

    def _collect_diff(self, repo: Repo, commit: Any) -> str:
        try:
            return repo.git.show(commit.hexsha, "--format=", "--no-renames")
        except GitCommandError as exc:
            LOGGER.debug("Unable to fetch diff for commit %s: %s", commit.hexsha, exc)
            return ""

    def _extract_author(self, commit: Any) -> str:
        author = getattr(commit, "author", None)
        if author is None:
            return "unknown"
        return getattr(author, "name", None) or getattr(author, "email", None) or "unknown"

    def _normalize_path(self, path: str | None) -> str:
        if not path:
            return ""
        return str(path).replace("\\", "/").lstrip("./")
