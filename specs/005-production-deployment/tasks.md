# Tasks: Local API Server

**Input**: Design documents from `/specs/005-production-deployment/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/openapi.yaml

**Tests**: Not explicitly requested in specification. Test tasks omitted.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Single project** extending existing `adk/` module
- API server code: `adk/server.py`, `adk/models.py`
- Docker files: `Dockerfile`, `docker-compose.yml`, `.dockerignore` at repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Add new dependencies and create basic server structure

- [ ] T001 Add FastAPI dependencies to adk/requirements.txt (fastapi, uvicorn[standard], pydantic-settings, httpx)
- [ ] T002 [P] Create Pydantic models file in adk/models.py with ChatRequest, ChatResponse, HealthStatus, ErrorResponse schemas
- [ ] T003 [P] Create .dockerignore file at repository root to exclude __pycache__, .env, .git, data/, *.pyc

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T004 Create base FastAPI application skeleton in adk/server.py with lifespan context manager for startup/shutdown
- [ ] T005 [P] Implement configuration settings class using pydantic-settings in adk/config.py (GOOGLE_API_KEY, PDF_PATH, DATA_DIR, PORT, LOG_LEVEL, GEMINI_MODEL)
- [ ] T006 [P] Create RFC 7807 error handler middleware in adk/server.py for consistent ErrorResponse format
- [ ] T007 Implement request logging middleware in adk/server.py (configurable via LOG_LEVEL)
- [ ] T008 Setup ADK Runner initialization in server startup (InMemorySessionService, InMemoryMemoryService, LoggingPlugin)
- [ ] T009 Create __main__.py entry point in adk/server.py for `python -m adk.server` command

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Access Agent via Local API (Priority: P1) 🎯 MVP

**Goal**: Developer can send messages to the educational agent via HTTP POST /chat and receive JSON responses with session continuity

**Independent Test**: Start server with `python -m adk.server`, send `curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d '{"message": "Hello"}'`, verify JSON response with session_id and agent message

### Implementation for User Story 1

- [ ] T010 [US1] Implement POST /chat endpoint in adk/server.py that accepts ChatRequest and returns ChatResponse
- [ ] T011 [US1] Implement session creation logic: generate session_id if not provided, call session_service.create_session()
- [ ] T012 [US1] Implement ADK runner.run_async() integration to process user message and extract final response
- [ ] T013 [US1] Add response metadata collection (response_time_ms, model name, tool_calls list)
- [ ] T014 [US1] Implement session context reuse for subsequent requests with same session_id
- [ ] T015 [US1] Add 503 error handling when Gemini API is unreachable
- [ ] T016 [US1] Persist chat messages to SQLite via storage.log_message() in adk/server.py

**Checkpoint**: At this point, the core API is functional. Can send messages and receive agent responses via HTTP.

---

## Phase 4: User Story 2 - Run in Container Locally (Priority: P1)

**Goal**: Application packaged as Docker container with all dependencies, runnable via `docker run`

**Independent Test**: `docker build -t learning-ai-agents .` then `docker run --rm -p 8000:8000 -e GOOGLE_API_KEY=... learning-ai-agents`, verify same behavior as non-containerized

### Implementation for User Story 2

- [ ] T017 [US2] Create Dockerfile at repository root using python:3.11-slim base image
- [ ] T018 [US2] Add COPY instructions for adk/, requirements.txt, and PDF content files
- [ ] T019 [US2] Configure Dockerfile to install dependencies and set WORKDIR
- [ ] T020 [US2] Set Dockerfile CMD to run uvicorn with adk.server:app on port 8000
- [ ] T021 [US2] Create docker-compose.yml at repository root with env_file support and port mapping
- [ ] T022 [US2] Add health check instruction to docker-compose.yml
- [ ] T023 [US2] Add volume mount for data/ directory in docker-compose.yml for persistent storage

**Checkpoint**: Container builds and runs. Application behavior identical to direct Python execution.

---

## Phase 5: User Story 3 - Interactive API Documentation (Priority: P2)

**Goal**: Auto-generated OpenAPI documentation accessible at /docs endpoint with interactive Swagger UI

**Independent Test**: Start server, navigate to http://localhost:8000/docs in browser, verify all endpoints documented with schemas and "Try it out" works

### Implementation for User Story 3

- [ ] T024 [US3] Configure FastAPI app with title, description, version metadata in adk/server.py
- [ ] T025 [US3] Add OpenAPI examples to ChatRequest and ChatResponse models in adk/models.py
- [ ] T026 [US3] Ensure all endpoint parameters have descriptions using Field() in adk/models.py
- [ ] T027 [US3] Add endpoint docstrings for /chat, /sessions, /sessions/{session_id} in adk/server.py
- [ ] T028 [US3] Verify /docs and /redoc endpoints are enabled (FastAPI default)

**Checkpoint**: Documentation UI fully functional with all endpoints, schemas, and interactive testing.

---

## Phase 6: User Story 4 - Health Check Endpoint (Priority: P2)

**Goal**: /health endpoint returns service status including Gemini API connectivity and storage status

**Independent Test**: `curl http://localhost:8000/health`, verify JSON response with status, version, uptime_seconds, checks object

