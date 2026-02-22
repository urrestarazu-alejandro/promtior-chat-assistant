# Testing Embedding Metadata System - Local Guide

Esta guía te muestra cómo probar el nuevo sistema de metadata de embeddings localmente.

## Pre-requisitos

1. **Ollama instalado y corriendo**
   ```bash
   # Verificar que Ollama esté corriendo
   curl http://localhost:11434/api/tags

   # Si no está corriendo, iniciar Ollama
   # macOS: Abre la app Ollama
   # Linux: ollama serve
   ```

2. **Modelos necesarios**
   ```bash
   # Instalar modelo de embeddings
   ollama pull nomic-embed-text

   # Instalar modelo LLM
   ollama pull tinyllama
   ```

3. **Dependencias instaladas**
   ```bash
   make install
   # o
   uv sync
   ```

## Escenario 1: Primera Ingesta con Ollama (Recomendado para dev)

### Paso 1: Configurar Variables de Entorno

```bash
# Crear archivo .env si no existe
cp .env.example .env

# Editar .env con estos valores:
ENVIRONMENT=development
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=tinyllama
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
```

### Paso 2: Limpiar ChromaDB Anterior (Opcional)

```bash
# Eliminar ChromaDB anterior (sin metadata)
rm -rf data/chroma_db
```

### Paso 3: Ejecutar Ingesta

```bash
# Ejecutar el script de ingesta
python -m src.promtior_assistant.ingest
```

**Salida esperada:**
```
============================================================
🚀 Starting data ingestion...
============================================================

🔍 Scraping https://promtior.ai...
✅ Scraped 15234 characters

📄 Loading PDF: AI-Engineer-Test-Promtior.pdf
   ✅ Extracted 12456 characters

✂️  Splitting text into chunks...
✅ Created 42 chunks

🧮 Initializing embeddings...
✅ Using Ollama embeddings (nomic-embed-text)
   Dimension: 768

💾 Storing in ChromaDB...
   Directory: ./data/chroma_db
   Provider: ollama
✅ ChromaDB populated successfully
✅ Embedding metadata saved

============================================================
✅ Data ingestion completed!
============================================================
   Chunks stored: 42
   Environment: development
   Vector DB: ./data/chroma_db
============================================================
```

### Paso 4: Verificar Metadata Guardada

```bash
# Ver el archivo de metadata
cat data/chroma_db/embedding_metadata.json
```

**Salida esperada:**
```json
{
  "embedding_provider": "ollama",
  "embedding_model": "nomic-embed-text",
  "embedding_dimension": 768
}
```

### Paso 5: Iniciar Servidor de Desarrollo

```bash
make dev
# o
uv run uvicorn src.promtior_assistant.main:app --reload
```

**Salida esperada:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
INFO:     Initializing Container dependencies...
INFO:       ✓ LLM initialized: tinyllama
INFO:       ✓ Embeddings initialized
INFO:     Container initialization complete
INFO:     Embedding metadata validated: EmbeddingMetadata(provider=ollama, model=nomic-embed-text, dim=768)
```

### Paso 6: Probar el Sistema RAG

```bash
# En otra terminal, hacer requests

# 1. Health check
curl http://localhost:8000/health

# 2. Pregunta en español
curl "http://localhost:8000/ask?q=¿Qué%20servicios%20ofrece%20Promtior?"

# 3. Pregunta en inglés (debe responder en inglés automáticamente)
curl "http://localhost:8000/ask?q=What%20services%20does%20Promtior%20offer?"

# 4. API v1
curl -X POST http://localhost:8000/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "¿Cuándo fue fundada Promtior?"}'
```

**Respuestas esperadas:**
- ✅ Responden en el MISMO idioma de la pregunta
- ✅ Son concisas (2-3 frases)
- ✅ Basadas en el contexto del RAG

---

## Escenario 2: Cambiar a OpenAI (Probar Validación)

### Paso 1: Configurar OpenAI

```bash
# Editar .env
ENVIRONMENT=development
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...  # Tu API key
OPENAI_MODEL=gpt-4o-mini
USE_OPENAI_EMBEDDINGS=true
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

### Paso 2: Intentar Iniciar Servidor (DEBE FALLAR)

```bash
# Reiniciar el servidor
make dev
```

**Error esperado:**
```
EmbeddingMismatchError: Embedding configuration mismatch detected!
Vector store was created with:
  - Provider: ollama
  - Model: nomic-embed-text
  - Dimension: 768
But you're trying to use:
  - Provider: openai
  - Model: text-embedding-3-small
  - Dimension: 1536

To fix this, you need to re-ingest data with the current provider.
Run: POST /admin/reingest?admin_key=<YOUR_KEY>
```

**¡Esto demuestra que la validación funciona!** 🎉

### Paso 3: Re-ingestar con OpenAI

```bash
# Opción A: Vía Script
python -m src.promtior_assistant.ingest

# Opción B: Vía API (requiere admin key configurada)
curl -X POST "http://localhost:8000/admin/reingest?admin_key=YOUR_ADMIN_KEY"
```

