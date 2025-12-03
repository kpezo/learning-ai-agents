# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a hierarchical multi-agent educational system built with **Google ADK (Agent Development Kit)** and **Google Gemini models**.

The system creates an educational agent with three specialist agents (Tutor, Curriculum Planner, Assessor) coordinated by a root agent that handles routing and delegation.

## Environment Setup

```bash
# Install ADK dependencies
pip install -r adk/requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env and add:
# - GOOGLE_API_KEY (required for Gemini)
# - PDF_PATH (path to educational content PDF, defaults to Intro.pdf)
# - GEMINI_MODEL (optional, defaults to gemini-2.5-flash-lite)
# - DATA_DIR (optional, defaults to ./data/ for persistent storage)
```

## Running the System

```bash
# Run the ADK agent system (interactive mode with streaming)
python -m adk.run_dev

# The system will ingest PDF, extract concepts/relationships, and propose questions
# Interactive loop allows follow-up questions during the session
```

## Architecture

### Core Agent Pattern

The system uses a **hierarchical delegation pattern**:
- **Root Agent**: Routes tasks to appropriate specialists based on request type
- **Tutor Agent**: Handles direct student interactions, explanations, and guidance
- **Curriculum Planner Agent**: Designs lesson plans, module structures, and learning sequences
- **Assessor Agent**: Creates quizzes, evaluates understanding, manages assessment flow

### Agent System (`adk/agent.py`)

- Uses ADK's native `Agent` with `sub_agents` for delegation
- Root agent automatically manages delegation to specialists
- **Event compaction**: Configured via `EventsCompactionConfig` (compaction_interval=6, overlap_size=2)
- Session/memory services: `InMemorySessionService` and `InMemoryMemoryService` from ADK
- Streaming events expose intermediate tool calls and agent steps

### RAG System (`adk/rag_setup.py`)

Simple keyword-based retrieval without external vector DB:
- `SimpleRetriever`: Basic TF-like scoring on chunked text (500 char chunks, 50 char overlap)
- `build_retriever()`: Extracts text from PDF using PyMuPDF, creates searchable chunks
- `get_retriever()`: LRU-cached singleton to avoid re-processing PDF

**RAG Tools** (`adk/tools.py`):
- `fetch_info(query)`: Returns relevant documents for a query
- `get_quiz_source(topic, max_chunks)`: Returns labeled snippets for quiz generation

### Persistent Storage (`adk/storage.py`)

SQLite-based persistent storage for user learning progress:
- **Location**: `./data/{user_id}.db` (configurable via `DATA_DIR` env var)
- **Quiz Results**: Topic, scores, timestamps, per-question details
- **Concept Mastery**: Tracks mastery level (0.0-1.0) per concept with times seen/correct
- **Knowledge Gaps**: Identified weak areas with resolution tracking
- **Session Logs**: Full conversation history per session
- **Extracted Concepts**: Cached PDF concept extraction results
- **Concept Relationships**: Cached relationship mappings between concepts

Key classes:
- `StorageService`: Main class with methods for all data operations
- `get_storage(user_id)`: Factory function returning cached storage instance

### Quiz State Management (`adk/quiz_tools.py`)

The system includes stateful quiz tools with persistent storage:
- `prepare_quiz(topic)`: Initializes quiz session with retrieved content, records to DB
- `get_quiz_step()`: Returns current question without advancing
- `advance_quiz(correct, concept_name)`: Moves to next question, updates mastery tracking
- `reveal_context()`: Shows source context after incorrect answers
- `get_learning_stats()`: Returns overall user learning statistics
- `get_weak_concepts(threshold)`: Returns concepts below mastery threshold
- `get_quiz_history(topic, limit)`: Returns quiz history for user

Quiz state is stored per-session in ADK session service AND persisted to SQLite for cross-session analytics.

### Question Agent Pipeline (`adk/question_pipeline.py`)

Multi-agent concept extraction system:
1. **Ingestion Agent**: Chunks PDF into passages (top-N retrieval)
2. **Concept Agent**: Extracts concepts with knowledge types (declarative/procedural/conditional)
3. **Relationship Agent**: Maps relationships between concepts
4. **Question Planner**: Generates clarifying questions based on gaps

Agent prompts are loaded from `AgentsExplanations/agents/*.md` files.

### Message Flow and Compaction (`adk/agent.py:106-113`)

- Event-based compaction configured at App level
- Automatically compacts event history at fixed intervals
- Maintains overlap for context continuity

## Key Implementation Details

### Supervisor Routing Logic (`adk/agent.py:78-103`)

- Root agent's instruction guides delegation: "Route tasks to the right specialist"
- ADK framework handles actual routing via `sub_agents` parameter
- No explicit routing logic needed; model decides which sub-agent to invoke

### Session Management

- Uses ADK's built-in `InMemorySessionService`
- Must call `create_session()` before first `runner.run_async()`
- Session includes `app_name`, `user_id`, `session_id`

### Persistent Storage Integration

- Storage is automatically initialized per user_id
- Quiz tools persist progress without explicit calls
- Use `StorageService.export_progress()` to get JSON export of all user data

## Development Patterns

### Adding New Specialist Agents

1. Create specialist using `_make_specialist(role, extra_tools)` in `adk/agent.py`
2. Add to `root_agent.sub_agents` list
3. Update root agent description to mention new specialist
4. No routing logic changes needed

### Adding New Tools

1. Define tool function in `adk/tools.py` or `adk/quiz_tools.py`
2. Add to tools list in `_make_specialist()` and/or `root_agent`
3. For stateful tools, access session via `ToolContext.session_id`
4. For persistent data, use `get_storage(user_id)` from `adk/storage.py`

### Modifying Agent Prompts

**Main Agents**: Edit instruction in `_base_instruction()` or specialist creation in `adk/agent.py`

**Question Pipeline**: Edit markdown prompt files in `AgentsExplanations/agents/`

### Working with Storage

```python
from adk.storage import get_storage

# Get storage for a user
storage = get_storage("user123")

# Record quiz progress
quiz_id = storage.start_quiz("session_abc", "algebra", 5)
storage.update_quiz_progress(quiz_id, correct=3, mistakes=2, details=[...])
storage.complete_quiz(quiz_id)

# Track concept mastery
storage.update_mastery("quadratic_equations", correct=True)
weak = storage.get_weak_concepts(threshold=0.5)

# Get user stats
stats = storage.get_user_stats()
export = storage.export_progress()  # Full JSON export
```

## Common Scenarios

### Changing the LLM Model

Set `GEMINI_MODEL` env var or edit `_gemini_model()` in `adk/agent.py:27-30`

### Adjusting Compaction Thresholds

Adjust `EventsCompactionConfig` parameters in `app` definition at `adk/agent.py:109-112`

### Running with Different PDFs

Set `PDF_PATH` environment variable to point to your educational content PDF. If not set, defaults to `Intro.pdf`.

### Changing Storage Location

Set `DATA_DIR` environment variable to change where user databases are stored. Defaults to `./data/`.

### Debugging Agent Decisions

Use `LoggingPlugin` in runner (see `adk/run_dev.py:30`) to see streaming events including tool calls and intermediate responses

### Exporting User Progress

```python
from adk.storage import get_storage
import json

storage = get_storage("user123")
progress = storage.export_progress()
with open("user123_progress.json", "w") as f:
    json.dump(progress, f, indent=2)
```
