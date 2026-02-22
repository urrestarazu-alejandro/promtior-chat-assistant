# Fase 2 - Adiciones FastAPI Pro

> **Estado**: ✅ COMPLETADO
> Este documento complementa el ARCHITECTURE_REFACTORING_PLAN.md con las tareas adicionales
> identificadas en la revisión de FastAPI Pro.

## Tareas Adicionales para Fase 2

### 2.1.5 ✨ Corregir Async/Await en Ollama Adapter
**Duración**: 1 hora
**Prioridad**: 🔴 CRÍTICA

**Problema**: El adaptador de Ollama usa `httpx.Client` (síncrono) dentro de funciones async, bloqueando el event loop.

**Archivo**: `src/promtior_assistant/infrastructure/llm/ollama_adapter.py`

```python
"""Ollama LLM adapter with CORRECT async implementation."""

import os
import httpx  # Async client
from pydantic import ConfigDict

from ...config import settings
from ...domain.ports.llm_port import LLMPort


class OllamaAdapter:
    """Adapter for Ollama LLM provider (async-first)."""

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "llama2",
        temperature: float = 0.7,
    ):
        self._base_url = base_url
        self._model = model
        self._temperature = temperature
        # ✅ Reuse async client (connection pooling)
        self._client: httpx.AsyncClient | None = None

    def _get_headers(self) -> dict[str, str]:
        """Get authorization headers if using remote Ollama."""
        is_remote = "localhost" not in self._base_url and "127.0.0.1" not in self._base_url
        headers = {}

        if is_remote:
            api_key = (
                settings.ollama_api_key
                or os.getenv("OLLAMA_API_KEY")
                or os.getenv("OLLAMA_AUTH_TOKEN")
            )
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"

        return headers

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create async HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=120.0)
        return self._client

    async def generate(self, prompt: str, temperature: float = 0.7) -> str:
        """Generate text from prompt using Ollama.

        Args:
            prompt: Input prompt
            temperature: Sampling temperature

        Returns:
            Generated text

        Raises:
            Exception: If API call fails
        """
        client = await self._get_client()

        # ✅ CORRECTO: await en llamada HTTP async
        response = await client.post(
            f"{self._base_url}/api/chat",
            json={
                "model": self._model,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
                "temperature": temperature or self._temperature,
            },
            headers=self._get_headers(),
        )

        if response.status_code != 200:
            raise Exception(f"Ollama API error: {response.status_code} - {response.text}")

        result = response.json()
        return result["message"]["content"]

    @property
    def model_name(self) -> str:
        """Get model name."""
        return self._model

    async def close(self):
        """Close HTTP client connection."""
        if self._client:
            await self._client.aclose()
            self._client = None
```

**Archivo**: `src/promtior_assistant/infrastructure/embeddings/ollama_embeddings.py`

Aplicar el mismo patrón (httpx.AsyncClient) a los embeddings.

---

### 2.1.6 ✨ Corregir Async/Await en Use Case
**Duración**: 30 minutos
**Prioridad**: 🔴 CRÍTICA

**Problema**: `time.sleep()` bloquea el event loop. Usar `asyncio.sleep()`.

**Archivo**: `src/promtior_assistant/application/use_cases/answer_question.py`

```python
"""Use case: Answer a question using RAG."""

import logging
import asyncio  # ✅ Usar asyncio en lugar de time

from ...domain.services.validators import InputValidator, OutputValidator
from ...domain.ports.llm_port import LLMPort
from ...domain.ports.vector_store_port import VectorStorePort

logger = logging.getLogger(__name__)


class AnswerQuestionUseCase:
    """Use case for answering questions using RAG."""

    def __init__(
        self,
        llm: LLMPort,
        vector_store: VectorStorePort,
        input_validator: InputValidator,
        output_validator: OutputValidator,
    ):
        self._llm = llm
        self._vector_store = vector_store
        self._input_validator = input_validator
        self._output_validator = output_validator

    def _build_prompt(self, question: str, context: str) -> str:
        """Build prompt for LLM."""
        return f"""Eres un asistente que responde preguntas sobre Promtior...

Contexto: {context}

Pregunta: {question}

Respuesta:"""

    async def execute(self, question: str) -> str:
        """Execute the use case."""
        validated_question = self._input_validator.validate(question)

        max_retries = 3
        last_error = None

        for attempt in range(max_retries):
            try:
                documents = await self._vector_store.retrieve_documents(
                    query=validated_question,
                    k=3,
                )

                context = "\n\n".join(doc.page_content for doc in documents)
                prompt = self._build_prompt(validated_question, context)
                answer = await self._llm.generate(prompt, temperature=0.7)
                validated_answer = self._output_validator.validate(answer)

                return validated_answer

            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    wait_time = 2**attempt
                    logger.warning(
                        f"RAG call failed (attempt {attempt + 1}/{max_retries}), "
                        f"retrying in {wait_time}s: {e}"
                    )
                    # ✅ CORRECTO: asyncio.sleep en lugar de time.sleep
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"RAG call failed after {max_retries} attempts: {e}")

        raise Exception(
            f"Failed to generate RAG answer after {max_retries} attempts: {last_error}"
        )
```

