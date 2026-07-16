from pathlib import Path

from config.settings import Settings
from dataset.loader import DatasetLoader
from metrics.extractor import MetricsExtractor
from parser.java_parser import JavaSourceParser
from services.cloner import RepositoryCloner
from services.prediction_engine import PredictionEngine
from services.report_generator import ReportGenerator


def test_prediction_engine_can_initialize_offline(tmp_path):
    settings = Settings(
        logs_dir=tmp_path / "logs",
        faiss_store_dir=tmp_path / "faiss",
        combined_dataset_path=Path("combined_dataset.json"),
        model_provider="local",
        embedding_provider="local",
        openai_api_key=None,
    )

    engine = PredictionEngine(
        settings=settings,
        cloner=RepositoryCloner(),
        parser=JavaSourceParser(),
        metrics_extractor=MetricsExtractor(),
        dataset_loader=DatasetLoader(settings.combined_dataset_path),
        report_generator=ReportGenerator(),
    )

    assert engine.vector_store is not None
