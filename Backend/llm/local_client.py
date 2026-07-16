"""Deterministic fallback LLM implementation used when no API key is available."""

from __future__ import annotations

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
        suggestions = [
            f"Refactor {request.class_name} into smaller, cohesive units with a single responsibility.",
            "Extract reusable logic into helper classes or methods to reduce coupling.",
            "Introduce tests around the extracted behavior before restructuring the code further.",
        ]
        return LLMResponse(
            explanation=explanation,
            refactoring_suggestions=suggestions,
            severity=request.severity,
            confidence=self._confidence_from_request(request),
            provider="local",
        )

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