---

### 2.3.5 ✨ Crear Pydantic Request/Response Schemas
**Duración**: 2 horas
**Prioridad**: 🟡 ALTA

**Archivo**: `src/promtior_assistant/presentation/schemas/request.py`

```python
"""Pydantic request schemas."""

from pydantic import BaseModel, Field, ConfigDict


class AskQuestionRequest(BaseModel):
    """Request schema for asking questions."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"question": "¿Qué servicios ofrece Promtior?"}
            ]
        }
    )

    question: str = Field(
        ...,
        min_length=3,
        max_length=2000,
        description="Question about Promtior",
        examples=["¿Qué servicios ofrece Promtior?"],
    )
```

**Archivo**: `src/promtior_assistant/presentation/schemas/response.py`

```python
"""Pydantic response schemas."""

from enum import Enum
from typing import Any
from pydantic import BaseModel, Field


class ResponseStatus(str, Enum):
    """Response status enum."""
    SUCCESS = "success"
    ERROR = "error"


class AskQuestionResponse(BaseModel):
    """Response schema for question answers."""

    question: str = Field(..., description="Original question")
    answer: str = Field(..., description="Generated answer")
    status: ResponseStatus = Field(default=ResponseStatus.SUCCESS)
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata (model, tokens, etc.)"
    )


class ErrorResponse(BaseModel):
    """Error response schema."""

    detail: str = Field(..., description="Error description")
    status: ResponseStatus = Field(default=ResponseStatus.ERROR)
    error_code: str | None = Field(None, description="Error code")
```

**Archivo**: `src/promtior_assistant/presentation/schemas/health.py`

```python
"""Health check schemas."""

from enum import Enum
from pydantic import BaseModel


class HealthStatus(str, Enum):
    """Health status enum."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class ComponentHealth(BaseModel):
    """Component health status."""
    status: HealthStatus
    latency_ms: float | None = None
    error: str | None = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: HealthStatus
    version: str
    environment: str
    components: dict[str, ComponentHealth]
```

---

### 2.3.6 ✨ Implementar Custom Exception Handlers
**Duración**: 1.5 horas
**Prioridad**: 🟡 MEDIA

**Archivo**: `src/promtior_assistant/presentation/api/exceptions.py`

```python
"""Custom exceptions and exception handlers."""

import logging
from fastapi import Request, status
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class BusinessRuleException(Exception):
    """Business rule violation."""

    def __init__(self, message: str, error_code: str = "BUSINESS_RULE_ERROR"):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class LLMProviderException(Exception):
    """LLM provider error."""
    pass


class VectorStoreException(Exception):
    """Vector store error."""
    pass


class ValidationException(Exception):
    """Input/output validation error."""

    def __init__(self, message: str, field: str | None = None):
        self.message = message
        self.field = field
        super().__init__(self.message)


async def business_rule_exception_handler(
    request: Request,
    exc: BusinessRuleException
) -> JSONResponse:
    """Handle business rule violations."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "detail": exc.message,
            "error_code": exc.error_code,
            "status": "error",
        },
    )


async def llm_provider_exception_handler(
    request: Request,
    exc: LLMProviderException
) -> JSONResponse:
    """Handle LLM provider errors."""
    logger.error(f"LLM provider error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "detail": "AI service temporarily unavailable. Please try again later.",
            "error_code": "LLM_UNAVAILABLE",
            "status": "error",
        },
    )


async def vector_store_exception_handler(
    request: Request,
    exc: VectorStoreException
) -> JSONResponse:
    """Handle vector store errors."""
    logger.error(f"Vector store error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "detail": "Knowledge base temporarily unavailable. Please try again later.",
            "error_code": "VECTOR_STORE_UNAVAILABLE",
            "status": "error",
        },
    )


async def validation_exception_handler(
    request: Request,
    exc: ValidationException
) -> JSONResponse:
    """Handle validation errors."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": exc.message,
            "error_code": "VALIDATION_ERROR",
            "field": exc.field,
            "status": "error",
        },
    )


def register_exception_handlers(app):
    """Register all custom exception handlers."""
    app.add_exception_handler(BusinessRuleException, business_rule_exception_handler)
    app.add_exception_handler(LLMProviderException, llm_provider_exception_handler)
    app.add_exception_handler(VectorStoreException, vector_store_exception_handler)
    app.add_exception_handler(ValidationException, validation_exception_handler)
```

