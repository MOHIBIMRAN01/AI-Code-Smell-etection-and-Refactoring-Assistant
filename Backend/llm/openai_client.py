"""OpenAI LLM adapter."""

from __future__ import annotations

import json
from typing import Any

from llm.base import BaseLLMService, LLMRequest, LLMResponse
from llm.local_client import LocalLLMService


class OpenAILLMService(BaseLLMService):
    """OpenAI-backed response generator with a deterministic fallback."""

    def __init__(self, model_name: str, api_key: str | None, base_url: str | None = None) -> None:
        self.model_name = model_name
        self.api_key = api_key
        self.base_url = base_url
        self._fallback = LocalLLMService()

    def generate(self, request: LLMRequest) -> LLMResponse:
        if not self.api_key:
            return self._fallback.generate(request)

        from openai import OpenAI

        client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        prompt = self._build_prompt(request)
        response = client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": "You are a precise software engineering assistant that returns strict JSON."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )
        content = response.choices[0].message.content or ""
        parsed = self._parse_response(content)
        return LLMResponse(
            explanation=parsed.get("explanation", ""),
            refactoring_suggestions=list(parsed.get("refactoring_suggestions", [])),
            severity=parsed.get("severity", request.severity),
            confidence=float(parsed.get("confidence", 0.75)),
            provider="openai",
        )

    def _build_prompt(self, request: LLMRequest) -> str:
        examples = json.dumps(request.retrieved_examples, indent=2)
        metrics = json.dumps(request.metrics, indent=2)
        history_context = request.history_context or {}
        commit_metadata = history_context.get("commit_metadata") or {}
        commit_messages = history_context.get("commit_messages") or []
        git_diff_summary = history_context.get("git_diff_summary") or []
        history_payload = json.dumps(
            {
                "commit_statistics": commit_metadata,
                "commit_messages": commit_messages,
                "git_diff_summary": git_diff_summary,
                "developer_activity": commit_metadata.get("contributors", []),
                "code_churn": commit_metadata.get("code_churn"),
                "lines_added": commit_metadata.get("lines_added"),
                "lines_deleted": commit_metadata.get("lines_deleted"),
            },
            indent=2,
        )
        source_code = request.source_code or ""

        return (
            f"You are a software engineering assistant analyzing Java code for code smells.\n"
            f"Task: detect code smells, use commit history as supporting evidence, explain the smell, suggest refactoring, and provide a confidence score.\n"
            f"Write refactoring suggestions that are specific to this file and class; avoid repeating the same generic advice across different files.\n"
            f"Ground each suggestion in the actual source code, metrics, and class structure when possible.\n"
            f"Smell type: {request.smell_type}\n"
            f"Class: {request.class_name}\n"
            f"File: {request.file_path}\n"
            f"Severity hint: {request.severity}\n"
            f"Context summary: {request.context_summary}\n"
            f"Current Java source code:\n{source_code}\n"
            f"Metrics: {metrics}\n"
            f"Commit history context: {history_payload}\n"
            f"Retrieved FAISS examples: {examples}\n"
            "Return strict JSON with keys: explanation, refactoring_suggestions, severity, confidence."
        )

    def _parse_response(self, content: str) -> dict[str, Any]:
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return {"explanation": content, "refactoring_suggestions": [], "severity": None, "confidence": 0.5}
