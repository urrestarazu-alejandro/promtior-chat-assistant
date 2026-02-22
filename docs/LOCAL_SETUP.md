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

For complete environment variables, see [CLAUDE.md](../CLAUDE.md#environment-variables).

Default development `.env`:
```bash
ENVIRONMENT=development
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=tinyllama
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
CHROMA_PERSIST_DIRECTORY=./data/chroma_db
```

### 4. Start Ollama

```bash
make ollama
```

This will:
1. Start Ollama container via Docker Compose
2. Pull configured Ollama model (default: phi3:mini)
3. Pull embeddings model (nomic-embed-text)

**Model options:**

| Model | RAM | Quality |
|-------|-----|---------|
| tinyllama | ~1GB | ✅ Recommended |
| phi3:mini | ~3GB | Good |
| llama2 | ~4GB | Basic |

### 5. Ingest Data

```bash
make ingest
```

This runs the ingestion pipeline:
1. Loads PDFs from `docs/` (priority)
2. Scrapes https://promtior.ai
3. Splits text into chunks (1500 chars, 300 overlap)
4. Generates embeddings with Ollama
5. Stores in ChromaDB

### 6. Run Development Server

```bash
make dev
```

Server starts at **http://localhost:8000**

## Available Commands

See [CLAUDE.md](../CLAUDE.md#commands) for complete command list.

| Command | Description |
|---------|-------------|
| `make install` | Install Python dependencies |
| `make ollama` | Start Ollama and pull models |
| `make ingest` | Ingest data into ChromaDB |
| `make dev` | Run development server |
| `make test` | Run unit tests |
| `make clean` | Clean cache files |

## Test Local

```bash
# Health check
curl http://localhost:8000/health

# Ask question
curl "http://localhost:8000/ask?q=When was Promtior founded?"
```

## Production Test Locally

```bash
export ENVIRONMENT=production
export LLM_PROVIDER=openai
export OPENAI_API_KEY=sk-...
export USE_OPENAI_EMBEDDINGS=true
make dev
```
