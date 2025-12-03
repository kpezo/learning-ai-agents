# Learning AI Agents

A hierarchical multi-agent educational system built with Google ADK (Agent Development Kit) and Gemini LLM. This platform creates adaptive learning experiences through intelligent tutoring, concept extraction from PDFs, and difficulty-adjusted quizzes.

## Features

- **Multi-Agent Orchestration**: Specialized AI agents for tutoring, assessment, curriculum planning, and content extraction
- **Adaptive Difficulty**: 6-level framework that dynamically adjusts based on learner performance
- **PDF-Based Learning**: Extract concepts and relationships from educational documents
- **Scaffolding Support**: Structured hints when learners struggle
- **Learning Analytics**: Track progress, concept mastery, and knowledge gaps
- **RAG Integration**: Keyword-based retrieval without external vector databases

## Quick Start

### Prerequisites

- Python 3.11+
- Google API Key (Gemini)

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/learning-ai-agents.git
cd learning-ai-agents

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r adk/requirements.txt
pip install -r requirements-dev.txt
```

### Configuration

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-2.5-flash-lite  # Optional
PDF_PATH=/path/to/your/pdf.pdf      # Optional, defaults to Intro.pdf
DATA_DIR=/path/to/data              # Optional, defaults to ./data
```

### Usage

```bash
# Interactive PDF Discussion
python -m adk.run_dev

# Adaptive Quiz System
python -m adk.run_quiz
```

## Architecture

### Multi-Agent System

The platform employs specialized agents coordinated by an orchestrator:

| Agent | Role |
|-------|------|
| **Tutor** | Explains concepts, provides examples, grounds responses in PDFs |
| **Assessor** | Prepares quizzes, evaluates answers, provides feedback |
| **Curriculum Planner** | Manages learning paths and difficulty progression |
| **Concept Agent** | Extracts concepts with declarative/procedural/conditional knowledge |
| **Relationship Agent** | Maps relationships between concepts |
| **Orchestrator** | Delegates to specialists and manages overall flow |

### Adaptive Difficulty Framework

```
Level 1: Foundation    - Definition, recognition, true/false (3 hints)
Level 2: Understanding - Explanation, comparison (2 hints)
Level 3: Application   - Scenario-based problems (2 hints)
Level 4: Analysis      - Synthesis, evaluation (1 hint)
Level 5: Synthesis     - Complex scenarios (1 hint)
Level 6: Mastery       - Teaching, edge cases (0 hints)
```

Performance thresholds:
- \>85% correct: Increase difficulty
- <50% correct: Decrease difficulty

### Scaffolding Support

When learners struggle, the system provides targeted support:

- **Definition**: Core meaning, keywords, recognition tasks
- **Process**: Step breakdown, sequencing, sub-goal identification
- **Relationships**: Connection mapping, dependency diagrams
- **Application**: Real-world examples, case studies

## Project Structure

```
learning-ai-agents/
├── adk/                      # Main application code
│   ├── agent.py              # Multi-agent definitions
│   ├── run_dev.py            # PDF discussion system
│   ├── run_quiz.py           # Adaptive quiz runner
│   ├── question_pipeline.py  # Agent pipeline
│   ├── quiz_tools.py         # Quiz state management
│   ├── difficulty.py         # Adaptive difficulty system
│   ├── scaffolding.py        # Hint generation
│   ├── storage.py            # SQLite persistence
│   └── rag_setup.py          # PDF retrieval
├── tests/                    # Test suite
│   ├── unit/                 # Unit tests
│   ├── integration/          # Integration tests
│   ├── evaluation/           # Agent evaluations
│   └── contract/             # Contract tests
├── AgentsExplanations/       # Agent prompts and specs
├── specs/                    # Feature specifications
└── data/                     # Runtime storage
```

## Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=adk --cov-report=html

# Run specific test categories
pytest tests/unit/           # Unit tests only
pytest tests/integration/    # Integration tests only
pytest -m "not slow"         # Skip slow tests
```

Code coverage minimum: 70%

## Development

### Code Quality Tools

```bash
# Format code
black .

# Lint
ruff check .

# Type checking
mypy adk/
```

### CI/CD

GitHub Actions workflow runs:
- Unit tests with coverage
- Integration tests
- Agent evaluations (main branch)
- Linting and formatting checks

## Technology Stack

- **AI/LLM**: Google ADK, Gemini 2.5 Flash Lite
- **Storage**: SQLite
- **PDF Processing**: PyMuPDF
- **Observability**: OpenTelemetry
- **Testing**: pytest, pytest-asyncio, pytest-cov