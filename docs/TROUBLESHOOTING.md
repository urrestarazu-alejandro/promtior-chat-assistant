---
title: "Troubleshooting"
description: "Soluciones a problemas comunes"
---

# Troubleshooting Guide

## Common Errors

### "Collection expecting embedding with dimension of 768, got 1536"

**Causa:** ChromaDB fue poblado con embeddings de Ollama (768 dimensiones) pero ahora se usan OpenAI embeddings (1536 dimensiones).

**Solución:**
```bash
# Cambiar directorio de ChromaDB
# En config.py, cambiar chroma_persist_directory a un directorio nuevo
# O ejecutar re-ingest con el directorio correcto
```

### "Database error: attempt to write a readonly database"

**Causa:** ChromaDB está en modo solo lectura.

**Solución:**
```bash
# Redeploy en Railway
railway redeploy -y

# Luego re-ingestar
curl -X POST 'https://promtior-chat-assistant-production.up.railway.app/admin/reingest?admin_key=promtior_reingest_2024'
```

### "Failed to generate RAG answer after 3 attempts"

**Causa:** Error de conexión con el LLM (Ollama o OpenAI).

**Solución:**
- Verificar que las variables de entorno estén configuradas correctamente
- Verificar que el LLM esté disponible
- Revisar logs: `railway logs --lines 50`

### "Empty response from AI"

**Causa:** El RAG no encontró documentos relevantes.

**Solución:**
- Verificar que los datos estén ingesados: `curl https://promtior-chat-assistant-production.up.railway.app/admin/reingest?admin_key=YOUR_KEY`
- Verificar que el sitio web y PDFs tengan el contenido esperado

### "No tengo esa información"

**Causa:** El RAG no encontró documentos relevantes para la pregunta en ChromaDB.

**Esto puede ocurrir cuando:**
1. ChromaDB está vacío (nunca se ejecutó re-ingest)
2. El contenido no existe en las fuentes de datos (sitio web o PDFs)
3. El chunking no capturó la información relevante
4. La pregunta es muy diferente a cómo está almacenada la información

**Solución:**
```bash
# 1. Re-ingestar datos
curl -X POST 'https://promtior-chat-assistant-production.up.railway.app/admin/reingest?admin_key=promtior_reingest_2024'

# 2. Verificar que ingestión fue exitosa (debe decir "success")
# La respuesta debe ser:
# {"status":"success","message":"Data re-ingested successfully"}

# 3. Probar con una pregunta que sepamos que está en los datos
curl 'https://promtior-chat-assistant-production.up.railway.app/ask?q=What services does Promtior offer?'
```

**Si el problema persiste:**
- El sitio web de Promtior está construido con Wix (JavaScript dinámico)
- El scraping con BeautifulSoup no puede obtener todo el contenido
- La información debe estar en los PDFs del directorio `docs/`

**Verificar contenido ingestado:**
- Revisar que el PDF `docs/AI-Engineer-Test-Promtior.pdf` contenga la información
- Ese PDF incluye: "In May 2023, Promtior was founded"

### Ollama Connection Issues (Development)

```bash
# Verificar que Ollama esté corriendo
docker ps | grep ollama

# Reiniciar Ollama
docker restart promtior-ollama

# Ver logs
docker logs promtior-ollama
```

### Memory Issues

Si el modelo de Ollama requiere más memoria:
```bash
# Usar un modelo más pequeño en .env
OLLAMA_MODEL=tinyllama      # ~1GB RAM
OLLAMA_MODEL=llama2         # ~4GB RAM
OLLAMA_MODEL=phi3:mini      # ~3GB RAM
```

## Railway Deployment

### Variables Requeridas en Producción

```bash
ENVIRONMENT=production
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
USE_OPENAI_EMBEDDINGS=true
```

### Re-ingest en Producción

```bash
curl -X POST 'https://promtior-chat-assistant-production.up.railway.app/admin/reingest?admin_key=promtior_reingest_2024'
```

### Verificar Configuración

```bash
# Health check
curl https://promtior-chat-assistant-production.up.railway.app/health

# Verificar respuesta
curl 'https://promtior-chat-assistant-production.up.railway.app/ask?q=test'
```
