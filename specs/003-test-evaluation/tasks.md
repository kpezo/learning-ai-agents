# Tasks: Tests & Evaluation Framework

**Input**: Design documents from `/specs/003-test-evaluation/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: This feature IS the testing infrastructure - tests are the primary deliverables.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Project type**: Single project (existing adk/ package)
- **Tests**: `tests/` at repository root
- **CI**: `.github/workflows/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and test structure creation

- [ ] T001 Create test directory structure: tests/, tests/unit/, tests/integration/, tests/evaluation/, tests/evaluation/evalsets/
- [ ] T002 [P] Create pytest configuration in pyproject.toml with test paths and markers
- [ ] T003 [P] Add test dependencies to requirements-dev.txt: pytest>=7.0.0, pytest-cov>=4.0.0, pytest-asyncio>=0.21.0
- [ ] T004 [P] Create tests/__init__.py and tests/unit/__init__.py for package recognition

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared fixtures and mocks that ALL user stories depend on

**CRITICAL**: No user story work can begin until this phase is complete

- [ ] T005 Create shared fixtures in tests/conftest.py: mock_retriever, test_storage (tmp_path based), mock_tool_context
- [ ] T006 [P] Implement mock_retriever fixture returning SimpleRetriever with predefined chunks in tests/conftest.py
- [ ] T007 [P] Implement test_storage fixture using tmp_path for isolated SQLite databases in tests/conftest.py
- [ ] T008 [P] Implement mock_tool_context fixture simulating ADK ToolContext with session state in tests/conftest.py
- [ ] T009 Add pytest markers configuration (unit, integration, evaluation, slow) in pyproject.toml

**Checkpoint**: Foundation ready - unit test implementation can now begin

---

## Phase 3: User Story 1 - Run Unit Tests Locally (Priority: P1)

**Goal**: Developers can run pytest to verify functionality with clear pass/fail feedback

**Independent Test**: Run `pytest tests/unit -v` and verify tests execute with clear output

### Implementation for User Story 1

- [ ] T010 [P] [US1] Create tests/unit/test_rag_setup.py with tests for SimpleRetriever, _chunk_text, build_retriever
- [ ] T011 [P] [US1] Create tests/unit/test_storage.py with tests for StorageService CRUD operations
- [ ] T012 [P] [US1] Create tests/unit/test_tools.py with tests for _fetch_info, _get_quiz_source
- [ ] T013 [P] [US1] Create tests/unit/test_quiz_tools.py with tests for quiz state management functions
- [ ] T014 [US1] Add test for SimpleRetriever.get_relevant_documents with various queries in tests/unit/test_rag_setup.py
- [ ] T015 [US1] Add test for _chunk_text with edge cases (empty text, overlap larger than chunk) in tests/unit/test_rag_setup.py
- [ ] T016 [US1] Add tests for StorageService.start_quiz, update_quiz_progress, complete_quiz in tests/unit/test_storage.py
- [ ] T017 [US1] Add tests for StorageService.update_mastery, get_mastery, get_weak_concepts in tests/unit/test_storage.py
- [ ] T018 [US1] Add tests for StorageService.add_knowledge_gap, resolve_gap, get_active_gaps in tests/unit/test_storage.py
- [ ] T019 [US1] Add tests for StorageService.get_user_stats, export_progress in tests/unit/test_storage.py
- [ ] T020 [US1] Add test for _fetch_info with mocked retriever in tests/unit/test_tools.py
- [ ] T021 [US1] Add test for _get_quiz_source with max_chunks parameter in tests/unit/test_tools.py
- [ ] T022 [US1] Add test for error handling when retriever not initialized in tests/unit/test_tools.py
- [ ] T023 [US1] Add tests for _prepare_quiz with mocked retriever and storage in tests/unit/test_quiz_tools.py
- [ ] T024 [US1] Add tests for _get_quiz_step state retrieval in tests/unit/test_quiz_tools.py
- [ ] T025 [US1] Add tests for _advance_quiz correct/incorrect flow in tests/unit/test_quiz_tools.py
- [ ] T026 [US1] Add tests for _reveal_context returning full snippet in tests/unit/test_quiz_tools.py
- [ ] T027 [US1] Add tests for _get_learning_stats, _get_weak_concepts, _get_quiz_history in tests/unit/test_quiz_tools.py
- [ ] T028 [US1] Verify all tests run with `pytest tests/unit -v` and produce clear output

**Checkpoint**: User Story 1 complete - developers can run unit tests locally with `pytest tests/unit -v`

