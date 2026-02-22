# CLAUDE.md — Promtior Chat Assistant

## Project Overview

RAG-based chatbot for Promtior built with FastAPI + LangChain + ChromaDB. Supports dual LLM providers: Ollama (development) and OpenAI (production). Deployed on Railway.

**Status**: Production MVP deployed with Clean Architecture (v2.1).
**Latest**: RAG v2.1 improvements (Feb 2026) - Embedding metadata tracking, multi-language prompts, optimized retrieval (k=5, chunk_size=1500).

## Tech Stack

- **Language:** Python 3.12+
- **Package Manager:** uv (10-100x faster than pip)
- **Framework:** FastAPI 0.100+
- **Architecture:** Clean/Hexagonal Architecture
- **RAG:** LangChain Core
- **Vector DB:** ChromaDB
- **LLM (dev):** Ollama (tinyllama)
- **LLM (prod):** OpenAI (gpt-4o-mini)
- **Embeddings:** nomic-embed-text (Ollama) / text-embedding-3-small (OpenAI)
- **Linter:** ruff
- **Type Checker:** mypy
- **Testing:** pytest + pytest-asyncio (96%+ coverage)
- **Deployment:** Railway + Docker

## Project Structure (v2.0 - Clean Architecture)

```
src/promtior_assistant/
├── __init__.py
├── main.py                    # FastAPI app with lifespan, middleware, endpoints
├── config.py                  # Pydantic Settings
├── ingest.py                  # Data ingestion (legacy, to be refactored)
├── rag.py                     # Legacy RAG (to be replaced)
├── services/
│   └── rag_service.py         # Legacy service (to be replaced)
├── domain/
│   ├── ports/
│   │   ├── llm_port.py           # LLM interface
│   │   ├── vector_store_port.py  # Vector store interface
│   │   └── embeddings_port.py    # Embeddings interface
│   └── services/
│       └── validators.py          # Input/Output validators
├── application/
│   └── use_cases/
│       └── answer_question.py     # Main use case with retry logic
├── infrastructure/
│   ├── container.py               # Dependency Injection Container
│   ├── factories.py               # LLM/Embeddings factories
│   ├── llm/
│   │   ├── ollama_async_adapter.py
│   │   └── openai_async_adapter.py
│   ├── embeddings/
│   │   ├── ollama_embeddings.py
│   │   └── ollama_async_embeddings.py
│   ├── vector_store/
│   │   └── chroma_adapter.py
│   └── persistence/
│       └── usage_tracker.py
└── presentation/
    ├── api/
    │   └── v1/
    │       ├── routes.py          # /api/v1 endpoints
    │       └── dependencies.py    # FastAPI dependencies
    ├── middleware/
    │   ├── logging.py
    │   ├── request_id.py
    │   └── timeout.py
    ├── schemas/
    │   ├── request.py
    │   └── response.py
    └── exceptions.py

tests/
├── conftest.py                   # Fixtures with RAG mocking
├── test_api.py                   # API tests (18 tests)
├── test_integration.py           # Integration tests (require Ollama)
└── unit/                         # Unit tests (92 tests)
    ├── test_adapters.py
    ├── test_config.py
    ├── test_container.py
    ├── test_dependencies.py
    ├── test_domain.py
    ├── test_exceptions.py
    ├── test_factories.py
    ├── test_rag_service.py
    ├── test_schemas.py
    ├── test_usage_tracker.py
    └── test_validators.py

docs/
├── ARCHITECTURE.md                    # Architecture documentation (updated)
├── ARCHITECTURE_REFACTORING_PLAN.md   # Clean Architecture plan
├── PHASE2_FASTAPI_PRO_ADDITIONS.md    # FastAPI Pro patterns
├── PYTHON_PRO_RECOMMENDATIONS.md      # Python 3.12+ best practices
├── API_CONFIGURATION.md               # API endpoints
├── LOCAL_SETUP.md                    # Local development setup
├── RAILWAY_DEPLOYMENT.md             # Railway deployment
└── TROUBLESHOOTING.md                # Common issues

data/chroma_db/    # Vector store (gitignored)
```