### Implementation for User Story 4

- [ ] T029 [US4] Implement GET /health endpoint in adk/server.py returning HealthStatus model
- [ ] T030 [US4] Add server start time tracking for uptime_seconds calculation
- [ ] T031 [US4] Implement Gemini API connectivity check using httpx async request
- [ ] T032 [US4] Implement storage health check (verify SQLite database accessible)
- [ ] T033 [US4] Add logic to determine overall status: healthy (all up), degraded (storage up but gemini down), unhealthy (storage down)
- [ ] T034 [US4] Return 503 status code when overall status is unhealthy

**Checkpoint**: Health endpoint fully functional, reports accurate status for all dependencies.

---

## Phase 7: Sessions Management (Supporting Endpoints)

**Goal**: Session listing and detail endpoints for debugging and management

**Independent Test**: `curl http://localhost:8000/sessions`, verify JSON array of sessions; `curl http://localhost:8000/sessions/{id}`, verify session details with message history

### Implementation

- [ ] T035 [P] Implement GET /sessions endpoint in adk/server.py returning list of SessionInfo
- [ ] T036 [P] Implement GET /sessions/{session_id} endpoint in adk/server.py returning SessionDetail with message history
- [ ] T037 Add SessionInfo and SessionDetail models to adk/models.py
- [ ] T038 Add 404 handling for session not found in GET /sessions/{session_id}

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements and validation

- [ ] T039 Add startup validation: fail fast if GOOGLE_API_KEY not set with clear error message
- [ ] T040 [P] Update adk/__init__.py to export server module
- [ ] T041 Verify all success criteria from spec.md (startup <5s, response <3s overhead, image <1GB)
- [ ] T042 Run quickstart.md validation scenarios manually
- [ ] T043 [P] Update CLAUDE.md with server running instructions and PORT configuration

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phases 3-6)**: All depend on Foundational phase completion
  - US1 and US2 are both P1 priority, can proceed in parallel if desired
  - US3 and US4 are P2 priority, can proceed after P1 or in parallel
- **Sessions Management (Phase 7)**: Depends on US1 (needs /chat to create sessions)
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after US1 is complete (needs working server to containerize)
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - Documentation works with any endpoints
- **User Story 4 (P2)**: Can start after Foundational (Phase 2) - Independent endpoint

### Within Each User Story

- Core implementation before integration
- Validation and error handling after happy path
- Story complete before moving to next priority

### Parallel Opportunities

- T002 and T003 can run in parallel (different files)
- T005 and T006 can run in parallel (different concerns)
- T035 and T036 can run in parallel (different endpoints)
- US3 and US4 can be worked on in parallel (independent P2 features)

---

## Parallel Example: Phase 1 Setup

```bash
# Launch together:
Task: "Add FastAPI dependencies to adk/requirements.txt"
Task: "Create Pydantic models file in adk/models.py"
Task: "Create .dockerignore file at repository root"
```

## Parallel Example: User Story 2

```bash
# After T017 (base Dockerfile), these can run together:
Task: "Create docker-compose.yml at repository root"
Task: "Add health check instruction to docker-compose.yml"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: `curl http://localhost:8000/chat -d '{"message":"test"}'`
5. Deploy/demo if ready - core API is functional

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add User Story 1 → Test with curl → MVP complete!
3. Add User Story 2 → Docker build/run → Containerized MVP
4. Add User Story 3 → /docs works → Enhanced DX
5. Add User Story 4 → /health works → Production-ready local server
6. Each story adds value without breaking previous stories

### Suggested MVP Scope

**Minimum**: Phase 1 + Phase 2 + Phase 3 (User Story 1)
- Delivers: Working HTTP API for agent interaction
- Tests with: `curl -X POST http://localhost:8000/chat -d '{"message":"Hello"}'`

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
