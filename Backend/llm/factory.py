"""Factory for selecting the active LLM provider."""

from __future__ import annotations

from config.settings import Settings
from llm.base import BaseLLMService
from llm.compatible_client import OpenAICompatibleLLMService
from llm.gemini_client import GeminiLLMService
from llm.groq_client import GroqLLMService
from llm.local_client import LocalLLMService
from llm.mistral_client import MistralLLMService
from llm.openai_client import OpenAILLMService


def build_llm_service(settings: Settings) -> BaseLLMService:
    """Create the configured LLM service."""

    provider = settings.model_provider.lower().strip()
    if provider == "openai":
        return OpenAILLMService(settings.model_name, settings.openai_api_key, settings.openai_base_url)
    if provider == "gemini":
        return GeminiLLMService(settings.gemini_api_key)
    if provider == "groq":
        return GroqLLMService(settings.model_name, settings.groq_api_key)
    if provider == "mistral":
        return MistralLLMService(settings.model_name, settings.mistral_api_key)
    if provider in {"qwen", "llama", "openai-compatible"}:
        base_url = settings.qwen_base_url if provider == "qwen" else settings.llama_base_url
        return OpenAICompatibleLLMService(settings.model_name, settings.openai_api_key, base_url)
    return LocalLLMService()

