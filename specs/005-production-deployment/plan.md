# Implementation Plan: Local API Server

**Branch**: `005-production-deployment` | **Date**: 2025-12-03 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/005-production-deployment/spec.md`

## Summary

Transform the existing CLI-only educational agent system into an HTTP API-accessible service with Docker containerization. The core deliverables are: (1) a FastAPI server exposing the ADK agents via RESTful endpoints with session management, and (2) a Docker container packaging all dependencies for consistent local development environments.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI, uvicorn, google-adk, google-genai, pymupdf, python-dotenv
**Storage**: SQLite (existing storage.py implementation)
**Testing**: pytest, pytest-asyncio (existing from 003-test-evaluation)
**Target Platform**: Linux/macOS/Windows (local development)
**Project Type**: Single project extending existing `adk/` module
**Performance Goals**: Server startup <5s, API response <3s overhead (excluding Gemini latency)
**Constraints**: Container image <1GB, local-only (no cloud deployment)
**Scale/Scope**: Single developer local use, concurrent request handling via async

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The project constitution uses template placeholders, so no specific gates are enforced. Following general best practices:

| Gate | Status | Notes |
|------|--------|-------|
| Library-First | PASS | Extends existing adk/ module without breaking CLI |
| Test-First | PASS | Will use existing pytest infrastructure |
| Simplicity | PASS | FastAPI chosen for minimal boilerplate + auto-docs |

## Project Structure

### Documentation (this feature)

```text
specs/005-production-deployment/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (OpenAPI spec)
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
adk/
├── __init__.py          # Existing
├── agent.py             # Existing - root_agent, app
├── run_dev.py           # Existing - CLI runner
├── server.py            # NEW - FastAPI application
├── storage.py           # Existing - SQLite persistence
├── tools.py             # Existing
├── quiz_tools.py        # Existing
├── rag_setup.py         # Existing
└── question_pipeline.py # Existing

tests/
├── test_server.py       # NEW - API endpoint tests
└── ...                  # Existing tests

Dockerfile               # NEW - Container build definition
docker-compose.yml       # NEW - Local development orchestration
.dockerignore            # NEW - Build context exclusions
```

**Structure Decision**: Single project structure extending the existing `adk/` module with a new `server.py` file for the FastAPI application. Docker configuration files at repository root.

## Complexity Tracking

No violations requiring justification.
