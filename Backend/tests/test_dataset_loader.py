from pathlib import Path

from dataset.loader import DatasetLoader


def test_dataset_loader_builds_examples_and_documents():
    loader = DatasetLoader(Path("combined_dataset.json"))
    examples = loader.load_examples()
    documents = loader.to_documents()

    assert len(examples) > 0
    assert len(documents) >= len(examples)
    assert examples[0].repository_name
    assert "problematic classes" in documents[0].page_content.lower()
