---
title: "Claude Code Skills - Catálogo Completo"
description: "Guía de referencia para todos los skills disponibles en el proyecto Promtior Chat Assistant"
---

# Claude Code Skills - Catálogo Completo

Este documento cataloga y explica los **28 skills** disponibles en `.claude/skills/` para el proyecto Promtior Chat Assistant.

## Overview

Los **skills** son agentes especializados que asisten en tareas específicas de desarrollo de software. Se invocan con `@.claude/skills/<skill-name>/SKILL.md` o se activan proactivamente según el contexto del proyecto.

---

## Categorías de Skills

### Arquitectura y Diseño

| Skill | Descripción | Cuándo Usarlo |
|-------|-------------|---------------|
| [`architect-review`](#architect-review) | Revisiones de arquitectura, Clean/Hexagonal Architecture | Revisiones de diseño, evaluación de escalabilidad |
| [`senior-architect`](#senior-architect) | Diseño de sistemas, diagramas, decisiones técnicas | Diseño de arquitectura, evaluación de trade-offs |
| [`software-architecture`](#software-architecture) | Patrones de calidad, principios DDD/Clean | Desarrollo con calidad, refactorización |

### Python Development

| Skill | Descripción | Cuándo Usarlo |
|-------|-------------|---------------|
| [`python-pro`](#python-pro) | Python 3.12+, async, rendimiento | Desarrollo Python moderno, optimización |
| [`python-patterns`](#python-patterns) | Framework selection, type hints, patrones | Decisiones técnicas, arquitectura Python |
| [`python-testing-patterns`](#python-testing-patterns) | pytest, fixtures, TDD | Testing Python, setup de tests |
| [`python-performance-optimization`](#python-performance-optimization) | Profiling, optimización | Debug de rendimiento, bottlenecks |
| [`python-packaging`](#python-packaging) | Distribución PyPI | Empaquetado, CLI tools |
| [`python-development-python-scaffold`](#python-development-python-scaffold) | Scaffold proyectos Python | Nuevos proyectos |

### FastAPI & Web

| Skill | Descripción | Cuándo Usarlo |
|-------|-------------|---------------|
| [`fastapi-pro`](#fastapi-pro) | FastAPI 0.100+, Pydantic V2, async | APIs FastAPI, optimización |
| [`fastapi-templates`](#fastapi-templates) | Templates proyectos FastAPI | Nuevos proyectos FastAPI |
| [`fastapi-router-py`](#fastapi-router-py) | CRUD routes, autenticación | Rutas, endpoints |

### Testing & Quality

| Skill | Descripción | Cuándo Usarlo |
|-------|-------------|---------------|
| [`testing-patterns`](#testing-patterns) | Jest patterns, factories, mocking | Testing (general), TDD |
| [`test-fixing`](#test-fixing) | Arreglar tests fallando | Debug de tests, CI failures |

### DevOps & Deployment

| Skill | Descripción | Cuándo Usarlo |
|-------|-------------|---------------|
| [`docker-expert`](#docker-expert) | Docker, multi-stage, seguridad | Containerización, Dockerfiles |
| [`railway/*`](#railway-skills) | Railway deployment | Deploy a Railway |

### LangChain & AI

| Skill | Descripción | Cuándo Usarlo |
|-------|-------------|---------------|
| [`langchain-architecture`](#langchain-architecture) | LangChain, agents, RAG | Aplicaciones LLM, chatbots |
| [`embedding-strategies`](#embedding-strategies) | Embeddings, vector search | RAG, similarity search |

### Seguridad

| Skill | Descripción | Cuándo Usarlo |
|-------|-------------|---------------|
| [`api-security-best-practices`](#api-security-best-practices) | Auth, validación, rate limiting | Seguridad API |
| [`html-injection-testing`](#html-injection-testing) | Testing XSS (autorizado) | Testing seguridad |

### Documentación

| Skill | Descripción | Cuándo Usarlo |
|-------|-------------|---------------|
| [`wiki-page-writer`](#wiki-page-writer) | Documentación con Mermaid | Docs técnicas, deep-dives |
| [`mermaid-expert`](#mermaid-expert) | Diagramas Mermaid | Diagramas arquitectura |

### Otros

| Skill | Descripción | Cuándo Usarlo |
|-------|-------------|---------------|
| [`java-pro`](#java-pro) | Java 21+, virtual threads, Spring | Desarrollo Java |
| [`agent-tool-builder`](#agent-tool-builder) | Construcción de tools para agents | Herramientas para AI agents |
| [`linux-shell-scripting`](#linux-shell-scripting) | Scripts shell Linux | Automatización |
| [`prompt-engineer`](#prompt-engineer) | Prompt engineering | LLMs, prompts |
| [`commit`](#commit) | Conventional commits | Git commits |
| [`ai-wrapper-product`](#ai-wrapper-product) | Productos AI wrapper | SaaS AI |

---

## Detalle de Skills

### architect-review

**Path:** `.claude/skills/architect-review/SKILL.md`

Revisiones de arquitectura especializadas en patrones modernos:
- Clean Architecture y Hexagonal Architecture
- Microservicios y arquitectura orientada a eventos
- Domain-Driven Design (DDD)
- Principios SOLID

**Uso típico:**
```
"Review this microservice design for proper bounded context boundaries"
"Assess the architectural impact of adding event sourcing to our system"
```

### senior-architect

**Path:** `.claude/skills/senior-architect/SKILL.md`

 toolkit completo para arquitectura de sistemas:
- Diagramas automáticos con scripts
- Análisis de dependencias
- Patrones de arquitectura
- Decisiones de tech stack

**Scripts disponibles:**
```bash
python scripts/architecture_diagram_generator.py <project-path>
python scripts/project_architect.py <target-path>
python scripts/dependency_analyzer.py [options]
```

### software-architecture

**Path:** `.claude/skills/software-architecture/SKILL.md`

Principios de calidad para desarrollo:
- Clean Architecture y DDD
- Early return pattern
- Library-first approach
- Anti-patrones a evitar (utils, helpers, common)

### python-pro

**Path:** `.claude/skills/python-pro/SKILL.md`

Experto en Python 3.12+ con enfoque moderno:
- Features Python 3.12+ (pattern matching, type hints)
- Async/await patterns
- FastAPI, Pydantic V2
- pytest, coverage
- Docker, deployment

**Ejemplos de uso:**
```
"Help me migrate from pip to uv for package management"
"Optimize this Python code for better async performance"
"Design a FastAPI application with proper error handling"
```

### python-patterns

**Path:** `.claude/skills/python-patterns/SKILL.md`

Guía de decisión para patrones Python:
- Framework selection (FastAPI vs Django vs Flask)
- Async vs Sync decision tree
- Type hints strategy
- Project structure principles

**Decisión de framework:**
```
API/Microservices → FastAPI
Full-stack/CMS → Django  
Simple/Learning → Flask
AI/ML API → FastAPI
```

### python-testing-patterns

**Path:** `.claude/skills/python-testing-patterns/SKILL.md`

Testing comprehensivo con pytest:
- Fixtures y mocking
- TDD workflow
- Async testing
- Property-based testing

**Recursos:**
- `resources/implementation-playbook.md` - patrones detallados

### python-performance-optimization

**Path:** `.claude/skills/python-performance-optimization/SKILL.md`

Optimización de rendimiento Python:
- cProfile, py-spy, memory_profiler
- Bottleneck identification
- Async optimization
- Memory optimization

### python-packaging

**Path:** `.claude/skills/python-packaging/SKILL.md`

Distribución de packages Python:
- pyproject.toml setup
- CLI tools
- PyPI publishing

### fastapi-pro

**Path:** `.claude/skills/fastapi-pro/SKILL.md`

Experto en FastAPI avanzado:
- FastAPI 0.100+ features
- Pydantic V2
- SQLAlchemy 2.0 async
- WebSockets, background tasks
- Middleware, lifespan events

**Capacidades:**
- Dependency injection avanzado
- Custom exception handlers
- Rate limiting, circuit breaker
- Observability, logging

### fastapi-templates

**Path:** `.claude/skills/fastapi-templates/SKILL.md`

Templates para nuevos proyectos FastAPI:
- Estructura de proyecto
- Patrones de código
- Recursos en `resources/implementation-playbook.md`

### fastapi-router-py

**Path:** `.claude/skills/fastapi-router-py/SKILL.md`

Creación de rutas FastAPI con:
- CRUD operations
- Authentication dependencies
- Response models
- HTTP status codes

### testing-patterns

**Path:** `.claude/skills/testing-patterns/SKILL.md`

Patrones de testing (enfocado en Jest/TypeScript):
- Factory pattern
- Custom render functions
- Mocking strategies
- TDD workflow

### test-fixing

**Path:** `.claude/skills/test-fixing/SKILL.md`

Metodología para arreglar tests fallando:
1. Run tests: `make test`
2. Smart error grouping
3. Fix infrastructure first → then API → finally logic
4. Verify each group

**Workflow:**
```
1. Run `make test` → identify failures
2. Group by: error type, module, root cause
3. Fix highest impact first
4. Verify with focused tests
```

### docker-expert

**Path:** `.claude/skills/docker-expert/SKILL.md`

Experto Docker con enfoque en:
- Multi-stage builds
- Image optimization
- Security hardening
- Docker Compose orchestration
- .dockerignore optimization

**Checklist de seguridad:**
- [ ] Non-root user (USER directive)
- [ ] Secrets proper management
- [ ] Base image updated
- [ ] Minimal attack surface
- [ ] Health checks

### langchain-architecture

**Path:** `.claude/skills/langchain-architecture/SKILL.md`

Aplicaciones LLM con LangChain:
- Agents (ReAct, OpenAI Functions, etc.)
- Chains (LLMChain, SequentialChain, etc.)
- Memory (Buffer, Summary, Window, etc.)
- Document processing
- RAG implementation

**Patrón RAG:**
```python
from langchain.chains import RetrievalQA
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
```

### api-security-best-practices

**Path:** `.claude/skills/api-security-best-practices/SKILL.md`

Seguridad API comprehensiva:
- JWT authentication
- OAuth 2.0
- Input validation (Zod, Pydantic)
- Rate limiting
- SQL injection prevention
- XSS protection

**OWASP API Top 10:**
1. Broken Object Level Authorization
2. Broken Authentication
3. Broken Object Property Level Authorization
4. Unrestricted Resource Consumption
5. Broken Function Level Authorization

### html-injection-testing

**Path:** `.claude/skills/html-injection-testing/SKILL.md`

Testing de vulnerabilidades XSS (solo contextos autorizados):
- Técnicas de inyección HTML
- Metodología de testing
- Validación de sanitización

### wiki-page-writer

**Path:** `.claude/skills/wiki-page-writer/SKILL.md`

Documentación técnica avanzada:
- Mermaid diagrams (min 2 por página)
- Dark-mode colors obligatorios
- Citas con file:line_number
- Estructura: Overview → Architecture → Components → Data Flow → Implementation

**Requisitos:**
- Frontmatter VitePress
- Minimum 5 source files citados
- Pseudocode cuando sea necesario

### mermaid-expert

**Path:** `.claude/skills/mermaid-expert/SKILL.md`

Diagramas Mermaid profesionales:
- Flowcharts, sequence diagrams
- ERDs, class diagrams
- State diagrams
- Gantt, timeline

**Tipos soportados:**
```
graph, sequenceDiagram, classDiagram,
stateDiagram-v2, erDiagram, gantt, pie,
gitGraph, journey, quadrantChart, timeline
```

### java-pro

**Path:** `.claude/skills/java-pro/SKILL.md`

Java 21+ expert:
- Virtual threads (Project Loom)
- Pattern matching
- Spring Boot 3.x
- GraalVM Native Image

### agent-tool-builder

**Path:** `.claude/skills/agent-tool-builder/SKILL.md`

Construcción de tools para AI agents:
- Definición de tools
- Integración con agents
- Tool execution patterns

### linux-shell-scripting

**Path:** `.claude/skills/linux-shell-scripting/SKILL.md`

Scripts shell para producción:
- Automatización
- Monitoreo
- Backup scripts

### prompt-engineer

**Path:** `.claude/skills/prompt-engineer/SKILL.md`

Prompt engineering para LLMs:
- Técnicas de prompting
- Optimización de prompts
- Chain-of-thought

### commit

**Path:** `.claude/skills/commit/SKILL.md`

Conventional commits (formato Sentry):
```
feat: Add new feature
fix: Bug fix
refactor: Code refactoring
test: Testing
docs: Documentation
chore: Maintenance
```

### ai-wrapper-product

**Path:** `.claude/skills/ai-wrapper-product/SKILL.md`

Productos AI wrapper (SaaS):
- Prompt engineering para productos
- Cost management
- Rate limiting
- Patrones de negocio AI

---

## Railway Skills

El proyecto tiene skills específicos para Railway en `.claude/skills/railway/`:

| Skill | Descripción |
|-------|-------------|
| `railway/new` | Deploy a Railway |
| `railway/deploy` | Push código a Railway |
| `railway/status` | Estado del deployment |
| `railway/metrics` | Métricas de uso |
| `railway/environment` | Variables de entorno |
| `railway/database` | Bases de datos |
| `railway/domain` | Dominios |
| `railway/projects` | Proyectos |
| `railway/deployment` | Deployment lifecycle |
| `railway/service` | Servicios |
| `railway/railway-docs` | Documentación Railway |
| `railway/central-station` | Comunidad Railway |

---

## Guía de Uso

### Invocación Explícita

```bash
@.claude/skills/<skill-name>/SKILL.md
```

### Activación Proactiva

Los skills se activan automáticamente según el contexto del proyecto (definido en CLAUDE.md):

**Python/FastAPI:** `python-pro`, `fastapi-pro`, `python-patterns`
**Testing:** `test-fixing`, `python-testing-patterns`
**Docker:** `docker-expert`
**Arquitectura:** `architect-review`, `senior-architect`
**Seguridad:** `api-security-best-practices`

### Selección de Skill

```
¿Necesitas...?
├── Arquitectura/Diseño → architect-review, senior-architect
├── Código Python → python-pro, python-patterns
├── FastAPI → fastapi-pro, fastapi-templates
├── Testing → test-fixing, python-testing-patterns
├── Docker → docker-expert
├── LLM/LangChain → langchain-architecture
├── Seguridad → api-security-best-practices
├── Docs → wiki-page-writer, mermaid-expert
└── Railway → railway/*
```

---

## Referencia Rápida

| Tarea | Skill Recomendado |
|-------|-------------------|
| Diseñar arquitectura | `architect-review` |
| Revisar código | `architect-review` |
| Nuevo proyecto Python | `python-pro` |
| Optimizar rendimiento | `python-performance-optimization` |
| FastAPI avanzado | `fastapi-pro` |
| Nuevos endpoints | `fastapi-router-py` |
| Arreglar tests | `test-fixing` |
| Docker optimization | `docker-expert` |
| RAG/LLM | `langchain-architecture` |
| Seguridad API | `api-security-best-practices` |
| Documentación | `wiki-page-writer` |
| Diagramas | `mermaid-expert` |
| Deploy Railway | `railway/new` |

---

## Referencias

- [CLAUDE.md](./CLAUDE.md) - Configuración del proyecto
- [.claude/skills/](../.claude/skills/) - Skills source
- [docs/](./) - Documentación adicional
