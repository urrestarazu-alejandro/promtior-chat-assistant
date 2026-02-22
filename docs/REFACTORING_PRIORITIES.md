# Plan de Refactoring por Prioridades

> **Objetivo**: Implementar mejoras de prioridad ALTA y MEDIA en 1 día (6-8 horas)

---

## PRIORIDAD ALTA 🔴 (Crítico - 2-3 horas)

Problemas que causan **10-20x degradación de performance** o bloquean funcionalidad.

### 1.1 Container Singleton Pattern + Lifespan Events
**Impacto**: 10-20x mejor performance (evita recrear conexiones en cada request)

| Tarea | Archivo | Esfuerzo |
|-------|---------|----------|
| Crear `infrastructure/container.py` | `src/promtior_assistant/infrastructure/container.py` | 1h |
| Crear `infrastructure/factories.py` | `src/promtior_assistant/infrastructure/factories.py` | 30min |
| Agregar lifespan events a `main.py` | `src/promtior_assistant/main.py` | 30min |
| Tests de verificación | - | 30min |

**Código existente que se reemplaza**: `@lru_cache` en `rag.py`

---

### 1.2 Corregir Async/Await (httpx.AsyncClient)
**Impacto**: Elimina bloqueo del event loop

| Tarea | Archivo | Esfuerzo |
|-------|---------|----------|
| Cambiar `httpx.Client` → `httpx.AsyncClient` | `infrastructure/llm/ollama_adapter.py` | 15min |
| Cambiar `time.sleep()` → `asyncio.sleep()` | `services/rag_service.py` | 15min |
| Tests de verificación | - | 15min |

**Nota**: Esto evita que todas las requests se bloqueen cuando una está esperando respuesta del LLM.

---

## PRIORIDAD MEDIA 🟡 (Importante - 3-4 horas)

Mejoras arquitecturales que facilitan testing y mantenimiento.

### 2.1 Separación de Responsabilidades
**Impacto**: Código más mantenible y testeable

| Tarea | Archivo Destino | Esfuerzo |
|-------|-----------------|----------|
| Mover `InputValidator` + `OutputValidator` | `domain/services/validators.py` | 20min |
| Mover `UsageTracker` | `infrastructure/persistence/usage_tracker.py` | 20min |
| Mover `CustomOllamaChat` | `infrastructure/llm/ollama_adapter.py` | 20min |
| Mover `CustomOllamaEmbeddings` | `infrastructure/embeddings/ollama_embeddings.py` | 20min |
| Crear `services/rag_service.py` (reorganizado) | `src/promtior_assistant/services/rag_service.py` | 30min |
| Actualizar imports | Varios | 20min |
| Tests de regresión | - | 30min |

---

### 2.2 Pydantic V2 Schemas (Request/Response)
**Impacto**: Validación automática, mejor OpenAPI docs

| Tarea | Archivo | Esfuerzo |
|-------|---------|----------|
| Crear `presentation/schemas/request.py` | `src/promtior_assistant/presentation/schemas/request.py` | 20min |
| Crear `presentation/schemas/response.py` | `src/promtior_assistant/presentation/schemas/response.py` | 20min |
| Actualizar routes | `presentation/api/v1/routes.py` | 20min |

---

### 2.3 Estructura de Directorios Base
**Impacto**: Organización necesaria para las otras tareas

| Tarea | Comando | Esfuerzo |
|-------|---------|----------|
| Crear directorios | `mkdir -p domain/services infrastructure/llm infrastructure/embeddings infrastructure/vector_store infrastructure/persistence services presentation/api/v1 presentation/schemas` | 10min |

---

## PRIORIDAD BAJA 🟢 (2-3 horas)

Mejoras nice-to-have para producción.

### 3.1 Middleware Stack
| Tarea | Esfuerzo |
|-------|----------|
| RequestIDMiddleware | 20min |
| LoggingMiddleware | 20min |
| TimeoutMiddleware | 20min |

### 3.2 Custom Exception Handlers
| Tarea | Esfuerzo |
|-------|----------|
| Exception handlers | 20min |
| Registro en main.py | 10min |

### 3.3 Health Checks Production-Ready
| Tarea | Esfuerzo |
|-------|----------|
| `/health/live` endpoint | 15min |
| `/health/ready` endpoint | 15min |

---

## OPCIONAL 🌙 (Fuera de scope)

- Fase 2 completa (Puertos + Adaptadores)
- Clean Architecture completa
- Tests con >80% cobertura
- mypy strict mode

---

## Timeline Sugerido (1 día)

```
09:00 - 09:30  → Estructura de directorios
09:30 - 10:30  → Container + Factories + Lifespan
10:30 - 11:00  → Async/Await fix
11:00 - 12:00  → Separación de responsabilidades
12:00 - 13:00  → ALMUERZO
13:00 - 14:00  → Pydantic schemas
14:00 - 15:00  → Tests + verificación
```

---

## Verificación Post-Implementación

```bash
# Tests deben pasar
make test

# API debe funcionar
curl http://localhost:8000/health
curl "http://localhost:8000/ask?q=test"

# Logs deben mostrar startup/shutdown correcto
# No debe haber errores de imports
uv run ruff check src/
```

---

## Archivos a Modificar/Crear

### Nuevos archivos
- `src/promtior_assistant/domain/__init__.py`
- `src/promtior_assistant/domain/services/__init__.py`
- `src/promtior_assistant/domain/services/validators.py` ✨
- `src/promtior_assistant/infrastructure/__init__.py`
- `src/promtior_assistant/infrastructure/container.py` ✨
- `src/promtior_assistant/infrastructure/factories.py` ✨
- `src/promtior_assistant/infrastructure/llm/__init__.py`
- `src/promtior_assistant/infrastructure/embeddings/__init__.py`
- `src/promtior_assistant/infrastructure/vector_store/__init__.py`
- `src/promtior_assistant/infrastructure/persistence/__init__.py`
- `src/promtior_assistant/infrastructure/persistence/usage_tracker.py` ✨
- `src/promtior_assistant/services/__init__.py`
- `src/promtior_assistant/services/rag_service.py` ✨
- `src/promtior_assistant/presentation/__init__.py`
- `src/promtior_assistant/presentation/api/__init__.py`
- `src/promtior_assistant/presentation/api/v1/__init__.py`
- `src/promtior_assistant/presentation/schemas/__init__.py`
- `src/promtior_assistant/presentation/schemas/request.py` ✨
- `src/promtior_assistant/presentation/schemas/response.py` ✨

### Archivos a modificar
- `src/promtior_assistant/main.py` (lifespan + imports)
- `src/promtior_assistant/rag.py` (limpiar, mantener compat)
- `src/promtior_assistant/ingest.py` (actualizar imports)

✨ = Alta prioridad
