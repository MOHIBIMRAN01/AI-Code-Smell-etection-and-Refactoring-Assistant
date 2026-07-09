# EvolutionSmellAI

EvolutionSmellAI: Evolution-Aware Code Smell Detection using Git Commit History, Retrieval-Augmented Generation (FAISS), and Large Language Models

This project analyzes Java GitHub repositories, detects likely code smells, estimates severity, retrieves similar historical examples from `combined_dataset.json`, and uses Git commit history as supporting evidence before asking an LLM to explain the result and recommend refactorings.

## Features

- GitHub repository cloning
- Java source parsing with `javalang`
- Metric extraction and smell heuristics
- Retrieval-Augmented Generation with FAISS
- OpenAI as the default LLM provider
- Optional Gemini and OpenAI-compatible endpoints for Llama/Qwen gateways
- JSON and PDF report generation
- FastAPI REST API
- Bootstrap frontend

## Run Locally

1. Create and activate a virtual environment.
2. Install dependencies with `pip install -r requirements.txt`.
3. Copy `.env.example` to `.env` and fill in any keys you want to use.
4. Start the API with `uvicorn api.main:app --reload`.
5. Open `http://127.0.0.1:8000/` in your browser.

## API

- `GET /api/health`
- `POST /api/analyze`
- `GET /api/reports/{analysis_id}/json`
- `GET /api/reports/{analysis_id}/pdf`

## Notes

- The LLM never runs without retrieval context because the analysis engine always pulls similar examples from the historical dataset first.
- If no API key is configured, the system falls back to deterministic local responders so the application still works offline.
