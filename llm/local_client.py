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
            confidence=0.72,
            provider="local",
        )
