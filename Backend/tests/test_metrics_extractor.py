from metrics.extractor import MetricsExtractor
from models.domain import ClassMetrics, MethodMetrics


def test_metrics_extractor_identifies_large_class_and_long_method():
    extractor = MetricsExtractor()
    class_metrics = ClassMetrics(
        name="Sample",
        file_path="Sample.java",
        line_count=320,
        method_count=16,
        field_count=2,
        import_count=5,
        comment_lines=0,
        blank_lines=0,
        method_metrics=[MethodMetrics(name="a", line_count=30, parameter_count=1, complexity=14)],
    )

    evaluated = extractor.evaluate_class(class_metrics)

    assert evaluated.complexity_score > 0
    assert "Large Class" in evaluated.smell_candidates
    assert "Long Method" in evaluated.smell_candidates