Actualizar `main.py`:

```python
from .presentation.api.exceptions import register_exception_handlers

app = FastAPI(...)
register_exception_handlers(app)
```

---

### 2.3.7 ✨ Agregar Middleware Stack
**Duración**: 2 horas
**Prioridad**: 🟡 ALTA

**Archivo**: `src/promtior_assistant/presentation/api/middleware/request_id.py`

```python
"""Request ID middleware."""

import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Add unique request ID to each request."""

    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
```

**Archivo**: `src/promtior_assistant/presentation/api/middleware/logging_middleware.py`

```python
"""Logging middleware."""

import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Log all HTTP requests with structured logging."""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        request_id = getattr(request.state, "request_id", "unknown")

        # Log request
        logger.info(
            "Request started",
            extra={
                "request_id": request_id,
                "method": request.method,
                "url": str(request.url),
                "client": request.client.host if request.client else None,
            }
        )

        response = await call_next(request)

        # Log response
        duration = time.time() - start_time
        logger.info(
            "Request completed",
            extra={
                "request_id": request_id,
                "status_code": response.status_code,
                "duration_ms": round(duration * 1000, 2),
            }
        )

        return response
```

**Archivo**: `src/promtior_assistant/presentation/api/middleware/timeout.py`

```python
"""Timeout middleware."""

import asyncio
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from fastapi import HTTPException, status


class TimeoutMiddleware(BaseHTTPMiddleware):
    """Global timeout for all requests."""

    def __init__(self, app, timeout: float = 30.0):
        super().__init__(app)
        self.timeout = timeout

    async def dispatch(self, request: Request, call_next):
        try:
            return await asyncio.wait_for(
                call_next(request),
                timeout=self.timeout
            )
        except asyncio.TimeoutError:
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Request timeout exceeded"
            )
```

Actualizar `main.py`:

```python
from .presentation.api.middleware.request_id import RequestIDMiddleware
from .presentation.api.middleware.logging_middleware import LoggingMiddleware
from .presentation.api.middleware.timeout import TimeoutMiddleware

# Add middleware (order matters!)
app.add_middleware(TimeoutMiddleware, timeout=30.0)
app.add_middleware(LoggingMiddleware)
app.add_middleware(RequestIDMiddleware)
```

---

### 2.3.8 ✨ Health Checks Production-Ready
**Duración**: 1.5 horas
**Prioridad**: 🟡 MEDIA

**Archivo**: `src/promtior_assistant/presentation/api/v1/health.py`

```python
"""Health check endpoints."""

import time
from fastapi import APIRouter, status, HTTPException

from ....infrastructure.container import Container
from ...schemas.health import HealthResponse, HealthStatus, ComponentHealth

router = APIRouter(tags=["health"])


async def check_llm_health() -> ComponentHealth:
    """Check LLM provider health."""
    try:
        start = time.time()
        llm = Container.get_llm()
        # Simple health check
        await llm.generate("ping", temperature=0)
        latency = (time.time() - start) * 1000
        return ComponentHealth(status=HealthStatus.HEALTHY, latency_ms=round(latency, 2))
    except Exception as e:
        return ComponentHealth(
            status=HealthStatus.UNHEALTHY,
            error=str(e)
        )


async def check_vector_store_health() -> ComponentHealth:
    """Check vector store health."""
    try:
        start = time.time()
        vector_store = Container.get_vector_store()
        # Simple health check
        await vector_store.retrieve_documents("ping", k=1)
        latency = (time.time() - start) * 1000
        return ComponentHealth(status=HealthStatus.HEALTHY, latency_ms=round(latency, 2))
    except Exception as e:
        return ComponentHealth(
            status=HealthStatus.UNHEALTHY,
            error=str(e)
        )


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
)
async def health_check() -> HealthResponse:
    """Comprehensive health check."""
    components = {
        "llm": await check_llm_health(),
        "vector_store": await check_vector_store_health(),
    }

    # Determine overall status
    if all(c.status == HealthStatus.HEALTHY for c in components.values()):
        overall_status = HealthStatus.HEALTHY
    elif any(c.status == HealthStatus.UNHEALTHY for c in components.values()):
        overall_status = HealthStatus.UNHEALTHY
    else:
        overall_status = HealthStatus.DEGRADED

    return HealthResponse(
        status=overall_status,
        version="0.1.0",
        environment=settings.environment,
        components=components,
    )


@router.get(
    "/health/live",
    status_code=status.HTTP_200_OK,
)
async def liveness():
    """Kubernetes liveness probe."""
    return {"status": "ok"}


@router.get(
    "/health/ready",
    status_code=status.HTTP_200_OK,
)
async def readiness():
    """Kubernetes readiness probe."""
    try:
        Container.get_llm()
        Container.get_vector_store()
        return {"status": "ready"}
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service not ready"
        )
```

