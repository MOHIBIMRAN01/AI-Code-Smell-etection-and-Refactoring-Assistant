"""REST API route definitions."""

from __future__ import annotations

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Response, Header
from sqlalchemy.orm import Session

from api.dependencies import get_prediction_engine, get_app_settings
from models.schemas import AnalyzeRepositoryRequest, AnalysisResponse, FindingResponse, ReportLinks
from services.prediction_engine import PredictionEngine
from utils.errors import AnalysisError, AppError

from config.database import get_db
from models.db_models import Analysis, Finding

router = APIRouter(prefix="/api", tags=["analysis"])

def get_user_id(x_user_id: str = Header(..., alias="X-User-ID")) -> str:
    """Dependency helper to retrieve the client's persistent UUID from the request headers."""
    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing X-User-ID client identification header"
        )
    return x_user_id

@router.get("/health")
def health_check() -> dict[str, str]:
    """Basic health endpoint."""
    return {"status": "ok"}

# Authenticated analyses list
@router.get("/analyses", response_model=list[AnalysisResponse])
def get_user_analyses(
    user_id: str = Depends(get_user_id),
    db: Session = Depends(get_db)
):
    """List all analyses run by the client's UUID."""
    analyses = db.query(Analysis).filter(Analysis.user_id == user_id).order_by(Analysis.created_at.desc()).all()
    
    response = []
    for a in analyses:
        findings_list = [
            FindingResponse(
                file_path=f.file_path,
                class_name=f.class_name,
                smell_type=f.smell_type,
                severity=f.severity,
                confidence=f.confidence,
                rationale=f.rationale,
                metrics=f.metrics,
                refactoring_suggestions=f.refactoring_suggestions,
                similar_examples=f.similar_examples,
                llm_provider=f.llm_provider
            ) for f in a.findings
        ]
        response.append(
            AnalysisResponse(
                analysis_id=a.id,
                repository_url=a.repository_url,
                repository_name=a.repository_name,
                repository_path=a.repository_path,
                total_java_files=a.total_java_files,
                analyzed_classes=a.analyzed_classes,
                findings=findings_list,
                summary=a.summary,
                json_report_path=None,
                pdf_report_path=None,
                created_at=a.created_at
            )
        )
    return response

@router.post("/analyze", response_model=AnalysisResponse)
def analyze_repository(
    request: AnalyzeRepositoryRequest,
    engine: PredictionEngine = Depends(get_prediction_engine),
    user_id: str = Depends(get_user_id),
    db: Session = Depends(get_db),
) -> AnalysisResponse:
    """Analyze a GitHub repository and return smell findings."""
    try:
        result = engine.analyze(request)
        settings = get_app_settings()
        repo_expires_at = datetime.utcnow() + timedelta(minutes=settings.repo_clone_ttl_minutes)

        # Persist analysis, findings, reports, and temporary repo clone in the database.
        db_analysis = Analysis(
            id=result.analysis_id,
            user_id=user_id,
            repository_url=result.repository_url,
            repository_name=result.repository_name,
            repository_path=result.repository_path,
            total_java_files=result.total_java_files,
            analyzed_classes=result.analyzed_classes,
            summary=result.summary,
            repo_archive_blob=result.repo_archive_bytes,
            json_report_blob=result.json_bytes,
            pdf_report_blob=result.pdf_bytes,
            repo_expires_at=repo_expires_at,
            created_at=datetime.utcnow()
        )
        db.add(db_analysis)

        for finding in result.findings:
            db_finding = Finding(
                analysis_id=result.analysis_id,
                file_path=finding.file_path,
                class_name=finding.class_name,
                smell_type=finding.smell_type,
                severity=finding.severity,
                confidence=finding.confidence,
                rationale=finding.rationale,
                metrics=finding.metrics,
                refactoring_suggestions=finding.refactoring_suggestions,
                similar_examples=finding.similar_examples,
                llm_provider=finding.llm_provider
            )
            db.add(db_finding)

        db.commit()

        findings_response = [
            FindingResponse(
                file_path=f.file_path,
                class_name=f.class_name,
                smell_type=f.smell_type,
                severity=f.severity,
                confidence=f.confidence,
                rationale=f.rationale,
                metrics=f.metrics,
                refactoring_suggestions=f.refactoring_suggestions,
                similar_examples=f.similar_examples,
                llm_provider=f.llm_provider
            ) for f in result.findings
        ]

        return AnalysisResponse(
            analysis_id=result.analysis_id,
            repository_url=result.repository_url,
            repository_name=result.repository_name,
            repository_path=result.repository_path,
            total_java_files=result.total_java_files,
            analyzed_classes=result.analyzed_classes,
            findings=findings_response,
            summary=result.summary,
            json_report_path=None,
            pdf_report_path=None,
            created_at=db_analysis.created_at
        )

    except AnalysisError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except AppError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

