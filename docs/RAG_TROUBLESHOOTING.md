# RAG Troubleshooting Guide

Esta guía te ayuda a diagnosticar y solucionar problemas cuando el RAG no responde correctamente a ciertas preguntas.

## Problema Común: "El RAG no responde mi pregunta"

Si el RAG no puede responder una pregunta específica aunque la información esté en los datos, sigue estos pasos:

### 1. Usa el Script de Diagnóstico

```bash
# Diagnóstico básico (recupera 5 documentos)
uv run python scripts/diagnose_rag.py "When was Promtior founded?"

# Diagnóstico con más documentos
uv run python scripts/diagnose_rag.py "When was Promtior founded?" 10
```

**El script te mostrará:**
- ✅ Qué documentos se están recuperando
- ✅ El contenido de cada documento
- ✅ Si contienen palabras clave relevantes
- ✅ La fuente de cada documento (PDF, website, etc.)

### 2. Interpreta los Resultados

#### Caso 1: Los documentos NO contienen la información
```
✗ Document 1 - no keywords found
✗ Document 2 - no keywords found
✗ Document 3 - no keywords found
```

**Problema**: El chunking está separando la información relevante.

**Solución**: Re-ingestar con parámetros mejorados (ya configurado):
```bash
# Limpiar ChromaDB
rm -rf data/chroma_db

# Re-ingestar con configuración mejorada
make ingest
```

#### Caso 2: Los documentos SÍ contienen la información
```
✓ Document 3 contains: founded, 2016
✓ Document 5 contains: established, creation
```

**Problema**: El prompt o el LLM no están extrayendo bien la información.

**Solución**: Revisar el prompt en `src/promtior_assistant/application/use_cases/answer_question.py`

#### Caso 3: La información está en documentos de baja prioridad
```
Document 1: Score 0.85 - ✗ no keywords
Document 2: Score 0.82 - ✗ no keywords
...
Document 8: Score 0.65 - ✓ contains: founded, 2016
```

**Problema**: La búsqueda por similitud no está priorizando bien.

**Solución**: Ajustar los parámetros de recuperación (k) o mejorar los embeddings.

---

## Parámetros de Configuración del RAG

### Chunking (en `src/promtior_assistant/ingest.py`)

```python
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1500,      # Tamaño de cada chunk (caracteres)
    chunk_overlap=300,    # Solapamiento entre chunks
    length_function=len,
)
```

**Valores actuales (optimizados):**
- `chunk_size=1500` (antes: 1000)
- `chunk_overlap=300` (antes: 200)

**Cuándo ajustar:**
- Si la información se está fragmentando → **Aumentar chunk_size**
- Si hay poca coherencia entre chunks → **Aumentar chunk_overlap**
- Si los chunks son muy genéricos → **Reducir chunk_size**

### Recuperación (en `src/promtior_assistant/application/use_cases/answer_question.py`)

```python
documents = await self._vector_store.retrieve_documents(
    query=validated_question,
    k=5,  # Número de documentos a recuperar
)
```

**Valores actuales (optimizados):**
- `k=5` (antes: 3)

**Cuándo ajustar:**
- Si falta información → **Aumentar k** (6-10)
- Si hay mucho ruido → **Reducir k** (3-4)
- Para preguntas muy específicas → **k=3-5**
- Para preguntas generales → **k=7-10**

---

## Mejoras Recientes (2026-02-21)

### 1. Aumento de Documentos Recuperados
```diff
- k=3  # Solo 3 documentos
+ k=5  # Ahora 5 documentos (66% más contexto)
```

**Beneficio**: Mayor probabilidad de encontrar información relevante.

### 2. Mejor Chunking
```diff
- chunk_size=1000, chunk_overlap=200
+ chunk_size=1500, chunk_overlap=300
```

**Beneficios**:
- Chunks más grandes = más contexto por documento
- Mayor overlap = mejor continuidad de información
- Menos fragmentación de conceptos relacionados

### 3. Script de Diagnóstico
```bash
uv run python scripts/diagnose_rag.py "tu pregunta"
```

**Beneficio**: Visibilidad completa de qué está recuperando el RAG.

---

## Guía de Testing RAG

### 1. Preparación
```bash
# Re-ingestar datos con configuración mejorada
rm -rf data/chroma_db
make ingest

# Iniciar servidor
make dev
```