## Commands

```bash
# Install dependencies
make install          # uv sync --all-extras

# Run dev server
make dev              # uv run uvicorn src.promtior_assistant.main:app --reload

# Run unit tests (mocked, no Ollama needed)
make test             # uv run pytest -v -m "not integration"

# Run all tests (requires Ollama running)
make test-all         # uv run pytest -v

# Run integration tests only
make test-integration # uv run pytest -v -m integration

# Lint & format
uv run ruff check src/ tests/         # Check code quality
uv run ruff check src/ tests/ --fix   # Auto-fix issues
uv run ruff format src/ tests/        # Format code

# Type checking (when configured)
uv run mypy src/promtior_assistant

# Clean caches
make clean
```

## Architecture Patterns (Current - v2.0)

### Implemented Patterns (Clean Architecture)
- **Container Pattern** for dependency injection (singleton instances)
- **Ports & Adapters** (Hexagonal Architecture) for framework independence
- **Factory pattern** for LLM/embeddings provider switching
- **Retry logic** with exponential backoff (3 attempts) in `AnswerQuestionUseCase`
- **Input/Output validation** via `InputValidator` / `OutputValidator` in domain layer
- **Pydantic Settings** for typed, validated configuration
- **FastAPI Lifespan** for proper startup/shutdown
- **Middleware Stack** (RequestID, Logging, Timeout)
- **Custom Exception Handlers** for granular error handling

### Planned Patterns (Future)
- Phase 3: Full Clean Architecture if project grows beyond thresholds

### Planned Patterns (v2.0 - See docs/ARCHITECTURE_REFACTORING_PLAN.md)
- ✨ **Container Singleton Pattern** for dependency injection (replaces @lru_cache)
- ✨ **FastAPI Lifespan Events** for proper startup/shutdown
- ✨ **Ports & Adapters** (Hexagonal Architecture) for framework independence
- ✨ **Clean Architecture** layers: Domain → Application → Infrastructure → Presentation
- ✨ **Async/Await best practices** (httpx.AsyncClient, asyncio.sleep)
- ✨ **Pydantic V2 Schemas** for request/response validation
- ✨ **Custom Exception Handlers** for granular error handling
- ✨ **Middleware Stack** (RequestID, Logging, Timeout)
- ✨ **Production Health Checks** (/health, /health/live, /health/ready)

## Architecture Roadmap

### Phase 1: Separation + DI Container (Week 1 - 6-9h)
**Goal**: Separate responsibilities and implement Container pattern

- [ ] Create directory structure (domain/, infrastructure/, presentation/)
- [ ] Move validators to domain layer
- [ ] Move infrastructure code (LLM adapters, embeddings, vector store)
- [ ] Implement Container singleton pattern
- [ ] Add FastAPI Lifespan events
- [ ] Tests pass without regression

**Benefits**: 10-20x performance improvement, eliminate memory leaks, proper resource management

### Phase 2: Ports + FastAPI Pro Patterns (Week 2-4 - 16-20h)
**Goal**: Add abstraction layer and modern FastAPI patterns

- [ ] Create ports (interfaces) for LLM, Embeddings, VectorStore
- [ ] Implement adapters for OpenAI and Ollama
- [ ] Fix async/await patterns (httpx.AsyncClient, asyncio.sleep)
- [ ] Add Pydantic V2 request/response schemas
- [ ] Implement custom exception handlers
- [ ] Add middleware stack (RequestID, Logging, Timeout)
- [ ] Production-ready health checks
- [ ] Unit tests with mocks (>80% coverage)

**Benefits**: Framework independence, testability, production-ready observability

### Phase 3: Clean Architecture Complete (Month 3-6 - Evaluate)
**Goal**: Full Clean Architecture if project grows beyond thresholds

**Criteria for Phase 3**:
- Endpoints > 10
- Lines of code > 3000
- Multiple business domains
- Cyclomatic complexity > 10 average

See `docs/ARCHITECTURE_REFACTORING_PLAN.md` for full details.

