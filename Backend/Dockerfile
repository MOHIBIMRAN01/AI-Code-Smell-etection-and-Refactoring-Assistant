FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DATABASE_URL=sqlite:////tmp/app.db

WORKDIR /app

# Install git (required by GitPython for repository cloning)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY Backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY Backend /app

EXPOSE 8000

# Create temp directory for SQLite database
RUN mkdir -p /tmp

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
