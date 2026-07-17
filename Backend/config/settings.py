"""Application configuration and environment loading."""

from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    """Runtime settings loaded from environment variables and .env files."""

    model_config = SettingsConfigDict(env_file=str(BASE_DIR / ".env"), env_file_encoding="utf-8", extra="ignore")

    app_name: str = "EvolutionSmellAI"
    environment: str = "development"
    api_prefix: str = "/api"
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    frontend_url: str = "http://localhost:3000"

    data_dir: Path = Field(default=BASE_DIR / "data")
    logs_dir: Path = Field(default=BASE_DIR / "logs")
    frontend_dir: Path = Field(default=BASE_DIR / "frontend")
    docs_dir: Path = Field(default=BASE_DIR / "docs")
    combined_dataset_path: Path = Field(default=BASE_DIR / "combined_dataset.json")
    config_file_path: Path = Field(default=BASE_DIR / "config" / "config.yaml")
    faiss_store_dir: Path = Field(default=BASE_DIR / "data" / "faiss_store")

    model_provider: str = "gemini"
    model_name: str = "gemini-1.5-flash"
    embedding_provider: str = "local"
    embedding_model: str = "local"
    default_retrieval_k: int = 5
    max_files_to_analyze: int = 70  # Balanced: enough coverage but faster (was 100)
    max_findings_per_file: int = 5  # Reduced from 10 to speed up analysis
    max_findings_per_repository: int = 30  # Reduced from 50 to focus on critical issues
    max_history_commits_per_file: int = 5  # Reduced from 10 to speed up git analysis
    max_parallel_llm_calls: int = 3  # Run 3 LLM calls in parallel (saves 5-7 min)

    openai_api_key: str | None = None
    openai_base_url: str | None = None
    gemini_api_key: str | None = None
    groq_api_key: str | None = None
    mistral_api_key: str | None = None
    qwen_base_url: str | None = None
    llama_base_url: str | None = None
    allow_network_clone: bool = True
    request_timeout_seconds: int = 900  # Increased to 15 minutes for massive repos like Quarkus
    repo_clone_ttl_minutes: int = 30
    repo_cleanup_interval_seconds: int = 60


def get_settings() -> Settings:
    """Create a fresh settings object."""

    return Settings()