## Python 3.12+ Enhancements (Planned)

See `docs/PYTHON_PRO_RECOMMENDATIONS.md` for comprehensive guide.

### Critical (Week 1 - 4-5h)
- [ ] Configure mypy strict mode for type safety
- [ ] Add bandit for security scanning
- [ ] Configure safety for dependency vulnerabilities
- [ ] Enhance input sanitization

### High Priority (Week 2-3 - 6-7h)
- [ ] Enhanced ruff config (50+ linters: B, C4, S, ASYNC, PERF, etc.)
- [ ] Pre-commit hooks (ruff, mypy, bandit)
- [ ] pytest-cov with 80% threshold
- [ ] Context managers for resource management

### Medium Priority (Week 4-6 - 8-10h)
- [ ] Property-based testing with Hypothesis
- [ ] Performance profiling (py-spy, memray)
- [ ] Structural pattern matching in factories
- [ ] Benchmark tests with pytest-benchmark

## Coding Rules

1. **Python 3.12+ features** — use modern syntax (type hints, `|` union, f-strings)
2. **Async-first** — all endpoints and RAG calls are async
3. **No comments unless requested** — code should be self-documenting via clear names and docstrings
4. **ruff** is the only linter — follow its rules (currently: `E`, `F`, `I`, `W`, `UP`)
   - Planned: 50+ additional rules (B, C4, S, ASYNC, PERF, SIM, etc.)
5. **Line length:** 100 characters max
6. **Imports:** sorted by ruff (`I` rule — isort-compatible)
7. **Never commit secrets** — `.env` is gitignored, use `.env.example` as template
8. **Never log API keys** — `OPENAI_API_KEY` and similar must stay out of logs/output
9. **Tests must pass before finishing work** — run `make test` after changes
10. **Follow existing patterns** — factory functions, Pydantic models, LangChain abstractions
11. **Type hints required** — all public functions must have complete type annotations
12. **Security first** — validate all user input, escape output, scan for vulnerabilities

## Environment Variables

| Variable | Dev Default | Production | Description |
|----------|-------------|------------|-------------|
| `ENVIRONMENT` | `development` | `production` | Environment mode |
| `LLM_PROVIDER` | `ollama` | `openai` | LLM provider |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | — | Ollama server URL |
| `OLLAMA_MODEL` | `tinyllama` | — | Ollama model name |
| `OLLAMA_EMBEDDING_MODEL` | `nomic-embed-text` | `nomic-embed-text` | Ollama embedding model |
| `OLLAMA_API_KEY` | — | Required (remote) | Ollama API key (if remote) |
| `OPENAI_API_KEY` | — | **Required** | OpenAI API key |
| `OPENAI_MODEL` | `gpt-4o-mini` | `gpt-4o-mini` | OpenAI model name |
| `OPENAI_EMBEDDING_MODEL` | `text-embedding-3-small` | `text-embedding-3-small` | OpenAI embedding |
| `USE_OPENAI_EMBEDDINGS` | `false` | `false` | Use OpenAI embeddings in prod |
| `ADMIN_REINGEST_KEY` | — | Required | Admin key for /admin/reingest |

**ChromaDB Path**:
- Development: `./data/chroma_db`
- Production: `/tmp/chroma_db` (Railway ephemeral storage)

## API Endpoints

| Method | Path | Description | Status |
|--------|------|-------------|--------|
| GET | `/` | API info and usage examples | ✅ Production |
| GET | `/health` | Basic health check | ✅ Production |
| GET | `/ask?q=<question>` | Ask a RAG question (legacy) | ✅ Production |
| POST | `/admin/reingest?admin_key=<KEY>` | Re-ingest data into ChromaDB | ✅ Production |
| POST | `/api/v1/ask` | Ask question (v1, with schemas) | 🔜 Planned Phase 2 |
| GET | `/health/live` | Kubernetes liveness probe | 🔜 Planned Phase 2 |
| GET | `/health/ready` | Kubernetes readiness probe | 🔜 Planned Phase 2 |

## Data Flow

