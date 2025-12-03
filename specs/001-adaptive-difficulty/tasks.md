# Tasks: Adaptive Difficulty System

**Input**: Design documents from `/specs/001-adaptive-difficulty/`
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, contracts/ ✓, quickstart.md ✓

**Tests**: Included as specified in plan.md (pytest with mocking for ADK ToolContext)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Project type**: Single project extending the existing `adk/` module
- **Source**: `adk/` for new modules, extending existing files
- **Tests**: `tests/unit/`, `tests/integration/`, `tests/contract/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and test infrastructure

- [ ] T001 Create test directory structure: `tests/unit/`, `tests/integration/`, `tests/contract/`
- [ ] T002 [P] Configure pytest fixtures for ADK ToolContext mocking in tests/conftest.py
- [ ] T003 [P] Create difficulty level constants module in adk/difficulty_levels.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T004 Add SQLite schema extensions to adk/storage.py: `performance_records` table
- [ ] T005 [P] Add SQLite schema extensions to adk/storage.py: `difficulty_history` table
- [ ] T006 [P] Add columns to `concept_mastery` table migration in adk/storage.py
- [ ] T007 Create DifficultyLevel dataclass with level metadata in adk/difficulty.py
- [ ] T008 Define DIFFICULTY_LEVELS constant (1-6) with question types and hint allowances in adk/difficulty.py
- [ ] T009 Create PerformanceRecord dataclass in adk/difficulty.py
- [ ] T010 Create PerformanceTrend dataclass in adk/difficulty.py
- [ ] T011 Create DifficultyAdjustment dataclass in adk/difficulty.py
- [ ] T012 Create ScaffoldingSupport dataclass in adk/scaffolding.py
- [ ] T013 Define SCAFFOLDING_STRATEGIES constant (definition, process, relationship, application) in adk/scaffolding.py
- [ ] T014 Add StorageService methods for performance records CRUD in adk/storage.py
- [ ] T015 Add StorageService methods for difficulty history CRUD in adk/storage.py

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Automatic Difficulty Adjustment During Quiz (Priority: P1) 🎯 MVP

**Goal**: Implement automatic difficulty level adjustment (1-6) based on real-time learner performance during quiz

**Independent Test**: Start a quiz, answer mix of correct/incorrect responses, verify difficulty level changes appropriately between questions

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T016 [P] [US1] Unit test for difficulty increase logic (3 consecutive ≥85%) in tests/unit/test_difficulty.py
- [ ] T017 [P] [US1] Unit test for difficulty decrease logic (2 consecutive <50%) in tests/unit/test_difficulty.py
- [ ] T018 [P] [US1] Unit test for difficulty maintain logic (60-85% optimal zone) in tests/unit/test_difficulty.py
- [ ] T019 [P] [US1] Unit test for difficulty level clamping (1-6 bounds) in tests/unit/test_difficulty.py
- [ ] T020 [P] [US1] Contract test for get_difficulty_level tool in tests/contract/test_difficulty_tools.py
- [ ] T021 [P] [US1] Contract test for set_difficulty_level tool in tests/contract/test_difficulty_tools.py
- [ ] T022 [P] [US1] Contract test for record_performance tool in tests/contract/test_difficulty_tools.py

### Implementation for User Story 1

- [ ] T023 [US1] Implement calculate_performance_trend() function in adk/difficulty.py
- [ ] T024 [US1] Implement calculate_difficulty_adjustment() function with increase/decrease/maintain logic in adk/difficulty.py
- [ ] T025 [US1] Implement _get_difficulty_level() tool function in adk/difficulty.py
- [ ] T026 [US1] Implement _set_difficulty_level() tool function with session state in adk/difficulty.py
- [ ] T027 [US1] Implement _record_performance() tool function with adjustment trigger in adk/difficulty.py
- [ ] T028 [US1] Create FunctionTool wrappers (get_difficulty_level_tool, set_difficulty_level_tool, record_performance_tool) in adk/difficulty.py
- [ ] T029 [US1] Extend prepare_quiz() to initialize difficulty:level session state (default 3) in adk/quiz_tools.py
- [ ] T030 [US1] Extend advance_quiz() to call record_performance internally in adk/quiz_tools.py
- [ ] T031 [P] [US1] Integration test for full difficulty adjustment flow in tests/integration/test_adaptive_quiz.py

**Checkpoint**: User Story 1 complete - automatic difficulty adjustment works during quiz

---

## Phase 4: User Story 2 - Difficulty-Appropriate Question Generation (Priority: P2)

**Goal**: Generate quiz questions appropriate for the learner's current difficulty level

**Independent Test**: Set specific difficulty level, verify generated questions match expected question types for that level

### Tests for User Story 2

- [ ] T032 [P] [US2] Unit test for question type mapping per difficulty level in tests/unit/test_difficulty.py
- [ ] T033 [P] [US2] Unit test for get_allowed_question_types() function in tests/unit/test_difficulty.py
- [ ] T034 [P] [US2] Contract test for get_difficulty_level returning question_types in tests/contract/test_difficulty_tools.py

### Implementation for User Story 2

- [ ] T035 [US2] Implement get_allowed_question_types() helper function in adk/difficulty.py
- [ ] T036 [US2] Update assessor agent instructions with difficulty level question type mappings in adk/agent.py
- [ ] T037 [US2] Ensure get_difficulty_level response includes question_types list in adk/difficulty.py

**Checkpoint**: User Story 2 complete - questions match difficulty level

---

## Phase 5: User Story 3 - Scaffolding Support When Struggling (Priority: P2)

**Goal**: Provide scaffolding hints and simplified explanations when learner's difficulty decreases

**Independent Test**: Trigger difficulty decrease, verify appropriate scaffolding hints provided with next question

### Tests for User Story 3

- [ ] T038 [P] [US3] Unit test for scaffolding strategy selection by struggle area in tests/unit/test_scaffolding.py
- [ ] T039 [P] [US3] Unit test for struggle area auto-detection from error patterns in tests/unit/test_scaffolding.py
- [ ] T040 [P] [US3] Contract test for get_scaffolding tool in tests/contract/test_difficulty_tools.py

### Implementation for User Story 3

- [ ] T041 [US3] Implement detect_struggle_area() function based on recent error patterns in adk/scaffolding.py
- [ ] T042 [US3] Implement _get_scaffolding() tool function in adk/scaffolding.py
- [ ] T043 [US3] Create get_scaffolding_tool FunctionTool wrapper in adk/scaffolding.py
- [ ] T044 [US3] Update difficulty adjustment to set scaffolding_active flag on decrease in adk/difficulty.py
- [ ] T045 [US3] Add scaffolding hints to advance_quiz response when scaffolding_active in adk/quiz_tools.py
- [ ] T046 [P] [US3] Integration test for scaffolding activation on difficulty decrease in tests/integration/test_adaptive_quiz.py

**Checkpoint**: User Story 3 complete - scaffolding activates when learner struggles

---

## Phase 6: User Story 4 - Performance Tracking and History (Priority: P3)

**Goal**: Track and persist performance data (score, time, hints, difficulty, concept) for trend analysis

**Independent Test**: Answer several questions, retrieve performance history, verify all metrics captured correctly

### Tests for User Story 4

- [ ] T047 [P] [US4] Unit test for performance record creation and storage in tests/unit/test_difficulty.py
- [ ] T048 [P] [US4] Unit test for trend analysis (improving/stable/declining) in tests/unit/test_difficulty.py
- [ ] T049 [P] [US4] Contract test for get_performance_trend tool in tests/contract/test_difficulty_tools.py

### Implementation for User Story 4

- [ ] T050 [US4] Implement save_performance_record() in StorageService in adk/storage.py
- [ ] T051 [US4] Implement get_recent_performance_records() in StorageService in adk/storage.py
- [ ] T052 [US4] Implement calculate_trend_direction() (EMA-based) in adk/difficulty.py
- [ ] T053 [US4] Implement _get_performance_trend() tool function in adk/difficulty.py
- [ ] T054 [US4] Create get_performance_trend_tool FunctionTool wrapper in adk/difficulty.py
- [ ] T055 [US4] Update record_performance to persist to SQLite in adk/difficulty.py
- [ ] T056 [P] [US4] Integration test for performance persistence across session in tests/integration/test_adaptive_quiz.py

**Checkpoint**: User Story 4 complete - performance tracking and history works

---

## Phase 7: User Story 5 - Hint System Based on Difficulty Level (Priority: P3)

**Goal**: Provide tiered hints (3/2/1/0/0/0 for levels 1-6) with usage affecting difficulty calculations

**Independent Test**: Check available hints at each difficulty level, verify hint count affects difficulty calculations

### Tests for User Story 5

- [ ] T057 [P] [US5] Unit test for hint allowance per difficulty level (3,2,1,0,0,0) in tests/unit/test_difficulty.py
- [ ] T058 [P] [US5] Unit test for hint usage tracking in session state in tests/unit/test_difficulty.py
- [ ] T059 [P] [US5] Unit test for hint usage affecting difficulty adjustment in tests/unit/test_difficulty.py
- [ ] T060 [P] [US5] Contract test for get_difficulty_hint tool in tests/contract/test_difficulty_tools.py

### Implementation for User Story 5

- [ ] T061 [US5] Implement _get_difficulty_hint() tool function with allowance enforcement in adk/difficulty.py
- [ ] T062 [US5] Create get_difficulty_hint_tool FunctionTool wrapper in adk/difficulty.py
- [ ] T063 [US5] Track hints_used_current in session state in adk/difficulty.py
- [ ] T064 [US5] Factor hint usage into difficulty adjustment calculation in adk/difficulty.py
- [ ] T065 [US5] Reset hint counter on question advance in adk/quiz_tools.py
- [ ] T066 [P] [US5] Integration test for hint system end-to-end in tests/integration/test_adaptive_quiz.py

**Checkpoint**: User Story 5 complete - tiered hint system with difficulty impact works

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final integration, documentation, and quality improvements

- [ ] T067 [P] Add difficulty tools to assessor agent in adk/agent.py
- [ ] T068 [P] Implement _get_concept_difficulty_stats() tool for per-concept analysis in adk/difficulty.py
- [ ] T069 [P] Create get_concept_difficulty_stats_tool FunctionTool wrapper in adk/difficulty.py
- [ ] T070 Update StorageService.export_progress() to include difficulty data in adk/storage.py
- [ ] T071 [P] Add comprehensive docstrings to all public functions in adk/difficulty.py
- [ ] T072 [P] Add comprehensive docstrings to all public functions in adk/scaffolding.py
- [ ] T073 Run quickstart.md validation: verify all import paths and usage examples work
- [ ] T074 Full integration test: complete quiz session with difficulty adaptation in tests/integration/test_adaptive_quiz.py

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User stories can then proceed in priority order (P1 → P2 → P3)
  - US1 and US2 can run in parallel (different core functionality)
  - US3 depends on US1 (needs difficulty adjustment to trigger scaffolding)
  - US4 and US5 can run in parallel with each other
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational - No dependencies on other stories
- **User Story 3 (P2)**: Depends on US1 (scaffolding triggers on difficulty decrease)
- **User Story 4 (P3)**: Can start after Foundational - No dependencies on other stories
- **User Story 5 (P3)**: Depends on US1 (hints affect difficulty calculations)

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Dataclasses/models before service functions
- Service functions before tool functions
- Tool functions before FunctionTool wrappers
- Core implementation before quiz_tools.py integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- All tests for a user story marked [P] can run in parallel
- US1 and US2 can be worked in parallel (independent core functionality)
- US4 and US5 can be worked in parallel (both P3, different concerns)

---

## Parallel Example: User Story 1 Tests

```bash
# Launch all tests for User Story 1 together:
Task: "Unit test for difficulty increase logic in tests/unit/test_difficulty.py"
Task: "Unit test for difficulty decrease logic in tests/unit/test_difficulty.py"
Task: "Unit test for difficulty maintain logic in tests/unit/test_difficulty.py"
Task: "Unit test for difficulty level clamping in tests/unit/test_difficulty.py"
Task: "Contract test for get_difficulty_level tool in tests/contract/test_difficulty_tools.py"
Task: "Contract test for set_difficulty_level tool in tests/contract/test_difficulty_tools.py"
Task: "Contract test for record_performance tool in tests/contract/test_difficulty_tools.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test difficulty adjustment independently
5. Deploy/demo if ready - basic adaptive difficulty works!

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy (MVP - core adjustment!)
3. Add User Story 2 → Test independently → Deploy (questions match levels)
4. Add User Story 3 → Test independently → Deploy (scaffolding support)
5. Add User Story 4 → Test independently → Deploy (performance history)
6. Add User Story 5 → Test independently → Deploy (tiered hints)
7. Polish phase → Full feature complete

### Key Integration Points

- `adk/difficulty.py`: Core difficulty logic, adjustment algorithm, tools
- `adk/scaffolding.py`: Scaffolding strategies and tool
- `adk/storage.py`: Schema extensions, performance/history persistence
- `adk/quiz_tools.py`: Integration points (prepare_quiz, advance_quiz)
- `adk/agent.py`: Assessor agent tool registration and instructions

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Default difficulty level is 3 (Application) for new users
- Performance stored both in session state (runtime) and SQLite (persistence)
