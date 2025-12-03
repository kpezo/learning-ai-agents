# Tasks: Advanced Pedagogical Metrics

**Input**: Design documents from `/specs/008-pedagogical-metrics/`
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, contracts/ ✓

**Tests**: Unit tests and integration tests included as specified in plan.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

This project extends the existing `adk/` module structure:
- **Source**: `adk/` at repository root
- **New submodule**: `adk/metrics/`
- **Tests**: `tests/` at repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create metrics module directory structure at adk/metrics/
- [ ] T002 [P] Add numpy dependency to adk/requirements.txt
- [ ] T003 [P] Create adk/metrics/__init__.py with module exports
- [ ] T004 [P] Create tests/ directory if not exists and add tests/__init__.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T005 Add data transfer objects (DTOs) from contracts to adk/metrics/types.py
- [ ] T006 Add storage schema extensions to adk/storage.py using contracts/storage_schema.sql
- [ ] T007 Create storage CRUD methods for bkt_parameters table in adk/storage.py
- [ ] T008 [P] Create storage CRUD methods for question_parameters table in adk/storage.py
- [ ] T009 [P] Create storage CRUD methods for learner_ability table in adk/storage.py
- [ ] T010 [P] Create storage CRUD methods for zpd_status table in adk/storage.py
- [ ] T011 [P] Create storage CRUD methods for behavioral_events table in adk/storage.py
- [ ] T012 [P] Create storage CRUD methods for domain_thresholds table in adk/storage.py
- [ ] T013 Create database migration helper for concept_mastery table extensions in adk/storage.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Probabilistic Mastery Tracking (Priority: P1) 🎯 MVP

**Goal**: Calculate mastery probability using Bayesian Knowledge Tracing (BKT) that accounts for guessing and slip errors

**Independent Test**: Answer a sequence of questions and verify mastery probability updates correctly according to BKT formulas

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T014 [P] [US1] Create unit tests for BKT update formulas in tests/test_bkt.py
- [ ] T015 [P] [US1] Create unit tests for BKT mastery threshold detection in tests/test_bkt.py
- [ ] T016 [P] [US1] Create unit tests for BKT confidence interval calculation in tests/test_bkt.py

### Implementation for User Story 1

- [ ] T017 [US1] Implement BKTCalculator class with update() method in adk/metrics/bkt.py
- [ ] T018 [US1] Implement Bayesian update formulas (correct/incorrect) in adk/metrics/bkt.py
- [ ] T019 [US1] Implement learning transition P(L_t+1) calculation in adk/metrics/bkt.py
- [ ] T020 [US1] Implement confidence interval calculation (95% CI) in adk/metrics/bkt.py
- [ ] T021 [US1] Implement is_mastered() threshold checking (95% default) in adk/metrics/bkt.py
- [ ] T022 [US1] Add parameter validation (p_g + p_s < 1 constraint) in adk/metrics/bkt.py
- [ ] T023 [US1] Create BKT storage integration methods in adk/storage.py (save_bkt_state, get_bkt_model)

**Checkpoint**: BKT mastery tracking should be fully functional and testable independently

---

## Phase 4: User Story 2 - Question Difficulty Calibration (Priority: P1)

**Goal**: Calibrate question difficulty using Item Response Theory (IRT) 3PL model to match questions to learner ability

**Independent Test**: Verify question difficulty parameters predict learner success rates accurately

### Tests for User Story 2

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T024 [P] [US2] Create unit tests for 3PL probability calculation in tests/test_irt.py
- [ ] T025 [P] [US2] Create unit tests for Newton-Raphson ability estimation in tests/test_irt.py
- [ ] T026 [P] [US2] Create unit tests for Fisher information calculation in tests/test_irt.py
- [ ] T027 [P] [US2] Create unit tests for optimal question selection in tests/test_irt.py

### Implementation for User Story 2

- [ ] T028 [US2] Implement IRTCalculator class with probability() method in adk/metrics/irt.py
- [ ] T029 [US2] Implement 3PL probability formula P(correct|theta,a,b,c) in adk/metrics/irt.py
- [ ] T030 [US2] Implement Newton-Raphson MLE for ability estimation in adk/metrics/irt.py
- [ ] T031 [US2] Implement Fisher information calculation I(theta) in adk/metrics/irt.py
- [ ] T032 [US2] Implement select_optimal_question() for maximum information in adk/metrics/irt.py
- [ ] T033 [US2] Add parameter validation (a: 0.5-2.5, b: -3 to +3, c: 0-0.35) in adk/metrics/irt.py
- [ ] T034 [US2] Create IRT storage integration for question_parameters in adk/storage.py
- [ ] T035 [US2] Create learner ability storage methods in adk/storage.py