### Current (v2.1 - Clean Architecture + RAG Improvements)
```
User request → Middleware Stack (RequestID, Logging, Timeout)
→ Pydantic Request Schema → Use Case (AnswerQuestion)
→ Vector Store Port → Retrieve 5 Documents (was 3)
→ Build Context (~7500 chars, was ~3000)
→ LLM Port → Generate Answer (multi-language, 2-3 sentences)
→ Output Validator → Pydantic Response Schema
→ Custom Exception Handlers → JSON Response

Startup: ChromaAdapter validates embedding metadata (provider + dimension)
```

## RAG v2.1 Improvements (Feb 2026)

### What Changed

**1. Embedding Metadata Tracking** (Prevents silent failures)
- Automatically saves `embedding_metadata.json` during ingestion
- Validates provider/dimension on startup
- Raises clear `EmbeddingMismatchError` if mismatch detected
- Files: `domain/models/embedding_metadata.py`, `infrastructure/vector_store/chroma_adapter.py`

**2. Multi-Language Prompt** (Automatic language detection)
- Detects question language and responds in the same language
- Enforces 2-3 sentence responses (conciseness)
- No more hardcoded Spanish prompts
- File: `application/use_cases/answer_question.py:44-70`

**3. Retrieval Optimization** (+150% context)
- Documents retrieved: 3 → 5 (+66%)
- Chunk size: 1000 → 1500 chars (+50%)
- Chunk overlap: 200 → 300 chars (+50%)
- Total context: ~3000 → ~7500 chars
- Files: `application/use_cases/answer_question.py:94`, `ingest.py:131-132`

**4. Developer Tooling**
- New `scripts/diagnose_rag.py` for debugging retrieval
- New `make quickstart` command for one-line setup
- Comprehensive docs: `docs/RAG_V2_IMPROVEMENTS.md`, `docs/RAG_TROUBLESHOOTING.md`

### Migration to v2.1

```bash
# Required: Re-ingest data to create metadata
rm -rf data/chroma_db
make ingest

# Verify metadata exists
cat data/chroma_db/embedding_metadata.json

# Start server (validation happens here)
make dev
```

See `docs/RAG_V2_IMPROVEMENTS.md` for full technical deep-dive.

## Key Files to Understand

### Clean Architecture Code
- `src/promtior_assistant/application/use_cases/answer_question.py` — Main use case with retry logic
- `src/promtior_assistant/infrastructure/container.py` — Dependency Injection Container
- `src/promtior_assistant/infrastructure/factories.py` — LLM/Embeddings factories
- `src/promtior_assistant/domain/ports/` — Port interfaces (LLM, VectorStore, Embeddings)
- `src/promtior_assistant/main.py` — FastAPI app with lifespan, middleware, endpoints

### Legacy Code (to be refactored)
- `src/promtior_assistant/rag.py` — Legacy RAG chain
- `src/promtior_assistant/ingest.py` — Data pipeline (scraping + PDF)

### RAG v2.1 Documentation (⭐ New!)
- 📘 `docs/RAG_V2_IMPROVEMENTS.md` — **Technical deep-dive** of v2.1 improvements with diagrams
- 📘 `docs/RAG_TROUBLESHOOTING.md` — RAG debugging guide and common issues
- 📘 `docs/TESTING_EMBEDDING_METADATA.md` — Step-by-step testing guide for metadata system
- 📘 `docs/CLEANUP_SUMMARY.md` — Directory structure cleanup (chroma_db_v2 → chroma_db)
- 🔧 `scripts/diagnose_rag.py` — RAG diagnostic tool for debugging retrieval

### Architecture & Planning
- 📘 `docs/ARCHITECTURE_REFACTORING_PLAN.md` — **Master refactoring plan** (v2.0 with FastAPI Pro)
- 📘 `docs/PHASE2_FASTAPI_PRO_ADDITIONS.md` — FastAPI-specific tasks and patterns
- 📘 `docs/PYTHON_PRO_RECOMMENDATIONS.md` — Python 3.12+ best practices and tooling
- 📘 `docs/ARCHITECTURE.md` — Current architecture documentation
- 📘 `docs/TROUBLESHOOTING.md` — Common issues and solutions