---

### 2.5 Actualizar Routes con Pydantic y Annotated
**Duración**: 1 hora

**Archivo**: `src/promtior_assistant/presentation/api/v1/routes.py`

```python
"""API routes v1 with Pydantic schemas and Annotated types."""

from typing import Annotated
from fastapi import APIRouter, Depends, status

from ....application.use_cases.answer_question import AnswerQuestionUseCase
from ...schemas.request import AskQuestionRequest
from ...schemas.response import AskQuestionResponse, ErrorResponse, ResponseStatus
from .dependencies import get_answer_question_use_case

router = APIRouter()


@router.post(
    "/ask",
    response_model=AskQuestionResponse,
    status_code=status.HTTP_200_OK,
    responses={
        500: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        503: {"model": ErrorResponse},
    },
    summary="Ask a question about Promtior",
    description="Submit a question and receive an AI-generated answer using RAG",
)
async def ask_question(
    request: AskQuestionRequest,
    use_case: Annotated[
        AnswerQuestionUseCase,
        Depends(get_answer_question_use_case)
    ],
) -> AskQuestionResponse:
    """Ask a question about Promtior using RAG."""
    answer = await use_case.execute(request.question)

    return AskQuestionResponse(
        question=request.question,
        answer=answer,
        status=ResponseStatus.SUCCESS,
        metadata={
            "model": use_case._llm.model_name,
            "provider": settings.llm_provider,
        }
    )
```

**Actualizar dependencies.py**:

```python
"""Dependency injection for FastAPI."""

from ....application.use_cases.answer_question import AnswerQuestionUseCase
from ....domain.services.validators import InputValidator, OutputValidator
from ....infrastructure.container import Container


def get_answer_question_use_case() -> AnswerQuestionUseCase:
    """Create AnswerQuestionUseCase with Container dependencies.

    Returns:
        Configured use case with singleton dependencies
    """
    return AnswerQuestionUseCase(
        llm=Container.get_llm(),
        vector_store=Container.get_vector_store(),
        input_validator=InputValidator(),
        output_validator=OutputValidator(),
    )
```

---

## Criterios de Aceptación Adicionales - Fase 2

### ✨ Async/Await Correctness
- [x] `httpx.AsyncClient` usado en todos los adaptadores HTTP
- [x] `asyncio.sleep()` usado en lugar de `time.sleep()`
- [x] No hay llamadas bloqueantes en funciones async
- [x] Connection pooling funciona correctamente

### ✨ Pydantic V2 Schemas
- [x] Request schemas en `presentation/schemas/request.py`
- [x] Response schemas en `presentation/schemas/response.py`
- [x] Health schemas en `presentation/schemas/health.py`
- [x] Validación automática funciona
- [x] OpenAPI docs muestran schemas correctamente

### ✨ Custom Exception Handlers
- [x] Exception handlers en `presentation/api/exceptions.py`
- [x] Handlers registrados en `main.py`
- [x] Errores de negocio retornan 400
- [x] Errores de LLM retornan 503
- [x] Validación retorna 422

### ✨ Middleware Stack
- [x] RequestID middleware implementado
- [x] Logging middleware implementado
- [x] Timeout middleware implementado
- [x] Middleware registrados en orden correcto
- [x] Logs estructurados muestran request_id

### ✨ Health Checks
- [x] `/health` endpoint con componentes
- [x] `/health/live` para Kubernetes liveness
- [x] `/health/ready` para Kubernetes readiness
- [x] Health checks no bloquean startup
- [x] Respuestas usan Pydantic schemas