### 2. Probar Preguntas Específicas

```bash
# Terminal 1: Servidor corriendo
make dev

# Terminal 2: Diagnóstico
uv run python scripts/diagnose_rag.py "When was Promtior founded?"

# Terminal 3: Pregunta real al RAG
curl "http://localhost:8000/ask?q=When%20was%20Promtior%20founded?"
```

### 3. Comparar Resultados

| Paso | Qué verificar |
|------|---------------|
| Diagnóstico | ¿Los documentos contienen la información? |
| API Response | ¿El RAG respondió correctamente? |
| Si ambos SÍ | ✅ Todo funciona |
| Si diagnóstico SÍ pero API NO | 🔧 Problema de prompt/LLM |
| Si diagnóstico NO | 🔧 Problema de chunking/recuperación |

---

## Preguntas de Prueba Recomendadas

### Preguntas Generales (Deberían funcionar bien)
```bash
curl "http://localhost:8000/ask?q=What%20services%20does%20Promtior%20offer?"
curl "http://localhost:8000/ask?q=¿Qué%20es%20Promtior?"
```

### Preguntas Específicas (Requieren información puntual)
```bash
curl "http://localhost:8000/ask?q=When%20was%20Promtior%20founded?"
curl "http://localhost:8000/ask?q=¿Cuándo%20fue%20fundada%20Promtior?"
curl "http://localhost:8000/ask?q=Who%20are%20the%20founders?"
```

### Preguntas Multi-Idioma
```bash
# Español → debe responder en español
curl "http://localhost:8000/ask?q=¿Qué%20servicios%20ofrece%20Promtior?"

# Inglés → debe responder en inglés
curl "http://localhost:8000/ask?q=What%20services%20does%20Promtior%20offer?"
```

---

## Solución de Problemas Comunes

### Problema: "ChromaDB no tiene datos"
```bash
Error: No documents found in ChromaDB
```

**Solución:**
```bash
make ingest
```

### Problema: "Embedding dimension mismatch"
```bash
EmbeddingMismatchError: Vector store was created with ollama...
```

**Solución:**
```bash
# Re-ingestar con el provider correcto
rm -rf data/chroma_db
make ingest
```

### Problema: "LLM no responde"
```bash
Error: Failed to generate RAG answer after 3 attempts
```

**Solución:**
```bash
# Verificar que Ollama esté corriendo
curl http://localhost:11434/api/tags

# O reiniciar Ollama
make ollama
```

### Problema: "Respuestas genéricas o incorrectas"

**Diagnóstico:**
```bash
uv run python scripts/diagnose_rag.py "tu pregunta específica"
```

**Posibles causas:**
1. Documentos recuperados no contienen información → Ajustar chunking
2. Documentos contienen información pero RAG no la usa → Mejorar prompt
3. Información está en documentos de baja prioridad → Aumentar k

---

## Comandos Útiles

```bash
# Ver qué documentos hay en ChromaDB
uv run python -c "
from langchain_chroma import Chroma
from src.promtior_assistant.infrastructure.factories import create_embeddings
from src.promtior_assistant.config import settings

embeddings = create_embeddings()
db = Chroma(persist_directory=settings.chroma_persist_directory, embedding_function=embeddings)
print(f'Total documents: {db._collection.count()}')
"

# Limpiar y empezar de cero
rm -rf data/chroma_db
make clean
make ingest

# Ver logs de Ollama
docker logs promtior-ollama -f

# Verificar metadata de embeddings
cat data/chroma_db/embedding_metadata.json
```

---

## Métricas de Calidad RAG

Para evaluar la calidad de tu RAG:

1. **Precisión**: ¿Las respuestas son correctas?
2. **Recall**: ¿Encuentra toda la información disponible?
3. **Concisión**: ¿Las respuestas son concisas (2-3 frases)?
4. **Multi-idioma**: ¿Responde en el idioma de la pregunta?
5. **Consistencia**: ¿Responde igual a preguntas similares?

**Testing recomendado:**
- 10+ preguntas variadas (generales + específicas)
- 50%+ en cada idioma (español + inglés)
- Verificar que k=5 es suficiente para tus casos de uso

---

**Última actualización**: 2026-02-21
**Versión RAG**: v2.1 (k=5, chunk_size=1500)
