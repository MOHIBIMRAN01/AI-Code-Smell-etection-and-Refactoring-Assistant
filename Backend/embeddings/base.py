"""Embedding service abstractions."""

from __future__ import annotations

from abc import ABC, abstractmethod

from langchain_core.embeddings import Embeddings


class BaseEmbeddingService(Embeddings, ABC):
    """Embedding contract used by the retrieval pipeline."""

    def __call__(self, input: str | list[str]) -> list[float] | list[list[float]]:
        """Support callable-style embedding access used by LangChain internals."""

        if isinstance(input, list):
            return self.embed_documents(input)
        return self.embed_query(input)

    @abstractmethod
    def embed_documents(self, texts: list[str]) -> list[list[float]]:  # type: ignore[override]
        """Embed a batch of documents."""

    @abstractmethod
    def embed_query(self, text: str) -> list[float]:  # type: ignore[override]
        """Embed a single query string."""
