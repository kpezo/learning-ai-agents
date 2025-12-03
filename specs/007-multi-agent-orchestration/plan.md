# Implementation Plan: Multi-Agent Orchestration Expansion

**Branch**: `007-multi-agent-orchestration` | **Date**: 2025-12-03 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/007-multi-agent-orchestration/spec.md`

## Summary

Expand the current 3-agent hierarchical system (Tutor, Curriculum Planner, Assessor) to a 5-specialist architecture (Diagnostic, Tutor, Quiz, Feedback, PathPlanner) with LLM-driven routing via a Coordinator agent. Implement ADK's `SequentialAgent` and `LoopAgent` orchestration patterns for learning cycles that repeat until mastery.

## Technical Context

**Language/Version**: Python 3.11+ (existing project uses `google-adk`, `google-genai`, `pymupdf`, `python-dotenv`)
**Primary Dependencies**: `google-adk` (SequentialAgent, LoopAgent, ParallelAgent, LlmAgent), Gemini model
**Storage**: SQLite via `adk/storage.py` for persistent user progress; ADK `InMemorySessionService` for session state
**Testing**: pytest, pytest-cov, pytest-asyncio (from spec 003-test-evaluation)
**Target Platform**: Local development / Python CLI (interactive mode via `python -m adk.run_dev`)
**Project Type**: Single project (existing `adk/` package)
**Performance Goals**: Agent transitions within 2 seconds (SC-006)
**Constraints**: Must maintain conversation continuity; mastery threshold configurable (default 85%)
**Scale/Scope**: Single user sessions; 5 specialist agents + 1 coordinator

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The constitution template is not yet populated with project-specific principles. The following checks are based on common development principles:

| Gate | Status | Notes |
|------|--------|-------|
| Library-First | PASS | Extends existing `adk/` package structure |
| CLI Interface | PASS | Uses existing `python -m adk.run_dev` interface |
| Test-First | NEEDS ATTENTION | Tests should be written before implementation per TDD |
| Integration Testing | PASS | ADK agent interactions testable via evalset |
| Simplicity | PASS | Uses ADK native patterns, no custom orchestration |

## Project Structure

### Documentation (this feature)

```text
specs/007-multi-agent-orchestration/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
adk/
├── __init__.py
├── agent.py             # MODIFY: Add 5 specialists + coordinator
├── orchestration.py     # NEW: SequentialAgent/LoopAgent patterns
├── quiz_tools.py        # MODIFY: Add feedback integration
├── diagnostic_tools.py  # NEW: Prerequisite checking tools
├── path_tools.py        # NEW: Learning path recommendation tools
├── storage.py           # MODIFY: Add agent transition tracking
├── rag_setup.py
├── tools.py
└── run_dev.py          # MODIFY: Update runner for new agents

tests/
├── unit/
│   ├── test_agents.py           # NEW: Agent unit tests
│   ├── test_orchestration.py    # NEW: Orchestration pattern tests
│   └── test_diagnostic_tools.py # NEW: Diagnostic tool tests
├── integration/
│   ├── test_routing.py          # NEW: Coordinator routing tests
│   └── test_learning_cycle.py   # NEW: Full cycle integration tests
└── contract/
    └── test_agent_contracts.py  # NEW: Agent input/output contracts
```

**Structure Decision**: Extend existing `adk/` single-project structure. Add `orchestration.py` module for ADK workflow agents (SequentialAgent, LoopAgent). Add new tool modules for specialist capabilities.

## Complexity Tracking

No constitution violations requiring justification - design uses native ADK patterns.
