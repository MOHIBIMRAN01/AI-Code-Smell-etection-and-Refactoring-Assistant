"""Generate JSON and PDF reports for an analysis run entirely in-memory."""

from __future__ import annotations

import html
import io
import json
from datetime import datetime
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from models.domain import AnalysisResult, Finding
from utils.errors import ReportError


def _soft_wrap(text: str | None, for_pdf: bool = False) -> str:
    """Insert soft wrap opportunities into long tokens so PDF/HTML can wrap."""
    if text is None:
        return ""
    s = str(text)
    if for_pdf:
        for sep in ['/', '.', '-', '_', '?', '&']:
            s = s.replace(sep, sep + ' ')
    else:
        for sep in ['/', '.', '-', '_', '?', '&']:
            s = s.replace(sep, sep + '\u200b')
    return s


def _truncate(text: str, max_chars: int = 300, suffix: str = "…") -> str:
    """Truncate *text* to *max_chars* characters, appending *suffix* if cut."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip() + suffix


class ReportGenerator:
    """Build analysis reports as in-memory bytes (no disk writes)."""

    def generate(self, result: AnalysisResult) -> tuple[bytes, bytes]:
        """Return (json_bytes, pdf_bytes) for the analysis result."""
        try:
            json_bytes = self._build_json(result)
            pdf_bytes = self._build_pdf(result)
            return json_bytes, pdf_bytes
        except Exception as exc:
            raise ReportError(f"Unable to generate reports: {exc}") from exc

    # ------------------------------------------------------------------ #
    # JSON                                                                 #
    # ------------------------------------------------------------------ #

    def _build_json(self, result: AnalysisResult) -> bytes:
        data = {
            "analysis_id": result.analysis_id,
            "repository_url": result.repository_url,
            "repository_name": result.repository_name,
            "repository_path": result.repository_path,
            "total_java_files": result.total_java_files,
            "analyzed_classes": result.analyzed_classes,
            "summary": result.summary,
            "findings": [self._finding_to_dict(f) for f in result.findings],
        }
        return json.dumps(data, indent=2).encode("utf-8")

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

    # ------------------------------------------------------------------ #
    # PDF (in-memory via BytesIO)                                         #
    # ------------------------------------------------------------------ #

    def _build_pdf(self, result: AnalysisResult) -> bytes:
        buffer = io.BytesIO()

        styles = getSampleStyleSheet()
        title_style = styles["Title"]
        heading_style = ParagraphStyle(
            name="Heading2",
            parent=styles["Heading2"],
            textColor=colors.HexColor("#0f172a"),
            spaceBefore=8,
            spaceAfter=6,
        )
        body_style = ParagraphStyle(
            name="Body", parent=styles["BodyText"], leading=12, spaceAfter=6
        )
        meta_style = ParagraphStyle(
            name="Meta",
            parent=styles["BodyText"],
            leading=10,
            textColor=colors.HexColor("#475569"),
            spaceAfter=4,
        )
        cell_style = ParagraphStyle(
            name="TableCell", parent=body_style, fontSize=8, leading=10, wordWrap="CJK"
        )
        header_cell_style = ParagraphStyle(
            name="TableHeaderCell", parent=body_style, fontSize=8, leading=10, wordWrap="CJK"
        )

        document = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=18 * mm,
            rightMargin=18 * mm,
            topMargin=16 * mm,
            bottomMargin=16 * mm,
        )

        story = [Paragraph("EvolutionSmellAI Report", title_style), Spacer(1, 8)]
        story.append(Paragraph(f"Repository: {result.repository_name}", body_style))
        story.append(Paragraph(f"Repository URL: {result.repository_url}", body_style))
        story.append(Paragraph(f"Summary: {_truncate(result.summary, max_chars=600)}", body_style))
        story.append(Spacer(1, 8))

        history_summary = self._extract_commit_history_summary(result)
        story.append(Paragraph("Commit History Analysis", heading_style))
        story.append(Spacer(1, 4))
        history_rows = [
            [Paragraph(html.escape("Metric"), header_cell_style), Paragraph(html.escape("Value"), header_cell_style)],
            [Paragraph(html.escape("Total commits"), cell_style), Paragraph(html.escape(_soft_wrap(str(history_summary["total_commits"]), for_pdf=True)), cell_style)],
            [Paragraph(html.escape("Commit frequency"), cell_style), Paragraph(html.escape(_soft_wrap(f"{history_summary['commit_frequency']:.2f}/day", for_pdf=True)), cell_style)],
            [Paragraph(html.escape("Last modified"), cell_style), Paragraph(html.escape(_soft_wrap(str(history_summary["last_modified"]), for_pdf=True)), cell_style)],
            [Paragraph(html.escape("Code churn"), cell_style), Paragraph(html.escape(_soft_wrap(str(history_summary["code_churn"]), for_pdf=True)), cell_style)],
            [Paragraph(html.escape("Lines added"), cell_style), Paragraph(html.escape(_soft_wrap(str(history_summary["lines_added"]), for_pdf=True)), cell_style)],
            [Paragraph(html.escape("Lines deleted"), cell_style), Paragraph(html.escape(_soft_wrap(str(history_summary["lines_deleted"]), for_pdf=True)), cell_style)],
            [Paragraph(html.escape("Top contributors"), cell_style), Paragraph(html.escape(_soft_wrap(_truncate(", ".join(history_summary["top_contributors"]) or "Not available", max_chars=200), for_pdf=True)), cell_style)],
            [Paragraph(html.escape("Recent commit messages"), cell_style), Paragraph(html.escape(_soft_wrap(_truncate("; ".join(history_summary["recent_commit_messages"]) or "Not available", max_chars=400), for_pdf=True)), cell_style)],
            [Paragraph(html.escape("Hotspot score"), cell_style), Paragraph(html.escape(_soft_wrap(str(history_summary["hotspot_score"]), for_pdf=True)), cell_style)],
        ]
        history_table = Table(history_rows, repeatRows=1, colWidths=[45 * mm, 110 * mm], splitByRow=1)
        history_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#111827")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#64748b")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("WORDWRAP", (0, 0), (-1, -1), "CJK"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f8fafc")),
                ("TEXTCOLOR", (0, 1), (-1, -1), colors.HexColor("#0f172a")),
            ])
        )
        story.append(history_table)
        story.append(Spacer(1, 10))

        if not result.findings:
            story.append(Paragraph("No smell findings were detected in this repository.", body_style))
            document.build(story)
            return buffer.getvalue()

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
        table = Table(data, repeatRows=1, colWidths=[70 * mm, 30 * mm, 30 * mm, 20 * mm, 20 * mm], splitByRow=1)
        table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#111827")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#64748b")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f8fafc")),
            ])
        )
        story.append(table)
        document.build(story)
        return buffer.getvalue()

    # ------------------------------------------------------------------ #
    # Helpers                                                              #
    # ------------------------------------------------------------------ #

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

        if history_blocks:
            total_commits = max(int(block.get("total_commits", 0) or 0) for block in history_blocks)
        else:
            total_commits = max(raw_history_counts) if raw_history_counts else 0
        commit_frequency = max(float(block.get("commit_frequency", 0.0) or 0.0) for block in history_blocks) if history_blocks else 0.0
        code_churn = sum(int(block.get("code_churn", 0) or 0) for block in history_blocks)
        lines_added = sum(int(block.get("lines_added", 0) or 0) for block in history_blocks)
        lines_deleted = sum(int(block.get("lines_deleted", 0) or 0) for block in history_blocks)
        hotspot_score = max(float(block.get("hotspot_score", 0.0) or 0.0) for block in history_blocks) if history_blocks else 0.0

        dates = []
        for block in history_blocks:
            value = block.get("last_modified_date")
            if isinstance(value, str) and value:
                try:
                    dates.append(datetime.fromisoformat(value.replace("Z", "+00:00")))
                except ValueError:
                    continue

        contributors = sorted({c[:80] for block in history_blocks for c in block.get("contributors", []) if c})
        messages = [str(m)[:120] for block in history_blocks for m in block.get("recent_commit_messages", []) if m]

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