---

## Phase 4: User Story 2 - Agent Behavior Evaluation (Priority: P1)

**Goal**: Developers can evaluate agent behavior against predefined scenarios with pass/fail reporting

**Independent Test**: Run `python tests/evaluation/run_evaluation.py` and verify scenario results

### Implementation for User Story 2

- [ ] T029 [P] [US2] Create tests/evaluation/evalsets/ directory structure
- [ ] T030 [P] [US2] Create tutor_scenarios.json with 5 evaluation scenarios in tests/evaluation/evalsets/
- [ ] T031 [P] [US2] Create assessor_scenarios.json with 5 evaluation scenarios in tests/evaluation/evalsets/
- [ ] T032 [P] [US2] Create curriculum_scenarios.json with 5 evaluation scenarios in tests/evaluation/evalsets/
- [ ] T033 [US2] Create run_evaluation.py script to load evalsets and run scenarios in tests/evaluation/
- [ ] T034 [US2] Implement scenario loader in run_evaluation.py: load JSON, validate against schema
- [ ] T035 [US2] Implement pattern matching logic in run_evaluation.py: regex matching for expected_patterns
- [ ] T036 [US2] Implement pass threshold calculation in run_evaluation.py: count matched patterns vs total
- [ ] T037 [US2] Implement evaluation result reporting in run_evaluation.py: per-scenario and aggregate results
- [ ] T038 [US2] Add CLI arguments to run_evaluation.py: --agent, --verbose, --threshold
- [ ] T039 [US2] Verify evaluation runs with `python tests/evaluation/run_evaluation.py --verbose`

**Checkpoint**: User Story 2 complete - developers can evaluate agent behavior with scenario-based testing

---

## Phase 5: User Story 3 - Automated Testing in CI Pipeline (Priority: P2)

**Goal**: Tests run automatically on push/PR with failure notifications

**Independent Test**: Push a commit and verify GitHub Actions runs tests automatically

### Implementation for User Story 3

- [ ] T040 [P] [US3] Create .github/workflows/ directory if not exists
- [ ] T041 [US3] Create .github/workflows/test.yml with unit test job
- [ ] T042 [US3] Configure test.yml to trigger on push and pull_request events
- [ ] T043 [US3] Add Python setup step in test.yml: actions/setup-python@v5 with python-version 3.11
- [ ] T044 [US3] Add dependency installation step in test.yml: pip install -r adk/requirements.txt and test deps
- [ ] T045 [US3] Add unit test execution step in test.yml: pytest tests/unit --cov=adk --cov-report=xml
- [ ] T046 [US3] Add evaluation job in test.yml that runs only on main branch
- [ ] T047 [US3] Configure evaluation job to depend on unit-tests job success
- [ ] T048 [US3] Verify workflow syntax with act or manual push to trigger

**Checkpoint**: User Story 3 complete - CI pipeline automatically runs tests on code push

---

## Phase 6: User Story 4 - Tool Function Testing (Priority: P2)

**Goal**: Comprehensive tool function tests including edge cases and error handling

**Independent Test**: Run `pytest tests/unit/test_tools.py tests/unit/test_quiz_tools.py -v` with all tests passing

### Implementation for User Story 4

- [ ] T049 [P] [US4] Add edge case test: _fetch_info with empty query in tests/unit/test_tools.py
- [ ] T050 [P] [US4] Add edge case test: _get_quiz_source with max_chunks=0 in tests/unit/test_tools.py
- [ ] T051 [P] [US4] Add edge case test: _prepare_quiz with no matching content in tests/unit/test_quiz_tools.py
- [ ] T052 [P] [US4] Add edge case test: _get_quiz_step before prepare_quiz called in tests/unit/test_quiz_tools.py
- [ ] T053 [P] [US4] Add edge case test: _advance_quiz at end of quiz in tests/unit/test_quiz_tools.py
- [ ] T054 [US4] Add test for quiz state persistence across multiple advance_quiz calls in tests/unit/test_quiz_tools.py
- [ ] T055 [US4] Add test for concept mastery update integration in tests/unit/test_quiz_tools.py
- [ ] T056 [US4] Add test for storage error handling (graceful failure) in tests/unit/test_quiz_tools.py
- [ ] T057 [US4] Verify all tool tests pass with clear error messages on failure

**Checkpoint**: User Story 4 complete - comprehensive tool function testing with edge cases

---

## Phase 7: User Story 5 - Test Coverage Reporting (Priority: P3)

