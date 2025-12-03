# Tasks: Storage Enhancements

**Input**: Design documents from `/specs/004-storage-enhancements/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: Tests NOT explicitly requested in spec. Test tasks included for critical functionality only.

**Organization**: Tasks grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4, US5)
- Include exact file paths in descriptions

## Path Conventions

- **Project structure**: `adk/` package at repository root
- **Tests**: `tests/` at repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Schema migration framework and base configuration

- [ ] T001 Create schema_version table and migration framework in adk/storage.py
- [ ] T002 [P] Add CURRENT_SCHEMA_VERSION constant and MIGRATIONS list in adk/storage.py
- [ ] T003 [P] Implement _get_schema_version() method in StorageService class in adk/storage.py
- [ ] T004 Implement _migrate_if_needed() with backup/rollback in adk/storage.py
- [ ] T005 [P] Create get_session_service() factory function in adk/services.py (NEW FILE)
- [ ] T006 [P] Create get_memory_service() factory function in adk/services.py

**Checkpoint**: Migration framework ready - schema updates now safe to apply

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T007 Update adk/run_dev.py to use DatabaseSessionService instead of InMemorySessionService
- [ ] T008 [P] Add DATA_DIR environment variable handling for sessions.db path in adk/run_dev.py
- [ ] T009 Configure Runner with session_service from get_session_service() in adk/run_dev.py
- [ ] T010 [P] Add session listing helper function list_user_sessions() in adk/services.py
- [ ] T011 [P] Create tests/test_migration.py with basic migration tests

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Resume Conversation Across Sessions (Priority: P1) 🎯 MVP

**Goal**: Learners can close the app and resume exactly where they left off

**Independent Test**: Start a conversation, close app, restart, verify conversation context is restored (FR-001, FR-002)

### Implementation for User Story 1

- [ ] T012 [US1] Replace InMemorySessionService with DatabaseSessionService in adk/agent.py
- [ ] T013 [US1] Update session creation pattern in adk/run_dev.py to use try/except get_or_create
- [ ] T014 [US1] Add session restoration logic to load most recent session on startup in adk/run_dev.py
- [ ] T015 [P] [US1] Implement list_sessions() method in StorageService for FR-003 in adk/storage.py
- [ ] T016 [P] [US1] Add session selection prompt on startup in adk/run_dev.py (FR-003)
- [ ] T017 [US1] Update quiz state restoration to sync with ADK session state in adk/quiz_tools.py
- [ ] T018 [US1] Verify quiz:index and quiz:snippets persist across restarts in adk/quiz_tools.py
- [ ] T019 [US1] Add performance logging for session restore time (SC-001) in adk/run_dev.py

**Checkpoint**: User Story 1 complete - sessions persist across app restarts

---

## Phase 4: User Story 2 - Semantic Memory for Personalization (Priority: P2)

**Goal**: System remembers user preferences and learning patterns across sessions

**Independent Test**: Tell system a preference, restart in new session, verify preference is remembered (FR-004, FR-005)

### Implementation for User Story 2

- [ ] T020 [P] [US2] Add UserMemory dataclass to adk/storage.py per data-model.md
- [ ] T021 [P] [US2] Create user_memories table in migration v1.0.0 in adk/storage.py
- [ ] T022 [US2] Implement save_user_memory() method in StorageService in adk/storage.py
- [ ] T023 [US2] Implement get_user_memories() method with fact_type filter in adk/storage.py
- [ ] T024 [US2] Implement update_user_memory_confidence() for repeated preferences in adk/storage.py
- [ ] T025 [P] [US2] Add InMemoryMemoryService to Runner configuration in adk/run_dev.py
- [ ] T026 [US2] Create auto_save_to_memory callback function in adk/agent.py
- [ ] T027 [US2] Add after_agent_callback=auto_save_to_memory to specialist agents in adk/agent.py
- [ ] T028 [P] [US2] Add preload_memory tool to specialist agent tools list in adk/agent.py
- [ ] T029 [US2] Create memory_tools.py with save_preference() FunctionTool in adk/memory_tools.py (NEW FILE)
- [ ] T030 [US2] Create get_user_preferences() FunctionTool in adk/memory_tools.py
- [ ] T031 [US2] Add memory tools to specialist agents in adk/agent.py
- [ ] T032 [US2] Update _base_instruction() to mention preference detection in adk/agent.py
- [ ] T032.1 [US2] Inject retrieved user preferences into agent system prompt before response generation in adk/agent.py (FR-005)

**Checkpoint**: User Story 2 complete - preferences persist across sessions

---

## Phase 5: User Story 3 - Knowledge Graph for Concept Navigation (Priority: P2)

**Goal**: Enable prerequisite/learning path queries on concept relationships

**Independent Test**: Query prerequisites for a concept, verify correct relationship chain returned (FR-006, FR-007, FR-008)

### Implementation for User Story 3

- [ ] T033 [P] [US3] Add weight and learning_order columns to concept_relationships in migration v1.0.0 in adk/storage.py
- [ ] T034 [US3] Implement get_prerequisites() with recursive CTE in adk/storage.py
- [ ] T035 [US3] Implement get_enabled_concepts() query in adk/storage.py
- [ ] T036 [US3] Implement get_learning_path() with BFS/recursive CTE in adk/storage.py (FR-008)
- [ ] T037 [P] [US3] Create adk/graph_tools.py with get_prerequisites_tool FunctionTool (NEW FILE)
- [ ] T038 [P] [US3] Add get_enabled_concepts_tool FunctionTool in adk/graph_tools.py
- [ ] T039 [P] [US3] Add get_learning_path_tool FunctionTool in adk/graph_tools.py
- [ ] T040 [US3] Add graph query tools to curriculum_planner_agent in adk/agent.py
- [ ] T041 [US3] Update curriculum planner instruction to use graph tools in adk/agent.py
- [ ] T042 [P] [US3] Create tests/test_graph_queries.py with prerequisite chain tests

**Checkpoint**: User Story 3 complete - graph navigation available to agents

---

## Phase 6: User Story 4 - Data Export and Backup (Priority: P3)

**Goal**: Users can export all learning data and import into fresh installation

**Independent Test**: Export data, import into new storage, verify all data restored (FR-009, FR-010, FR-011)

### Implementation for User Story 4

- [ ] T043 [US4] Add EXPORT_VERSION constant to adk/storage.py
- [ ] T044 [US4] Update export_progress() to include version, user_memories, session_summaries in adk/storage.py
- [ ] T045 [US4] Add checksum calculation to export_progress() in adk/storage.py
- [ ] T046 [US4] Implement import_progress() method in StorageService in adk/storage.py (FR-010)
- [ ] T047 [US4] Implement _migrate_export_data() for version differences in adk/storage.py (FR-011)
- [ ] T048 [US4] Add validate_import() to check version and checksum in adk/storage.py
- [ ] T049 [P] [US4] Create export_data_tool FunctionTool in adk/memory_tools.py
- [ ] T050 [P] [US4] Create import_data_tool FunctionTool in adk/memory_tools.py
- [ ] T051 [US4] Add export/import commands to adk/run_dev.py CLI
- [ ] T052 [P] [US4] Create tests/test_export_import.py with round-trip tests

**Checkpoint**: User Story 4 complete - data portability available

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T053 [P] Performance optimization for session restore (SC-001 target: <2s for 100 messages)
- [ ] T054 [P] Performance optimization for graph queries (SC-003 target: <500ms for 500 concepts)
- [ ] T055 Add error handling for storage corruption with recovery attempt (Edge Case)
- [ ] T056 [P] Add storage size warning when approaching limit (Edge Case)
- [ ] T057 Update CLAUDE.md with new storage patterns and services
- [ ] T058 Run quickstart.md validation end-to-end
- [ ] T059 [P] Add type hints to all new methods in adk/storage.py and adk/services.py

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Phase 2 completion
  - US1 (P1): No dependencies on other stories - START HERE
  - US2 (P2): Can start after Phase 2, independent of US1
  - US3 (P2): Can start after Phase 2, independent of US1/US2
  - US4 (P3): Can start after Phase 2, should export all data including from US2-US3
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Start here - Foundation for all persistence
- **User Story 2 (P2)**: Independent - Uses ADK MemoryService, not US1 session
- **User Story 3 (P2)**: Independent - Extends storage.py only
- **User Story 4 (P3)**: Should export data from all stories, recommend doing last

### Within Each User Story

- Models/dataclasses before service methods
- Service methods before FunctionTools
- FunctionTools before agent integration
- Core implementation before CLI/UI integration

### Parallel Opportunities

- All tasks marked [P] can run in parallel within their phase
- US1, US2, US3 can proceed in parallel after Phase 2
- All model/dataclass tasks across stories marked [P] can run together

---

## Parallel Example: User Story 2

```bash
# Launch parallel model tasks:
Task: "Add UserMemory dataclass to adk/storage.py"

