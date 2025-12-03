# Research: Local API Server

**Feature**: 005-production-deployment
**Date**: 2025-12-03

## Research Tasks

### 1. FastAPI + ADK Integration Pattern

**Decision**: Use FastAPI with async endpoints that wrap ADK Runner calls

**Rationale**:
- FastAPI is async-native and aligns with ADK's `runner.run_async()` pattern
- FastAPI automatically generates OpenAPI documentation (FR-005)
- Built-in request validation via Pydantic models
- uvicorn provides production-ready ASGI server

**Alternatives Considered**:
- Flask: Not async-native, would require additional libraries (flask-async)
- Starlette: Lower-level than needed; FastAPI builds on Starlette anyway
- aiohttp: Less integrated OpenAPI support, more manual setup

### 2. Session Management Strategy

**Decision**: Combine ADK InMemorySessionService with API-level session tracking

**Rationale**:
- ADK sessions (`InMemorySessionService`) handle conversation context
- API layer generates and returns `session_id` to clients
- Clients include `session_id` in subsequent requests for context continuity
- Session data persists to SQLite via existing `storage.py` for durability

**Implementation Pattern**:
```python
# First request (no session_id) → create new session
session_id = f"session-{uuid.uuid4().hex[:8]}"
await session_service.create_session(app_name, user_id, session_id)

# Subsequent requests → reuse session_id from client
# ADK maintains conversation context internally
```

**Alternatives Considered**:
- Redis sessions: Overkill for local-only use case
- JWT tokens: Unnecessary complexity for single-user local development
- Cookies: Less API-friendly than explicit session_id in JSON

### 3. Docker Base Image Selection

**Decision**: Use `python:3.11-slim` as base image

**Rationale**:
- Slim variant reduces image size (vs full python image)
- Python 3.11 matches existing project requirements
- Debian-based for compatibility with PyMuPDF native dependencies
- Multi-stage build not required given single-purpose container

**Alternatives Considered**:
- `python:3.11-alpine`: PyMuPDF has compatibility issues on Alpine
- `python:3.11`: Full image unnecessarily large (~900MB vs ~150MB slim)
- Distroless: Too restrictive for debugging local development issues

### 4. Configuration Management

**Decision**: Environment variables with python-dotenv fallback

**Rationale**:
- Consistent with existing `.env` pattern in project
- Docker containers easily configured via `-e` or `--env-file`
- FastAPI/Pydantic Settings can validate required vars at startup

**Required Environment Variables**:
| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GOOGLE_API_KEY` | Yes | - | Gemini API authentication |
| `PDF_PATH` | No | `Intro.pdf` | Educational content source |
| `DATA_DIR` | No | `./data/` | SQLite database location |
| `PORT` | No | `8000` | API server port |
| `LOG_LEVEL` | No | `INFO` | Logging verbosity |
| `GEMINI_MODEL` | No | `gemini-2.5-flash-lite` | Model selection |

### 5. Error Response Format

**Decision**: Use RFC 7807 Problem Details structure

**Rationale**:
- Industry standard for HTTP API errors
- Provides structured, parseable error responses
- FastAPI HTTPException can be customized for this format

**Error Response Schema**:
```json
{
  "type": "error_type",
  "title": "Human-readable title",
  "status": 422,
  "detail": "Detailed error description",
  "instance": "/api/chat"
}
```

**Status Code Mapping**:
| Scenario | Status | Type |
|----------|--------|------|
| Invalid request body | 422 | `validation_error` |
| Session not found | 404 | `session_not_found` |
| Gemini API unreachable | 503 | `upstream_unavailable` |
| Missing API key | 500 | `configuration_error` |

### 6. Streaming vs Request-Response

**Decision**: Start with request-response; streaming as future enhancement

**Rationale**:
- Request-response is simpler to implement and test
- Existing `run_dev.py` streams events, but API clients need simple JSON response first
- Streaming (SSE) can be added later for real-time agent thoughts
- Most integration use cases (curl, Postman, frontend POC) work fine with sync responses

**Alternatives Considered**:
- Server-Sent Events (SSE): Adds complexity; defer to future iteration
- WebSockets: Overkill for request-response pattern

### 7. Health Check Implementation

**Decision**: Dedicated `/health` endpoint with Gemini connectivity test

**Rationale**:
- Required by FR-006
- Validates both server running and external dependency (Gemini API)
- Simple lightweight check suitable for scripting/tooling

**Health Response Schema**:
```json
{
  "status": "healthy|degraded|unhealthy",
  "version": "0.1.0",
  "uptime_seconds": 123.45,
  "checks": {
    "gemini_api": {"status": "up|down", "latency_ms": 150},
    "storage": {"status": "up|down", "database_size_bytes": 1024}
  }
}
```

### 8. Concurrency Model

**Decision**: Rely on FastAPI/uvicorn async handling

**Rationale**:
- FastAPI handles concurrent requests via async/await
- Each request gets independent ADK session context
- No custom threading/multiprocessing required
- uvicorn workers can be scaled if needed (`--workers N`)

## Dependencies to Add

```text
# In adk/requirements.txt or separate requirements-server.txt
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pydantic-settings>=2.0.0  # For configuration management
httpx>=0.25.0             # For health check async HTTP calls
```

## Open Questions Resolved

| Question | Resolution |
|----------|------------|
| How to handle long-running agent responses? | Request-response with reasonable timeout (60s); streaming deferred |
| Should we use middleware for logging? | Yes, FastAPI middleware for request logging |
| How to handle multiple users? | user_id from request (or default "local_user" for simplicity) |
