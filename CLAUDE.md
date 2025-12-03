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

### RAG System (`rag_setup.py`)

Simple keyword-based retrieval without external vector DB:
- `SimpleRetriever`: Basic TF-like scoring on chunked text (500 char chunks, 50 char overlap)
- `build_retriever()`: Extracts text from PDF using PyMuPDF, creates searchable chunks
- `get_retriever()`: LRU-cached singleton to avoid re-processing PDF

**RAG Tools** (`adk/tools.py`):
- `fetch_info(query)`: Returns relevant documents for a query
- `get_quiz_source(topic, max_chunks)`: Returns labeled snippets for quiz generation

### Quiz State Management (`adk/quiz_tools.py`)

The system includes stateful quiz tools:
- `prepare_quiz(topic)`: Initializes quiz session with retrieved content
- `get_quiz_step()`: Returns current question without advancing
- `advance_quiz(correct: bool)`: Moves to next question if correct=True
- `reveal_context(chunk_index)`: Shows source context after incorrect answers

Quiz state is stored per-session in the session service and enforces sequential answering.

### Question Agent Pipeline (`adk/question_pipeline.py`)

Multi-agent concept extraction system:
1. **Ingestion Agent**: Chunks PDF into passages (top-N retrieval)
2. **Concept Agent**: Extracts concepts with knowledge types (declarative/procedural/conditional)
3. **Relationship Agent**: Maps relationships between concepts
4. **Question Planner**: Generates clarifying questions based on gaps

Agent prompts are loaded from `AgentsExplanations/agents/*.md` files.

### Message Flow and Compaction (`adk/agent.py:98-105`)

- Event-based compaction configured at App level
- Automatically compacts event history at fixed intervals
- Maintains overlap for context continuity

## Key Implementation Details

### Supervisor Routing Logic (`adk/agent.py:72-94`)

- Root agent's instruction guides delegation: "Route tasks to the right specialist"
- ADK framework handles actual routing via `sub_agents` parameter
- No explicit routing logic needed; model decides which sub-agent to invoke

### Session Management

- Uses ADK's built-in `InMemorySessionService`
- Must call `create_session()` before first `runner.run_async()`
- Session includes `app_name`, `user_id`, `session_id`

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

### Modifying Agent Prompts

**Main Agents**: Edit instruction in `_base_instruction()` or specialist creation in `adk/agent.py`

**Question Pipeline**: Edit markdown prompt files in `AgentsExplanations/agents/`

## Common Scenarios

### Changing the LLM Model

Set `GEMINI_MODEL` env var or edit `_gemini_model()` in `adk/agent.py:24-27`

### Adjusting Compaction Thresholds

Adjust `EventsCompactionConfig` parameters in `app` definition at `adk/agent.py:101-104`

### Running with Different PDFs

Set `PDF_PATH` environment variable to point to your educational content PDF. If not set, defaults to `Intro.pdf`.

### Debugging Agent Decisions

Use `LoggingPlugin` in runner (see `adk/run_dev.py:30`) to see streaming events including tool calls and intermediate responses
