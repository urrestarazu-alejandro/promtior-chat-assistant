---
title: "Architecture"
description: "Arquitectura técnica del sistema con diagramas Mermaid - Clean Architecture v2.0"
---

# Arquitectura del Sistema

## 1. Overview

Este documento describe la arquitectura técnica del Promtior RAG Chatbot Assistant, un sistema de Retrieval Augmented Generation (RAG) que responde preguntas sobre Promtior utilizando inteligencia artificial.

El sistema implementa **Clean Architecture (Hexagonal)** con las siguientes capas:
- **Domain**: Entidades, puertos (interfaces) y servicios de validación
- **Application**: Casos de uso
- **Infrastructure**: Implementaciones de adapters, factories, Container DI
- **Presentation**: API FastAPI, middlewares, schemas

## 2. Architecture Diagram

```mermaid
flowchart TB
    subgraph Client["User Interface"]
        H["HTTP Client<br/>curl / Browser"]
    end

    subgraph Presentation["Presentation Layer"]
        API["FastAPI App<br/>main.py:67-72"]
        M1["LoggingMiddleware<br/>middleware/logging.py"]
        M2["RequestIDMiddleware<br/>middleware/request_id.py"]
        M3["TimeoutMiddleware<br/>middleware/timeout.py"]
        V1["/api/v1 routes<br/>routes.py"]
    end

    subgraph Application["Application Layer"]
        UC["AnswerQuestionUseCase<br/>use_cases/answer_question.py"]
    end

    subgraph Domain["Domain Layer"]
        VP["VectorStorePort<br/>ports/vector_store_port.py"]
        LP["LLMPort<br/>ports/llm_port.py"]
        EP["EmbeddingsPort<br/>ports/embeddings_port.py"]
        Val["Validators<br/>services/validators.py"]
    end

    subgraph Infrastructure["Infrastructure Layer"]
        Cont["Container<br/>container.py"]
        F["Factories<br/>factories.py"]
        Ollama["OllamaAsyncAdapter<br/>llm/ollama_async_adapter.py"]
        OpenAI["OpenAIAsyncAdapter<br/>llm/openai_async_adapter.py"]
        Chroma["ChromaAdapter<br/>vector_store/chroma_adapter.py"]
        UT["UsageTracker<br/>persistence/usage_tracker.py"]
    end

    subgraph Storage["Data Layer"]
        CV["ChromaDB<br/>Vector Database"]
    end

    subgraph LLM_Providers["LLM Providers"]
        OLL["Ollama<br/>tinyllama / nomic-embed-text"]
        OAI["OpenAI<br/>gpt-4o-mini / text-embedding-3-small"]
    end

    H --> API
    API --> M1 --> M2 --> M3 --> V1
    V1 --> UC
    UC --> Val
    UC --> VP
    UC --> LP
    VP <--> Chroma
    Chroma <--> CV
    Cont --> F
    F --> Ollama
    F --> OpenAI
    LP <--> Ollama
    LP <--> OpenAI

    classDef dark fill:#2d333b,stroke:#6d5dfc,color:#e6edf3
    classDef domain fill:#1a4731,stroke:#22c55e,color:#e6edf3
    classDef infra fill:#2d333b,stroke:#f59e0b,color:#e6edf3
    class Client,Presentation,Application dark
    class Domain domain
    class Infrastructure,Storage,CV infra
```

## 3. Request Flow

```mermaid
sequenceDiagram
    autonumber
    participant U as User
    participant F as FastAPI
    participant M as Middleware Stack
    participant UC as AnswerQuestionUseCase
    participant V as VectorStorePort
    participant L as LLMPort
    participant C as Container

    U->>F: GET /ask?q=question
    F->>M: Request flows through middleware
    Note over M: Logging, RequestID, Timeout
    
    M->>UC: execute(question)
    Note over UC: InputValidator.validate()

    UC->>V: retrieve_documents(query, k=3)
    V-->>UC: Top-3 relevant chunks

    UC->>L: generate(prompt)
    Note over L: Ollama or OpenAI

    L-->>UC: Answer text
    Note over UC: OutputValidator.validate()

    UC-->>M: answer string
    M-->>F: Response

    F-->>U: {"question","answer","status"}
```

## 4. Component Details

### 4.1 FastAPI Application (`main.py`)

