"""Parse Git commit data into useful evolution metrics for smell analysis."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Sequence

from commit_analyzer import CommitInfo


@dataclass(slots=True)
class CommitMetadata:
    """Aggregated commit statistics for a Java file or repository."""

    total_commits: int
    commit_frequency: float
    code_churn: int
    lines_added: int
    lines_deleted: int
    contributors: list[str] = field(default_factory=list)
    last_modified_date: datetime | None = None
    recent_commit_messages: list[str] = field(default_factory=list)
    hotspot_score: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation."""

        return {
            "total_commits": self.total_commits,
            "commit_frequency": self.commit_frequency,
            "code_churn": self.code_churn,
            "lines_added": self.lines_added,
            "lines_deleted": self.lines_deleted,
            "contributors": self.contributors,
            "last_modified_date": self.last_modified_date.isoformat() if self.last_modified_date else None,
            "recent_commit_messages": self.recent_commit_messages,
            "hotspot_score": self.hotspot_score,
        }


class MetadataParser:
    """Transform raw commit history into structural evolution statistics."""

    def parse(self, commits: Sequence[CommitInfo]) -> CommitMetadata:
        """Build summary metrics for the supplied commit history."""

        ordered_commits = [commit for commit in commits if commit is not None]
        if not ordered_commits:
            return CommitMetadata(
                total_commits=0,
                commit_frequency=0.0,
                code_churn=0,
                lines_added=0,
                lines_deleted=0,
                contributors=[],
                last_modified_date=None,
                recent_commit_messages=[],
                hotspot_score=0.0,
            )

        ordered_commits = sorted(ordered_commits, key=lambda item: item.date or datetime.min.replace(tzinfo=timezone.utc))
        total_commits = len(ordered_commits)
        lines_added = sum(commit.lines_added for commit in ordered_commits)
        lines_deleted = sum(commit.lines_deleted for commit in ordered_commits)
        code_churn = lines_added + lines_deleted
        contributors = sorted({commit.author for commit in ordered_commits if commit.author})
        last_modified_date = max((commit.date for commit in ordered_commits if commit.date), default=None)
        recent_commit_messages = [commit.message.strip() for commit in ordered_commits[-5:] if commit.message.strip()]
        commit_frequency = self._calculate_commit_frequency(ordered_commits)
        hotspot_score = self._calculate_hotspot_score(total_commits, code_churn, commit_frequency, contributors, last_modified_date)

        return CommitMetadata(
            total_commits=total_commits,
            commit_frequency=commit_frequency,
            code_churn=code_churn,
            lines_added=lines_added,
            lines_deleted=lines_deleted,
            contributors=contributors,
            last_modified_date=last_modified_date,
            recent_commit_messages=recent_commit_messages,
            hotspot_score=hotspot_score,
        )

    def _calculate_commit_frequency(self, commits: Sequence[CommitInfo]) -> float:
        if not commits:
            return 0.0

        dates = [commit.date for commit in commits if commit.date]
        if not dates:
            return float(len(commits))

        first_date = min(dates)
        last_date = max(dates)
        span_days = (last_date - first_date).total_seconds() / 86400.0
        if span_days <= 0:
            return float(len(commits))
        return round(len(commits) / span_days, 2)

    def _calculate_hotspot_score(
        self,
        total_commits: int,
        code_churn: int,
        commit_frequency: float,
        contributors: Sequence[str],
        last_modified_date: datetime | None,
    ) -> float:
        if total_commits == 0:
            return 0.0

        recency_factor = 1.0
        if last_modified_date is not None:
            age_days = (datetime.now(timezone.utc) - last_modified_date).days
            if age_days > 180:
                recency_factor = 0.5
            elif age_days > 90:
                recency_factor = 0.75

        churn_component = min(code_churn / max(total_commits, 1), 20.0) * 0.4
        frequency_component = min(commit_frequency, 10.0) * 0.5
        contributor_component = min(len(contributors), 5) * 0.7
        score = churn_component + frequency_component + contributor_component + recency_factor
        return round(min(score, 100.0), 2)
