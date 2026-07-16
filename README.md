# EvolutionSmellAI

EvolutionSmellAI: Evolution-Aware Code Smell Detection using Git Commit History, Retrieval-Augmented Generation (FAISS), and Large Language Models

This project analyzes Java GitHub repositories, detects likely code smells, estimates severity, retrieves similar historical examples from `combined_dataset.json`, and uses Git commit history as supporting evidence before asking an LLM to explain the result and recommend refactorings.

## Features

- **AI-Powered Code Smell Detection**: Clones GitHub repositories, parses Java source code with `javalang`, and calculates method/class complexity metric profiles.
- **Retrieval-Augmented Generation (RAG)**: Uses a local FAISS vector store to retrieve historical code smell patterns from `combined_dataset.json` to contextualize AI suggestions.
- **LLM Reasoning**: Leverages OpenAI, Google Gemini, or local gateways (Ollama/Llama/Qwen) to generate code rationales and refactoring recommendations.
- **Next.js 16 & React 19 Frontend**: A highly responsive, interactive Single Page Application built with React 19 and Tailwind CSS.
- **Interactive Results Dashboard**: Displays visual severity distribution charts, scan metadata cards, and a searchable, sortable findings data grid.
- **Dynamic Light & Dark Theme Support**: Features a Slate Light Theme (default) and a premium Dark Theme customized with black, cream, and coral colors, toggled via a header button.
- **PostgreSQL Database Storage (Neon DB Ready)**: Integrates SQLAlchemy to save all scans, java class profiles, findings, and generated PDF report blobs.
- **Anonymous Multi-Tenancy**: Auto-generates a client UUID stored in local storage and sent via `X-User-ID` headers to prevent users from accessing each other's scan data.
- **Export Formats**: Supports downloading complete analysis results as formatted JSON or custom PDF documents.
- **Clean Subfolder Architecture**: Reorganized into independent `/Backend` (FastAPI) and `/Frontend` (Next.js) directories for containerization and easy hosting.

## Run Locally

### Backend Server

1. Create and activate a virtual environment.
2. Navigate to the backend directory:
   ```bash
   cd Backend
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and configure your database URL and API keys.
5. Start the FastAPI server:
   ```bash
   uvicorn api.main:app --reload
   ```

### Frontend Server

1. Navigate to the frontend directory:
   ```bash
   cd Frontend
   ```
2. Install Node dependencies:
   ```bash
   npm install
   ```
3. Start the Next.js development server:
   ```bash
   npm run dev
   ```

## API Endpoints

- `GET /api/health` - Basic health check status
- `POST /api/analyze` - Scan a repository URL and label
- `GET /api/analyses` - List all past analyses run by the calling client UUID
- `GET /api/reports/{analysis_id}/data` - Retrieve full database finding records
- `GET /api/reports/{analysis_id}/json` - Download JSON format report
- `GET /api/reports/{analysis_id}/pdf` - Download PDF format document

## Notes

- The LLM never runs without retrieval context because the analysis engine always pulls similar examples from the historical database first.
- If no database URL is provided, the backend falls back to a local SQLite database file `app.db` automatically for ease of testing.
- If no LLM API key is configured, the system falls back to a deterministic responder so the application still functions offline.