### Deployment
- 🚀 `docs/RAILWAY_DEPLOYMENT.md` — Railway deployment guide
- 🚀 `docs/API_CONFIGURATION.md` — API endpoint documentation
- 🚀 `docs/LOCAL_SETUP.md` — Local development setup

## Common Pitfalls & Known Issues

### Current (v2.1)
1. **ChromaDB requires data**: `data/chroma_db/` must exist with ingested data before `/ask` works
2. **Integration tests need Ollama**: Run `docker-compose up -d` or `make ollama` first
3. **Admin key required**: `ADMIN_REINGEST_KEY` environment variable must match for `/admin/reingest`
4. **Embedding metadata validation**: After switching providers (Ollama ↔ OpenAI), re-ingest required
   - **Error**: `EmbeddingMismatchError` if metadata doesn't match
   - **Fix**: `rm -rf data/chroma_db && make ingest`

### Fixed in v2.1 ✅
- ✅ **Silent embedding mismatches**: Now caught at startup with clear error messages
- ✅ **Language inconsistency**: Multi-language prompts auto-detect question language
- ✅ **Poor retrieval for specific questions**: Increased k=5, chunk_size=1500
- ✅ **No debugging tools**: Added `scripts/diagnose_rag.py`
- ✅ **Confusing directory names**: Simplified `chroma_db_v2` → `chroma_db`

### Legacy Code Issues (to be addressed in future phases)
- Legacy code in `rag.py` and `rag_service.py` uses `@lru_cache` (to be replaced with Container pattern)

### Future Improvements (Python Pro / Phase 3)
1. 🟡 **No Type Safety**: Missing mypy configuration and incomplete type hints
   - **Impact**: Runtime errors that could be caught at type-check time
   - **Fix**: mypy strict mode + complete type hints (Python Pro Phase 1)

2. 🟡 **Security Gaps**: No input sanitization for injection attacks, no security scanning
   - **Impact**: Vulnerable to XSS, code injection
   - **Fix**: Enhanced validation + bandit scanning (Python Pro Phase 1)

3. ✅ **Observability** (Partially Implemented): Request tracking, structured logging, health checks exist
   - **Status**: Middleware stack implemented in v2.0
   - **Remaining**: Production metrics, tracing

## Available Claude Skills

This project has 31 Claude Code skills configured in `.claude/skills/`:

### Architecture & Design (⭐ Core Skills)
- **architect-review** — Architecture review, Clean/Hexagonal Architecture, SOLID principles
- **senior-architect** — System design, tech stack decisions, architecture diagrams
- **software-architecture** — Quality-focused architecture patterns

### Python Development (⭐ Core Skills)
- **python-pro** — Python 3.12+ expert, modern patterns, async, performance
- **python-patterns** — Framework selection, async patterns, type hints
- **python-testing-patterns** — pytest, fixtures, mocking, TDD
- **python-performance-optimization** — Profiling, bottleneck optimization
- **python-packaging** — Package distribution, PyPI publishing

### FastAPI & Web (⭐ Core Skills)
- **fastapi-pro** — FastAPI 0.100+, async patterns, Pydantic V2, production patterns
- **fastapi-templates** — FastAPI project scaffolding
- **fastapi-router-py** — FastAPI router patterns, CRUD operations

### Testing & Quality
- **testing-patterns** — Jest/pytest patterns, factory functions, mocking
- **test-fixing** — Systematically fix failing tests

### Database & Performance
- **sql-optimization-patterns** — Query optimization, indexing strategies
- **sql-injection-testing** — Security testing (authorized contexts only)

### DevOps & Deployment
- **docker-expert** — Docker, multi-stage builds, optimization, security
- **railway** — Railway deployment, environment configuration

### Security
- **api-security-best-practices** — API authentication, authorization, input validation
- **html-injection-testing** — HTML injection testing (authorized contexts)

### Documentation
- **wiki-page-writer** — Technical documentation with Mermaid diagrams
- **mermaid-expert** — Mermaid diagram creation

