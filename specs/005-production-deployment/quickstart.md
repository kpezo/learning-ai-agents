# Quickstart: Local API Server

**Feature**: 005-production-deployment

## Prerequisites

- Python 3.11+
- Docker (optional, for containerized deployment)
- `GOOGLE_API_KEY` environment variable set

## Option 1: Run Directly

### Install Dependencies

```bash
# From repository root
pip install -r adk/requirements.txt
pip install fastapi uvicorn[standard] pydantic-settings httpx
```

### Start the Server

```bash
# From repository root
python -m adk.server

# Or with custom port
PORT=9000 python -m adk.server
```

### Verify

```bash
# Health check
curl http://localhost:8000/health

# Interactive documentation
open http://localhost:8000/docs
```

## Option 2: Run with Docker

### Build the Container

```bash
# From repository root
docker build -t learning-ai-agents .
```

### Run the Container

```bash
# With .env file
docker run --rm -p 8000:8000 --env-file .env learning-ai-agents

# Or with explicit env vars
docker run --rm -p 8000:8000 \
  -e GOOGLE_API_KEY=your_api_key \
  -e PDF_PATH=/app/Intro.pdf \
  learning-ai-agents
```

### Using Docker Compose

```bash
# Start services
docker compose up

# Background mode
docker compose up -d

# View logs
docker compose logs -f

# Stop
docker compose down
```

## API Usage

### Start a New Conversation

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What are AI agents?"}'
```

Response:
```json
{
  "session_id": "session-abc12345",
  "message": "AI agents are autonomous systems that...",
  "agent_name": "tutor"
}
```

### Continue a Conversation

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Can you quiz me on that?",
    "session_id": "session-abc12345"
  }'
```

### Start a Quiz

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Give me a quiz about agents",
    "session_id": "session-abc12345"
  }'
```

### Check Server Health

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "uptime_seconds": 120.5,
  "checks": {
    "gemini_api": {"status": "up", "latency_ms": 150},
    "storage": {"status": "up"}
  }
}
```

### List Sessions

```bash
curl "http://localhost:8000/sessions?user_id=local_user&limit=5"
```

### Get Session History

```bash
curl http://localhost:8000/sessions/session-abc12345
```

## Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GOOGLE_API_KEY` | Yes | - | Gemini API key |
| `PDF_PATH` | No | `Intro.pdf` | Educational content PDF |
| `DATA_DIR` | No | `./data/` | Storage directory |
| `PORT` | No | `8000` | Server port |
| `LOG_LEVEL` | No | `INFO` | Logging level |
| `GEMINI_MODEL` | No | `gemini-2.5-flash-lite` | Model name |

## Common Issues

### "GOOGLE_API_KEY not set"

Ensure the environment variable is exported:
```bash
export GOOGLE_API_KEY=your_api_key_here
```

Or create a `.env` file in the repository root.

### "Port already in use"

Change the port:
```bash
PORT=9000 python -m adk.server
```

### Container can't find PDF

Mount the PDF file:
```bash
docker run --rm -p 8000:8000 \
  -e GOOGLE_API_KEY=your_key \
  -v $(pwd)/MyContent.pdf:/app/content.pdf \
  -e PDF_PATH=/app/content.pdf \
  learning-ai-agents
```

## Next Steps

1. Explore the API documentation at http://localhost:8000/docs
2. Build a frontend that connects to the API
3. Test different educational scenarios via curl/Postman
