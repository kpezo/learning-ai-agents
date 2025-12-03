# Learning AI Agents - Project Specification

## Executive Summary

This project implements a **Hierarchical Multi-Agent Educational System** using Google's Agent Development Kit (ADK) and Gemini models. The system provides adaptive, personalized learning experiences through:

- **Concept extraction** from educational PDFs
- **Knowledge relationship mapping** between concepts
- **Adaptive quiz generation** based on learner performance
- **Multi-turn tutoring conversations** with context retention

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Architecture](#2-architecture)
3. [Current Implementation](#3-current-implementation)
4. [Agent Specifications](#4-agent-specifications)
5. [Tool Specifications](#5-tool-specifications)
6. [Data Models](#6-data-models)
7. [Workflow Patterns](#7-workflow-patterns)
8. [Configuration](#8-configuration)
9. [Dependencies](#9-dependencies)
10. [Known Gaps & Future Work](#10-known-gaps--future-work)

---

## 1. Project Overview

### 1.1 Purpose

Build an intelligent tutoring system that:
- Ingests educational content from PDFs
- Extracts and structures concepts with declarative/procedural/conditional knowledge
- Maps relationships between concepts (prerequisite, enables, part-of, etc.)
- Generates adaptive quiz questions based on knowledge gaps
- Tracks learner progress and adjusts difficulty dynamically
- Provides personalized tutoring with grounded responses

### 1.2 Target Users

- **Learners**: Students seeking personalized education
- **Educators**: Teachers wanting AI-assisted curriculum delivery
- **Developers**: Those building educational AI systems

### 1.3 Key Features

| Feature | Status | Description |
|---------|--------|-------------|
| PDF Ingestion | ✅ Implemented | Extract and chunk text from PDFs |
| Concept Extraction | ✅ Implemented | Identify concepts with knowledge types |
| Relationship Mapping | ✅ Implemented | Map concept relationships |
| Question Generation | ✅ Implemented | Generate clarifying questions |
| Stateful Quizzes | ✅ Implemented | Sequential quiz flow with hints |
| RAG Retrieval | ❌ Missing | `rag_setup.py` not implemented |
| Adaptive Difficulty | 📋 Designed | 6-level framework proposed |
| PDF Reports | 📋 Designed | Export progress reports |
| Persistent Storage | ❌ Missing | In-memory only |

---

## 2. Architecture

### 2.1 System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                               │
│                    (Interactive CLI / ADK Web)                       │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      ROOT COORDINATOR AGENT                          │
│          (Routes tasks to appropriate specialist agents)             │
└─────────────────────────────────────────────────────────────────────┘
        │               │               │               │
        ▼               ▼               ▼               ▼
┌───────────┐   ┌───────────┐   ┌───────────┐   ┌───────────┐
│  Tutor    │   │Curriculum │   │ Assessor  │   │ Question  │
│  Agent    │   │ Planner   │   │  Agent    │   │ Pipeline  │
└───────────┘   └───────────┘   └───────────┘   └───────────┘
        │               │               │               │
        ▼               ▼               ▼               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         TOOL LAYER                                   │
│  [fetch_info] [get_quiz_source] [prepare_quiz] [advance_quiz] ...   │
└─────────────────────────────────────────────────────────────────────┘
        │               │
        ▼               ▼
┌───────────────┐   ┌───────────────┐
│  RAG System   │   │Session/Memory │
│ (rag_setup)   │   │   Services    │
└───────────────┘   └───────────────┘
```

### 2.2 Directory Structure

```
learning-ai-agents/
├── adk/                              # ADK agent implementations
│   ├── agent.py                      # Root supervisor + specialists
│   ├── question_pipeline.py          # Sequential concept extraction
│   ├── tools.py                      # RAG-backed tools
│   ├── quiz_tools.py                 # Stateful quiz management
│   ├── run_dev.py                    # Interactive development runner
│   ├── requirements.txt              # ADK dependencies
│   └── Intro.pdf                     # Sample educational content
│
├── AgentsExplanations/               # Agent specifications
│   ├── agents/                       # Prompt templates
│   │   ├── ingestion-agent.md
│   │   ├── concept-agent.md
│   │   ├── relationship-agent.md
│   │   ├── question-planner.md
│   │   ├── followup-judge.md
│   │   └── orchestrator.md
│   └── question-agent-spec.md        # Full system specification
│
├── planning/                         # Design documents
│   ├── building-adaptive-quiz-agent-google-adk.md
│   ├── enhancements.md               # Proposed enhancements
│   └── kaggle-days/                  # Day-by-day learning guides
│
├── CLAUDE.md                         # Development instructions
├── SPECIFICATION.md                  # This document
├── .env                              # Configuration
└── .env.example                      # Environment template
```

### 2.3 Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| Framework | Google ADK | Agent orchestration, tools, sessions |
| LLM | Google Gemini | Language understanding and generation |
| PDF Processing | PyMuPDF | Extract text from educational PDFs |
| Session Management | ADK InMemorySessionService | Conversation state |
| Memory | ADK InMemoryMemoryService | Cross-session knowledge |
| Observability | ADK LoggingPlugin | Debug and trace agent execution |

---

## 3. Current Implementation

### 3.1 Two Agent Systems

The codebase provides **two distinct agent systems**:

#### System A: Hierarchical Delegation (`adk/agent.py`)

```python
root_agent = Agent(
    name="education_supervisor",
    sub_agents=[tutor_agent, curriculum_planner_agent, assessor_agent]
)
```

- **Purpose**: LLM-driven routing to specialist agents
- **Pattern**: Hierarchical delegation with shared tools
- **Entry Point**: Import `root_agent` from `adk.agent`

#### System B: Question Pipeline (`adk/question_pipeline.py`)

```python
question_pipeline = SequentialAgent(
    sub_agents=[ingestion_agent, concept_agent, relationship_agent, question_planner_agent]
)
```

- **Purpose**: Fixed sequential concept extraction from PDFs
- **Pattern**: Sequential agent with context passing via `output_key`
- **Entry Point**: `python -m adk.run_dev`

### 3.2 Entry Points

| Command | Description |
|---------|-------------|
| `python -m adk.run_dev` | Interactive runner with question pipeline |
| Import `adk.agent.root_agent` | Use hierarchical supervisor system |
| Import `adk.agent.app` | Use App wrapper with event compaction |

### 3.3 Event Compaction

Configured in `adk/agent.py`:

```python
app = App(
    name="education_app",
    root_agent=root_agent,
    events_compaction_config=EventsCompactionConfig(
        compaction_interval=6,  # Compact every 6 turns
        overlap_size=2          # Keep 2 turns for context
    )
)
```

---

## 4. Agent Specifications

### 4.1 Tutor Agent

**Purpose**: Direct student interactions, explanations, and guidance.

**Instruction**:
```
You are a Tutor working with students.
Ground every response in the provided snippets or retrieved context.
Be concise and actionable.
For quizzes: call prepare_quiz(topic) once, then get_quiz_step to pull the
current item, ask one question at a time, and only move on after
advance_quiz(correct=True). If the learner is wrong, call
advance_quiz(correct=False) and reveal_context to give more detail.
```

**Tools**: `fetch_info`, `get_quiz_source`, `prepare_quiz`, `get_quiz_step`, `advance_quiz`, `reveal_context`, `preload_memory`

### 4.2 Curriculum Planner Agent

**Purpose**: Design lesson plans, module structures, and learning sequences.

**Instruction**: Same base instruction as Tutor.

**Tools**: Same tool set as Tutor.

### 4.3 Assessor Agent

**Purpose**: Create quizzes, evaluate understanding, manage assessment flow.

**Instruction**: Same base instruction as Tutor.

**Tools**: Same tool set as Tutor.

### 4.4 Question Pipeline Agents

#### 4.4.1 Ingestion Agent

**Purpose**: Chunk PDFs, embed, and return top passages for retrieval.

**Output Schema**:
```json
[{"id": "...", "text": "...", "score": 0.0}]
```

**Tool**: `ingest_pdf(pdf_path, top_n=20)`

**Output Key**: `passages`

#### 4.4.2 Concept Agent

**Purpose**: Extract key concepts with declarative/procedural/conditional fields.

**Input**: `{passages}` from ingestion agent

**Output Schema**:
```json
{
  "concepts": [
    {
      "name": "...",
      "declarative": "...",
      "procedural": "...",
      "conditional_use": "...",
      "conditional_avoid": "...",
      "confidence": 0.0-1.0
    }
  ],
  "gaps": ["..."]
}
```

**Output Key**: `concepts`

#### 4.4.3 Relationship Agent

**Purpose**: Map relationships between concepts with rationale.

**Input**: `{concepts}` and `{passages}`

**Output Schema**:
```json
{
  "relationships": [
    {
      "between": ["ConceptA", "ConceptB"],
      "type": "depends-on|enables|alternative-to|part-of|...",
      "direction": "A->B or bidirectional",
      "rationale": "...",
      "usage_impact": "...",
      "confidence": 0.0-1.0
    }
  ],
  "gaps": ["..."]
}
```

**Relationship Types**:
- `depends-on`: Prerequisite relationship
- `enables`: Conceptual unlocking
- `alternative-to`: Different approaches
- `part-of`: Hierarchical containment
- `sequence-before`: Ordering dependency
- `sequence-after`: Ordering dependency
- `conflicts-with`: Contradictory concepts

**Output Key**: `relationships`

#### 4.4.4 Question Planner Agent

**Purpose**: Generate clarifying questions from gaps.

**Input**: `{concepts}` and `{relationships}`

**Output Schema**:
```json
{
  "questions": [
    {"stage": "big-picture|detail", "text": "..."}
  ]
}
```

**Rules**:
- Ask 3-6 questions
- Big-picture questions first, then detail
- Atomic questions (≤3 concepts per question)
- Cover declarative, procedural, and conditional gaps

**Output Key**: `questions`

---

## 5. Tool Specifications

### 5.1 RAG Tools (`adk/tools.py`)

#### `fetch_info(query: str) -> dict`

Retrieve relevant chunks from the domain PDF.

**Returns**:
```python
# Success
{"status": "success", "snippets": ["...", "..."]}

# Error (if RAG not initialized)
{"status": "error", "error_message": "Retriever not initialized..."}
```

#### `get_quiz_source(topic: str, max_chunks: int = 3) -> dict`

Return concise snippets for quiz generation.

**Returns**:
```python
{"status": "success", "snippets": ["Snippet 1: ...", "Snippet 2: ..."]}
```

### 5.2 Quiz Tools (`adk/quiz_tools.py`)

All quiz tools use `ToolContext` for stateful session management.

**Session State Keys**:
- `quiz:snippets` - Retrieved documents for current quiz
- `quiz:topic` - Current quiz topic
- `quiz:index` - Current question index (0-based)
- `quiz:mistakes` - Mistake count on current question

#### `prepare_quiz(topic: str, max_chunks: int = 3) -> dict`

Initialize quiz state from RAG snippets.

**Returns**:
```python
{
    "status": "success",
    "topic": "algebra",
    "total_questions": 3,
    "current_index": 0
}
```

#### `get_quiz_step() -> dict`

Return current quiz step with hint snippet.

**Returns**:
```python
{
    "status": "success",
    "topic": "algebra",
    "question_number": 1,
    "total_questions": 3,
    "hint_snippet": "First 400 chars of snippet...",
    "mistakes_on_question": 0
}
```

#### `advance_quiz(correct: bool) -> dict`

Update quiz progress. Move forward if correct, stay if incorrect.

**Returns**:
```python
{
    "status": "success",
    "done": False,
    "next_question_number": 2,
    "total_questions": 3,
    "mistakes_on_current": 0
}
```

#### `reveal_context() -> dict`

Return full context for current quiz item (for struggling learners).

**Returns**:
```python
{
    "status": "success",
    "context": "Full snippet text...",
    "question_number": 1,
    "total_questions": 3
}
```

### 5.3 Pipeline Tools

#### `ingest_pdf(pdf_path: str | None = None, top_n: int = 20) -> dict`

Return top passages from PDF using `build_retriever()`.

**Returns**:
```python
{"passages": [{"id": "0", "text": "...", "score": 1.0}, ...]}
```

---

## 6. Data Models

### 6.1 Concept Model

```python
@dataclass
class Concept:
    name: str                      # Unique concept identifier
    declarative: str               # What is it?
    procedural: str                # How does it work?
    conditional_use: str           # When to use it?
    conditional_avoid: str         # When NOT to use it?
    confidence: float              # 0.0 - 1.0
```

### 6.2 Relationship Model

```python
@dataclass
class Relationship:
    between: List[str]             # 2-3 concept names
    type: str                      # Relationship type enum
    direction: str                 # "A->B" or "bidirectional"
    rationale: str                 # Why this relationship exists
    usage_impact: str              # How it affects learning
    confidence: float              # 0.0 - 1.0
```

### 6.3 Question Model

```python
@dataclass
class Question:
    stage: str                     # "big-picture" or "detail"
    text: str                      # The question text
```

### 6.4 Quiz State Model

```python
@dataclass
class QuizState:
    snippets: List[str]            # Retrieved content chunks
    topic: str                     # Current topic
    index: int                     # Current question index
    mistakes: int                  # Mistakes on current question
```

### 6.5 Knowledge Graph Schema (Proposed)

From `planning/building-adaptive-quiz-agent-google-adk.md`:

```json
{
  "ConceptNode": {
    "id": "uuid",
    "name": "string",
    "node_type": "domain|course|module|topic|concept|skill",
    "hierarchy_level": 1-5,
    "properties": {
      "difficulty": "novice|beginner|intermediate|advanced|expert",
      "bloom_taxonomy_level": "remember|understand|apply|analyze|evaluate|create",
      "estimated_learning_time_minutes": "integer"
    }
  },
  "RelationshipEdge": {
    "id": "string",
    "source_id": "string",
    "target_id": "string",
    "relationship_type": "prerequisite|enables|part_of|similar_to|...",
    "is_directed": true,
    "properties": {
      "strength": 0.0-1.0,
      "prerequisite_type": "hard|soft|recommended"
    }
  }
}
```

---

## 7. Workflow Patterns

### 7.1 Question Pipeline Workflow

```
User Input (PDF Path)
        ↓
┌───────────────────────┐
│   Ingestion Agent     │ → ingest_pdf() → {passages}
└───────────────────────┘
        ↓
┌───────────────────────┐
│    Concept Agent      │ → LLM extraction → {concepts}
└───────────────────────┘
        ↓
┌───────────────────────┐
│  Relationship Agent   │ → LLM mapping → {relationships}
└───────────────────────┘
        ↓
┌───────────────────────┐
│ Question Planner      │ → LLM generation → {questions}
└───────────────────────┘
        ↓
Final JSON Output
```

### 7.2 Quiz Flow Workflow

```
User: "Take a quiz on [topic]"
        ↓
prepare_quiz(topic) → Store snippets in session
        ↓
get_quiz_step() → Return hint for question 1
        ↓
User answers
        ↓
┌─────────────────────────────────────┐
│ Agent evaluates answer (via LLM)    │
├─────────────────────────────────────┤
│ If correct:                         │
│   advance_quiz(correct=True)        │
│   → index += 1, mistakes = 0        │
│   → Get next question               │
├─────────────────────────────────────┤
│ If incorrect:                       │
│   advance_quiz(correct=False)       │
│   → mistakes += 1                   │
│   reveal_context()                  │
│   → Show full snippet               │
│   → Ask to retry                    │
└─────────────────────────────────────┘
        ↓
Repeat until done (index >= len(snippets))
```

### 7.3 Hierarchical Routing Workflow

```
User Request
        ↓
┌───────────────────────────────┐
│    Education Supervisor       │
│  (LLM-driven routing)         │
└───────────────────────────────┘
        │
        ├─→ "Explain X" → Tutor Agent
        ├─→ "Plan lesson on Y" → Curriculum Planner
        ├─→ "Quiz me on Z" → Assessor Agent
        └─→ Complex/unclear → Supervisor handles directly
```

---

## 8. Configuration

### 8.1 Environment Variables

```bash
# Required
GOOGLE_API_KEY=<your-gemini-api-key>

# Optional
PDF_PATH=/path/to/educational.pdf    # Defaults to Intro.pdf
GEMINI_MODEL=gemini-2.5-flash-lite   # Model selection
```

### 8.2 Model Configuration

Default model selection in `adk/agent.py`:

```python
def _gemini_model() -> Gemini:
    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
    return Gemini(model=model_name)
```

**Available Models**:
- `gemini-2.5-flash-lite` (default, fast, cost-effective)
- `gemini-2.0-flash`
- `gemini-2.0-pro`

### 8.3 Compaction Configuration

```python
EventsCompactionConfig(
    compaction_interval=6,  # Compact every 6 conversation turns
    overlap_size=2          # Keep 2 turns for context continuity
)
```

---

## 9. Dependencies

### 9.1 Python Packages (`adk/requirements.txt`)

```
google-adk                                    # Agent Development Kit
opentelemetry-instrumentation-google-genai    # Observability
pymupdf                                       # PDF text extraction
python-dotenv                                 # Environment management
```

### 9.2 ADK Imports

```python
# Core agents
from google.adk.agents import Agent, LlmAgent, SequentialAgent

# Models
from google.adk.models.google_llm import Gemini

# Tools
from google.adk.tools import FunctionTool, AgentTool, preload_memory
from google.adk.tools.tool_context import ToolContext

# Session/Memory
from google.adk.sessions import InMemorySessionService
from google.adk.memory import InMemoryMemoryService

# App wrapper
from google.adk.apps.app import App, EventsCompactionConfig

# Runner
from google.adk.runners import Runner

# Observability
from google.adk.plugins.logging_plugin import LoggingPlugin

# Types
from google.genai import types
```

---

## 10. Known Gaps & Future Work

### 10.1 Critical Missing Component

#### RAG System (`rag_setup.py`)

**Status**: NOT IMPLEMENTED

**Impact**: All RAG tools return error responses. Tutor and Assessor workflows are broken.

**Required Implementation**:

```python
# Expected API in rag_setup.py

class SimpleRetriever:
    """Keyword-based retriever without external vector DB."""

    def __init__(self, chunks: List[str]):
        self.chunks = chunks

    def get_relevant_documents(self, query: str) -> List[Document]:
        """Return relevant chunks based on TF-like scoring."""
        pass

def build_retriever(pdf_path: str) -> SimpleRetriever:
    """Extract text from PDF, chunk (500 chars, 50 overlap), return retriever."""
    pass

@lru_cache(maxsize=1)
def get_retriever() -> SimpleRetriever:
    """Cached singleton retriever."""
    pdf_path = os.getenv("PDF_PATH", "Intro.pdf")
    return build_retriever(pdf_path)
```

### 10.2 Proposed Enhancements (from `planning/enhancements.md`)

#### Enhancement 1: Adaptive Difficulty System

**6-Level Framework**:
| Level | Name | Question Types | Hints |
|-------|------|----------------|-------|
| 1 | Foundation | definition, recognition | 3 |
| 2 | Understanding | explanation, comparison | 2 |
| 3 | Application | scenario, problem_solving | 1 |
| 4 | Analysis | relationship, cause_effect | 0 |
| 5 | Synthesis | design, integration | 0 |
| 6 | Mastery | teach_back, edge_cases | 0 |

**Required Tools**:
- `analyze_performance_trend(window_size=5)`
- `calculate_optimal_difficulty(current_level, trend, complexity)`
- `get_scaffolding_hints(concept_id, difficulty, struggle_area)`
- `record_answer_performance(score, time, hints, difficulty, concept)`

#### Enhancement 2: PDF Report Generator

**Report Sections**:
1. Executive Summary (mastery %, time, achievements)
2. Concept Mastery Breakdown
3. Learning Analytics (score progression, difficulty trends)
4. Strengths & Improvements
5. Personalized Recommendations

**Required Tools**:
- `compile_mastery_summary()`
- `generate_analytics_charts()`
- `create_recommendations(mastery_summary)`
- `generate_pdf_report(summary, analytics, recommendations)`

### 10.3 Tests & Evaluation

**Missing**:
- `.evalset.json` files for ADK evaluation
- `test_config.json` with evaluation thresholds
- Pytest test suite
- CI/CD integration

**Recommended Structure**:
```
eval/
├── test_config.json
├── basic_tutoring.evalset.json
├── quiz_flows.evalset.json
├── adaptive_difficulty.evalset.json
└── test_eval.py
```

### 10.4 Persistent Storage

**Current State**: All data in-memory, lost on restart.

**Needed**:
- `DatabaseSessionService` for session persistence
- `VertexAiMemoryBankService` for long-term memory
- Knowledge graph database for concept relationships

### 10.5 Production Deployment

**Not Implemented**:
- Vertex AI Agent Engine deployment scripts
- Cloud Run containerization
- A2A protocol exposure for remote access

---

## Appendix A: Running the System

### A.1 Setup

```bash
# Clone and navigate
cd learning-ai-agents

# Install dependencies
pip install -r adk/requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your GOOGLE_API_KEY
```

### A.2 Run Interactive Mode

```bash
python -m adk.run_dev
```

**Default Scenario**:
```
Ingest the PDF (PDF_PATH env or Intro.pdf), extract main concepts and their
relationships, classify declarative/procedural/conditional knowledge, and
propose clarifying questions. Return the concepts, relationships, and 3-6
atomic questions to ask me next.
```

### A.3 Commands in Interactive Mode

- Type your message and press Enter
- `/exit` to quit the session

---

## Appendix B: ADK Patterns Reference

### B.1 Agent Creation Pattern

```python
specialist = LlmAgent(
    name="role_name",
    description="What this agent does",
    model=Gemini(model="gemini-2.5-flash-lite"),
    instruction="Your detailed prompt here",
    tools=[tool1, tool2],
    output_key="result_key"  # For sequential pipelines
)
```

### B.2 Sequential Pipeline Pattern

```python
pipeline = SequentialAgent(
    name="my_pipeline",
    sub_agents=[agent1, agent2, agent3]  # Runs in order
)
```

### B.3 Tool with Session State Pattern

```python
def my_tool(param: str, tool_context: ToolContext = None) -> dict:
    if tool_context:
        tool_context.state["my:key"] = value  # Write
        data = tool_context.state.get("my:key")  # Read
    return {"status": "success", "data": data}
```

### B.4 Runner with Streaming Pattern

```python
runner = Runner(
    agent=root_agent,
    app_name="my_app",
    session_service=InMemorySessionService(),
    memory_service=InMemoryMemoryService(),
    plugins=[LoggingPlugin()]
)

async for event in runner.run_async(
    user_id="user_id",
    session_id="session_id",
    new_message=types.Content(role="user", parts=[types.Part(text="...")])
):
    if event.is_final_response():
        print(event.content.parts[0].text)
```

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-03 | Claude | Initial specification |
