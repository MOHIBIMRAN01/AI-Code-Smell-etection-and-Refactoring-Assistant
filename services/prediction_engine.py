"""Repository analysis orchestration pipeline."""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from commit_analyzer import CommitAnalyzer
from config.settings import Settings
from context_builder import ContextBuilder
from dataset.loader import DatasetLoader
from embeddings.local_embeddings import LocalHashEmbeddingService
from embeddings.openai_embeddings import OpenAIEmbeddingService
from llm.base import LLMRequest
from metadata_parser import MetadataParser
from llm.factory import build_llm_service
from metrics.extractor import MetricsExtractor, SmellCandidate
from models.domain import AnalysisResult, Finding
from models.schemas import AnalyzeRepositoryRequest
from parser.java_parser import JavaSourceParser
from rag.vector_store import HistoricalVectorStore
from services.cloner import RepositoryCloner
from services.report_generator import ReportGenerator
from utils.errors import AnalysisError
from utils.files import ensure_directory

LOGGER = logging.getLogger(__name__)


class PredictionEngine:
    """End-to-end analysis engine combining parsing, metrics, retrieval, and LLM reasoning."""

    def __init__(
        self,
        settings: Settings,
        cloner: RepositoryCloner,
        parser: JavaSourceParser,
        metrics_extractor: MetricsExtractor,
        dataset_loader: DatasetLoader,
        report_generator: ReportGenerator,
    ) -> None:
        self.settings = settings
        self.cloner = cloner
        self.parser = parser
        self.metrics_extractor = metrics_extractor
        self.dataset_loader = dataset_loader
        self.report_generator = report_generator
        self.llm_service = build_llm_service(settings)
        self.embedding_service = self._build_embeddings()
        self.vector_store = self._build_vector_store()
        self.metadata_parser = MetadataParser()
        self.context_builder = ContextBuilder(self.metadata_parser)

    def analyze(self, request: AnalyzeRepositoryRequest) -> AnalysisResult:
        """Run the full analysis pipeline for the provided repository URL."""

        analysis_id = f"analysis_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid4().hex[:8]}"
        try:
            repository_path = self.cloner.clone(request.repository_url, branch=request.branch)
            java_files = self._discover_java_files(repository_path)
            if not java_files:
                raise AnalysisError(
                    "No Java files were found in the repository. This tool currently only supports Java repositories."
                )
            findings: list[Finding] = []
            analyzed_classes = 0
            max_findings = self.settings.max_findings_per_repository

            for file_path in java_files[: self.settings.max_files_to_analyze]:
                relative_file_path = file_path.relative_to(repository_path).as_posix()
                commit_history = self._analyze_commit_history(repository_path, relative_file_path)
                parsed_file = self.parser.parse_file(file_path)
                for class_metrics in parsed_file.classes:
                    analyzed_classes += 1
                    evaluated_class = self.metrics_extractor.evaluate_class(class_metrics)
                    smell_candidates = self._select_smells(evaluated_class)
                    for smell_candidate in smell_candidates:
                        if len(findings) >= max_findings:
                            break
                        findings.append(
                            self._build_finding(
                                smell_candidate=smell_candidate,
                                class_metrics=evaluated_class,
                                parsed_file_path=parsed_file.file_path,
                                source_code=parsed_file.source_code,
                                commit_history=commit_history,
                            )
                        )
                    if len(findings) >= max_findings:
                        break
                if len(findings) >= max_findings:
                    break

            summary = self._build_summary(
                findings,
                len(java_files),
                analyzed_classes,
                limited=len(java_files) > self.settings.max_files_to_analyze or len(findings) >= max_findings,
            )
            result = AnalysisResult(
                analysis_id=analysis_id,
                repository_url=request.repository_url,
                repository_name=repository_path.name,
                repository_path=str(repository_path),
                total_java_files=len(java_files),
                analyzed_classes=analyzed_classes,
                findings=findings,
                summary=summary,
            )
            json_path, pdf_path = self.report_generator.generate(result)
            result.json_report_path = str(json_path)
            result.pdf_report_path = str(pdf_path)
            return result
        except Exception as exc:
            raise AnalysisError(f"Repository analysis failed: {exc}") from exc

    def _build_embeddings(self):
        if self.settings.embedding_provider.lower() == "openai" and self.settings.openai_api_key:
            return OpenAIEmbeddingService(self.settings.embedding_model, self.settings.openai_api_key, self.settings.openai_base_url)
        return LocalHashEmbeddingService()

    def _build_vector_store(self) -> HistoricalVectorStore:
        documents = self.dataset_loader.to_documents()
        ensure_directory(self.settings.faiss_store_dir)
        return HistoricalVectorStore.load_or_build(documents, self.embedding_service, self.settings.faiss_store_dir)

    def _discover_java_files(self, repository_path: Path) -> list[Path]:
        return sorted(repository_path.rglob("*.java"))

    def _select_smells(self, class_metrics) -> list[SmellCandidate]:
        # Prefer detailed candidates computed by the MetricsExtractor
        smell_candidates = self.metrics_extractor.get_smell_candidates(class_metrics)

        if not smell_candidates:
            smell_candidates = [
                SmellCandidate(
                    smell_type="Potential Structural Smell",
                    severity="low",
                    confidence=0.5,
                    rationale="The class does not cross the main heuristic thresholds, but the retrieval context still warrants review.",
                )
            ]
        return smell_candidates[: self.settings.max_findings_per_file]

    def _build_finding(
        self,
        smell_candidate: SmellCandidate,
        class_metrics,
        parsed_file_path: str,
        source_code: str | None = None,
        commit_history=None,
    ) -> Finding:
        query = (
            f"{smell_candidate.smell_type} for Java class {class_metrics.name} with {class_metrics.line_count} lines, "
            f"{class_metrics.method_count} methods, {class_metrics.field_count} fields, and score {class_metrics.complexity_score}."
        )
        retrieved_documents = self.vector_store.retrieve(query, k=self.settings.default_retrieval_k)
        retrieved_examples = [
            {
                "repository_name": document.metadata.get("repository_name", "unknown"),
                "version": document.metadata.get("version", "unknown"),
                "problematic_classes": str(document.metadata.get("problematic_classes", "")),
                "highly_problematic_classes": str(document.metadata.get("highly_problematic_classes", "")),
                "summary": document.page_content,
            }
            for document in retrieved_documents
        ]
        history_context = self._build_history_context(
            source_code=source_code,
            source_file=parsed_file_path,
            commit_history=commit_history,
            retrieved_examples=retrieved_examples,
        )

        llm_request = LLMRequest(
            smell_type=smell_candidate.smell_type,
            severity=smell_candidate.severity,
            file_path=parsed_file_path,
            class_name=class_metrics.name,
            source_code=source_code,
            metrics={
                "line_count": class_metrics.line_count,
                "method_count": class_metrics.method_count,
                "field_count": class_metrics.field_count,
                "import_count": class_metrics.import_count,
                "complexity_score": class_metrics.complexity_score,
            },
            retrieved_examples=retrieved_examples,
            context_summary=smell_candidate.rationale,
            history_context=history_context,
        )
        llm_response = self.llm_service.generate(llm_request)
        return Finding(
            file_path=parsed_file_path,
            class_name=class_metrics.name,
            smell_type=smell_candidate.smell_type,
            severity=llm_response.severity or smell_candidate.severity,
            confidence=max(smell_candidate.confidence, llm_response.confidence),
            rationale=llm_response.explanation,
            metrics={
                "line_count": class_metrics.line_count,
                "method_count": class_metrics.method_count,
                "field_count": class_metrics.field_count,
                "import_count": class_metrics.import_count,
                "complexity_score": class_metrics.complexity_score,
                "history_context": history_context,
            },
            refactoring_suggestions=llm_response.refactoring_suggestions,
            similar_examples=retrieved_examples,
            llm_provider=llm_response.provider,
        )

    def _analyze_commit_history(self, repository_path: Path, relative_file_path: str) -> list:
        try:
            analyzer = CommitAnalyzer(
                repository_path=repository_path,
                max_commits=self.settings.max_history_commits_per_file,
            )
            return analyzer.get_commits_for_file(relative_file_path)
        except Exception as exc:
            LOGGER.debug("Git history analysis was skipped for %s: %s", relative_file_path, exc)
            return []

    def _build_history_context(self, source_code: str | None, source_file: str, commit_history, retrieved_examples: list[dict[str, object]]) -> dict[str, object]:
        if not commit_history and not retrieved_examples:
            return {}

        context = self.context_builder.build_context(
            source_code=source_code,
            commit_history=commit_history,
            retrieved_examples=retrieved_examples,
            source_file=source_file,
        )
        return context.to_dict()

    def _build_summary(
        self,
        findings: list[Finding],
        total_java_files: int,
        analyzed_classes: int,
        limited: bool = False,
    ) -> str:
        smell_count = len(findings)
        if not total_java_files:
            return "No Java files were found in the repository."
        if smell_count == 0:
            return f"Analyzed {total_java_files} Java files and {analyzed_classes} classes. No major smells crossed the thresholds."

        base_summary = (
            f"Analyzed {total_java_files} Java files and {analyzed_classes} classes. "
            f"Detected {smell_count} smell findings across the repository."
        )
        if limited:
            return f"{base_summary} The result set was limited to the first {self.settings.max_findings_per_repository} findings for performance reasons."
        return base_summary
