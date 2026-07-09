"""Deterministic local embeddings for offline execution and tests."""

from __future__ import annotations

import math
import re
from collections import Counter

from embeddings.base import BaseEmbeddingService


class LocalHashEmbeddingService(BaseEmbeddingService):
    """A lightweight hashing-based embedding implementation."""

    def __init__(self, dimension: int = 256) -> None:
        self.dimension = dimension

    def embed_documents(self, texts: list[str]) -> list[list[float]]:  # type: ignore[override]
        return [self._embed_text(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:  # type: ignore[override]
        return self._embed_text(text)

    def _embed_text(self, text: str) -> list[float]:
        tokens = re.findall(r"[A-Za-z0-9_]+", text.lower())
        counts = Counter(tokens)
        vector = [0.0] * self.dimension
        for token, count in counts.items():
            index = abs(hash(token)) % self.dimension
            vector[index] += float(count)
        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / norm for value in vector]