### Other Languages (Available but not primary)
- **java-pro** — Java 21+ expert
- **tailwind-patterns** — Tailwind CSS v4
- **tailwind-design-system** — Design systems
- **langchain-architecture** — LLM applications with LangChain

**Usage**: Use `@.claude/skills/<skill-name>/SKILL.md` to invoke skills, or let Claude proactively use them based on context.

## Development Workflow

### 1. Before Starting Work
```bash
# Pull latest
git pull origin main

# Install/update dependencies
make install

# Verify tests pass
make test
```

### 2. Development Cycle
```bash
# Create feature branch
git checkout -b feat/your-feature-name

# Make changes...

# Run tests frequently
make test

# Lint and format
uv run ruff check src/ tests/ --fix
uv run ruff format src/ tests/

# Verify all tests pass
make test-all
```

### 3. Before Committing
```bash
# Final checks
make test              # Unit tests must pass
uv run ruff check src/ tests/  # No linting errors
# uv run mypy src/     # Type checks (when configured)

# Commit with conventional commit message
git add .
git commit -m "feat: Add new feature X"

# Push
git push origin feat/your-feature-name
```

### 4. Using Refactoring Plans
When implementing refactoring phases:

1. **Read the plan first**: `docs/ARCHITECTURE_REFACTORING_PLAN.md`
2. **Check prerequisites**: Ensure Phase N-1 is complete
3. **Follow checklist**: Use the task checklist in Anexo A
4. **Run tests after each step**: Don't batch testing to the end
5. **Commit frequently**: Small, atomic commits per task
6. **Verify criteria**: Check acceptance criteria before marking complete

## Performance Benchmarks

### Current (v2.0 - Clean Architecture)
- **Requests/sec**: ~100-500 rps (with Container singleton pattern)
- **P95 Latency**: 500ms-2s
- **Memory**: No leaks (proper resource cleanup)
- **Connection pooling**: ✅ Enabled
- **Observability**: ✅ Production-ready (middleware, health checks)

## Testing Strategy

### Current Coverage
- **Unit tests**: 110 tests (API, adapters, validators, containers, factories)
- **Integration tests**: 2 tests (require Ollama)
- **Coverage**: 96.58% (exceeds 90% target)

### Testing Areas Covered
- API endpoints (/, /health, /health/live, /health/ready, /ask, /admin/reingest, /api/v1/ask)
- LLM Adapters (Ollama, OpenAI)
- Vector Store Adapter (ChromaDB)
- Dependency Injection Container
- Factories (LLM, Embeddings)
- Domain Validators
- Use Cases (AnswerQuestion)
- Exception handlers
- Middleware (logging, request_id, timeout)

## Additional Resources

- **Original Requirements**: `docs/AI-Engineer-Test-Promtior.pdf`
- **Railway Dashboard**: https://railway.app (check deployment logs)
- **LangChain Docs**: https://python.langchain.com/docs/
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Pydantic V2 Docs**: https://docs.pydantic.dev/latest/

## Quick Reference

### Common Commands
```bash
make install          # Install dependencies
make dev              # Start dev server
make test             # Run unit tests
make test-all         # Run all tests (needs Ollama)
make clean            # Clean caches

uv run ruff check src/ --fix   # Lint + autofix
uv run ruff format src/        # Format code
```

### Important Files
- `CLAUDE.md` — **This file** (project overview)
- `docs/ARCHITECTURE_REFACTORING_PLAN.md` — Master refactoring plan
- `docs/PYTHON_PRO_RECOMMENDATIONS.md` — Python best practices
- `.env.example` — Environment variables template
- `pyproject.toml` — Project configuration
- `Makefile` — Common commands

### Key Directories
- `src/promtior_assistant/` — Application code
- `tests/` — Test suite
- `docs/` — Documentation
- `.claude/skills/` — Claude Code skills (31 available)
- `data/` — Vector database (gitignored)

---

**Last Updated**: 2026-02-21
**Version**: 1.0 (MVP in production, refactoring planned)
**Maintainer**: Check git log for contributors