**Goal**: Developers can view coverage reports and enforce coverage thresholds

**Independent Test**: Run `pytest tests/unit --cov=adk --cov-report=html` and open htmlcov/index.html

### Implementation for User Story 5

- [ ] T058 [P] [US5] Configure pytest-cov in pyproject.toml with coverage paths and output formats
- [ ] T059 [P] [US5] Add coverage fail threshold (70%) in pyproject.toml: --cov-fail-under=70
- [ ] T060 [US5] Update test.yml to generate XML coverage report for CI integration
- [ ] T061 [US5] Add codecov/codecov-action@v4 step in test.yml for coverage upload
- [ ] T062 [US5] Add .coveragerc with source paths and omit patterns (tests/, __pycache__)
- [ ] T063 [US5] Verify coverage report generation with `pytest tests/unit --cov=adk --cov-report=html`
- [ ] T064 [US5] Verify coverage threshold enforcement: tests fail if coverage below 70%

**Checkpoint**: User Story 5 complete - coverage reporting and threshold enforcement working

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Integration tests and final validation

- [ ] T065 [P] Create tests/integration/test_agent_flow.py for multi-agent delegation tests
- [ ] T066 [P] Add integration test: supervisor routes to tutor agent in tests/integration/test_agent_flow.py
- [ ] T067 [P] Add integration test: quiz flow from prepare to complete in tests/integration/test_agent_flow.py
- [ ] T068 Validate all tests pass: `pytest tests/ -v`
- [ ] T069 Validate coverage meets target: `pytest tests/unit --cov=adk --cov-fail-under=70`
- [ ] T070 Run quickstart.md validation: execute all commands and verify output
- [ ] T071 Update CLAUDE.md with testing section if not already present

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - US1 and US2 are both P1 and can run in parallel
  - US3 and US4 are both P2 and depend on US1 completion
  - US5 is P3 and can start after foundational
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Phase 2 - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Phase 2 - No dependencies on other stories
- **User Story 3 (P2)**: Can start after Phase 2 - Integrates US1 tests into CI
- **User Story 4 (P2)**: Can start after US1 - Extends tool tests
- **User Story 5 (P3)**: Can start after Phase 2 - Independent coverage feature

### Within Each User Story

- Files marked [P] within a story can be created in parallel
- Sequential tasks depend on earlier tasks in the same story
- Story complete before moving to next priority (for solo developer)

### Parallel Opportunities

- T002, T003, T004 can run in parallel (Setup)
- T006, T007, T008 can run in parallel (Foundational fixtures)
- T010, T011, T012, T013 can run in parallel (US1 test files)
- T029, T030, T031, T032 can run in parallel (US2 evalsets)
- T049, T050, T051, T052, T053 can run in parallel (US4 edge cases)
- T058, T059 can run in parallel (US5 config)
- T065, T066, T067 can run in parallel (Polish integration tests)

---

## Parallel Example: User Story 1

```bash
# Launch all test file creation together:
Task: "Create tests/unit/test_rag_setup.py"
Task: "Create tests/unit/test_storage.py"
Task: "Create tests/unit/test_tools.py"
Task: "Create tests/unit/test_quiz_tools.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 + 2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1 (unit tests)
4. Complete Phase 4: User Story 2 (evaluations)
5. **STOP and VALIDATE**: Run `pytest tests/unit -v` and `python tests/evaluation/run_evaluation.py`
6. Deploy/demo if ready - developers can now run tests locally

### Incremental Delivery

1. Setup + Foundational → Test infrastructure ready
2. Add User Story 1 → Developers can run unit tests (MVP!)
3. Add User Story 2 → Developers can evaluate agents
4. Add User Story 3 → CI automation
5. Add User Story 4 → Comprehensive tool testing
6. Add User Story 5 → Coverage reporting
7. Each story adds value without breaking previous stories

---

## Summary

- **Total Tasks**: 71
- **Phase 1 (Setup)**: 4 tasks
- **Phase 2 (Foundational)**: 5 tasks
- **Phase 3 (US1 - Unit Tests)**: 19 tasks
- **Phase 4 (US2 - Evaluations)**: 11 tasks
- **Phase 5 (US3 - CI)**: 9 tasks
- **Phase 6 (US4 - Tool Tests)**: 9 tasks
- **Phase 7 (US5 - Coverage)**: 7 tasks
- **Phase 8 (Polish)**: 7 tasks
- **Parallel opportunities**: 29 tasks marked [P]
- **Suggested MVP**: Complete through User Story 2 (Phase 4)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
