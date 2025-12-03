# Implementation Plan: Storage Enhancements

**Branch**: `004-storage-enhancements` | **Date**: 2025-12-03 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-storage-enhancements/spec.md`

## Summary

Enhance the existing SQLite-based storage system (`adk/storage.py`) to support:
1. **Session Persistence**: Replace `InMemorySessionService` with `DatabaseSessionService` for conversation continuity
2. **Semantic Memory**: Integrate ADK's `MemoryService` for cross-session knowledge retention with automatic consolidation
3. **Knowledge Graph**: Extend existing `concept_relationships` table with graph query capabilities (prerequisites, learning paths)
4. **Data Export/Import**: Portable data format for backup and migration

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: google-adk (DatabaseSessionService, MemoryService, preload_memory, load_memory), SQLite3
**Storage**: SQLite (existing via `adk/storage.py`) + ADK SessionService/MemoryService
**Testing**: pytest, pytest-asyncio (existing from 003-test-evaluation)
**Target Platform**: Local development only (SQLite)
**Project Type**: Single project (adk/ package structure)
**Performance Goals**: Session restore < 2s for 100 messages (SC-001), Graph queries < 500ms for 500 concepts (SC-003)
**Constraints**: Zero data loss during migration (SC-004), Local-only (no cloud services)
**Scale/Scope**: Single user, single device, single Gemini API key

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The project constitution uses a template structure. Applying general best practices:
- ✅ Building on existing library (`adk/storage.py`)
- ✅ Enhancing existing functionality rather than creating new projects
- ✅ Using ADK's built-in services rather than custom solutions
- ✅ Minimal new dependencies (ADK already included)

## Project Structure

### Documentation (this feature)

```text
specs/004-storage-enhancements/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output (via /speckit.tasks)
```

### Source Code (repository root)

```text
adk/
├── agent.py             # Update: Add DatabaseSessionService, MemoryService
├── storage.py           # Update: Add graph queries, export format versioning
├── quiz_tools.py        # Existing: Already uses session state
├── run_dev.py           # Update: Configure persistent services
├── memory_tools.py      # New: Memory retrieval tools for agents
└── graph_queries.py     # New: Concept graph traversal functions

tests/
├── test_storage.py      # Update: Add migration, graph query tests
├── test_session_persistence.py  # New: Session restore tests
└── test_memory_integration.py   # New: Cross-session memory tests
```

**Structure Decision**: Extend existing `adk/` structure with minimal new files. Graph queries added as separate module to maintain single responsibility.

## Complexity Tracking

No constitution violations identified. Implementation follows ADK patterns directly.
