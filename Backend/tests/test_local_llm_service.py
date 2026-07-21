from llm.base import LLMRequest
from llm.local_client import LocalLLMService


def test_local_llm_service_generates_smell_specific_suggestions():
    service = LocalLLMService()

    large_class_response = service.generate(
        LLMRequest(
            smell_type="Large Class",
            severity="medium",
            file_path="src/main/java/demo/AnnotationUtils.java",
            class_name="AnnotationUtils",
            metrics={"line_count": 320, "method_count": 18, "field_count": 7, "complexity_score": 64.5},
            retrieved_examples=[],
            context_summary="The class contains a high number of lines or methods, making it harder to understand and maintain.",
            source_code="class AnnotationUtils {}",
        )
    )

    long_method_response = service.generate(
        LLMRequest(
            smell_type="Long Method",
            severity="medium",
            file_path="src/main/java/demo/Processor.java",
            class_name="Processor",
            metrics={"line_count": 140, "method_count": 4, "field_count": 2, "complexity_score": 29.2},
            retrieved_examples=[],
            context_summary="At least one method is longer or more complex than the recommended threshold.",
            source_code="class Processor {}",
        )
    )

    assert large_class_response.refactoring_suggestions != long_method_response.refactoring_suggestions
    assert any("AnnotationUtils" in suggestion for suggestion in large_class_response.refactoring_suggestions)
    assert any("Processor" in suggestion for suggestion in long_method_response.refactoring_suggestions)
    assert all("AnnotationUtils" not in suggestion for suggestion in long_method_response.refactoring_suggestions)
    assert all("C:\\" not in suggestion for suggestion in large_class_response.refactoring_suggestions)
    assert all("C:\\" not in suggestion for suggestion in long_method_response.refactoring_suggestions)
    assert any("src/main/java/demo" in suggestion for suggestion in large_class_response.refactoring_suggestions)
    assert any("src/main/java/demo" in suggestion for suggestion in long_method_response.refactoring_suggestions)