# Launch parallel tool creation:
Task: "Create memory_tools.py with save_preference() FunctionTool"
Task: "Create get_user_preferences() FunctionTool"
```

---

## Parallel Example: User Story 3

```bash
# Launch all graph tools in parallel (different files, no deps):
Task: "Create adk/graph_tools.py with get_prerequisites_tool"
Task: "Add get_enabled_concepts_tool in adk/graph_tools.py"
Task: "Add get_learning_path_tool in adk/graph_tools.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T006)
2. Complete Phase 2: Foundational (T007-T011)
3. Complete Phase 3: User Story 1 (T012-T019)
4. **STOP and VALIDATE**: Test session persistence independently
5. Deploy/demo if ready - MVP complete!

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → **Deploy/Demo (MVP!)**
3. Add User Story 2 → Test independently → Deploy/Demo (Personalization added)
4. Add User Story 3 → Test independently → Deploy/Demo (Graph navigation added)
5. Add User Story 4 → Test independently → Deploy/Demo (Full data portability)
6. Each story adds value without breaking previous stories

---

## Summary

| Phase | Tasks | Parallel Opportunities | Key Deliverable |
|-------|-------|----------------------|-----------------|
| Setup | T001-T006 | 4 parallel (T002,T003,T005,T006) | Migration framework |
| Foundational | T007-T011 | 3 parallel (T008,T010,T011) | DatabaseSessionService configured |
| US1 (P1) | T012-T019 | 2 parallel (T015,T016) | Session persistence MVP |
| US2 (P2) | T020-T032 | 6 parallel (T020,T021,T025,T028,T029,T030) | Semantic memory |
| US3 (P2) | T033-T042 | 5 parallel (T033,T037,T038,T039,T042) | Graph navigation |
| US4 (P3) | T043-T052 | 3 parallel (T049,T050,T052) | Data export/import |
| Polish | T053-T059 | 4 parallel (T053,T054,T056,T059) | Performance & cleanup |

**Total Tasks**: 59
**MVP Scope**: T001-T019 (19 tasks, covers US1)
**Suggested First Deploy**: After US1 completion (Phase 3)

---

## Notes

- [P] tasks = different files, no dependencies within phase
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
