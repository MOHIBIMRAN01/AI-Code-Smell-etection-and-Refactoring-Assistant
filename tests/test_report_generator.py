import json

from models.domain import AnalysisResult, Finding
from services.report_generator import ReportGenerator


def test_report_generator_includes_refactoring_suggestions(tmp_path):
    report_generator = ReportGenerator(tmp_path)
    result = AnalysisResult(
        analysis_id="analysis-123",
        repository_url="https://github.com/example/repo",
        repository_name="example-repo",
        repository_path=str(tmp_path / "example-repo"),
        total_java_files=1,
        analyzed_classes=1,
        summary="One smell was detected.",
        findings=[
            Finding(
                file_path=str(tmp_path / "example-repo" / "src" / "main" / "java" / "demo" / "Example.java"),
                class_name="Example",
                smell_type="Large Class",
                severity="medium",
                confidence=0.82,
                rationale="The class contains too many responsibilities.",
                metrics={"line_count": 240},
                refactoring_suggestions=[
                    "Extract cohesive methods into helper classes.",
                    "Split unrelated state into smaller value objects.",
                ],
                similar_examples=[],
                llm_provider="local",
            )
        ],
    )

    json_path, pdf_path = report_generator.generate(result)

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["findings"][0]["refactoring_suggestions"] == [
        "Extract cohesive methods into helper classes.",
        "Split unrelated state into smaller value objects.",
    ]

    html_content = (tmp_path / f"{result.analysis_id}.html").read_text(encoding="utf-8")
    normalized_html = html_content.replace("\u200b", "")
    assert "Refactoring Suggestions" in html_content
    assert "Extract cohesive methods into helper classes." in html_content
    assert "src/main/java/demo/Example.java" in normalized_html
    assert str(tmp_path) not in normalized_html
    assert pdf_path.exists()
