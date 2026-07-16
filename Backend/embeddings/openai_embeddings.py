"""OpenAI embeddings wrapper with a fallback to local deterministic embeddings."""

from __future__ import annotations

from embeddings.base import BaseEmbeddingService
from embeddings.local_embeddings import LocalHashEmbeddingService


class OpenAIEmbeddingService(BaseEmbeddingService):
    """OpenAI embeddings implementation used when credentials are available."""

    def __init__(self, model_name: str, api_key: str | None, base_url: str | None = None) -> None:
        self.model_name = model_name
        self.api_key = api_key
        self.base_url = base_url
        self._fallback = LocalHashEmbeddingService()

    def embed_documents(self, texts: list[str]) -> list[list[float]]:  # type: ignore[override]
        if not self.api_key:
            return self._fallback.embed_documents(texts)
        from langchain_openai import OpenAIEmbeddings

        client = OpenAIEmbeddings(model=self.model_name, api_key=self.api_key, base_url=self.base_url)
        return client.embed_documents(texts)

    def embed_query(self, text: str) -> list[float]:  # type: ignore[override]
        if not self.api_key:
            return self._fallback.embed_query(text)
        from langchain_openai import OpenAIEmbeddings

        client = OpenAIEmbeddings(model=self.model_name, api_key=self.api_key, base_url=self.base_url)
        return client.embed_query(text)
