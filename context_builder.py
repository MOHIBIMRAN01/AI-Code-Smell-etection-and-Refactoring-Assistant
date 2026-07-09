"""Build a unified evolution-aware context payload for smell analysis."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Sequence

from commit_analyzer import CommitInfo
from metadata_parser import CommitMetadata, MetadataParser


@dataclass(slots=True)
class EvolutionContext:
    """Merged context used by the prediction engine and LLM prompt builder."""

    source_code: str | None = None
    source_file: str | None = None
    commit_metadata: CommitMetadata | None = None
    commit_messages: list[str] = field(default_factory=list)
    git_diff_summary: list[str] = field(default_factory=list)
    retrieved_examples: list[dict[str, Any]] = field(default_factory=list)
    raw_commit_history: list[CommitInfo] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Return a serializable view of the evolution context."""

        return {
            "source_file": self.source_file,
            "source_code": self.source_code,
            "commit_metadata": self.commit_metadata.to_dict() if self.commit_metadata else None,
            "commit_messages": self.commit_messages,
            "git_diff_summary": self.git_diff_summary,
            "retrieved_examples": self.retrieved_examples,
            "raw_commit_history": [
                {
                    "hash": commit.hash,
                    "author": commit.author,
                    "message": commit.message,
                    "date": commit.date.isoformat() if commit.date else None,
                    "modified_files": commit.modified_files,
                    "lines_added": commit.lines_added,
                    "lines_deleted": commit.lines_deleted,
                }
                for commit in self.raw_commit_history
            ],
        }


class ContextBuilder:
    """Merge parsed source code, commit history, and retrieval context into one payload."""

    def __init__(self, metadata_parser: MetadataParser | None = None) -> None:
        self.metadata_parser = metadata_parser or MetadataParser()

    def build_context(
        self,
        source_code: str | None,
        commit_history: Sequence[CommitInfo] | None = None,
        retrieved_examples: Sequence[dict[str, Any]] | None = None,
        source_file: str | None = None,
    ) -> EvolutionContext:
        """Construct an evolution-aware context object from available signals."""

        commits = list(commit_history or [])
        metadata = self.metadata_parser.parse(commits) if commits else None
        return EvolutionContext(
            source_code=source_code,
            source_file=source_file,
            commit_metadata=metadata,
            commit_messages=self._collect_commit_messages(commits),
            git_diff_summary=self._summarize_diffs(commits),
            retrieved_examples=list(retrieved_examples or []),
            raw_commit_history=commits,
        )

    def _collect_commit_messages(self, commits: Sequence[CommitInfo]) -> list[str]:
        return [commit.message.strip() for commit in commits if commit.message and commit.message.strip()]

    def _summarize_diffs(self, commits: Sequence[CommitInfo], limit: int = 5) -> list[str]:
        summaries: list[str] = []
        for commit in commits[:limit]:
            files = ", ".join(commit.modified_files[:3]) or "no files"
            summaries.append(
                f"{commit.hash[:8]} | {commit.author} | {commit.message.splitlines()[0] if commit.message else 'No message'} | {files}"
            )
        return summaries
