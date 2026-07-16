# Architecture Overview

EvolutionSmellAI is an evolution-aware code smell detection system that combines repository history, FAISS retrieval, and LLM reasoning.

The system follows a clean, layered design:

- `api/` exposes FastAPI routes and handles request/response serialization.
- `services/` contains orchestration, cloning, and report generation.
- `parser/` turns Java source into structured class and method metadata.
- `metrics/` derives smell-related heuristics from parsed code.
- `dataset/` loads the historical JSON dataset into normalized examples.
- `rag/` and `embeddings/` build the retrieval layer on FAISS.
- `llm/` abstracts OpenAI, Gemini, and OpenAI-compatible providers.
- `frontend/` provides a simple Bootstrap UI for manual analysis.

The LLM layer always receives retrieved historical examples before generating an explanation or refactoring recommendation.
