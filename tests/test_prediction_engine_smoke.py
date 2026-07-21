from pathlib import Path

from config.settings import Settings
from dataset.loader import DatasetLoader
from metrics.extractor import MetricsExtractor
from models.domain import ClassMetrics
from models.schemas import AnalyzeRepositoryRequest
from parser.java_parser import JavaSourceParser, ParsedJavaFile
from services.cloner import RepositoryCloner
from services.prediction_engine import PredictionEngine
from services.report_generator import ReportGenerator


def test_prediction_engine_can_initialize_offline(tmp_path):
    settings = Settings(
        repositories_dir=tmp_path / "repositories",
        reports_dir=tmp_path / "reports",
        logs_dir=tmp_path / "logs",
        faiss_store_dir=tmp_path / "faiss",
        combined_dataset_path=Path("combined_dataset.json"),
        model_provider="local",
        embedding_provider="local",
        openai_api_key=None,
    )

    engine = PredictionEngine(
        settings=settings,
        cloner=RepositoryCloner(settings.repositories_dir),
        parser=JavaSourceParser(),
        metrics_extractor=MetricsExtractor(),
        dataset_loader=DatasetLoader(settings.combined_dataset_path),
        report_generator=ReportGenerator(settings.reports_dir),
    )

    assert engine.vector_store is not None


def test_prediction_engine_defers_commit_history_for_smell_free_classes(tmp_path):
    settings = Settings(
        repositories_dir=tmp_path / "repositories",
        reports_dir=tmp_path / "reports",
        logs_dir=tmp_path / "logs",
        faiss_store_dir=tmp_path / "faiss",
        combined_dataset_path=Path("combined_dataset.json"),
        model_provider="local",
        embedding_provider="local",
        openai_api_key=None,
    )

    engine = PredictionEngine(
        settings=settings,
        cloner=RepositoryCloner(settings.repositories_dir),
        parser=JavaSourceParser(),
        metrics_extractor=MetricsExtractor(),
        dataset_loader=DatasetLoader(settings.combined_dataset_path),
        report_generator=ReportGenerator(settings.reports_dir),
    )

    repository_path = tmp_path / "repo"
    repository_path.mkdir()
    java_file = repository_path / "Example.java"
    java_file.write_text("class Example {}\n", encoding="utf-8")

    parsed_file = ParsedJavaFile(
        file_path=str(java_file),
        source_code="class Example {}\n",
        classes=[
            ClassMetrics(
                name="Example",
                file_path=str(java_file),
                line_count=1,
                method_count=0,
                field_count=0,
                import_count=0,
                comment_lines=0,
                blank_lines=0,
            )
        ],
        import_count=0,
        loc=1,
        comment_lines=0,
        blank_lines=0,
        parsing_errors=[],
    )

    engine.cloner.clone = lambda repository_url, branch=None: repository_path  # type: ignore[assignment]
    engine._discover_java_files = lambda repo_path: [java_file]  # type: ignore[assignment]
    engine.parser.parse_file = lambda file_path: parsed_file  # type: ignore[assignment]
    engine.metrics_extractor.evaluate_class = lambda class_metrics: class_metrics  # type: ignore[assignment]
    engine.metrics_extractor.get_smell_candidates = lambda class_metrics: []  # type: ignore[assignment]

    commit_history_calls = {"count": 0}

    def fail_commit_history(*args, **kwargs):
        commit_history_calls["count"] += 1
        raise AssertionError("commit history should not be fetched when there are no smell candidates")

    engine._analyze_commit_history = fail_commit_history  # type: ignore[assignment]
    engine.report_generator.generate = lambda result: (tmp_path / "report.json", tmp_path / "report.pdf")  # type: ignore[assignment]

    result = engine.analyze(AnalyzeRepositoryRequest(repository_url=str(repository_path)))

    assert commit_history_calls["count"] == 0
    assert result.findings == []
