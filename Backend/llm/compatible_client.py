"""OpenAI-compatible LLM adapter for providers such as Qwen and Llama gateways."""

from __future__ import annotations

from llm.openai_client import OpenAILLMService


class OpenAICompatibleLLMService(OpenAILLMService):
    """Adapter for any OpenAI-compatible chat API endpoint."""
