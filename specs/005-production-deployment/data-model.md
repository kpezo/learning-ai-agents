# Data Model: Local API Server

**Feature**: 005-production-deployment
**Date**: 2025-12-03

## Entities

### ChatRequest

Incoming message from API client to the educational agent.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `message` | string | Yes | User message text to send to the agent |
| `session_id` | string | No | Existing session ID for context continuity. If omitted, creates new session |
| `user_id` | string | No | User identifier for storage. Defaults to "local_user" |

**Validation Rules**:
- `message`: Non-empty string, max 10,000 characters
- `session_id`: UUID format if provided
- `user_id`: Alphanumeric with underscores, max 64 characters

### ChatResponse

Agent response returned to the API client.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `session_id` | string | Yes | Session identifier (new or existing) |
| `message` | string | Yes | Agent response text |
| `agent_name` | string | Yes | Name of responding agent (e.g., "tutor", "assessor") |
| `metadata` | object | No | Optional response metadata |

**Metadata Object**:
| Field | Type | Description |
|-------|------|-------------|
| `response_time_ms` | integer | Server processing time in milliseconds |
| `model` | string | Gemini model used |
| `tool_calls` | array | List of tools invoked by agent |

### HealthStatus

Health check response showing service status.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `status` | enum | Yes | Overall health: "healthy", "degraded", "unhealthy" |
| `version` | string | Yes | API server version |
| `uptime_seconds` | float | Yes | Seconds since server start |
| `checks` | object | Yes | Individual component health checks |

**Checks Object**:
| Field | Type | Description |
|-------|------|-------------|
| `gemini_api` | HealthCheck | Gemini API connectivity status |
| `storage` | HealthCheck | SQLite storage status |

**HealthCheck Object**:
| Field | Type | Description |
|-------|------|-------------|
| `status` | string | "up" or "down" |
| `latency_ms` | integer | Response time (optional) |
| `error` | string | Error message if down (optional) |

### ErrorResponse

Structured error response following RFC 7807.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | string | Yes | Error type identifier |
| `title` | string | Yes | Human-readable error title |
| `status` | integer | Yes | HTTP status code |
| `detail` | string | Yes | Detailed error description |
| `instance` | string | No | Request path that caused error |

### SessionInfo

Session metadata for listing/managing sessions.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `session_id` | string | Yes | Unique session identifier |
| `user_id` | string | Yes | Associated user |
| `created_at` | datetime | Yes | Session creation timestamp |
| `last_activity` | datetime | Yes | Last message timestamp |
| `message_count` | integer | Yes | Total messages in session |

## State Transitions

### Session Lifecycle

```
[No Session] --POST /chat (no session_id)--> [Active Session]
     ^                                             |
     |                                             v
     +----------- Session expires -----------[Expired Session]
                  (future feature)
```

**Session States**:
1. **No Session**: Client has no session_id
2. **Active Session**: Valid session_id with conversation context
3. **Expired Session**: Session_id no longer valid (future: TTL-based cleanup)

### Request Flow

```
Client Request
     |
     v
[Validate Request] --invalid--> [422 Error Response]
     |
     | valid
     v
[Get/Create Session] --error--> [500 Error Response]
     |
     | success
     v
[Run ADK Agent] --Gemini unreachable--> [503 Error Response]
     |
     | success
     v
[Persist to Storage]
     |
     v
[Return ChatResponse]
```

## Relationship to Existing Models

The API layer introduces new request/response models but reuses existing storage models from `adk/storage.py`:

| API Entity | Storage Entity | Relationship |
|------------|----------------|--------------|
| ChatRequest | SessionLog | Messages logged via `storage.log_message()` |
| ChatResponse | SessionLog | Responses logged with agent_name |
| SessionInfo | session_logs table | Derived from session log aggregation |

No new database tables required. All persistence uses existing `StorageService` methods.

## Pydantic Model Examples

```python
# adk/models.py (new file)
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=10000)
    session_id: Optional[str] = None
    user_id: str = Field(default="local_user", max_length=64)

class ToolCall(BaseModel):
    name: str
    arguments: dict

class ResponseMetadata(BaseModel):
    response_time_ms: int
    model: str
    tool_calls: List[ToolCall] = []

class ChatResponse(BaseModel):
    session_id: str
    message: str
    agent_name: str
    metadata: Optional[ResponseMetadata] = None

class HealthStatusEnum(str, Enum):
    healthy = "healthy"
    degraded = "degraded"
    unhealthy = "unhealthy"

class HealthCheck(BaseModel):
    status: str  # "up" or "down"
    latency_ms: Optional[int] = None
    error: Optional[str] = None

class HealthStatus(BaseModel):
    status: HealthStatusEnum
    version: str
    uptime_seconds: float
    checks: dict[str, HealthCheck]

class ErrorResponse(BaseModel):
    type: str
    title: str
    status: int
    detail: str
    instance: Optional[str] = None
```