**Checkpoint**: IRT question calibration should be fully functional and testable independently

---

## Phase 5: User Story 3 - Zone of Proximal Development Maintenance (Priority: P2)

**Goal**: Keep learners in optimal ZPD (60-85% success rate) with automatic difficulty adjustment

**Independent Test**: Monitor learner success rate over time and verify it stays within 60-85% optimal range

### Tests for User Story 3

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T036 [P] [US3] Create unit tests for ZPD zone evaluation in tests/test_zpd.py
- [ ] T037 [P] [US3] Create unit tests for difficulty recommendation logic in tests/test_zpd.py
- [ ] T038 [P] [US3] Create unit tests for exit detection triggers in tests/test_zpd.py

### Implementation for User Story 3

- [ ] T039 [US3] Implement ZPDEvaluator class with evaluate() method in adk/metrics/zpd.py
- [ ] T040 [US3] Implement zone classification logic (frustration/optimal/boredom) in adk/metrics/zpd.py
- [ ] T041 [US3] Implement success rate EMA calculation from recent results in adk/metrics/zpd.py
- [ ] T042 [US3] Implement difficulty recommendation logic (1-6 scale) in adk/metrics/zpd.py
- [ ] T043 [US3] Implement consecutive correct/incorrect streak tracking in adk/metrics/zpd.py
- [ ] T044 [US3] Add zone transition thresholds (50%, 60%, 85%, 90%) in adk/metrics/zpd.py
- [ ] T045 [US3] Create ZPD storage integration methods in adk/storage.py

**Checkpoint**: ZPD maintenance should be fully functional and testable independently

---

## Phase 6: User Story 4 - Frustration and Boredom Detection (Priority: P2)

**Goal**: Detect frustration and boredom from behavioral indicators (response time, hints, abandonment)

**Independent Test**: Simulate frustration patterns (rapid incorrect attempts) and verify system responds appropriately

### Tests for User Story 4

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T046 [P] [US4] Create unit tests for frustration detection in tests/test_behavioral.py
- [ ] T047 [P] [US4] Create unit tests for boredom detection in tests/test_behavioral.py
- [ ] T048 [P] [US4] Create unit tests for response time analysis in tests/test_behavioral.py

### Implementation for User Story 4

- [ ] T049 [US4] Implement BehavioralAnalyzer class with analyze() method in adk/metrics/behavioral.py
- [ ] T050 [US4] Implement detect_frustration() with configurable thresholds in adk/metrics/behavioral.py
- [ ] T051 [US4] Implement detect_boredom() with response time ratio analysis in adk/metrics/behavioral.py
- [ ] T052 [US4] Implement response time ratio calculation (actual/expected) in adk/metrics/behavioral.py
- [ ] T053 [US4] Add rapid attempt detection (< 3 seconds between attempts) in adk/metrics/behavioral.py
- [ ] T054 [US4] Add hint usage pattern analysis in adk/metrics/behavioral.py
- [ ] T055 [US4] Create behavioral event logging methods in adk/storage.py

**Checkpoint**: Behavioral detection should be fully functional and testable independently

---

## Phase 7: User Story 5 - Domain-Specific Mastery Thresholds (Priority: P3)

**Goal**: Apply different mastery thresholds based on content domain (80% general, 85% STEM, 95% safety)

**Independent Test**: Complete quizzes in different domains and verify mastery is evaluated against correct threshold

### Tests for User Story 5

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T056 [P] [US5] Create unit tests for domain threshold lookup in tests/test_bkt.py
- [ ] T057 [P] [US5] Create unit tests for consistency count requirements in tests/test_bkt.py

### Implementation for User Story 5

- [ ] T058 [US5] Extend BKTCalculator to accept domain parameter in adk/metrics/bkt.py
- [ ] T059 [US5] Implement domain threshold lookup from storage in adk/metrics/bkt.py
- [ ] T060 [US5] Implement consistency count requirement checking in adk/metrics/bkt.py
- [ ] T061 [US5] Add domain assignment to concept_mastery in adk/storage.py
- [ ] T062 [US5] Create domain threshold CRUD operations in adk/storage.py

