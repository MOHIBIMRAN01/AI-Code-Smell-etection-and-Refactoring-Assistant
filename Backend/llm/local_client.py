"""Deterministic fallback LLM implementation used when no API key is available."""

from __future__ import annotations

from pathlib import Path
from collections.abc import Sequence

from llm.base import BaseLLMService, LLMRequest, LLMResponse


class LocalLLMService(BaseLLMService):
    """Rule-based local response generator."""

    def generate(self, request: LLMRequest) -> LLMResponse:
        history_note = ""
        if request.history_context:
            metadata = request.history_context.get("commit_metadata") or {}
            if metadata.get("total_commits"):
                history_note = (
                    f" Evolution signals from the repository history suggest {metadata.get('total_commits')} relevant commits, "
                    f"{metadata.get('code_churn', 0)} units of churn, and a hotspot score of {metadata.get('hotspot_score', 0)}."
                )

        explanation = (
            f"{request.smell_type} was detected in {request.class_name} because the measured metrics suggest "
            f"{request.context_summary.lower()}. The current source structure, the repository history, and the retrieved examples "
            f"all point to the same pattern of increasing problem density at comparable scale.{history_note}"
        )
        suggestions = self._build_suggestions(request)
        return LLMResponse(
            explanation=explanation,
            refactoring_suggestions=suggestions,
            severity=request.severity,
            confidence=self._confidence_from_request(request),
            provider="local",
        )

    def _build_suggestions(self, request: LLMRequest) -> list[str]:
        smell_type = (request.smell_type or "").strip().lower()
        class_name = request.class_name or "this class"
        metrics = request.metrics if isinstance(request.metrics, dict) else {}
        line_count = int(metrics.get("line_count", 0) or 0)
        method_count = int(metrics.get("method_count", 0) or 0)
        field_count = int(metrics.get("field_count", 0) or 0)
        complexity_score = float(metrics.get("complexity_score", 0) or 0)
        file_path = Path((request.file_path or "").replace("\\", "/"))
        folder_path = file_path.parent.as_posix()
        location_label = folder_path if folder_path and folder_path != "." else "the repository root"

        if smell_type == "large class":
            return self._unique([
                f"Split {class_name} in {location_label} into smaller classes around the main responsibilities visible in {file_path.as_posix()}.",
                f"Move the {method_count} methods and {field_count} fields in {class_name} into focused collaborator classes where the ownership is clearer.",
                f"Extract shared behavior from {class_name} into reusable helpers, then add tests for the extracted pieces before further splitting the code under {location_label}.",
            ])

        if smell_type == "god class":
            return self._unique([
                f"Break {class_name} in {location_label} into service, domain, and helper responsibilities instead of keeping all orchestration in {file_path.as_posix()}.",
                f"Move behavior that depends on the {line_count} lines and complexity score {complexity_score:.2f} into smaller components with explicit ownership inside {location_label}.",
                f"Extract the highest-risk workflows from {class_name} first, then cover them with tests before removing the remaining duplication.",
            ])

        if smell_type == "long method":
            return self._unique([
                f"Extract the nested branches and repeated steps from the long method in {class_name} under {location_label} into named helper methods.",
                f"Introduce guard clauses and early returns so the control flow in {file_path.as_posix()} becomes easier to follow.",
                f"Add tests around each extracted branch before shortening the original method further.",
            ])

        if smell_type == "data class":
            return self._unique([
                f"Move behavior that belongs to {class_name} into the class instead of keeping it only as state in {file_path.as_posix()}.",
                f"Encapsulate the {field_count} fields behind intention-revealing methods or a value-object boundary.",
                f"Reduce direct field exposure in {location_label} and add tests for the new domain methods before changing the state layout.",
            ])

        if smell_type == "long parameter list":
            return self._unique([
                f"Introduce a parameter object or builder for the method signatures in {class_name} so related inputs are grouped together.",
                f"Replace the long argument lists in {file_path.as_posix()} with smaller abstractions that reflect the real domain concepts.",
                f"Keep the old call sites covered by tests while migrating them to the new parameter object.",
            ])

        if smell_type == "large class" and complexity_score >= 60:
            return self._unique([
                f"Split {class_name} by the responsibilities implied by its high complexity score in {file_path.as_posix()}.",
                f"Extract the most frequently changed logic into separate classes or services.",
                f"Add focused tests around the extracted units before moving the remaining code.",
            ])

        return self._unique([
            f"Refactor {class_name} in {file_path.as_posix()} by isolating the part of the code that most strongly matches the detected smell.",
            f"Extract the reusable logic into smaller helpers or collaborators so the file becomes easier to maintain.",
            f"Add tests around the extracted behavior under {location_label} before making the next structural change.",
        ])

    def _unique(self, suggestions: Sequence[str]) -> list[str]:
        seen: set[str] = set()
        result: list[str] = []
        for suggestion in suggestions:
            normalized = suggestion.strip()
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            result.append(normalized)
        return result

    def _confidence_from_request(self, request: LLMRequest) -> float:
        """Compute a basic confidence for local responses based on severity and metrics."""
        base = 0.5
        sev_map = {"low": 0.0, "medium": 0.15, "high": 0.25}
        sev_boost = sev_map.get((request.severity or "").lower(), 0.0)
        complexity = 0.0
        if request.metrics and isinstance(request.metrics, dict):
            complexity = float(request.metrics.get("complexity_score", 0))
        # small influence from complexity (scaled)
        complexity_boost = min(0.15, complexity / 200.0)
        conf = base + sev_boost + complexity_boost
        return round(min(0.99, conf), 2)
