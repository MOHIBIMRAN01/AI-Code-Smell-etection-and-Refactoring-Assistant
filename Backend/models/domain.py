"""Internal domain models used by the analysis pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class HistoricalExample:
    """Historical record retrieved from the dataset."""

    repository_name: str
    repository_link: str | None
    version: str
    summary: str
    problematic_classes: float
    highly_problematic_classes: float
    lines_of_code: float | None = None
    classes: float | None = None
    packages: float | None = None
    external_packages: float | None = None
    external_classes: float | None = None
    commits: float | None = None
    branches: float | None = None
    releases: float | None = None
    contributors: float | None = None
    watches: float | None = None
    stars: float | None = None
    forks: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class Document:
    """Lightweight retrieval document used by the FAISS pipeline."""

    page_content: str
    id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class MethodMetrics:
    """Metrics derived for a single Java method."""

    name: str
    line_count: int
    parameter_count: int
    complexity: int
    start_line: int | None = None
    end_line: int | None = None


@dataclass(slots=True)
class ClassMetrics:
    """Metrics derived for a single Java class."""

    name: str
    file_path: str
    line_count: int
    method_count: int
    field_count: int
    import_count: int
    comment_lines: int
    blank_lines: int
    method_metrics: list[MethodMetrics] = field(default_factory=list)
    complexity_score: float = 0.0
    smell_candidates: list[str] = field(default_factory=list)


@dataclass(slots=True)
class Finding:
    """A detected smell together with its explanation and recommendation."""

    file_path: str
    class_name: str
    smell_type: str
    severity: str
    confidence: float
    rationale: str
    metrics: dict[str, Any]
    refactoring_suggestions: list[str]
    similar_examples: list[dict[str, Any]]
    llm_provider: str


@dataclass(slots=True)
class AnalysisResult:
    """Full repository analysis result."""

    analysis_id: str
    repository_url: str
    repository_name: str
    repository_path: str
    total_java_files: int
    analyzed_classes: int
    findings: list[Finding]
    summary: str
    json_bytes: bytes | None = None
    pdf_bytes: bytes | None = None
    repo_archive_bytes: bytes | None = None
