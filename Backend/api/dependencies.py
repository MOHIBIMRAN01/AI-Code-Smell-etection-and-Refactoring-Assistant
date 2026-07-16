"""Dependency injection container for the FastAPI application."""

from __future__ import annotations

import logging
from functools import lru_cache

from config.settings import Settings, get_settings
from dataset.loader import DatasetLoader
from metrics.extractor import MetricsExtractor
from parser.java_parser import JavaSourceParser
from services.prediction_engine import PredictionEngine
from services.report_generator import ReportGenerator

LOGGER = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_app_settings() -> Settings:
    return get_settings()


@lru_cache(maxsize=1)
def get_prediction_engine() -> PredictionEngine:
    """Lazily instantiate PredictionEngine with deferred git imports."""
    # Import RepositoryCloner only when needed (lazy import)
    # This allows the app to start even if git is not available in the environment
    try:
        from services.cloner import RepositoryCloner
    except ImportError as exc:
        LOGGER.warning(
            "Failed to import RepositoryCloner - git may not be available: %s", exc
        )
        raise
    
    settings = get_app_settings()
    return PredictionEngine(
        settings=settings,
        cloner=RepositoryCloner(),
        parser=JavaSourceParser(),
        metrics_extractor=MetricsExtractor(),
        dataset_loader=DatasetLoader(settings.combined_dataset_path),
        report_generator=ReportGenerator(),
    )
