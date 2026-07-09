"""Generate JSON, HTML, and PDF reports for an analysis run."""

from __future__ import annotations

import html
from datetime import datetime
from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from models.domain import AnalysisResult, Finding
from utils.errors import ReportError
from utils.files import ensure_directory, write_json

def _soft_wrap(text: str | None, for_pdf: bool = False) -> str:
    """Insert soft wrap opportunities into long tokens so PDF/HTML can wrap.

    For HTML output we insert zero-width spaces so links stay intact but can wrap.
    For PDF output ReportLab fonts often lack zero-width glyphs; use a normal
    space after separators so ReportLab can break the line without rendering
    unknown-glyph boxes.
    """
    if text is None:
        return ""
    s = str(text)
    if for_pdf:
        # Insert a normal space after common separators to allow ReportLab to wrap
        for sep in ['/', '.', '-', '_', '?', '&']:
            s = s.replace(sep, sep + ' ')
    else:
        # Use zero-width space for HTML so visual content doesn't get extra spaces
        for sep in ['/', '.', '-', '_', '?', '&']:
            s = s.replace(sep, sep + '\u200b')
    return s


class ReportGenerator:
    """Persist the analysis output as JSON, HTML, and PDF."""

    def __init__(self, reports_dir: Path) -> None:
        self.reports_dir = reports_dir
        ensure_directory(reports_dir)

    def generate(self, result: AnalysisResult) -> tuple[Path, Path]:
        """Generate report formats and return the JSON and PDF paths."""

        json_path = self.reports_dir / f"{result.analysis_id}.json"
        pdf_path = self.reports_dir / f"{result.analysis_id}.pdf"
        html_path = self.reports_dir / f"{result.analysis_id}.html"

        try:
            write_json(json_path, self._result_to_dict(result, html_path))
            self._build_pdf(pdf_path, result)
            self._build_html(html_path, result)
            return json_path, pdf_path
        except Exception as exc:  # pragma: no cover - file generation failures are environment dependent
            raise ReportError(f"Unable to generate reports: {exc}") from exc

    def _result_to_dict(self, result: AnalysisResult, html_path: Path) -> dict[str, object]:
        return {
            "analysis_id": result.analysis_id,
            "repository_url": result.repository_url,
            "repository_name": result.repository_name,
            "repository_path": result.repository_path,
            "total_java_files": result.total_java_files,
            "analyzed_classes": result.analyzed_classes,
            "summary": result.summary,
            "html_report_path": str(html_path),
            "findings": [self._finding_to_dict(finding) for finding in result.findings],
        }

    def _finding_to_dict(self, finding: Finding) -> dict[str, object]:
        return {
            "file_path": finding.file_path,
            "class_name": finding.class_name,
            "smell_type": finding.smell_type,
            "severity": finding.severity,
            "confidence": finding.confidence,
            "rationale": finding.rationale,
            "metrics": finding.metrics,
            "refactoring_suggestions": finding.refactoring_suggestions,
            "similar_examples": finding.similar_examples,
            "llm_provider": finding.llm_provider,
        }

    def _extract_commit_history_summary(self, result: AnalysisResult) -> dict[str, Any]:
        history_blocks: list[dict[str, Any]] = []
        raw_history_counts: list[int] = []
        for finding in result.findings:
            history_context = finding.metrics.get("history_context") if isinstance(finding.metrics, dict) else None
            if not isinstance(history_context, dict):
                continue
            commit_metadata = history_context.get("commit_metadata")
            if isinstance(commit_metadata, dict):
                history_blocks.append(commit_metadata)
            # If commit_metadata is not present, fall back to raw_commit_history length
            raw_history = history_context.get("raw_commit_history")
            if isinstance(raw_history, list):
                raw_history_counts.append(len(raw_history))

        if not history_blocks and not raw_history_counts:
            return {
                "total_commits": 0,
                "commit_frequency": 0.0,
                "last_modified": "Not available",
                "code_churn": 0,
                "lines_added": 0,
                "lines_deleted": 0,
                "top_contributors": [],
                "recent_commit_messages": [],
                "hotspot_score": 0.0,
            }

        # Prefer explicit commit metadata when available; otherwise use raw history counts
        if history_blocks:
            total_commits = max(int(block.get("total_commits", 0) or 0) for block in history_blocks)
        else:
            total_commits = max(raw_history_counts) if raw_history_counts else 0
        commit_frequency = max(float(block.get("commit_frequency", 0.0) or 0.0) for block in history_blocks)
        code_churn = sum(int(block.get("code_churn", 0) or 0) for block in history_blocks)
        lines_added = sum(int(block.get("lines_added", 0) or 0) for block in history_blocks)
        lines_deleted = sum(int(block.get("lines_deleted", 0) or 0) for block in history_blocks)
        hotspot_score = max(float(block.get("hotspot_score", 0.0) or 0.0) for block in history_blocks)

        dates = []
        for block in history_blocks:
            value = block.get("last_modified_date")
            if isinstance(value, str) and value:
                try:
                    dates.append(datetime.fromisoformat(value.replace("Z", "+00:00")))
                except ValueError:
                    continue

        contributors = sorted({contributor for block in history_blocks for contributor in block.get("contributors", []) if contributor})
        messages = [message for block in history_blocks for message in block.get("recent_commit_messages", []) if message]

        return {
            "total_commits": total_commits,
            "commit_frequency": round(commit_frequency, 2),
            "last_modified": self._format_date(max(dates, default=None)),
            "code_churn": code_churn,
            "lines_added": lines_added,
            "lines_deleted": lines_deleted,
            "top_contributors": contributors[:5],
            "recent_commit_messages": messages[:5],
            "hotspot_score": round(hotspot_score, 2),
        }

    def _format_date(self, value: datetime | None) -> str:
        if not value:
            return "Not available"
        return value.strftime("%Y-%m-%d %H:%M")

    def _build_pdf(self, pdf_path: Path, result: AnalysisResult) -> None:
        styles = getSampleStyleSheet()
        title_style = styles["Title"]
        heading_style = ParagraphStyle(name="Heading2", parent=styles["Heading2"], textColor=colors.HexColor("#0f172a"), spaceBefore=8, spaceAfter=6)
        body_style = ParagraphStyle(name="Body", parent=styles["BodyText"], leading=12, spaceAfter=6)
        meta_style = ParagraphStyle(name="Meta", parent=styles["BodyText"], leading=10, textColor=colors.HexColor("#475569"), spaceAfter=4)

        document = SimpleDocTemplate(
            str(pdf_path),
            pagesize=A4,
            leftMargin=18 * mm,
            rightMargin=18 * mm,
            topMargin=16 * mm,
            bottomMargin=16 * mm,
        )

        story = [Paragraph("EvolutionSmellAI Report", title_style), Spacer(1, 8)]
        story.append(Paragraph(f"Repository: {result.repository_name}", body_style))
        story.append(Paragraph(f"Repository URL: {result.repository_url}", body_style))
        story.append(Paragraph(f"Summary: {result.summary}", body_style))
        story.append(Spacer(1, 8))

        history_summary = self._extract_commit_history_summary(result)
        story.append(Paragraph("Commit History Analysis", heading_style))
        cell_style = ParagraphStyle(name="TableCell", parent=body_style, fontSize=8, leading=10, wordWrap="CJK")
        header_cell_style = ParagraphStyle(name="TableHeaderCell", parent=body_style, fontSize=8, leading=10, wordWrap="CJK")
        history_rows = [
            [Paragraph(html.escape("Total commits"), header_cell_style), Paragraph(html.escape(_soft_wrap(str(history_summary["total_commits"]), for_pdf=True)), cell_style)],
            [Paragraph(html.escape("Commit frequency"), header_cell_style), Paragraph(html.escape(_soft_wrap(f"{history_summary['commit_frequency']:.2f}/day", for_pdf=True)), cell_style)],
            [Paragraph(html.escape("Last modified"), header_cell_style), Paragraph(html.escape(_soft_wrap(str(history_summary["last_modified"]), for_pdf=True)), cell_style)],
            [Paragraph(html.escape("Code churn"), header_cell_style), Paragraph(html.escape(_soft_wrap(str(history_summary["code_churn"]), for_pdf=True)), cell_style)],
            [Paragraph(html.escape("Lines added"), header_cell_style), Paragraph(html.escape(_soft_wrap(str(history_summary["lines_added"]), for_pdf=True)), cell_style)],
            [Paragraph(html.escape("Lines deleted"), header_cell_style), Paragraph(html.escape(_soft_wrap(str(history_summary["lines_deleted"]), for_pdf=True)), cell_style)],
            [Paragraph(html.escape("Top contributors"), header_cell_style), Paragraph(html.escape(_soft_wrap(", ".join(history_summary["top_contributors"]) or "Not available", for_pdf=True)), cell_style)],
            [Paragraph(html.escape("Recent commit messages"), header_cell_style), Paragraph(html.escape(_soft_wrap("; ".join(history_summary["recent_commit_messages"]) or "Not available", for_pdf=True)), cell_style)],
            [Paragraph(html.escape("Hotspot score"), header_cell_style), Paragraph(html.escape(_soft_wrap(str(history_summary["hotspot_score"]), for_pdf=True)), cell_style)],
        ]
        history_table = Table(history_rows, repeatRows=1, colWidths=[45 * mm, 110 * mm])
        history_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#111827")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#64748b")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("WORDWRAP", (0, 0), (-1, -1), "CJK"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f8fafc")),
                    ("BACKGROUND", (1, 1), (-1, -1), colors.HexColor("#f8fafc")),
                ]
            )
        )
        story.append(history_table)
        story.append(Spacer(1, 10))

        if not result.findings:
            story.append(Paragraph("No smell findings were detected in this repository.", body_style))
            document.build(story)
            return

        story.append(Paragraph("Findings", heading_style))
        data = [["File", "Class", "Smell", "Severity", "Confidence"]]
        for finding in result.findings:
            data.append([
                Paragraph(html.escape(_soft_wrap(str(finding.file_path), for_pdf=True)), meta_style),
                Paragraph(html.escape(_soft_wrap(str(finding.class_name), for_pdf=True)), meta_style),
                Paragraph(html.escape(_soft_wrap(str(finding.smell_type), for_pdf=True)), meta_style),
                Paragraph(html.escape(_soft_wrap(str(finding.severity), for_pdf=True)), meta_style),
                Paragraph(html.escape(_soft_wrap(f"{finding.confidence:.2f}", for_pdf=True)), meta_style),
            ])

        table = Table(
            data,
            repeatRows=1,
            colWidths=[70 * mm, 30 * mm, 30 * mm, 20 * mm, 20 * mm],
        )
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#111827")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#64748b")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f8fafc")),
                ]
            )
        )
        story.append(table)
        document.build(story)

    def _build_html(self, html_path: Path, result: AnalysisResult) -> None:
        history_summary = self._extract_commit_history_summary(result)
        findings_rows = "".join(
            f"<tr><td>{html.escape(_soft_wrap(str(finding.file_path)))}</td><td>{html.escape(_soft_wrap(str(finding.class_name)))}</td><td>{html.escape(_soft_wrap(str(finding.smell_type)))}</td><td>{html.escape(_soft_wrap(str(finding.severity)))}</td><td>{html.escape(_soft_wrap(f'{finding.confidence:.2f}'))}</td></tr>"
            for finding in result.findings
        )
        history_rows = "".join(
            f"<tr><th>{html.escape(label)}</th><td>{html.escape(_soft_wrap(str(value)))}</td></tr>"
            for label, value in [
                ("Total commits", history_summary["total_commits"]),
                ("Commit frequency", f"{history_summary['commit_frequency']:.2f}/day"),
                ("Last modified", history_summary["last_modified"]),
                ("Code churn", history_summary["code_churn"]),
                ("Lines added", history_summary["lines_added"]),
                ("Lines deleted", history_summary["lines_deleted"]),
                ("Top contributors", ", ".join(history_summary["top_contributors"]) or "Not available"),
                ("Recent commit messages", "; ".join(history_summary["recent_commit_messages"]) or "Not available"),
                ("Hotspot score", history_summary["hotspot_score"]),
            ]
        )
        html_content = f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>EvolutionSmellAI Report</title>
  <style>
    :root {{ color-scheme: dark; }}
    body {{ font-family: Arial, sans-serif; margin: 0; padding: 24px; background: #020617; color: #e2e8f0; }}
    .card {{ background: #111827; border: 1px solid #334155; border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 10px 25px rgba(15, 23, 42, 0.3); }}
    h1, h2 {{ color: #f8fafc; }}
    p {{ line-height: 1.6; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 8px; }}
    th, td {{ border: 1px solid #334155; padding: 10px; text-align: left; }}
    th {{ background: #0f172a; color: #f8fafc; }}
    tr:nth-child(even) td {{ background: #0f172a; }}
    .meta {{ color: #94a3b8; }}
  </style>
</head>
<body>
  <div class=\"card\">
    <h1>EvolutionSmellAI Report</h1>
    <p><strong>Repository:</strong> {html.escape(result.repository_name)}</p>
    <p><strong>Repository URL:</strong> {html.escape(result.repository_url)}</p>
    <p><strong>Summary:</strong> {html.escape(result.summary)}</p>
  </div>

  <div class=\"card\">
    <h2>Commit History Analysis</h2>
    <table>
      <tbody>
        {history_rows}
      </tbody>
    </table>
  </div>

  <div class=\"card\">
    <h2>Findings</h2>
    <table>
      <thead>
        <tr><th>File</th><th>Class</th><th>Smell</th><th>Severity</th><th>Confidence</th></tr>
      </thead>
      <tbody>
        {findings_rows or '<tr><td colspan="5">No smell findings were detected in this repository.</td></tr>'}
      </tbody>
    </table>
  </div>
</body>
</html>
"""
        html_path.write_text(html_content, encoding="utf-8")
