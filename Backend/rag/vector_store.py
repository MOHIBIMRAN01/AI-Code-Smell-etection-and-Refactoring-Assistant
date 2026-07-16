"""FAISS vector store wrapper for historical code smell examples."""

from __future__ import annotations

from pathlib import Path

from langchain_community.vectorstores import FAISS

from embeddings.base import BaseEmbeddingService
from models.domain import Document


class HistoricalVectorStore:
    """Thin wrapper around a FAISS index used for retrieval."""

    def __init__(self, vectorstore: FAISS, documents: list[Document]) -> None:
        self.vectorstore = vectorstore
        self.documents = documents

    @classmethod
    def build(cls, documents: list[Document], embeddings: BaseEmbeddingService) -> "HistoricalVectorStore":
        vectorstore = FAISS.from_documents(documents, embeddings)
        return cls(vectorstore=vectorstore, documents=documents)

    @classmethod
    def load_or_build(
        cls,
        documents: list[Document],
        embeddings: BaseEmbeddingService,
        storage_dir: Path,
    ) -> "HistoricalVectorStore":
        index_file = storage_dir / "index.faiss"
        metadata_file = storage_dir / "index.pkl"
        if index_file.exists() and metadata_file.exists():
            vectorstore = FAISS.load_local(str(storage_dir), embeddings, allow_dangerous_deserialization=True)
            return cls(vectorstore=vectorstore, documents=documents)

        storage_dir.mkdir(parents=True, exist_ok=True)
        vectorstore = FAISS.from_documents(documents, embeddings)
        vectorstore.save_local(str(storage_dir))
        return cls(vectorstore=vectorstore, documents=documents)

    def retrieve(self, query: str, k: int = 5) -> list[Document]:
        """Return the most similar historical documents."""

        return self.vectorstore.similarity_search(query, k=k)
