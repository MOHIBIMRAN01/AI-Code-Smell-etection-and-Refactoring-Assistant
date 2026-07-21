"""Large language model service abstraction."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class LLMRequest:
    """Structured prompt payload for smell explanation and refactoring."""

    smell_type: str
    severity: str
    file_path: str
    class_name: str
    metrics: dict[str, float | int | str]
    retrieved_examples: list[dict[str, str]]
    context_summary: str
    source_code: str | None = None
    history_context: dict[str, Any] | None = None


@dataclass(slots=True)
class LLMResponse:
    """Structured response returned by the LLM service."""

    explanation: str
    refactoring_suggestions: list[str] = field(default_factory=list)
    severity: str | None = None
    confidence: float = 0.0
    provider: str = "local"


class BaseLLMService(ABC):
    """Common interface for all LLM providers."""

    @abstractmethod
    def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate an explanation and refactoring advice."""
