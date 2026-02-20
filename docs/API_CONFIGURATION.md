---
title: "API Configuration"
description: "Configuración de APIs y variables de entorno"
---

# API Configuration

## Environment Variables

### Production (OpenAI)

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `ENVIRONMENT` | Entorno | `production` |
| `LLM_PROVIDER` | Proveedor de LLM | `openai` |
| `OPENAI_API_KEY` | Clave de API de OpenAI | `sk-...` |
| `OPENAI_MODEL` | Modelo de OpenAI | `gpt-4o-mini` |
| `OPENAI_EMBEDDING_MODEL` | Modelo de embeddings | `text-embedding-3-small` |
| `USE_OPENAI_EMBEDDINGS` | Usar embeddings de OpenAI | `true` |
| `CHROMA_PERSIST_DIRECTORY` | Directorio de ChromaDB | `./data/chroma_db_v2` |

### Development (Ollama)

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `ENVIRONMENT` | Entorno | `development` |
| `LLM_PROVIDER` | Proveedor de LLM | `ollama` |
| `OLLAMA_BASE_URL` | URL de Ollama | `http://localhost:11434` |
| `OLLAMA_MODEL` | Modelo de Ollama | `llama2` |
| `OLLAMA_EMBEDDING_MODEL` | Modelo de embeddings | `nomic-embed-text` |

## API Endpoints

### GET /

Información de la API.

**Response:**
```json
{
  "message": "Promtior RAG Assistant API",
  "version": "0.1.0",
  "environment": "production",
  "usage": "GET /ask?q=your_question",
  "examples": [
    "/ask?q=¿Qué servicios ofrece Promtior?",
    "/ask?q=¿Cuándo fue fundada la empresa?"
  ]
}
```

### GET /health

Health check.

**Response:**
```json
{
  "status": "ok",
  "environment": "production"
}
```

### GET /ask

Preguntar sobre Promtior.

**Query Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| `q` | string | Pregunta (required, max 500 chars) |

**Response:**
```json
{
  "question": "¿Qué servicios ofrece Promtior?",
  "answer": "Promtior ofrece servicios de consultoría...",
  "status": "success"
}
```

**Error Response:**
```json
{
  "detail": "Error processing question: ..."
}
```

### POST /admin/reingest

Re-ingestar datos en ChromaDB.

**Query Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| `admin_key` | string | Clave de admin (required) |

**Response:**
```json
{
  "status": "success",
  "message": "Data re-ingested successfully"
}
```

## LLM Configuration

### OpenAI (Production)

```python
# rag.py:251-259
ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7,
)
```

### Ollama (Development)

```python
# rag.py:260-264
CustomOllamaChat(
    model="gpt-oss:20b",
    temperature=0.7,
    base_url="http://localhost:11434",
)
```

## Embeddings

### OpenAI

```python
OpenAIEmbeddings(
    model="text-embedding-3-small",
)
# Dimension: 1536
```

### Ollama

```python
CustomOllamaEmbeddings(
    model="nomic-embed-text",
    base_url="http://localhost:11434",
)
# Dimension: 768
```

## Railway Configuration

### Variables Requeridas

```
ENVIRONMENT=production
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
USE_OPENAI_EMBEDDINGS=true
```

### Dockerfile

El Dockerfile copia el directorio `docs/` para la carga de PDFs:

```dockerfile
COPY docs/ ./docs/
```
