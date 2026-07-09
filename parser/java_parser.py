"""Parse Java source files into structured class and method metadata."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from pathlib import Path

import javalang

from models.domain import ClassMetrics, MethodMetrics

LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class ParsedJavaFile:
    """Structured Java file result."""

    file_path: str
    source_code: str
    classes: list[ClassMetrics]
    import_count: int
    loc: int
    comment_lines: int
    blank_lines: int
    parsing_errors: list[str]


class JavaSourceParser:
    """Parse Java source files using javalang with a safe fallback path."""

    def parse_file(self, file_path: Path) -> ParsedJavaFile:
        """Parse a single Java source file."""

        source_code = file_path.read_text(encoding="utf-8", errors="ignore")
        loc = self._count_loc(source_code)
        comment_lines = self._count_comment_lines(source_code)
        blank_lines = sum(1 for line in source_code.splitlines() if not line.strip())
        import_count = len(re.findall(r"^\s*import\s+", source_code, flags=re.MULTILINE))

        try:
            tree = javalang.parse.parse(source_code)
            classes = self._extract_classes(file_path, source_code, tree)
            return ParsedJavaFile(
                file_path=str(file_path),
                source_code=source_code,
                classes=classes,
                import_count=import_count,
                loc=loc,
                comment_lines=comment_lines,
                blank_lines=blank_lines,
                parsing_errors=[],
            )
        except Exception as exc:  # pragma: no cover - fallback is important for malformed sources
            LOGGER.warning("Falling back to regex parsing for %s: %s", file_path, exc)
            class_names = re.findall(r"\bclass\s+([A-Za-z_][A-Za-z0-9_]*)", source_code)
            classes = [
                ClassMetrics(
                    name=name,
                    file_path=str(file_path),
                    line_count=loc,
                    method_count=0,
                    field_count=0,
                    import_count=import_count,
                    comment_lines=comment_lines,
                    blank_lines=blank_lines,
                    complexity_score=0.0,
                )
                for name in class_names or [file_path.stem]
            ]
            return ParsedJavaFile(
                file_path=str(file_path),
                source_code=source_code,
                classes=classes,
                import_count=import_count,
                loc=loc,
                comment_lines=comment_lines,
                blank_lines=blank_lines,
                parsing_errors=[str(exc)],
            )

    def _extract_classes(self, file_path: Path, source_code: str, tree: javalang.tree.CompilationUnit) -> list[ClassMetrics]:
        classes: list[ClassMetrics] = []
        source_lines = source_code.splitlines()

        for type_declaration in tree.types:
            if not hasattr(type_declaration, "name"):
                continue
            class_name = str(type_declaration.name)
            methods = []
            for method in getattr(type_declaration, "methods", []):
                methods.append(self._build_method_metrics(method, source_lines))
            field_count = len(getattr(type_declaration, "fields", []))
            class_loc = self._estimate_class_loc(type_declaration, source_lines)
            classes.append(
                ClassMetrics(
                    name=class_name,
                    file_path=str(file_path),
                    line_count=class_loc,
                    method_count=len(methods),
                    field_count=field_count,
                    import_count=len(tree.imports),
                    comment_lines=self._count_comment_lines(source_code),
                    blank_lines=sum(1 for line in source_lines if not line.strip()),
                    method_metrics=methods,
                )
            )
        return classes or [
            ClassMetrics(
                name=file_path.stem,
                file_path=str(file_path),
                line_count=self._count_loc(source_code),
                method_count=0,
                field_count=0,
                import_count=len(tree.imports),
                comment_lines=self._count_comment_lines(source_code),
                blank_lines=sum(1 for line in source_lines if not line.strip()),
            )
        ]

    def _build_method_metrics(self, method: javalang.tree.MethodDeclaration, source_lines: list[str]) -> MethodMetrics:
        start_line = method.position.line if method.position else None
        method_name = method.name
        parameter_count = len(method.parameters or [])
        complexity = 1 + self._estimate_method_complexity(source_lines, start_line or 1)
        line_count = self._estimate_method_lines(source_lines, start_line or 1)
        end_line = start_line + line_count - 1 if start_line else None
        return MethodMetrics(
            name=method_name,
            line_count=line_count,
            parameter_count=parameter_count,
            complexity=complexity,
            start_line=start_line,
            end_line=end_line,
        )

    def _count_loc(self, source_code: str) -> int:
        return sum(1 for line in source_code.splitlines() if line.strip())

    def _count_comment_lines(self, source_code: str) -> int:
        comment_pattern = re.compile(r"^\s*(//|/\*|\*|\*/)")
        return sum(1 for line in source_code.splitlines() if comment_pattern.match(line))

    def _estimate_method_complexity(self, source_lines: list[str], start_line: int) -> int:
        snippet = "\n".join(source_lines[max(start_line - 1, 0) : start_line + 60])
        decision_keywords = [" if ", " for ", " while ", " case ", " catch ", "&&", "||", "?"]
        return sum(snippet.count(keyword) for keyword in decision_keywords)

    def _estimate_method_lines(self, source_lines: list[str], start_line: int) -> int:
        if start_line <= 0 or start_line > len(source_lines):
            return 1
        depth = 0
        started = False
        end_line = start_line
        for index in range(start_line - 1, len(source_lines)):
            line = source_lines[index]
            depth += line.count("{")
            depth -= line.count("}")
            if "{" in line:
                started = True
            if started and depth <= 0:
                end_line = index + 1
                break
        return max(1, end_line - start_line + 1)

    def _estimate_class_loc(self, type_declaration: javalang.tree.TypeDeclaration, source_lines: list[str]) -> int:
        if not getattr(type_declaration, "position", None):
            return len(source_lines)
        return max(1, len(source_lines) - type_declaration.position.line + 1)
