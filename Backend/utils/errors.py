"""Custom application exceptions."""

from __future__ import annotations


class AppError(Exception):
    """Base class for domain-specific errors."""


class ConfigurationError(AppError):
    """Raised when required configuration is invalid or missing."""


class DatasetError(AppError):
    """Raised when the historical dataset cannot be loaded."""


class CloneError(AppError):
    """Raised when a repository cannot be cloned or accessed."""


class ParseError(AppError):
    """Raised when source code parsing fails."""


class AnalysisError(AppError):
    """Raised when the end-to-end analysis pipeline fails."""


class ReportError(AppError):
    """Raised when a report cannot be generated."""

