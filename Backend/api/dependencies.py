"""Dependency injection container for the FastAPI application."""

from __future__ import annotations

from functools import lru_cache

from config.settings import Settings, get_settings
from dataset.loader import DatasetLoader
from metrics.extractor import MetricsExtractor
from parser.java_parser import JavaSourceParser
from services.cloner import RepositoryCloner
from services.prediction_engine import PredictionEngine
from services.report_generator import ReportGenerator


@lru_cache(maxsize=1)
def get_app_settings() -> Settings:
    return get_settings()


@lru_cache(maxsize=1)
def get_prediction_engine() -> PredictionEngine:
    settings = get_app_settings()
    return PredictionEngine(
        settings=settings,
        cloner=RepositoryCloner(),
        parser=JavaSourceParser(),
        metrics_extractor=MetricsExtractor(),
        dataset_loader=DatasetLoader(settings.combined_dataset_path),
        report_generator=ReportGenerator(),
    )
