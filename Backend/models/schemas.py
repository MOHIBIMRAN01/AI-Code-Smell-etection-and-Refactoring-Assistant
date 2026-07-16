"""Pydantic schemas used by the REST API."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class AnalyzeRepositoryRequest(BaseModel):
    """Incoming request for repository analysis."""

    repository_url: str = Field(..., min_length=8)
    branch: str | None = None
    analysis_label: str | None = None


class FindingResponse(BaseModel):
    """Detected smell information returned to the client."""

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


class AnalysisResponse(BaseModel):
    """Overall repository analysis result."""

    analysis_id: str
    repository_url: str
    repository_name: str
    repository_path: str
    total_java_files: int
    analyzed_classes: int
    findings: list[FindingResponse]
    summary: str
    json_report_path: str | None = None
    pdf_report_path: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ReportLinks(BaseModel):
    """Report download links for the UI."""

    json_url: str
    pdf_url: str