**Salida esperada:**
```
🧮 Initializing embeddings...
✅ Using OpenAI embeddings (text-embedding-3-small)
   Dimension: 1536

💾 Storing in ChromaDB...
   Directory: ./data/chroma_db
   Provider: openai
   🗑️  Removing existing ChromaDB at data/chroma_db
✅ ChromaDB populated successfully
✅ Embedding metadata saved
```

### Paso 4: Verificar Nueva Metadata

```bash
cat data/chroma_db/embedding_metadata.json
```

**Ahora debe mostrar:**
```json
{
  "embedding_provider": "openai",
  "embedding_model": "text-embedding-3-small",
  "embedding_dimension": 1536
}
```

### Paso 5: Iniciar Servidor (Ahora SÍ Funciona)

```bash
make dev
```

**Salida esperada:**
```
INFO:     Embedding metadata validated: EmbeddingMetadata(provider=openai, model=text-embedding-3-small, dim=1536)
INFO:     Application startup complete.
```

---

## Escenario 3: Collections Separadas por Provider

### Verificar Collections en ChromaDB

```bash
# Listar archivos en ChromaDB
ls -la data/chroma_db/

# Deberías ver:
# - embedding_metadata.json (tu metadata)
# - chroma.sqlite3 (database)
# - Collection: promtior_docs_ollama (si usaste Ollama)
# - Collection: promtior_docs_openai (si usaste OpenAI)
```

**Nota**: Cada provider tiene su propia collection, por lo que técnicamente podrías tener ambas simultáneamente.

---

## Escenario 4: Ejecutar Tests

### Tests Unitarios (Sin Ollama)

```bash
# Ejecutar todos los tests unitarios (mocked)
make test

# Ejecutar solo tests de metadata
uv run pytest tests/unit/test_embedding_metadata.py -v

# Ejecutar solo tests de ChromaAdapter
uv run pytest tests/unit/test_chroma_adapter.py -v
```

### Tests de Integración (Requiere Ollama)

```bash
# Asegúrate de tener Ollama corriendo
make test-integration

# O manualmente
uv run pytest tests/test_integration.py -v
```

---

## Troubleshooting

### ❌ Error: "Ollama not running"

```bash
# Verificar Ollama
curl http://localhost:11434/api/tags

# Si falla, iniciar Ollama
# macOS: Abre la app
# Linux: ollama serve
```

### ❌ Error: "Model not found"

```bash
# Instalar modelos necesarios
ollama pull nomic-embed-text
ollama pull tinyllama
```

### ❌ Error: "ChromaDB readonly"

```bash
# Limpiar ChromaDB
rm -rf data/chroma_db

# Re-ingestar
python -m src.promtior_assistant.ingest
```

### ❌ Error: "No embedding_metadata.json"

**Esto es normal** si tienes ChromaDB creado antes de esta mejora.

El sistema detecta esto y hace **skip de validación** con un warning:
```
WARNING: No embedding metadata found.
This vector store was created before metadata tracking.
Skipping validation.
```

**Solución**: Re-ingestar datos para crear metadata:
```bash
python -m src.promtior_assistant.ingest
```

---

## Checklist de Pruebas Completo

### ✅ Funcionalidad Básica
- [ ] Ingesta con Ollama genera `embedding_metadata.json`
- [ ] Servidor inicia correctamente con metadata válida
- [ ] `/ask` responde preguntas en español
- [ ] `/ask` responde preguntas en inglés (multi-idioma)
- [ ] Respuestas son concisas (2-3 frases)

### ✅ Validación de Metadata
- [ ] Cambiar a OpenAI sin re-ingestar arroja `EmbeddingMismatchError`
- [ ] Error incluye detalles (provider, model, dimension)
- [ ] Error sugiere cómo resolver (re-ingest)

### ✅ Re-ingesta
- [ ] Re-ingestar con nuevo provider actualiza metadata
- [ ] Servidor inicia después de re-ingesta
- [ ] Collection name cambia según provider

### ✅ Backward Compatibility
- [ ] ChromaDB sin metadata funciona (skip validation)
- [ ] Legacy code (`rag_service.py`) sigue funcionando

### ✅ Tests
- [ ] `make test` pasa (110 tests unitarios)
- [ ] `make test-integration` pasa (requiere Ollama)
- [ ] Coverage > 90%

---

## Comandos Rápidos de Referencia

```bash
# Limpiar y empezar de cero
rm -rf data/chroma_db && python -m src.promtior_assistant.ingest

# Verificar metadata
cat data/chroma_db/embedding_metadata.json

# Iniciar servidor
make dev

# Hacer pregunta
curl "http://localhost:8000/ask?q=¿Qué%20es%20Promtior?"

# Ver logs con metadata
tail -f logs/app.log  # si configuraste logging en archivo

# Ejecutar tests
make test              # unitarios
make test-integration  # integración
make test-all          # todos
```

---

## Próximos Pasos Recomendados

1. **Probar Escenario 1** (Ollama) - Más rápido, sin costos
2. **Verificar metadata guardada** - Confirmar persistencia
3. **Probar preguntas multi-idioma** - Verificar nuevo prompt
4. **Intentar cambiar provider** - Ver validación en acción
5. **Re-ingestar con nuevo provider** - Ciclo completo

**Tiempo estimado**: 15-20 minutos para ciclo completo.

---

Última actualización: 2026-02-21
