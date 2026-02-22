---
title: "API Configuration"
description: "Configuración de APIs y variables de entorno"
---

# API Configuration

For complete environment variables reference, see [CLAUDE.md](../CLAUDE.md#environment-variables).

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

**Rate Limiting:** 30 requests/minute

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

**Rate Limit Exceeded:**
```json
{
  "error": "Rate limit exceeded",
  "message": "Too many requests. Please try again later.",
  "retry_after": "60"
}
```

### POST /admin/reingest

Re-ingestar datos en ChromaDB.

**⚠️ BREAKING CHANGE (v2.1):** Admin key now required via `Authorization` header (no longer accepts query parameter).

**Authentication:** Bearer token via Authorization header

**Headers:**
| Header | Value | Description |
|--------|-------|-------------|
| `Authorization` | `Bearer <admin_key>` | Admin authentication key (required) |

**Rate Limiting:** 3 requests/hour

**Example Request:**
```bash
curl -X POST https://your-app.up.railway.app/admin/reingest \
  -H "Authorization: Bearer your_admin_key_here"
```

**Response:**
```json
{
  "status": "success",
  "message": "Data re-ingested successfully"
}
```

**Error Responses:**

Missing Authorization header:
```json
{
  "detail": "Authorization header required. Use: Authorization: Bearer <admin_key>"
}
```

Invalid admin key:
```json
{
  "detail": "Invalid admin key."
}
```

Admin key not configured:
```json
{
  "detail": "Admin authentication not configured. Contact system administrator."
}
```

## Security Features (v2.1)

### CORS Configuration

**Development:**
- Allowed origins: `http://localhost:3000`, `http://localhost:8000`
- Credentials: `false`

**Production:**
- Allowed origins: Configurable via `CORS_ALLOWED_ORIGINS` environment variable (comma-separated)
- Credentials: `true` (only when specific origins are configured)
- Methods: `GET`, `POST`, `OPTIONS`
- Headers: `Content-Type`, `Authorization`, `X-Request-ID`

**Example:**
```bash
CORS_ALLOWED_ORIGINS=https://promtior.com,https://www.promtior.com
```

### Rate Limiting

Rate limiting is enforced per IP address using in-memory storage.

**Limits:**
- `GET /ask`: 30 requests/minute
- `POST /admin/reingest`: 3 requests/hour
- Default: 100 requests/hour, 20 requests/minute

**Response Headers:**
- `X-RateLimit-Limit`: Request limit
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Time when limit resets
- `Retry-After`: Seconds to wait (on 429 errors)

### Security Headers

All responses include OWASP-recommended security headers:

| Header | Value | Purpose |
|--------|-------|---------|
| `X-Content-Type-Options` | `nosniff` | Prevent MIME sniffing |
| `X-Frame-Options` | `DENY` | Prevent clickjacking |
| `X-XSS-Protection` | `1; mode=block` | Enable XSS filter |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | Control referrer info |
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains` | Force HTTPS (production only) |
| `Content-Security-Policy` | Restrictive CSP | Prevent XSS/injection |
| `Permissions-Policy` | Restrictive permissions | Disable unused features |

### Authentication

**Admin Endpoints:**
- Authentication: Bearer token via `Authorization` header
- Format: `Authorization: Bearer <admin_key>`
- Key stored in: `ADMIN_REINGEST_KEY` environment variable
- Security: Not visible in logs, browser history, or URL

**Migration from Query Parameters:**

❌ **Old method (deprecated):**
```bash
curl -X POST "/admin/reingest?admin_key=secret"
```

✅ **New method (required):**
```bash
curl -X POST "/admin/reingest" \
  -H "Authorization: Bearer secret"
```
