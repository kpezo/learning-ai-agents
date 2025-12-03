# Implementation Plan: Tests & Evaluation Framework

**Branch**: `003-test-evaluation` | **Date**: 2025-12-03 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-test-evaluation/spec.md`

## Summary

Implement a comprehensive test suite and ADK evaluation framework for the educational agent system. This includes pytest-based unit tests for all modules (tools, quiz_tools, storage, rag_setup), ADK evalset-based agent behavior evaluation, and GitHub Actions CI/CD integration. Tests must mock LLM API calls and use isolated SQLite databases.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: pytest, pytest-cov, pytest-asyncio, google-adk (evalset module), unittest.mock
**Storage**: SQLite (isolated test databases per test run)
**Testing**: pytest with pytest-cov for coverage
**Target Platform**: Linux/macOS development, GitHub Actions CI
**Project Type**: Single project (existing adk/ package)
**Performance Goals**: Full test suite < 30 seconds (excluding evaluations)
**Constraints**: Tests must not require external API calls; LLM responses mocked
**Scale/Scope**: ~4 modules to test, ~5 evaluation scenarios per agent

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The constitution template is not yet customized for this project. Proceeding with standard testing best practices:

| Gate | Status | Notes |
|------|--------|-------|
| Test-First Principle | PASS | This feature IS the test infrastructure |
| Library Self-Contained | PASS | Tests are standalone, independently runnable |
| No External Dependencies in Tests | PASS | All LLM calls will be mocked |
| Isolated Test Data | PASS | Using ephemeral SQLite databases |

## Project Structure

### Documentation (this feature)

```text
specs/003-test-evaluation/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (evaluation scenario schemas)
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)

```text
tests/
├── conftest.py          # Shared fixtures (mock retriever, test storage)
├── unit/
│   ├── test_tools.py        # Tests for adk/tools.py
│   ├── test_quiz_tools.py   # Tests for adk/quiz_tools.py
│   ├── test_storage.py      # Tests for adk/storage.py
│   └── test_rag_setup.py    # Tests for adk/rag_setup.py
├── integration/
│   └── test_agent_flow.py   # Integration tests for agent delegation
└── evaluation/
    ├── evalsets/
    │   ├── tutor_scenarios.json
    │   ├── assessor_scenarios.json
    │   └── curriculum_scenarios.json
    └── run_evaluation.py    # Evaluation runner script

.github/
└── workflows/
    └── test.yml             # CI pipeline configuration

pyproject.toml               # pytest configuration (or pytest.ini)
```

**Structure Decision**: Single project structure with dedicated `tests/` directory at repository root. Evaluation scenarios stored as JSON files following ADK evalset patterns.

## Complexity Tracking

> No constitution violations identified.

| Decision | Rationale |
|----------|-----------|
| Separate unit/integration/evaluation dirs | Clear separation of test types, different execution profiles |
| JSON evalset files | Follows ADK patterns, easily editable, versionable |
| pytest-cov for coverage | Industry standard, integrates with CI |