@router.get("/reports/{analysis_id}", response_model=ReportLinks)
def get_report_links(
    analysis_id: str, 
    user_id: str = Depends(get_user_id),
    db: Session = Depends(get_db)
) -> ReportLinks:
    """Return report download URLs for a completed analysis."""
    # Verify ownership
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id, Analysis.user_id == user_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found or access denied")

    return ReportLinks(
        json_url=f"/api/reports/{analysis_id}/json",
        pdf_url=f"/api/reports/{analysis_id}/pdf",
    )

@router.get("/reports/{analysis_id}/data", response_model=AnalysisResponse)
def get_report_data(
    analysis_id: str,
    user_id: str = Depends(get_user_id),
    db: Session = Depends(get_db)
) -> AnalysisResponse:
    """Get the full analysis details from the database."""
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id, Analysis.user_id == user_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found or access denied")

    findings = [
        FindingResponse(
            file_path=f.file_path,
            class_name=f.class_name,
            smell_type=f.smell_type,
            severity=f.severity,
            confidence=f.confidence,
            rationale=f.rationale,
            metrics=f.metrics,
            refactoring_suggestions=f.refactoring_suggestions,
            similar_examples=f.similar_examples,
            llm_provider=f.llm_provider
        ) for f in analysis.findings
    ]

    return AnalysisResponse(
        analysis_id=analysis.id,
        repository_url=analysis.repository_url,
        repository_name=analysis.repository_name,
        repository_path=analysis.repository_path,
        total_java_files=analysis.total_java_files,
        analyzed_classes=analysis.analyzed_classes,
        findings=findings,
        summary=analysis.summary,
        json_report_path=None,
        pdf_report_path=None,
        created_at=analysis.created_at
    )

@router.get("/reports/{analysis_id}/json")
def download_json_report(
    analysis_id: str, 
    user_id: str = Depends(get_user_id),
    db: Session = Depends(get_db)
) -> Response:
    """Download the JSON report generated for an analysis run."""
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id, Analysis.user_id == user_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found or access denied")

    if analysis.json_report_blob:
        return Response(
            content=analysis.json_report_blob,
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename=report-{analysis_id}.json"}
        )

    import json
    data = {
        "analysis_id": analysis.id,
        "repository_url": analysis.repository_url,
        "repository_name": analysis.repository_name,
        "repository_path": analysis.repository_path,
        "total_java_files": analysis.total_java_files,
        "analyzed_classes": analysis.analyzed_classes,
        "summary": analysis.summary,
        "findings": [
            {
                "file_path": f.file_path,
                "class_name": f.class_name,
                "smell_type": f.smell_type,
                "severity": f.severity,
                "confidence": f.confidence,
                "rationale": f.rationale,
                "metrics": f.metrics,
                "refactoring_suggestions": f.refactoring_suggestions,
                "similar_examples": f.similar_examples,
                "llm_provider": f.llm_provider
            } for f in analysis.findings
        ]
    }
    
    json_str = json.dumps(data, indent=2)
    return Response(
        content=json_str,
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename=report-{analysis_id}.json"}
    )

@router.get("/reports/{analysis_id}/pdf")
def download_pdf_report(
    analysis_id: str, 
    user_id: str = Depends(get_user_id),
    db: Session = Depends(get_db)
) -> Response:
    """Download the PDF report generated for an analysis run."""
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id, Analysis.user_id == user_id).first()
    if not analysis or not analysis.pdf_report_blob:
        raise HTTPException(status_code=404, detail="PDF report not found or access denied")

    return Response(
        content=analysis.pdf_report_blob,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=report-{analysis_id}.pdf"}
    )
