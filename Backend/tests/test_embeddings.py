from embeddings.local_embeddings import LocalHashEmbeddingService


def test_local_hash_embedding_service_is_callable():
    service = LocalHashEmbeddingService()

    query_vector = service("hello world")
    document_vectors = service(["hello world", "another document"])

    assert isinstance(query_vector, list)
    assert len(query_vector) == 256
    assert isinstance(document_vectors, list)
    assert len(document_vectors) == 2
    assert len(document_vectors[0]) == 256
