FROM python:3.12-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies
RUN uv pip install --system -r pyproject.toml

# Copy application code
COPY src/ ./src/

# Copy data directory (with ChromaDB)
COPY data/ ./data/

# Copy docs directory (for PDF ingestion)
COPY docs/ ./docs/

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "src.promtior_assistant.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips=*"]
