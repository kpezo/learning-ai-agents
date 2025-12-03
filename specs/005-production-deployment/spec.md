# Feature Specification: Local API Server

**Feature Branch**: `005-production-deployment`
**Created**: 2025-12-03
**Status**: Draft
**Input**: User description: "Local API server for the educational agent system - containerization and HTTP API access for local development and testing"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Access Agent via Local API (Priority: P1)

A developer runs the educational agent as a local HTTP server and interacts with it via API requests. This enables building web frontends, testing integrations, or using tools like curl/Postman to interact with the agent programmatically.

**Why this priority**: This is the core value proposition - transforming the CLI-only agent into an API-accessible service that can be integrated with other local applications.

**Independent Test**: Can be tested by starting the local server and sending an HTTP request, then verifying a valid agent response is received.

**Acceptance Scenarios**:

1. **Given** a configured environment with GOOGLE_API_KEY set, **When** the developer runs the server start command, **Then** the API server starts and listens on a local port.

2. **Given** a running local server, **When** a client sends a message via the API, **Then** it receives the agent's response in a structured JSON format.

3. **Given** a client with a valid session, **When** it sends multiple messages, **Then** conversation context is maintained across requests.

---

### User Story 2 - Run in Container Locally (Priority: P1)

The application is packaged in a Docker container that includes all dependencies. Developers can run this container locally without installing Python dependencies directly, ensuring consistent behavior.

**Why this priority**: Equally critical - containers eliminate dependency issues and provide a consistent runtime environment across different developer machines.

**Independent Test**: Can be tested by building the container and running it locally, then comparing behavior to the non-containerized application.

**Acceptance Scenarios**:

1. **Given** the application source code, **When** `docker build` is run, **Then** a container image is created with all dependencies included.

2. **Given** a container image and a .env file with GOOGLE_API_KEY, **When** `docker run` is executed, **Then** the API server starts and accepts requests on the configured port.

3. **Given** the same container image, **When** run on different machines (Mac, Linux, Windows with WSL), **Then** behavior is identical.

---

### User Story 3 - Interactive API Documentation (Priority: P2)

The local server provides auto-generated API documentation (OpenAPI/Swagger) that developers can use to explore endpoints, understand request/response formats, and test the API interactively.

**Why this priority**: Enhances developer experience but the core API functionality works without documentation UI.

**Independent Test**: Can be tested by accessing the /docs endpoint and verifying the Swagger UI loads with all endpoints documented.

**Acceptance Scenarios**:

1. **Given** a running local server, **When** a developer accesses /docs in a browser, **Then** they see interactive Swagger documentation.

2. **Given** the Swagger UI, **When** a developer clicks "Try it out" on an endpoint, **Then** they can send a test request and see the response.

3. **Given** API endpoints with request/response models, **When** viewing documentation, **Then** all fields are described with types and examples.

---

### User Story 4 - Health Check Endpoint (Priority: P2)

The server exposes a health check endpoint that reports whether the service is running and can connect to required dependencies (Gemini API).

**Why this priority**: Useful for development tooling and scripting but not essential for basic operation.

**Independent Test**: Can be tested by calling the health endpoint and verifying it returns status information.

**Acceptance Scenarios**:

1. **Given** a running server, **When** /health is called, **Then** it returns a 200 status with service health information.

2. **Given** a server with a valid GOOGLE_API_KEY, **When** /health is called, **Then** it confirms Gemini API connectivity.

3. **Given** a server with an invalid API key, **When** /health is called, **Then** it reports the Gemini API connection as unhealthy.

---

### Edge Cases

- What happens when GOOGLE_API_KEY is not set? Server fails to start with a clear error message indicating the missing configuration.
- How does the server handle malformed JSON requests? Returns 422 Unprocessable Entity with validation error details.
- What happens when the Gemini API is unreachable? Returns 503 Service Unavailable with an error message; subsequent requests can retry.
- How does the server handle concurrent requests? FastAPI handles concurrent requests via async; each request gets its own session context.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST expose a local HTTP API for agent interaction.

- **FR-002**: System MUST start via a simple command (e.g., `python -m adk.server` or `docker run`).

- **FR-003**: System MUST maintain conversation context across multiple API requests within a session.

- **FR-004**: System MUST be packageable as a Docker container image with all dependencies.

- **FR-005**: System MUST provide auto-generated OpenAPI documentation at /docs endpoint.

- **FR-006**: System MUST include a health check endpoint at /health.

- **FR-007**: System MUST read configuration from environment variables (GOOGLE_API_KEY, PDF_PATH, DATA_DIR, etc.).

- **FR-008**: System MUST return structured JSON responses with consistent error format.

- **FR-009**: System MUST log API requests for debugging (configurable log level).

- **FR-010**: System MUST persist session and learning data using the existing SQLite storage (storage.py).

### Key Entities

- **APIServer**: The FastAPI application instance with configured routes and middleware.

- **Session**: A conversation context maintained across API requests, identified by session_id.

- **ChatRequest**: Incoming message from client containing session_id (optional for new sessions) and user message.

- **ChatResponse**: Agent response containing session_id, agent message, and optional metadata (tokens used, response time).

- **HealthStatus**: Current state of the server including uptime, Gemini API connectivity, and storage status.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Server starts and accepts requests within 5 seconds of running the start command.

- **SC-002**: API response times average under 3 seconds for typical agent interactions (excluding Gemini API latency).

- **SC-003**: Container builds complete in under 3 minutes from source.

- **SC-004**: Container image size is under 1GB.

- **SC-005**: All existing agent functionality (quiz, tutoring, curriculum planning) works identically via API as via CLI.

- **SC-006**: OpenAPI documentation correctly describes all endpoints with request/response schemas.

## Assumptions

- System is designed for local development and testing only; not for production deployment.
- Web API will be implemented using FastAPI for async support and automatic OpenAPI documentation.
- Container technology will be Docker-compatible.
- The existing ADK agent system will be adapted to run in server mode alongside the existing CLI mode.
- Session storage uses the existing SQLite per-user storage pattern (storage.py).
- Configuration is managed via environment variables, consistent with existing .env pattern.
- Default port is 8000 but configurable via PORT environment variable.

## Clarifications

### Session 2025-12-03

- Q: Should this support cloud deployment? → A: No, local-only. Removed all cloud/production deployment scope.
- Q: Which web framework should be used for the API? → A: FastAPI - async-native, automatic OpenAPI docs, compatible with ADK async patterns.
- Q: How should session storage work? → A: Extend existing SQLite per-user storage (storage.py) to persist session state.
