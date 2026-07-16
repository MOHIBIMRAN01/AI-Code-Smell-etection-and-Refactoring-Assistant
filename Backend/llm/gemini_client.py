"""Gemini LLM adapter with a deterministic fallback."""

from __future__ import annotations

from llm.base import BaseLLMService, LLMRequest, LLMResponse
from llm.local_client import LocalLLMService


class GeminiLLMService(BaseLLMService):
    """Google Gemini integration with a fallback for offline operation."""

    def __init__(self, api_key: str | None) -> None:
        self.api_key = api_key
        self._fallback = LocalLLMService()

    def generate(self, request: LLMRequest) -> LLMResponse:
        if not self.api_key:
            return self._fallback.generate(request)

        import google.generativeai as genai

        genai.configure(api_key=self.api_key)
        model = genai.GenerativeModel("gemini-1.5-pro")
        history_context = request.history_context or {}
        commit_metadata = history_context.get("commit_metadata") or {}
        commit_messages = history_context.get("commit_messages") or []
        git_diff_summary = history_context.get("git_diff_summary") or []
        prompt = (
            f"Return strict JSON for smell {request.smell_type} in {request.class_name}. "
            f"Analyze the current Java source code, commit statistics, commit messages, code churn, lines added, lines deleted, "
            f"developer activity, git diff summary, and retrieved examples. "
            f"Use the commit history as supporting evidence, explain the smell, suggest refactoring, and provide a confidence score. "
            f"Source code: {request.source_code or ''}. "
            f"Metrics: {request.metrics}. "
            f"Commit statistics: {commit_metadata}. "
            f"Commit messages: {commit_messages}. "
            f"Diff summary: {git_diff_summary}. "
            f"Historical examples: {request.retrieved_examples}. "
            f"Context: {request.context_summary}."
        )
        response = model.generate_content(prompt)
        text = getattr(response, "text", "") or ""
        return self._fallback.generate(request) if not text else LLMResponse(
            explanation=text,
            refactoring_suggestions=[
                f"Split {request.class_name} into smaller responsibilities.",
                "Move repeated logic into extracted methods.",
            ],
            severity=request.severity,
            confidence=0.7,
            provider="gemini",
        )
