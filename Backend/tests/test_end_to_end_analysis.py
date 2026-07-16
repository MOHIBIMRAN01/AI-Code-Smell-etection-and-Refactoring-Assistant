from pathlib import Path

from git import Repo

from config.settings import Settings
from dataset.loader import DatasetLoader
from metrics.extractor import MetricsExtractor
from models.schemas import AnalyzeRepositoryRequest
from parser.java_parser import JavaSourceParser
from services.cloner import RepositoryCloner
from services.prediction_engine import PredictionEngine
from services.report_generator import ReportGenerator
from utils.repo_archive import extract_repository


def test_end_to_end_repository_analysis(tmp_path):
    repo_src = tmp_path / "sample-java-repo"
    source_dir = repo_src / "src"
    source_dir.mkdir(parents=True, exist_ok=True)
    (source_dir / "Sample.java").write_text(
        """package demo;

public class Sample {
    private int a;
    private int b;
    private int c;
    private int d;

    public void longMethod(int x, int y, int z, int q, int w) {
        if (x > 0) {
            for (int i = 0; i < 10; i++) {
                while (y > 0) {
                    System.out.println(i + y + z + q + w);
                    y--;
                }
            }
        }
    }
}
""",
        encoding="utf-8",
    )

    repo = Repo.init(repo_src)
    repo.git.config("user.email", "test@example.com")
    repo.git.config("user.name", "Test User")
    repo.index.add(["src/Sample.java"])
    repo.index.commit("initial commit")

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

    result = engine.analyze(AnalyzeRepositoryRequest(repository_url=str(repo_src)))

    assert result.total_java_files == 1
    assert result.analyzed_classes == 1
    assert result.findings
    assert result.findings[0].metrics.get("history_context") is not None
    assert result.findings[0].metrics["history_context"].get("commit_metadata") is not None
    assert result.findings[0].metrics["history_context"]["commit_metadata"].get("total_commits") == 1
    assert result.json_bytes
    assert result.pdf_bytes
    assert result.repo_archive_bytes
    assert result.repository_path.startswith("db://")

    extracted_repo = extract_repository(result.repo_archive_bytes, tmp_path / "extracted")
    assert (extracted_repo / "src" / "Sample.java").exists()