| Componente | Línea | Propósito |
|------------|-------|-----------|
| `app = FastAPI()` | 67-72 | Inicialización de aplicación FastAPI con lifespan |
| LoggingMiddleware | 132 | Request/response logging |
| RequestIDMiddleware | 133 | Request ID propagation |
| TimeoutMiddleware | 134 | Request timeout (60s default) |
| Exception handlers | 76-128 | Custom error handling |
| `/` endpoint | 149-161 | API info |
| `/health` endpoint | 164-167 | Basic health check |
| `/health/live` endpoint | 170-173 | Kubernetes liveness probe |
| `/health/ready` endpoint | 176-189 | Kubernetes readiness probe |
| `/ask` endpoint | 229-251 | Legacy endpoint |
| `/admin/reingest` endpoint | 192-226 | Data re-ingestion |
| `/api/v1/ask` endpoint | routes.py:11-36 | v1 API endpoint |

### 4.2 Configuration (`config.py`)

| Variable | Línea | Descripción |
|----------|-------|-------------|
| `Settings` class | 7-25 | Configuración centralizada con Pydantic |
| Environment switching | 15-18 | Dual support (Ollama/OpenAI) |
| ChromaDB path | 19-22 | Directorio de persistencia |

### 4.3 Domain Layer

| Componente | Archivo | Propósito |
|------------|---------|-----------|
| `LLMPort` | `domain/ports/llm_port.py` | Interface para providers LLM |
| `VectorStorePort` | `domain/ports/vector_store_port.py` | Interface para vector store |
| `EmbeddingsPort` | `domain/ports/embeddings_port.py` | Interface para embeddings |
| `InputValidator` | `domain/services/validators.py:18-48` | Validación de entrada |
| `OutputValidator` | `domain/services/validators.py:51-73` | Validación de salida |

### 4.4 Application Layer

| Componente | Archivo | Propósito |
|------------|---------|-----------|
| `AnswerQuestionUseCase` | `application/use_cases/answer_question.py` | Caso de uso principal con retry logic |

### 4.5 Infrastructure Layer

| Componente | Archivo | Propósito |
|------------|---------|-----------|
| `Container` | `infrastructure/container.py` | Dependency Injection con singleton pattern |
| `create_llm()` | `infrastructure/factories.py:9-38` | Factory para LLM |
| `create_embeddings()` | `infrastructure/factories.py:41-65` | Factory para embeddings |
| `OllamaAsyncAdapter` | `infrastructure/llm/ollama_async_adapter.py` | Adapter async para Ollama |
| `OpenAIAsyncAdapter` | `infrastructure/llm/openai_async_adapter.py` | Adapter async para OpenAI |
| `ChromaAdapter` | `infrastructure/vector_store/chroma_adapter.py` | Adapter para ChromaDB |
| `UsageTracker` | `infrastructure/persistence/usage_tracker.py` | Tracking de uso y costos |

### 4.6 Presentation Layer

| Componente | Archivo | Propósito |
|------------|---------|-----------|
| Middleware stack | `presentation/middleware/` | Logging, RequestID, Timeout |
| Request schemas | `presentation/schemas/request.py` | Pydantic request models |
| Response schemas | `presentation/schemas/response.py` | Pydantic response models |
| Exception handlers | `presentation/exceptions.py` | Custom exceptions |

## 5. Dependency Injection Container

El sistema implementa un Container pattern para gestión de dependencias:

```python
# infrastructure/container.py:33-46
class Container:
    @classmethod
    async def initialize(cls):
        cls._llm = create_llm()
        cls._embeddings = create_embeddings()
        cls._vector_store = ChromaVectorStoreAdapter(
            persist_directory=settings.chroma_persist_directory,
            embeddings=cls._embeddings,
        )
```

| Método | Propósito |
|--------|-----------|
| `get_llm()` | Retorna singleton de LLM |
| `get_embeddings()` | Retorna singleton de embeddings |
| `get_vector_store()` | Retorna instancia de ChromaAdapter |
| `initialize()` | Inicializa todos los singletons |
| `cleanup()` | Limpia recursos |

## 6. Environment Configuration

| Variable | Dev Default | Production | Descripción |
|----------|-------------|------------|-------------|
| `ENVIRONMENT` | `development` | `production` | Environment mode |
| `LLM_PROVIDER` | `ollama` | `openai` | LLM provider |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | — | Ollama server URL |
| `OLLAMA_MODEL` | `tinyllama` | — | Ollama model name |
| `OPENAI_API_KEY` | — | **Required** | OpenAI API key |
| `OPENAI_MODEL` | `gpt-4o-mini` | `gpt-4o-mini` | OpenAI model name |

## 7. Data Flow

