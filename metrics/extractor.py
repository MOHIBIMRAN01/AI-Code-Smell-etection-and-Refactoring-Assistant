"""Software metric extraction and heuristic smell scoring."""

from __future__ import annotations

from dataclasses import dataclass

from models.domain import ClassMetrics


@dataclass(slots=True)
class SmellCandidate:
    """Potential smell detected for a class or method."""

    smell_type: str
    severity: str
    confidence: float
    rationale: str


class MetricsExtractor:
    """Compute smell-related metrics from parsed Java classes."""

    def evaluate_class(self, class_metrics: ClassMetrics) -> ClassMetrics:
        """Augment a class with complexity and smell candidates."""

        score = self._compute_complexity_score(class_metrics)
        smell_candidates = self._detect_smells(class_metrics, score)
        class_metrics.complexity_score = score
        # Keep legacy string list for compatibility, but detailed candidates
        # can be fetched via `get_smell_candidates`.
        class_metrics.smell_candidates = [candidate.smell_type for candidate in smell_candidates]
        return class_metrics

    def get_smell_candidates(self, class_metrics: ClassMetrics) -> list[SmellCandidate]:
        """Return detailed SmellCandidate objects with computed confidences."""
        score = getattr(class_metrics, "complexity_score", None)
        if score is None or score == 0:
            score = self._compute_complexity_score(class_metrics)
        return self._detect_smells(class_metrics, score)

    def _compute_complexity_score(self, class_metrics: ClassMetrics) -> float:
        method_complexity = sum(method.complexity for method in class_metrics.method_metrics)
        method_count = max(class_metrics.method_count, 1)
        loc_ratio = class_metrics.line_count / method_count
        field_pressure = class_metrics.field_count / method_count
        return round(method_complexity + loc_ratio * 0.15 + field_pressure * 0.5 + class_metrics.import_count * 0.1, 2)

    def _detect_smells(self, class_metrics: ClassMetrics, score: float) -> list[SmellCandidate]:
        smells: list[SmellCandidate] = []

        if class_metrics.line_count >= 250 or class_metrics.method_count >= 15:
            severity = self._severity_from_threshold(class_metrics.line_count, 250, 450)
            smells.append(
                SmellCandidate(
                    smell_type="Large Class",
                    severity=severity,
                    confidence=self._confidence_for_large_class(class_metrics),
                    rationale="The class contains a high number of lines or methods, making it harder to understand and maintain.",
                )
            )

        if any(method.line_count >= 25 or method.complexity >= 12 for method in class_metrics.method_metrics):
            max_method_len = max((method.line_count for method in class_metrics.method_metrics), default=0)
            max_method_complexity = max((method.complexity for method in class_metrics.method_metrics), default=0)
            smells.append(
                SmellCandidate(
                    smell_type="Long Method",
                    severity=self._severity_from_threshold(max_method_len, 25, 45),
                    confidence=self._confidence_for_long_method(max_method_len, max_method_complexity),
                    rationale="At least one method is longer or more complex than the recommended threshold.",
                )
            )

        if class_metrics.field_count >= 12 and class_metrics.method_count <= 5:
            smells.append(
                SmellCandidate(
                    smell_type="Data Class",
                    severity="medium",
                    confidence=self._confidence_for_data_class(class_metrics),
                    rationale="The class stores many fields but exposes limited behavior, which often signals a data holder.",
                )
            )

        if any(method.parameter_count >= 5 for method in class_metrics.method_metrics):
            max_params = max((method.parameter_count for method in class_metrics.method_metrics), default=0)
            smells.append(
                SmellCandidate(
                    smell_type="Long Parameter List",
                    severity="medium",
                    confidence=self._confidence_for_long_parameter_list(max_params),
                    rationale="One or more methods accept many parameters, which makes the API difficult to call correctly.",
                )
            )

        if score >= 60:
            smells.append(
                SmellCandidate(
                    smell_type="God Class",
                    severity="high",
                    confidence=self._confidence_for_god_class(score),
                    rationale="The combined structural metrics indicate that the class may be taking on too many responsibilities.",
                )
            )

        return smells[:10]

    # --- Confidence heuristics ---
    def _clamp_confidence(self, value: float) -> float:
        return round(max(0.0, min(0.99, value)), 2)

    def _confidence_for_large_class(self, class_metrics: ClassMetrics) -> float:
        base = 0.55
        # stronger signal for lines and methods beyond thresholds
        line_excess = max(0, class_metrics.line_count - 250)
        method_excess = max(0, class_metrics.method_count - 15)
        boost = min(0.35, line_excess / 1000 + method_excess * 0.02)
        return self._clamp_confidence(base + boost)

    def _confidence_for_long_method(self, max_len: int, max_complexity: int) -> float:
        base = 0.5
        len_boost = min(0.3, max(0, max_len - 25) / 100)
        comp_boost = min(0.35, max(0, max_complexity - 12) / 40)
        return self._clamp_confidence(base + max(len_boost, comp_boost))

    def _confidence_for_data_class(self, class_metrics: ClassMetrics) -> float:
        base = 0.5
        field_excess = max(0, class_metrics.field_count - 12)
        method_penalty = max(0, 5 - class_metrics.method_count)
        boost = min(0.35, field_excess * 0.03 + method_penalty * 0.05)
        return self._clamp_confidence(base + boost)

    def _confidence_for_long_parameter_list(self, max_params: int) -> float:
        base = 0.45
        boost = min(0.45, (max_params - 5) * 0.08)
        return self._clamp_confidence(base + boost)

    def _confidence_for_god_class(self, score: float) -> float:
        base = 0.65
        boost = min(0.3, (score - 60) / 120)
        return self._clamp_confidence(base + boost)

    def _severity_from_threshold(self, value: float, low: float, high: float) -> str:
        if value >= high:
            return "high"
        if value >= low:
            return "medium"
        return "low"
