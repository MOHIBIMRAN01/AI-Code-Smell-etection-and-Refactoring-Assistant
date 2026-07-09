"""Load and normalize the historical dataset used as retrieval knowledge."""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any

from models.domain import Document, HistoricalExample
from utils.errors import DatasetError
from utils.files import read_json


def _to_float(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        if value != value:
            return None
        return float(value)
    if isinstance(value, str):
        cleaned = value.replace(",", "").strip()
        if not cleaned:
            return None
        try:
            return float(cleaned)
        except ValueError:
            return None
    return None


class DatasetLoader:
    """Parse combined_dataset.json and turn it into searchable documents."""

    def __init__(self, dataset_path: Path) -> None:
        self.dataset_path = dataset_path

    def load_examples(self) -> list[HistoricalExample]:
        """Load normalized historical examples."""

        if not self.dataset_path.exists():
            raise DatasetError(f"Dataset not found at {self.dataset_path}")

        payload = read_json(self.dataset_path)
        examples: list[HistoricalExample] = []

        for version_record in payload.get("versions", []):
            repository_name = str(version_record.get("Repository name", "Unknown repository")).strip()
            version = str(version_record.get("Version", "unknown")).strip()
            summary = self._build_summary(version_record)
            examples.append(
                HistoricalExample(
                    repository_name=repository_name,
                    repository_link=None,
                    version=version,
                    summary=summary,
                    problematic_classes=_to_float(version_record.get("Number of problematic classes")) or 0.0,
                    highly_problematic_classes=_to_float(version_record.get("Number of highly problematic classes")) or 0.0,
                    lines_of_code=_to_float(version_record.get("Lines of code")),
                    classes=_to_float(version_record.get("Number of classes")),
                    packages=_to_float(version_record.get("Number of packages")),
                    external_packages=_to_float(version_record.get("Number of external packages")),
                    external_classes=_to_float(version_record.get("Number of external classes")),
                    commits=_to_float(version_record.get("  Commits  ")),
                    metadata=dict(version_record),
                )
            )

        for repository_record in payload.get("repositories", []):
            repository_name = str(repository_record.get("Repository name", "Unknown repository")).strip()
            repository_link = repository_record.get("Repository link")
            summary = self._build_repository_summary(repository_record)
            examples.append(
                HistoricalExample(
                    repository_name=repository_name,
                    repository_link=str(repository_link) if repository_link else None,
                    version="repository-overview",
                    summary=summary,
                    problematic_classes=0.0,
                    highly_problematic_classes=0.0,
                    commits=_to_float(repository_record.get("Commits")),
                    branches=_to_float(repository_record.get("Branches")),
                    releases=_to_float(repository_record.get("Number of releases")),
                    contributors=_to_float(repository_record.get("Contributors")),
                    watches=_to_float(repository_record.get("Watches")),
                    stars=_to_float(repository_record.get("Stars")),
                    forks=_to_float(repository_record.get("Forks")),
                    metadata=dict(repository_record),
                )
            )

        return examples

    def to_documents(self) -> list[Document]:
        """Convert the historical examples to LangChain documents."""

        documents: list[Document] = []
        for index, example in enumerate(self.load_examples()):
            documents.append(
                Document(
                    page_content=example.summary,
                    id=f"historical-example-{index}",
                    metadata={
                        "repository_name": example.repository_name,
                        "version": example.version,
                        "problematic_classes": example.problematic_classes,
                        "highly_problematic_classes": example.highly_problematic_classes,
                        "repository_link": example.repository_link,
                        **{k: v for k, v in asdict(example).items() if k != "summary"},
                    },
                )
            )
        return documents

    def _build_summary(self, record: dict[str, Any]) -> str:
        return (
            f"Repository {record.get('Repository name', 'Unknown')} version {record.get('Version', 'unknown')} "
            f"has {record.get('Lines of code', 'n/a')} lines of code, {record.get('Number of classes', 'n/a')} classes, "
            f"{record.get('Number of problematic classes', 'n/a')} problematic classes, and "
            f"{record.get('Number of highly problematic classes', 'n/a')} highly problematic classes."
        )

    def _build_repository_summary(self, record: dict[str, Any]) -> str:
        return (
            f"Repository {record.get('Repository name', 'Unknown')} at {record.get('Repository link', 'n/a')} "
            f"has {record.get('Commits', 'n/a')} commits, {record.get('Branches', 'n/a')} branches, "
            f"{record.get('Number of releases', 'n/a')} releases, {record.get('Contributors', 'n/a')} contributors, "
            f"{record.get('Stars', 'n/a')} stars, and {record.get('Forks', 'n/a')} forks."
        )
