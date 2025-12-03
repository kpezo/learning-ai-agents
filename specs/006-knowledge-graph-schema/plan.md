# Implementation Plan: Knowledge Graph Schema Enhancement

**Branch**: `006-knowledge-graph-schema` | **Date**: 2025-12-03 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/006-knowledge-graph-schema/spec.md`

## Summary

Enhance the knowledge graph with hierarchical concept nodes (8 types across 5 levels), 12 relationship types, Bloom's taxonomy classification, provenance tracking, and LLM-based graph construction from educational PDFs. The system extends existing SQLite storage with graph-optimized tables.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: google-adk, google-genai, pymupdf, python-dotenv
**Storage**: SQLite via `adk/storage.py` (extending existing schema with graph tables)
**Testing**: pytest, pytest-cov, pytest-asyncio
**Target Platform**: Local development / CLI (macOS/Linux)
**Project Type**: Single project
**Performance Goals**: <200ms for hierarchy queries (SC-001), support 10,000 concepts (SC-006)
**Constraints**: Sub-second query performance, prevent circular hard prerequisites
**Scale/Scope**: 1000-10000 concepts, 12 relationship types, 5 hierarchy levels

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Pre-Design Check**: The constitution file (`.specify/memory/constitution.md`) is a template without specific project principles defined. No specific gates to enforce.

**Post-Design Check (Phase 1 Complete)**: Design follows existing project patterns:
- ✅ Extends existing SQLite storage (`adk/storage.py`) - no new database technologies
- ✅ Follows ADK FunctionTool patterns from existing codebase
- ✅ Reuses LLM extraction patterns from `question_pipeline.py`
- ✅ No external dependencies added beyond existing stack
- ✅ Test structure follows existing `tests/` organization

## Project Structure

### Documentation (this feature)

```text
specs/006-knowledge-graph-schema/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
adk/
├── __init__.py          # Package init
├── agent.py             # Root agent + specialists (existing)
├── tools.py             # RAG tools (existing)
├── quiz_tools.py        # Quiz state management tools (existing)
├── storage.py           # SQLite persistence (EXTEND with graph tables)
├── graph.py             # NEW: Knowledge graph service layer
├── graph_tools.py       # NEW: ADK tools for graph queries
├── extraction/          # NEW: LLM extraction module
│   ├── __init__.py
│   ├── concept_extractor.py   # Concept extraction from PDF
│   └── relationship_extractor.py  # Relationship inference
├── rag_setup.py         # PDF retrieval setup (existing)
├── question_pipeline.py # Concept extraction pipeline (existing, reference patterns)
└── run_dev.py           # Development runner (existing)

tests/
├── unit/
│   ├── test_graph.py           # Graph service unit tests
│   └── test_extraction.py      # Extraction logic tests
├── integration/
│   └── test_graph_storage.py   # Storage integration tests
└── contract/
    └── test_graph_api.py       # API contract tests
```

**Structure Decision**: Single project extending existing `adk/` structure. New modules follow established patterns from `storage.py` and `question_pipeline.py`. Graph functionality added as new files rather than modifying existing heavily.

## Complexity Tracking

No constitution violations to track (constitution is unconfigured template).
