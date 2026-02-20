---
title: "Local Setup"
description: "Guía completa para ejecutar el proyecto localmente"
---

# Local Setup Guide

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.12+ | Runtime |
| Docker | Latest | Container runtime |
| Docker Compose | Latest | Orchestration |
| uv | Latest | Package manager |
| Git | - | Version control |

## Installation Steps

### 1. Clone Repository

```bash
git clone https://github.com/urrestarazu-alejandro/promtior-chat-assistant.git
cd promtior-chat-assistant
```

### 2. Install Dependencies

```bash
make install
```

This runs `uv sync --all-extras` which installs all dependencies from `pyproject.toml`.

### 3. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your local configuration:

```bash
# Development environment
ENVIRONMENT=development
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=tinyllama
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
CHROMA_PERSIST_DIRECTORY=./data/chroma_db_v2
```

### 4. Start Ollama

```bash
make ollama
```

This will:
1. Start Ollama container via Docker Compose (`docker-compose.yml:2-8`)
2. Pull `tinyllama` model (~1GB)
3. Pull `nomic-embed-text` embeddings model (~274MB)

**Model options by memory usage:**

| Model | RAM | Quality |
|-------|-----|---------|
| tinyllama | ~1GB | Basic |
| llama2 | ~4GB | Good |
| phi3:mini | ~3GB | Good |
| gpt-oss:20b | ~13GB | Best |

To use a different model:
```bash
# Edit .env to change OLLAMA_MODEL
OLLAMA_MODEL=llama2

# Pull the model
docker exec promtior-ollama ollama pull llama2
```

### 5. Ingest Data

```bash
make ingest
```

This runs the ingestion pipeline (`src/promtior_assistant/ingest.py:86-164`):

1. Scrapes https://promtior.ai with BeautifulSoup
2. Loads PDFs from `docs/` directory with pypdf
3. Splits text into chunks (1000 chars, 200 overlap)
4. Generates embeddings with Ollama
5. Stores in ChromaDB

### 6. Run Development Server

```bash
make dev
```

Server starts at **http://localhost:8000**

## Verify Installation

### Health Check

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "ok",
  "environment": "development"
}
```

### Test Question

```bash
curl "http://localhost:8000/ask?q=What services does Promtior offer?"
```

Expected response:
```json
{
  "question": "What services does Promtior offer?",
  "answer": "Promtior ofrece...",
  "status": "success"
}
```

## Available Commands

| Command | Description |
|---------|-------------|
| `make install` | Install Python dependencies |
| `make ollama` | Start Ollama and pull models |
| `make ingest` | Ingest data into ChromaDB |
| `make dev` | Run development server with hot reload |
| `make test` | Run unit tests |
| `make test-all` | Run all tests |
| `make test-integration` | Run integration tests only |
| `make clean` | Clean cache files |
| `make docker-down` | Stop Ollama container |

## Project Structure

```
promtior-chat-assistant/
├── src/promtior_assistant/
│   ├── main.py          # FastAPI application
│   ├── config.py        # Settings (config.py:1-44)
│   ├── rag.py           # RAG chain implementation
│   └── ingest.py        # Data ingestion pipeline
├── docs/                # Documentation & PDFs
├── data/                # ChromaDB storage
├── docker-compose.yml   # Ollama container
├── Makefile            # Development commands
└── pyproject.toml      # Dependencies
```

## Troubleshooting

### Ollama Won't Start

```bash
# Check Docker is running
docker ps

# Check Ollama logs
docker logs promtior-ollama

# Restart Ollama
docker restart promtior-ollama
```

### Connection Refused

```bash
# Verify Ollama is listening on port 11434
docker exec promtior-ollama curl http://localhost:11434
```

### Empty Responses

```bash
# Re-ingest data
rm -rf data/chroma_db_v2
make ingest
```

### Port Already in Use

```bash
# Find what's using port 8000
lsof -i :8000

# Kill the process
kill <PID>
```

## Switching to Production Mode Locally

To test production configuration locally:

```bash
# Set production variables
export ENVIRONMENT=production
export LLM_PROVIDER=openai
export OPENAI_API_KEY=sk-...
export USE_OPENAI_EMBEDDINGS=true

# Run server
make dev
```