### 7.1 Ingestion Flow

```mermaid
flowchart LR
    A["Website<br/>promtior.ai"] --> B["scrape_promtior_website()<br/>ingest.py"]
    A1["docs/*.pdf"] --> C["load_pdfs()<br/>ingest.py"]
    B --> D["RecursiveCharacterTextSplitter<br/>chunk_size=1000<br/>chunk_overlap=200"]
    C --> D
    D --> E["Embeddings<br/>Ollama/OpenAI"]
    E --> F["ChromaDB<br/>persist_directory"]
```

### 7.2 Query Flow

```mermaid
flowchart TD
    Q["User Question"] --> V["Embed Question<br/>nomic-embed-text / text-embedding-3-small"]
    V --> S["Similarity Search<br/>k=3 chunks"]
    S --> C["Retrieve Context"]
    C --> P["Prompt + Context<br/>use_cases/answer_question.py:44-65"]
    P --> L["Generate Answer<br/>OllamaAsyncAdapter / OpenAIAsyncAdapter"]
    L --> A["Answer Response"]
```

## 8. Technology Stack

| Categoria | Tecnologia | Version |
|-----------|------------|---------|
| Web Framework | FastAPI | 0.100+ |
| Architecture | Clean/Hexagonal | — |
| RAG Framework | LangChain Core | — |
| Vector Database | ChromaDB | 0.4+ |
| Development LLM | Ollama (tinyllama) | Latest |
| Production LLM | OpenAI (gpt-4o-mini) | Latest |
| Embeddings | nomic-embed-text / text-embedding-3-small | Latest |
| PDF Processing | pypdf | 6.7+ |
| Deployment | Railway | Latest |
| Package Manager | uv | Latest |
| Linter | ruff | Latest |
| Testing | pytest | 9.0+ |

## 9. Testing Coverage

El proyecto mantiene **96%+ coverage** en código no-legacy:

```
TOTAL                                                                    394      9     40      3  96.58%
```

| Capa | Coverage |
|------|----------|
| Domain | 95%+ |
| Application | 100% |
| Infrastructure | 90%+ |
| Presentation | 80%+ |

## 10. Prompt Template

El sistema utiliza un prompt en español definido en `use_cases/answer_question.py:54-65`:

```
Eres un asistente que responde preguntas sobre Promtior,
una empresa de consultoría tecnológica y organizacional especializada
en inteligencia artificial.

Usa el siguiente contexto para responder la pregunta. Si no sabes la
respuesta basándote en el contexto, di que no tienes esa información.

Contexto: {context}

Pregunta: {question}

Respuesta:
```

## 11. Retry Logic

El sistema implementa retry exponencial con 3 intentos en `use_cases/answer_question.py:82-114`:

```python
max_retries = 3
for attempt in range(max_retries):
    try:
        # RAG execution
    except Exception as e:
        wait_time = 2 ** attempt  # 1s, 2s, 4s
        await asyncio.sleep(wait_time)
```

## 12. Legacy vs Clean Code

### Code to Replace (Legacy)

| Archivo | Estado | Notas |
|---------|--------|-------|
| `rag.py` | Legacy | Factory functions con lru_cache |
| `rag_service.py` | Legacy | Singleton con lru_cache |
| `ingest.py` | Legacy | Script de ingestión |

### Clean Architecture (Active)

| Capa | Directorio | Estado |
|------|------------|--------|
| Domain | `domain/` | ✅ Active |
| Application | `application/` | ✅ Active |
| Infrastructure | `infrastructure/` | ✅ Active |
| Presentation | `presentation/` | ✅ Active |

## 13. Source Code References

| Archivo | Capa | Propósito |
|---------|------|-----------|
| `main.py` | Presentation | FastAPI app, endpoints, middleware |
| `config.py` | Infrastructure | Settings, environment vars |
| `container.py` | Infrastructure | Dependency injection |
| `factories.py` | Infrastructure | LLM/Embeddings factories |
| `answer_question.py` | Application | Use case principal |
| `validators.py` | Domain | Input/Output validation |
| `llm_port.py` | Domain | LLM interface |
| `vector_store_port.py` | Domain | Vector store interface |
| `ollama_async_adapter.py` | Infrastructure | Ollama LLM adapter |
| `openai_async_adapter.py` | Infrastructure | OpenAI LLM adapter |
| `chroma_adapter.py` | Infrastructure | ChromaDB adapter |
| `ingest.py` | Infrastructure | Data ingestion (legacy) |
