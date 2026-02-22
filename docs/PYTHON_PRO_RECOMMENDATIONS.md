# Python Pro Recommendations - Anexo al Plan de Refactoring

> **Documento**: Anexo - Recomendaciones Python 3.12+ Expert
> **Versión**: 1.0
> **Fecha**: 2026-02-21
> **Estado**: ⏸️ Pendiente - No iniciado
> **Nota**: Dependiente de completarse después de ARCHITECTURE_REFACTORING_PLAN.md

---

## Tabla de Contenidos

1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Type Safety & Type Checking](#type-safety--type-checking)
3. [Modern Python Tooling](#modern-python-tooling)
4. [Python 3.12+ Patterns](#python-312-patterns)
5. [Performance & Profiling](#performance--profiling)
6. [Security Best Practices](#security-best-practices)
7. [Testing Enhancements](#testing-enhancements)
8. [Code Quality & Maintainability](#code-quality--maintainability)
9. [Implementation Checklist](#implementation-checklist)

---

## Resumen Ejecutivo

Este documento complementa el plan de refactoring arquitectural con recomendaciones específicas de **Python 3.12+** para asegurar que el código cumpla con los más altos estándares de calidad, performance y mantenibilidad del ecosistema Python moderno (2024-2025).

### Prioridades

| Prioridad | Categoría | Impacto | Esfuerzo |
|-----------|-----------|---------|----------|
| 🔴 **CRÍTICA** | Type Checking (mypy/pyright) | Alto | Medio |
| 🔴 **CRÍTICA** | Security Scanning (bandit) | Alto | Bajo |
| 🟡 **ALTA** | Pre-commit Hooks | Medio | Bajo |
| 🟡 **ALTA** | Enhanced Ruff Config | Medio | Bajo |
| 🟡 **ALTA** | pytest-cov Coverage | Alto | Bajo |
| 🟢 **MEDIA** | Property-based Testing | Medio | Medio |
| 🟢 **MEDIA** | Performance Profiling | Medio | Bajo |
| 🟢 **BAJA** | Advanced Type Hints | Bajo | Medio |

---

## Type Safety & Type Checking

### 1.1 Configurar mypy para Type Checking Estricto

**Prioridad**: 🔴 CRÍTICA
**Esfuerzo**: 2-3 horas
**Beneficio**: Prevenir ~40% de bugs antes de runtime

#### Agregar mypy a dependencies

Actualizar `pyproject.toml`:

```toml
[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "mypy>=1.8.0",  # ✨ Type checker
    "types-requests>=2.31.0",  # Type stubs
]
```

#### Configurar mypy strict mode

Agregar a `pyproject.toml`:

```toml
[tool.mypy]
python_version = "3.12"
strict = true
warn_return_any = true
warn_unused_configs = true
warn_redundant_casts = true
warn_unused_ignores = true
disallow_untyped_defs = true
disallow_any_unimported = true
no_implicit_optional = true
show_error_codes = true
show_error_context = true
pretty = true

# Per-module options
[[tool.mypy.overrides]]
module = "langchain.*"
ignore_missing_imports = true

[[tool.mypy.overrides]]
module = "langchain_core.*"
ignore_missing_imports = true

[[tool.mypy.overrides]]
module = "langchain_chroma.*"
ignore_missing_imports = true

[[tool.mypy.overrides]]
module = "langchain_openai.*"
ignore_missing_imports = true
```

#### Agregar type hints completos

**Ejemplo - Before (sin type hints)**:
```python
def create_llm():
    if settings.llm_provider == "openai":
        return OpenAIAdapter(...)
    return OllamaAdapter(...)
```

**Ejemplo - After (con type hints)**:
```python
def create_llm() -> LLMPort:
    """Create LLM adapter based on configuration.

    Returns:
        LLM adapter instance

    Raises:
        ValueError: If configuration is invalid
    """
    if settings.llm_provider == "openai":
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required")
        return OpenAIAdapter(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
        )
    return OllamaAdapter(
        base_url=settings.ollama_base_url,
        model=settings.ollama_model,
    )
```

#### Usar Protocol typing en lugar de ABC

**Ventaja**: Más flexible, compatible con duck typing de Python

**Ejemplo - Ports con Protocol**:
```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class LLMPort(Protocol):
    """Port for Language Model providers."""

    async def generate(self, prompt: str, temperature: float = 0.7) -> str:
        """Generate text from a prompt."""
        ...

    @property
    def model_name(self) -> str:
        """Get the model name."""
        ...
```

**Beneficios**:
- No requiere herencia explícita
- Más pythonic
- Compatible con structural subtyping
- Mejor para testing (mock objects automáticos)

---

### 1.2 Configurar pyright (Alternativa a mypy)

**Prioridad**: 🟢 MEDIA (elegir mypy O pyright)
**Esfuerzo**: 1 hora

**Ventajas de pyright**:
- Más rápido que mypy (escrito en Node.js)
- Mejor integración con VS Code
- Type narrowing más inteligente
- Mejor soporte para generics

Agregar `pyrightconfig.json`:

```json
{
  "include": ["src"],
  "exclude": ["**/node_modules", "**/__pycache__", ".venv"],
  "pythonVersion": "3.12",
  "pythonPlatform": "All",
  "typeCheckingMode": "strict",
  "reportMissingImports": true,
  "reportMissingTypeStubs": true,
  "reportUnusedImport": true,
  "reportUnusedClass": true,
  "reportUnusedFunction": true,
  "reportUnusedVariable": true,
  "reportDuplicateImport": true,
  "reportOptionalMemberAccess": true,
  "reportOptionalCall": true,
  "reportOptionalIterable": true,
  "reportOptionalContextManager": true,
  "reportOptionalOperand": true,
  "reportTypedDictNotRequiredAccess": "warning"
}
```

---

### 1.3 Type Stubs para Third-Party Libraries

**Prioridad**: 🟡 ALTA
**Esfuerzo**: 30 minutos

Agregar type stubs:

```toml
[project.optional-dependencies]
dev = [
    # ... existing deps
    "types-requests>=2.31.0",
    "types-beautifulsoup4>=4.12.0",
    "types-Pygments>=2.17.0",
]
```

---

## Modern Python Tooling

### 2.1 Enhanced Ruff Configuration

**Prioridad**: 🟡 ALTA
**Esfuerzo**: 1 hora
**Beneficio**: Detectar 50+ tipos de problemas adicionales

Actualizar `pyproject.toml`:

```toml
[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
# Habilitar muchos más linters
select = [
    "E",      # pycodestyle errors
    "W",      # pycodestyle warnings
    "F",      # pyflakes
    "I",      # isort
    "B",      # ✨ flake8-bugbear (bugs comunes)
    "C4",     # ✨ flake8-comprehensions (list/dict comprehensions)
    "UP",     # ✨ pyupgrade (syntax moderno)
    "S",      # ✨ flake8-bandit (security)
    "T20",    # ✨ flake8-print (no print statements)
    "SIM",    # ✨ flake8-simplify (simplificaciones)
    "TCH",    # ✨ flake8-type-checking (TYPE_CHECKING imports)
    "RUF",    # ✨ Ruff-specific rules
    "N",      # ✨ pep8-naming
    "D",      # ✨ pydocstyle (docstrings)
    "ANN",    # ✨ flake8-annotations (type hints)
    "ASYNC",  # ✨ flake8-async (async best practices)
    "A",      # ✨ flake8-builtins (shadowing builtins)
    "COM",    # ✨ flake8-commas
    "C90",    # ✨ mccabe (complexity)
    "DTZ",    # ✨ flake8-datetimez (timezone aware)
    "EM",     # ✨ flake8-errmsg
    "ISC",    # ✨ flake8-implicit-str-concat
    "ICN",    # ✨ flake8-import-conventions
    "G",      # ✨ flake8-logging-format
    "PIE",    # ✨ flake8-pie (misc lints)
    "PT",     # ✨ flake8-pytest-style
    "Q",      # ✨ flake8-quotes
    "RSE",    # ✨ flake8-raise
    "RET",    # ✨ flake8-return
    "SLF",    # ✨ flake8-self (private access)
    "SLOT",   # ✨ flake8-slots
    "TID",    # ✨ flake8-tidy-imports
    "ARG",    # ✨ flake8-unused-arguments
    "PTH",    # ✨ flake8-use-pathlib
    "ERA",    # ✨ eradicate (commented code)
    "PL",     # ✨ Pylint
    "TRY",    # ✨ tryceratops (exception handling)
    "FLY",    # ✨ flynt (f-strings)
    "PERF",   # ✨ Perflint (performance)
    "FURB",   # ✨ refurb (modernization)
    "LOG",    # ✨ flake8-logging
]

ignore = [
    "D100",   # Missing docstring in public module
    "D104",   # Missing docstring in public package
    "ANN101", # Missing type annotation for self
    "ANN102", # Missing type annotation for cls
    "COM812", # Trailing comma missing (conflicts with formatter)
    "ISC001", # Single line implicit string concatenation
]

# Allow autofix for all enabled rules
fixable = ["ALL"]
unfixable = []

[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = [
    "S101",   # Use of assert
    "ARG",    # Unused function arguments (fixtures)
    "PLR2004", # Magic value used in comparison
]

[tool.ruff.lint.mccabe]
max-complexity = 10  # ✨ Complejidad ciclomática máxima

[tool.ruff.lint.pydocstyle]
convention = "google"  # ✨ Google-style docstrings

[tool.ruff.lint.pylint]
max-args = 6  # ✨ Máximo argumentos por función
max-branches = 12
max-returns = 6
max-statements = 50

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
skip-magic-trailing-comma = false
line-ending = "auto"
```

**Beneficios**:
- Detecta bugs comunes (B)
- Previene problemas de seguridad (S)
- Moderniza syntax (UP, FURB)
- Mejora performance (PERF)
- Enforza docstrings (D)
- Async best practices (ASYNC)

---

### 2.2 Pre-commit Hooks

**Prioridad**: 🟡 ALTA
**Esfuerzo**: 30 minutos
**Beneficio**: Prevenir commits con código problemático

Crear `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-json
      - id: check-toml
      - id: check-merge-conflict
      - id: detect-private-key

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.15
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies:
          - types-requests
          - pydantic>=2.0

  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.6
    hooks:
      - id: bandit
        args: ["-c", "pyproject.toml"]
        additional_dependencies: ["bandit[toml]"]

  - repo: https://github.com/python-poetry/poetry
    rev: 1.7.0
    hooks:
      - id: poetry-check
```

Instalar pre-commit:

```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files  # Test inicial
```

---

### 2.3 pytest-cov para Coverage Tracking

**Prioridad**: 🟡 ALTA
**Esfuerzo**: 30 minutos
**Beneficio**: Asegurar >80% cobertura de tests

Actualizar `pyproject.toml`:

```toml
[project.optional-dependencies]
dev = [
    # ... existing
    "pytest-cov>=4.1.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
markers = [
    "integration: Integration tests that require Ollama running",
    "unit: Unit tests that don't require external dependencies",
]

# ✨ Coverage configuration
addopts = [
    "--cov=src/promtior_assistant",
    "--cov-report=html",
    "--cov-report=term-missing",
    "--cov-fail-under=80",  # Fail if coverage < 80%
]

[tool.coverage.run]
source = ["src"]
omit = [
    "*/tests/*",
    "*/__pycache__/*",
    "*/site-packages/*",
    "*/venv/*",
]
branch = true  # ✨ Branch coverage

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if TYPE_CHECKING:",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "pass",
    "\\.\\.\\.",  # Ellipsis
]
precision = 2
show_missing = true
skip_covered = false

[tool.coverage.html]
directory = "htmlcov"
```

Comandos útiles:

```bash
# Run tests con coverage
pytest --cov

# Coverage report HTML
pytest --cov --cov-report=html
open htmlcov/index.html

# Coverage report detallado
pytest --cov --cov-report=term-missing

# Fail si coverage < 80%
pytest --cov --cov-fail-under=80
```

---

## Python 3.12+ Patterns

### 3.1 Structural Pattern Matching

**Prioridad**: 🟢 MEDIA
**Esfuerzo**: 1-2 horas
**Python Version**: 3.10+

Usar pattern matching para código más limpio.

**Ejemplo - Factory con match/case**:

```python
# Before (if/elif)
def create_llm() -> LLMPort:
    if settings.llm_provider == "openai":
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required")
        return OpenAIAdapter(...)
    elif settings.llm_provider == "ollama":
        return OllamaAdapter(...)
    else:
        raise ValueError(f"Unknown provider: {settings.llm_provider}")

# After (match/case) - Python 3.12+
def create_llm() -> LLMPort:
    """Create LLM adapter based on configuration."""
    match settings.llm_provider:
        case "openai":
            if not settings.openai_api_key:
                raise ValueError("OPENAI_API_KEY is required")
            return OpenAIAdapter(
                api_key=settings.openai_api_key,
                model=settings.openai_model,
            )
        case "ollama":
            return OllamaAdapter(
                base_url=settings.ollama_base_url,
                model=settings.ollama_model,
            )
        case _:
            raise ValueError(f"Unknown LLM provider: {settings.llm_provider}")
```

**Ejemplo - Error handling con pattern matching**:

```python
from typing import Literal

ResponseType = Literal["success", "error", "timeout"]

def handle_llm_response(status: ResponseType, data: dict) -> str:
    """Handle LLM response based on status."""
    match (status, data):
        case ("success", {"content": str(content)}):
            return content
        case ("error", {"message": str(msg)}):
            raise LLMProviderException(msg)
        case ("timeout", _):
            raise TimeoutError("LLM request timed out")
        case _:
            raise ValueError(f"Unknown response: {status}, {data}")
```

---

### 3.2 Context Managers para Resource Management

**Prioridad**: 🟡 ALTA
**Esfuerzo**: 2 horas
**Beneficio**: Prevenir resource leaks

**Ejemplo - AsyncClient con context manager**:

```python
from contextlib import asynccontextmanager
from typing import AsyncIterator

class OllamaAdapter:
    """Ollama adapter with proper resource management."""

    def __init__(self, base_url: str, model: str):
        self._base_url = base_url
        self._model = model
        self._client: httpx.AsyncClient | None = None

    @asynccontextmanager
    async def _client_context(self) -> AsyncIterator[httpx.AsyncClient]:
        """Context manager for HTTP client."""
        client = httpx.AsyncClient(timeout=120.0)
        try:
            yield client
        finally:
            await client.aclose()

    async def generate(self, prompt: str, temperature: float = 0.7) -> str:
        """Generate text using Ollama."""
        async with self._client_context() as client:
            response = await client.post(
                f"{self._base_url}/api/chat",
                json={...},
            )
            if response.status_code != 200:
                raise Exception(f"Ollama error: {response.text}")
            return response.json()["message"]["content"]
```

**Ejemplo - Custom context manager para vector store**:

```python
from contextlib import asynccontextmanager

class ChromaVectorStoreAdapter:
    """ChromaDB adapter with connection management."""

    @asynccontextmanager
    async def transaction(self):
        """Database transaction context."""
        try:
            # Begin transaction
            await self._begin_transaction()
            yield self
            # Commit
            await self._commit()
        except Exception:
            # Rollback on error
            await self._rollback()
            raise
```

---

### 3.3 Modern Type Hints (Python 3.12+)

**Prioridad**: 🟢 BAJA
**Esfuerzo**: 2-3 horas
**Beneficio**: Mejor type safety

**Using `Self` for fluent interfaces**:

```python
from typing import Self

class QueryBuilder:
    """Fluent query builder."""

    def __init__(self):
        self._filters: list[str] = []

    def filter(self, field: str, value: str) -> Self:
        """Add filter (returns self for chaining)."""
        self._filters.append(f"{field}={value}")
        return self

    def limit(self, n: int) -> Self:
        """Set limit."""
        self._limit = n
        return self

# Usage
query = QueryBuilder().filter("status", "active").limit(10)
```

**Using `TypeGuard` for type narrowing**:

```python
from typing import TypeGuard

def is_valid_answer(value: str | None) -> TypeGuard[str]:
    """Check if value is a valid answer."""
    return value is not None and len(value.strip()) >= 5

def process_answer(answer: str | None) -> str:
    """Process answer with type narrowing."""
    if is_valid_answer(answer):
        # Type checker knows answer is str, not str | None
        return answer.upper()
    raise ValueError("Invalid answer")
```

**Using `TypedDict` for structured data**:

```python
from typing import TypedDict, NotRequired

class LLMResponse(TypedDict):
    """Type-safe LLM response structure."""
    content: str
    model: str
    tokens: NotRequired[int]  # Optional field
    cost: NotRequired[float]

def parse_response(data: dict) -> LLMResponse:
    """Parse response with type safety."""
    return {
        "content": data["content"],
        "model": data["model"],
        "tokens": data.get("tokens"),
        "cost": data.get("cost"),
    }
```

---

### 3.4 Dataclasses & Pydantic Best Practices

**Prioridad**: 🟡 ALTA
**Esfuerzo**: 1 hora

**Use frozen dataclasses for immutable value objects**:

```python
from dataclasses import dataclass, field

@dataclass(frozen=True, slots=True)
class Question:
    """Immutable question value object."""
    text: str
    language: str = "es"
    max_length: int = field(default=2000, repr=False)

    def __post_init__(self):
        """Validate on creation."""
        if len(self.text) > self.max_length:
            raise ValueError(f"Question too long: {len(self.text)} > {self.max_length}")
```

**Pydantic V2 validators**:

```python
from pydantic import BaseModel, Field, field_validator, model_validator

class AskQuestionRequest(BaseModel):
    """Request with custom validation."""

    question: str = Field(..., min_length=3, max_length=2000)
    language: str = Field(default="es", pattern="^(es|en)$")

    @field_validator("question")
    @classmethod
    def question_must_not_be_code(cls, v: str) -> str:
        """Prevent code injection."""
        forbidden = ["import", "exec", "eval", "__"]
        if any(word in v.lower() for word in forbidden):
            raise ValueError("Question contains forbidden keywords")
        return v

    @model_validator(mode="after")
    def check_spanish_question(self) -> Self:
        """Validate Spanish questions have '¿' prefix."""
        if self.language == "es" and not self.question.startswith("¿"):
            self.question = f"¿{self.question}"
        return self
```

---

## Performance & Profiling

### 4.1 Performance Profiling Setup

**Prioridad**: 🟢 MEDIA
**Esfuerzo**: 1 hora
**Beneficio**: Identificar bottlenecks

**Instalar profilers**:

```toml
[project.optional-dependencies]
dev = [
    # ... existing
    "py-spy>=0.3.14",       # ✨ Sampling profiler (no overhead)
    "memray>=1.11.0",       # ✨ Memory profiler
    "pytest-benchmark>=4.0.0",  # ✨ Benchmarking
]
```

**Profiling con py-spy**:

```bash
# Profile running application
py-spy record -o profile.svg -- python -m uvicorn src.promtior_assistant.main:app

# Profile tests
py-spy record -o test-profile.svg -- pytest tests/

# Top functions by CPU
py-spy top -- python -m uvicorn src.promtior_assistant.main:app
```

**Memory profiling con memray**:

```bash
# Record memory allocations
memray run -o memray.bin python -m uvicorn src.promtior_assistant.main:app

# Generate flamegraph
memray flamegraph memray.bin

# Generate table report
memray table memray.bin
```

**Benchmark tests con pytest-benchmark**:

```python
# tests/benchmark/test_rag_performance.py
import pytest

def test_answer_question_performance(benchmark, use_case):
    """Benchmark question answering."""
    result = benchmark(
        use_case.execute,
        "¿Qué servicios ofrece Promtior?"
    )

    # Assert performance
    assert benchmark.stats.mean < 2.0  # < 2s average
    assert benchmark.stats.stddev < 0.5  # Low variance
```

---

### 4.2 Async Performance Best Practices

**Prioridad**: 🟡 ALTA
**Esfuerzo**: 2 horas

**Use asyncio.gather for parallel operations**:

```python
import asyncio
from typing import Sequence

async def retrieve_from_multiple_sources(
    query: str,
    sources: Sequence[VectorStorePort]
) -> list[Document]:
    """Retrieve documents from multiple sources in parallel."""
    # ✅ Parallel retrieval (10x faster than sequential)
    results = await asyncio.gather(
        *[source.retrieve_documents(query, k=3) for source in sources],
        return_exceptions=True,  # Don't fail if one source fails
    )

    # Filter out exceptions
    documents = []
    for result in results:
        if not isinstance(result, Exception):
            documents.extend(result)

    return documents
```

**Use asyncio.timeout for better error handling** (Python 3.11+):

```python
import asyncio

async def generate_with_timeout(llm: LLMPort, prompt: str) -> str:
    """Generate with timeout."""
    async with asyncio.timeout(30.0):  # 30s timeout
        return await llm.generate(prompt)
    # Raises asyncio.TimeoutError if exceeds
```

**Connection pooling best practices**:

```python
class OllamaAdapter:
    """Adapter with connection pooling."""

    def __init__(self, base_url: str, model: str):
        self._base_url = base_url
        self._model = model
        # ✅ Configure connection pool limits
        self._client = httpx.AsyncClient(
            timeout=120.0,
            limits=httpx.Limits(
                max_keepalive_connections=20,
                max_connections=100,
                keepalive_expiry=30.0,
            ),
        )
```

---

## Security Best Practices

### 5.1 Security Scanning con Bandit

**Prioridad**: 🔴 CRÍTICA
**Esfuerzo**: 30 minutos
**Beneficio**: Prevenir vulnerabilidades de seguridad

**Instalar bandit**:

```toml
[project.optional-dependencies]
dev = [
    "bandit[toml]>=1.7.6",
]
```

**Configurar bandit** en `pyproject.toml`:

```toml
[tool.bandit]
targets = ["src"]
exclude_dirs = ["tests", ".venv"]
skips = []

[tool.bandit.assert_used]
skips = ["*/test_*.py"]
```

**Ejecutar bandit**:

```bash
# Scan for security issues
bandit -r src/

# Generate report
bandit -r src/ -f html -o bandit-report.html

# Fail CI if high severity issues
bandit -r src/ --severity-level high
```

---

### 5.2 Dependency Scanning con Safety

**Prioridad**: 🔴 CRÍTICA
**Esfuerzo**: 15 minutos

```bash
# Install safety
pip install safety

# Scan dependencies for vulnerabilities
safety check

# Scan specific file
safety check --file requirements.txt

# Generate JSON report
safety check --json
```

**Agregar a CI/CD**:

```yaml
# .github/workflows/security.yml
name: Security Scan

on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Bandit
        run: |
          pip install bandit[toml]
          bandit -r src/ --severity-level high
      - name: Run Safety
        run: |
          pip install safety
          safety check
```

---

### 5.3 Input Sanitization Patterns

**Prioridad**: 🟡 ALTA
**Esfuerzo**: 1 hora

**Sanitize user input to prevent injection**:

```python
import re
from html import escape

class InputValidator:
    """Enhanced input validator with security."""

    FORBIDDEN_PATTERNS = [
        r"<script",
        r"javascript:",
        r"on\w+\s*=",  # Event handlers
        r"import\s+",
        r"exec\s*\(",
        r"eval\s*\(",
    ]

    @classmethod
    def validate(cls, question: str) -> str:
        """Validate and sanitize question."""
        if not question or not question.strip():
            raise ValueError("Question cannot be empty")

        question = question.strip()

        # Check length
        if len(question) < cls.MIN_LENGTH:
            raise ValueError(f"Question too short (min {cls.MIN_LENGTH} chars)")
        if len(question) > cls.MAX_LENGTH:
            raise ValueError(f"Question too long (max {cls.MAX_LENGTH} chars)")

        # ✨ Check for forbidden patterns (injection prevention)
        for pattern in cls.FORBIDDEN_PATTERNS:
            if re.search(pattern, question, re.IGNORECASE):
                raise ValueError("Question contains forbidden patterns")

        # ✨ HTML escape (prevent XSS if rendered)
        question = escape(question)

        return question
```

---

### 5.4 Secrets Management

**Prioridad**: 🟡 ALTA
**Esfuerzo**: 30 minutos

**Never log secrets**:

```python
import logging
from typing import Any

logger = logging.getLogger(__name__)

class SecureSettings:
    """Settings with secure logging."""

    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.ollama_api_key = os.getenv("OLLAMA_API_KEY")

    def __repr__(self) -> str:
        """Prevent secrets in logs."""
        return (
            f"SecureSettings("
            f"openai_api_key={'***' if self.openai_api_key else None}, "
            f"ollama_api_key={'***' if self.ollama_api_key else None})"
        )

    def model_dump(self) -> dict[str, Any]:
        """Dump config without secrets."""
        return {
            "openai_api_key": "***" if self.openai_api_key else None,
            "ollama_api_key": "***" if self.ollama_api_key else None,
        }
```

**Scan for secrets in code**:

```bash
# Install detect-secrets
pip install detect-secrets

# Scan for secrets
detect-secrets scan

# Create baseline
detect-secrets scan > .secrets.baseline

# Audit findings
detect-secrets audit .secrets.baseline
```

---

## Testing Enhancements

### 6.1 Property-Based Testing con Hypothesis

**Prioridad**: 🟢 MEDIA
**Esfuerzo**: 2-3 horas
**Beneficio**: Encontrar edge cases automáticamente

**Instalar Hypothesis**:

```toml
[project.optional-dependencies]
dev = [
    "hypothesis>=6.98.0",
]
```

**Ejemplo - Test validators con property-based testing**:

```python
from hypothesis import given, strategies as st
import pytest

from src.promtior_assistant.domain.services.validators import InputValidator

class TestInputValidatorPropertyBased:
    """Property-based tests for InputValidator."""

    @given(st.text(min_size=3, max_size=2000))
    def test_valid_questions_always_pass(self, question: str):
        """Any text 3-2000 chars should validate."""
        # Hypothesis generates many test cases automatically
        result = InputValidator.validate(question)
        assert isinstance(result, str)
        assert len(result) >= 3
        assert len(result) <= 2000

    @given(st.text(max_size=2))
    def test_short_questions_always_fail(self, question: str):
        """Any text < 3 chars should fail."""
        with pytest.raises(ValueError, match="too short"):
            InputValidator.validate(question)

    @given(st.text(min_size=2001))
    def test_long_questions_always_fail(self, question: str):
        """Any text > 2000 chars should fail."""
        with pytest.raises(ValueError, match="too long"):
            InputValidator.validate(question)
```

**Ejemplo - Test LLM adapter con property-based**:

```python
from hypothesis import given, strategies as st

@given(
    prompt=st.text(min_size=1, max_size=1000),
    temperature=st.floats(min_value=0.0, max_value=1.0)
)
@pytest.mark.asyncio
async def test_llm_adapter_properties(mock_llm, prompt, temperature):
    """Test LLM adapter with various inputs."""
    # Setup mock
    mock_llm.generate.return_value = "Generated response"

    # Test
    result = await mock_llm.generate(prompt, temperature)

    # Properties that should always hold
    assert isinstance(result, str)
    assert len(result) > 0
    mock_llm.generate.assert_called_once_with(prompt, temperature)
```

---

### 6.2 Additional pytest Plugins

**Prioridad**: 🟡 ALTA
**Esfuerzo**: 1 hora

```toml
[project.optional-dependencies]
dev = [
    # ... existing
    "pytest-timeout>=2.2.0",      # ✨ Timeout tests
    "pytest-xdist>=3.5.0",        # ✨ Parallel testing
    "pytest-mock>=3.12.0",        # ✨ Better mocking
    "pytest-randomly>=3.15.0",    # ✨ Random test order
    "pytest-sugar>=1.0.0",        # ✨ Better output
    "pytest-clarity>=1.0.1",      # ✨ Better diffs
]
```

**Configurar plugins** en `pyproject.toml`:

```toml
[tool.pytest.ini_options]
# ... existing

# ✨ Timeout tests after 30s
timeout = 30

# ✨ Run tests in parallel
addopts = [
    # ... existing
    "-n", "auto",  # Use all CPU cores
]

# ✨ Randomize test order (find order-dependent bugs)
randomly_seed = 12345
```

**Uso**:

```bash
# Run tests in parallel
pytest -n auto

# Run specific tests with timeout
pytest tests/integration/ --timeout=60

# Run with coverage + parallel
pytest --cov -n auto
```

---

### 6.3 Test Organization Patterns

**Prioridad**: 🟡 ALTA
**Esfuerzo**: 2 horas

**Estructura recomendada**:

```
tests/
├── unit/
│   ├── domain/
│   │   └── test_validators.py
│   ├── application/
│   │   └── test_use_cases.py
│   └── infrastructure/
│       ├── test_llm_adapters.py
│       └── test_vector_store_adapters.py
├── integration/
│   ├── test_rag_pipeline.py
│   └── test_api_endpoints.py
├── benchmark/
│   └── test_performance.py
├── conftest.py  # Shared fixtures
└── factories.py  # Test data factories
```

**Shared fixtures** (`tests/conftest.py`):

```python
import pytest
from unittest.mock import AsyncMock

@pytest.fixture
def mock_llm():
    """Mock LLM for all tests."""
    llm = AsyncMock()
    llm.model_name = "mock-model"
    llm.generate.return_value = "Mock response"
    return llm

@pytest.fixture
def mock_vector_store():
    """Mock vector store for all tests."""
    store = AsyncMock()

    from unittest.mock import Mock
    mock_doc = Mock()
    mock_doc.page_content = "Test content"
    mock_doc.metadata = {"source": "test"}

    store.retrieve_documents.return_value = [mock_doc]
    return store

@pytest.fixture
def sample_question():
    """Sample question for tests."""
    return "¿Qué servicios ofrece Promtior?"
```

**Test factories** (`tests/factories.py`):

```python
from dataclasses import dataclass
from typing import Any

@dataclass
class QuestionFactory:
    """Factory for creating test questions."""

    @staticmethod
    def create(
        text: str = "¿Qué es Promtior?",
        language: str = "es",
    ) -> str:
        """Create test question."""
        return text

    @staticmethod
    def create_batch(n: int = 10) -> list[str]:
        """Create batch of questions."""
        return [
            f"¿Pregunta de test {i}?"
            for i in range(n)
        ]

    @staticmethod
    def create_invalid() -> str:
        """Create invalid question."""
        return "ab"  # Too short
```

---

## Code Quality & Maintainability

### 7.1 Documentation Standards

**Prioridad**: 🟡 ALTA
**Esfuerzo**: Ongoing

**Google-style docstrings**:

```python
def answer_question(question: str, max_retries: int = 3) -> str:
    """Answer a question using RAG.

    This function implements a retry mechanism for resilience and validates
    both input and output to ensure quality.

    Args:
        question: User question in natural language. Must be 3-2000 characters.
        max_retries: Maximum number of retry attempts. Defaults to 3.

    Returns:
        Generated answer from the RAG system, validated for quality.

    Raises:
        ValueError: If question is invalid (too short, too long, or empty).
        LLMProviderException: If LLM provider fails after all retries.
        VectorStoreException: If vector store is unavailable.

    Examples:
        >>> answer = answer_question("¿Qué es Promtior?")
        >>> print(answer)
        "Promtior es una empresa de consultoría..."

        >>> answer_question("ab")  # Too short
        ValueError: Question too short (min 3 chars)

    Note:
        This function makes external API calls and may take 1-5 seconds.
        Consider using async version for better performance.
    """
    pass
```

---

### 7.2 Complexity Metrics

**Prioridad**: 🟢 MEDIA
**Esfuerzo**: 30 minutos

**Instalar radon**:

```bash
pip install radon
```

**Analizar complejidad**:

```bash
# Cyclomatic complexity
radon cc src/ -a -nb

# Maintainability index
radon mi src/ -nb

# Raw metrics (LOC, comments, etc.)
radon raw src/
```

**Agregar a CI**:

```yaml
# .github/workflows/quality.yml
- name: Check Complexity
  run: |
    pip install radon
    radon cc src/ -a -nb --total-average -nc
```

**Meta**: Mantener complejidad ciclomática < 10 por función

---

### 7.3 Dependency Management con uv

**Prioridad**: 🟡 ALTA
**Esfuerzo**: 1 hora
**Beneficio**: 10-100x más rápido que pip

**Instalar uv**:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Usar uv en lugar de pip**:

```bash
# Create venv
uv venv

# Install dependencies
uv pip install -r requirements.txt

# Install dev dependencies
uv pip install -e ".[dev]"

# Sync dependencies (faster)
uv pip sync requirements.txt

# Compile requirements
uv pip compile pyproject.toml -o requirements.txt
```

**Actualizar Makefile**:

```makefile
.PHONY: install
install:
    uv pip install -e ".[dev]"

.PHONY: sync
sync:
    uv pip sync requirements.txt

.PHONY: upgrade
upgrade:
    uv pip compile pyproject.toml -o requirements.txt --upgrade
```

**Beneficios de uv**:
- 10-100x más rápido que pip
- Mejor resolución de dependencias
- Caching inteligente
- Compatible con pip

---

## Implementation Checklist

### Phase 1: Critical (Semana 1)

**Type Safety & Security** (4-5 horas):
- [ ] Configurar mypy strict mode
- [ ] Agregar type hints a funciones existentes
- [ ] Configurar bandit para security scanning
- [ ] Scan dependencies con safety
- [ ] Agregar input sanitization a validators

### Phase 2: High Priority (Semana 2-3)

**Tooling & Testing** (6-7 horas):
- [ ] Enhanced ruff configuration (50+ linters)
- [ ] Setup pre-commit hooks
- [ ] Configurar pytest-cov (80% threshold)
- [x] Agregar context managers para resources (partial)
- [x] Mejorar docstrings (Google style) (partial)

### Phase 3: Medium Priority (Semana 4-6)

**Advanced Patterns** (8-10 horas):
- [ ] Property-based testing con Hypothesis
- [ ] Performance profiling setup (py-spy, memray)
- [ ] Structural pattern matching en factories
- [ ] Additional pytest plugins
- [ ] Complexity metrics tracking

### Phase 4: Nice-to-Have (Ongoing)

**Optimization & Polish** (Variable):
- [ ] Advanced type hints (Self, TypeGuard)
- [ ] Benchmark tests
- [x] Dependency management con uv (ya en uso)
- [ ] Documentation improvements
- [ ] Code complexity reduction

---

## Comandos Útiles

```bash
# Type checking
mypy src/promtior_assistant

# Security scanning
bandit -r src/
safety check

# Enhanced linting
ruff check src/ --select ALL
ruff format src/

# Pre-commit
pre-commit install
pre-commit run --all-files

# Testing
pytest --cov --cov-fail-under=80
pytest -n auto  # Parallel
pytest --benchmark-only  # Benchmarks only

# Profiling
py-spy record -o profile.svg -- python -m uvicorn src.promtior_assistant.main:app
memray run -o memray.bin python -m uvicorn src.promtior_assistant.main:app

# Complexity
radon cc src/ -a -nb
radon mi src/ -nb

# Dependencies
uv pip install -e ".[dev]"
uv pip sync requirements.txt
```

---

## Métricas de Éxito

Al completar estas recomendaciones, el proyecto debe cumplir:

| Métrica | Target | Cómo Medir |
|---------|--------|------------|
| **Type Coverage** | 100% | `mypy src/` sin errores |
| **Test Coverage** | >80% | `pytest --cov --cov-fail-under=80` |
| **Security Issues** | 0 high/critical | `bandit -r src/ --severity-level high` |
| **Linting Issues** | 0 | `ruff check src/` sin errores |
| **Complexity** | <10 avg | `radon cc src/ -a` |
| **Maintainability** | >70 | `radon mi src/ -nb` |
| **Vulnerable Deps** | 0 | `safety check` |
| **Docstring Coverage** | 100% | `ruff check --select D` |

---

## Referencias

### Python 3.12+ Features
- [What's New in Python 3.12](https://docs.python.org/3/whatsnew/3.12.html)
- [PEP 695 – Type Parameter Syntax](https://peps.python.org/pep-0695/)
- [PEP 701 – Syntactic formalization of f-strings](https://peps.python.org/pep-0701/)

### Type Checking
- [mypy Documentation](https://mypy.readthedocs.io/)
- [pyright Documentation](https://microsoft.github.io/pyright/)
- [Type Hints Cheat Sheet](https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html)

### Testing
- [Hypothesis Documentation](https://hypothesis.readthedocs.io/)
- [pytest Best Practices](https://docs.pytest.org/en/stable/goodpractices.html)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)

### Code Quality
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [pre-commit Documentation](https://pre-commit.com/)
- [Radon Documentation](https://radon.readthedocs.io/)

### Security
- [Bandit Documentation](https://bandit.readthedocs.io/)
- [OWASP Python Security](https://owasp.org/www-project-python-security/)

---

## Resumen

Este documento proporciona recomendaciones específicas de **Python 3.12+** para complementar el plan de refactoring arquitectural. Las mejoras cubren:

✅ **Type Safety** - mypy/pyright para prevenir bugs
✅ **Security** - bandit/safety para prevenir vulnerabilidades
✅ **Tooling** - ruff enhanced, pre-commit hooks
✅ **Testing** - pytest-cov, Hypothesis, benchmarking
✅ **Performance** - profiling, async best practices
✅ **Quality** - complexity metrics, documentation

**Prioridad de implementación**:
1. 🔴 **CRÍTICA**: Type checking + Security (Semana 1)
2. 🟡 **ALTA**: Tooling + Coverage (Semana 2-3)
3. 🟢 **MEDIA**: Advanced patterns (Semana 4-6)

**Beneficios esperados**:
- 40% menos bugs (type checking)
- 100% security compliance (bandit + safety)
- >80% test coverage (pytest-cov)
- 10-100x faster dependency management (uv)
- Production-ready code quality

**Siguiente paso**: Comenzar con Phase 1 - Type Safety & Security (4-5 horas).