**Checkpoint**: Domain-specific thresholds should be fully functional and testable independently

---

## Phase 8: Integration (Quiz Tools & ADK Wrappers)

**Purpose**: Integrate metrics with existing quiz system and expose as ADK tools

- [ ] T063 [P] Create integration tests for metrics with quiz_tools in tests/test_metrics_integration.py
- [ ] T064 Update advance_quiz() to use BKT instead of simple mastery in adk/quiz_tools.py
- [ ] T065 Add response time tracking to quiz answer flow in adk/quiz_tools.py
- [ ] T066 Add ZPD-based difficulty adjustment to question selection in adk/quiz_tools.py
- [ ] T067 Create adk/metrics_tools.py with ADK FunctionTool wrappers
- [ ] T068 Add get_mastery_bkt tool wrapper in adk/metrics_tools.py
- [ ] T069 Add get_zpd_recommendation tool wrapper in adk/metrics_tools.py
- [ ] T070 Add get_learner_profile tool wrapper in adk/metrics_tools.py
- [ ] T071 Register metrics tools with specialist agents in adk/agent.py

**Checkpoint**: Metrics fully integrated with quiz system and accessible via ADK tools

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T072 [P] Add migration helper for existing users from simple mastery to BKT in adk/storage.py
- [ ] T073 [P] Validate all acceptance scenarios from spec.md
- [ ] T074 Run quickstart.md code examples to verify documentation accuracy
- [ ] T075 Update adk/metrics/__init__.py with public API exports
- [ ] T076 [P] Run full test suite with coverage report
- [ ] T077 Performance validation: verify BKT/IRT calculations < 100ms

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phases 3-7)**: All depend on Foundational phase completion
  - US1 (BKT) and US2 (IRT) can proceed in parallel (P1 stories)
  - US3 (ZPD) can start after Phase 2 (uses success rate, not BKT directly)
  - US4 (Behavioral) can start after Phase 2 (independent of other algorithms)
  - US5 (Domains) depends on US1 (BKT) being complete
- **Integration (Phase 8)**: Depends on US1, US2, US3, US4 being complete
- **Polish (Phase 9)**: Depends on all user stories and integration being complete

### User Story Dependencies

```
Phase 2 (Foundational)
     │
     ├──────┬──────┬──────┐
     ▼      ▼      ▼      ▼
   US1    US2    US3    US4   (can run in parallel)
   (BKT)  (IRT)  (ZPD)  (Behavioral)
     │
     ▼
   US5
   (Domains - extends BKT)
     │
     ▼
Phase 8 (Integration)
     │
     ▼
Phase 9 (Polish)
```

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Core calculator class first
- Algorithm implementation second
- Storage integration last

### Parallel Opportunities

- T002, T003, T004 can run in parallel (Setup phase)
- T008, T009, T010, T011, T012 can run in parallel (storage CRUD methods)
- All test tasks within a user story can run in parallel
- US1, US2, US3, US4 can be worked on in parallel after Foundational

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Create unit tests for BKT update formulas in tests/test_bkt.py"
Task: "Create unit tests for BKT mastery threshold detection in tests/test_bkt.py"
Task: "Create unit tests for BKT confidence interval calculation in tests/test_bkt.py"

# After tests pass (fail initially), implement sequentially:
Task: "Implement BKTCalculator class with update() method in adk/metrics/bkt.py"
Task: "Implement Bayesian update formulas in adk/metrics/bkt.py"
# ... etc
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (BKT Mastery)
4. **STOP and VALIDATE**: Test BKT independently with sample answers
5. Deploy/demo if ready - system now has probabilistic mastery tracking

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add User Story 1 (BKT) → Test independently → Core mastery tracking works
3. Add User Story 2 (IRT) → Test independently → Question calibration works
4. Add User Story 3 (ZPD) → Test independently → Difficulty adjustment works
5. Add User Story 4 (Behavioral) → Test independently → Frustration/boredom detection works
6. Add User Story 5 (Domains) → Test independently → Domain thresholds work
7. Integration + Polish → Full system validated

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (BKT)
   - Developer B: User Story 2 (IRT)
   - Developer C: User Stories 3 + 4 (ZPD + Behavioral)
3. After US1 complete: Developer A continues with US5
4. All integrate together in Phase 8

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- numpy required for BKT/IRT mathematical calculations
- Existing adk/storage.py patterns should be followed for new CRUD methods
