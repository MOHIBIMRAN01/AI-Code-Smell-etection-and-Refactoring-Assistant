"""Mistral LLM adapter — uses the OpenAI-compatible Mistral API."""

from __future__ import annotations

import json
from typing import Any

from llm.base import BaseLLMService, LLMRequest, LLMResponse
from llm.local_client import LocalLLMService


class MistralLLMService(BaseLLMService):
    """Mistral-backed response generator with a deterministic fallback."""

    MISTRAL_BASE_URL = "https://api.mistral.ai/v1"

    def __init__(self, model_name: str, api_key: str | None) -> None:
        self.model_name = model_name or "mistral-large-latest"
        self.api_key = api_key
        self._fallback = LocalLLMService()

    def generate(self, request: LLMRequest) -> LLMResponse:
        if not self.api_key:
            return self._fallback.generate(request)

        from openai import OpenAI

        client = OpenAI(api_key=self.api_key, base_url=self.MISTRAL_BASE_URL)
        prompt = self._build_prompt(request)

        try:
            response = client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert software engineer specializing in Java code quality analysis. "
                            "You detect code smells, explain them clearly with evidence from the source code and metrics, "
                            "and suggest concrete refactoring steps. Always return strict JSON only — no markdown, no extra text."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
                max_tokens=1024,
            )
            content = response.choices[0].message.content or ""
            parsed = self._parse_response(content)
            return LLMResponse(
                explanation=parsed.get("explanation", ""),
                refactoring_suggestions=list(parsed.get("refactoring_suggestions", [])),
                severity=parsed.get("severity", request.severity),
                confidence=float(parsed.get("confidence", 0.75)),
                provider="mistral",
            )
        except Exception:
            return self._fallback.generate(request)

    def _build_prompt(self, request: LLMRequest) -> str:
        metrics = json.dumps(request.metrics or {}, indent=2)
        examples = json.dumps(request.retrieved_examples or [], indent=2)

        history_context = request.history_context or {}
        commit_metadata = history_context.get("commit_metadata") or {}
        commit_messages = history_context.get("commit_messages") or []
        git_diff_summary = history_context.get("git_diff_summary") or []

        history_payload = json.dumps(
            {
                "commit_statistics": commit_metadata,
                "recent_commit_messages": commit_messages[:10],
                "git_diff_summary": git_diff_summary[:5],
                "code_churn": commit_metadata.get("code_churn"),
                "lines_added": commit_metadata.get("lines_added"),
                "lines_deleted": commit_metadata.get("lines_deleted"),
                "contributors": commit_metadata.get("contributors", []),
            },
            indent=2,
        )

        source_code = request.source_code or ""

        return (
            f"Analyze the following Java class for the code smell: **{request.smell_type}**\n\n"
            f"Class: {request.class_name}\n"
            f"File: {request.file_path}\n"
            f"Severity hint: {request.severity}\n"
            f"Context summary: {request.context_summary}\n\n"
            f"--- Java Source Code ---\n{source_code}\n\n"
            f"--- Measured Metrics ---\n{metrics}\n\n"
            f"--- Git Commit History ---\n{history_payload}\n\n"
            f"--- Similar Examples (from training data) ---\n{examples}\n\n"
            "Based on the actual source code and metrics above, return ONLY a JSON object with these keys:\n"
            "{\n"
            '  "explanation": "<detailed explanation of why this is a code smell, citing specific evidence from the code>",\n'
            '  "refactoring_suggestions": ["<step 1>", "<step 2>", "<step 3>"],\n'
            '  "severity": "<low|medium|high>",\n'
            '  "confidence": <float between 0.0 and 1.0>\n'
            "}"
        )

    def _parse_response(self, content: str) -> dict[str, Any]:
        # Strip markdown fences if present
        content = content.strip()
        if content.startswith("```"):
            lines = content.splitlines()
            content = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return {
                "explanation": content,
                "refactoring_suggestions": [],
                "severity": None,
                "confidence": 0.5,
            }
