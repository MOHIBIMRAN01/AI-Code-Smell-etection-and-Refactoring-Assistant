"""REST API route definitions."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from dataclasses import asdict

from api.dependencies import get_app_settings, get_prediction_engine
from config.settings import Settings
from models.schemas import AnalyzeRepositoryRequest, AnalysisResponse, FindingResponse, ReportLinks
from services.prediction_engine import PredictionEngine
from utils.errors import AnalysisError, AppError

router = APIRouter(prefix="/api", tags=["analysis"])


@router.get("/health")
def health_check() -> dict[str, str]:
    """Basic health endpoint."""

    return {"status": "ok"}


@router.post("/analyze", response_model=AnalysisResponse)
def analyze_repository(
    request: AnalyzeRepositoryRequest,
    engine: PredictionEngine = Depends(get_prediction_engine),
) -> AnalysisResponse:
    """Analyze a GitHub repository and return smell findings."""

    try:
        result = engine.analyze(request)
        return AnalysisResponse(
            analysis_id=result.analysis_id,
            repository_url=result.repository_url,
            repository_name=result.repository_name,
            repository_path=result.repository_path,
            total_java_files=result.total_java_files,
            analyzed_classes=result.analyzed_classes,
            findings=[FindingResponse(**asdict(finding)) for finding in result.findings],
            summary=result.summary,
            json_report_path=result.json_report_path,
            pdf_report_path=result.pdf_report_path,
        )
    except AnalysisError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except AppError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/reports/{analysis_id}", response_model=ReportLinks)
def get_report_links(analysis_id: str, settings: Settings = Depends(get_app_settings)) -> ReportLinks:
    """Return report download URLs for a completed analysis."""

    return ReportLinks(
        json_url=f"/api/reports/{analysis_id}/json",
        pdf_url=f"/api/reports/{analysis_id}/pdf",
    )


@router.get("/reports/{analysis_id}/json")
def download_json_report(analysis_id: str, settings: Settings = Depends(get_app_settings)) -> FileResponse:
    """Download the JSON report generated for an analysis run."""

    report_path = settings.reports_dir / f"{analysis_id}.json"
    if not report_path.exists():
        raise HTTPException(status_code=404, detail="JSON report not found")
    return FileResponse(report_path, media_type="application/json", filename=report_path.name)


@router.get("/reports/{analysis_id}/pdf")
def download_pdf_report(analysis_id: str, settings: Settings = Depends(get_app_settings)) -> FileResponse:
    """Download the PDF report generated for an analysis run."""

    report_path = settings.reports_dir / f"{analysis_id}.pdf"
    if not report_path.exists():
        raise HTTPException(status_code=404, detail="PDF report not found")
    return FileResponse(report_path, media_type="application/pdf", filename=report_path.name)
