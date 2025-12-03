# Tasks: Multi-Agent Orchestration Expansion

**Input**: Design documents from `/specs/007-multi-agent-orchestration/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `adk/` at repository root (existing package)
- **Tests**: `tests/unit/`, `tests/integration/`, `tests/contract/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and new module structure

- [ ] T001 Create `adk/orchestration.py` with module docstring and imports (SequentialAgent, LoopAgent, BaseAgent from google.adk.agents)
- [ ] T002 [P] Create `adk/diagnostic_tools.py` with module docstring and imports (FunctionTool, storage dependencies)
- [ ] T003 [P] Create `adk/path_tools.py` with module docstring and imports (FunctionTool, storage dependencies)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Database schema extensions and core infrastructure required by ALL user stories

**CRITICAL**: No user story work can begin until this phase is complete

- [ ] T004 Add `agent_transitions` table to `adk/storage.py` with schema: id, session_id, from_agent, to_agent, reason, message_excerpt, timestamp
- [ ] T005 Add `learning_cycles` table to `adk/storage.py` with schema: id, user_id, session_id, topic, cycle_number, quiz_score, mastery_achieved, started_at, completed_at
- [ ] T006 Add `diagnostic_results` table to `adk/storage.py` with schema: id, user_id, session_id, topic, prerequisite_gaps (JSON), learner_level, recommendations (JSON), timestamp
- [ ] T007 Add `log_transition()` method to StorageService class in `adk/storage.py`
- [ ] T008 Add `get_session_transitions()` method to StorageService class in `adk/storage.py`
- [ ] T009 Add `start_learning_cycle()` and `complete_learning_cycle()` methods to StorageService class in `adk/storage.py`
- [ ] T010 Add `save_diagnostic_result()` method to StorageService class in `adk/storage.py`

**Checkpoint**: Database schema ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Intelligent Task Routing (Priority: P1)

**Goal**: Coordinator agent routes messages to appropriate specialist agents based on content analysis

**Independent Test**: Send different message types and verify routing to correct specialist

### Implementation for User Story 1

- [ ] T011 [P] [US1] Define `DiagnosticAgent` LlmAgent in `adk/agent.py` with description "Assesses learner's existing knowledge and identifies prerequisite gaps"
- [ ] T012 [P] [US1] Define `TutorAgent` LlmAgent in `adk/agent.py` with description "Explains concepts and answers questions about the material"
- [ ] T013 [P] [US1] Define `QuizAgent` LlmAgent in `adk/agent.py` with description "Generates assessments and evaluates quiz answers"
- [ ] T014 [P] [US1] Define `FeedbackAgent` LlmAgent in `adk/agent.py` with description "Provides constructive analysis of quiz performance"
- [ ] T015 [P] [US1] Define `PathPlannerAgent` LlmAgent in `adk/agent.py` with description "Recommends learning paths based on progress and goals"
- [ ] T016 [US1] Create `CoordinatorAgent` as root Agent in `adk/agent.py` with sub_agents list containing all 5 specialists
- [ ] T017 [US1] Write routing instruction for CoordinatorAgent in `adk/agent.py` covering: new topics -> diagnostic, questions -> tutor, quiz requests -> quiz, progress inquiries -> pathplanner, unclear -> tutor fallback
- [ ] T018 [US1] Implement `log_agent_transition` tool function in `adk/storage.py` (FR-013: track which agent handled each message)
- [ ] T019 [US1] Implement `get_session_transitions` tool function in `adk/storage.py` for debugging agent routing
- [ ] T020 [US1] Add quiz pause/resume handling to CoordinatorAgent instruction in `adk/agent.py` (FR-011: mid-conversation agent switching)
- [ ] T021 [US1] Update `adk/run_dev.py` to use new CoordinatorAgent as root_agent instead of education_supervisor

**Checkpoint**: User Story 1 complete - messages route to correct specialists with transition tracking

---

## Phase 4: User Story 2 - Diagnostic Assessment for New Topics (Priority: P1)

**Goal**: Diagnostic agent assesses prerequisites and identifies knowledge gaps before teaching begins

**Independent Test**: Start a new topic and verify prerequisite check runs before tutoring

### Implementation for User Story 2

- [ ] T022 [P] [US2] Implement `get_prerequisites(topic)` tool in `adk/diagnostic_tools.py` using concept_relationships table with "depends-on" relationship type
- [ ] T023 [P] [US2] Implement `check_prerequisites_mastery(topic, user_id, threshold)` tool in `adk/diagnostic_tools.py` returning gaps list with current vs required mastery
- [ ] T024 [P] [US2] Implement `classify_learner_level(user_id)` tool in `adk/diagnostic_tools.py` returning beginner/intermediate/advanced based on mastery stats
- [ ] T025 [US2] Add `save_diagnostic_result()` tool to `adk/diagnostic_tools.py` for persisting diagnostic results to diagnostic_results table
- [ ] T026 [US2] Write instruction for DiagnosticAgent in `adk/agent.py` to: check prerequisites, identify gaps, classify learner level, save results, output recommendation (proceed/remediate/skip_ahead)
- [ ] T027 [US2] Add diagnostic tools list to DiagnosticAgent definition in `adk/agent.py`: get_prerequisites, check_prerequisites_mastery, classify_learner_level, save_diagnostic_result
- [ ] T028 [US2] Configure DiagnosticAgent output_key="diagnostic_result" in `adk/agent.py` for state sharing with subsequent agents

**Checkpoint**: User Story 2 complete - diagnostic assessment runs before new topics

---

## Phase 5: User Story 3 - Constructive Feedback After Quizzes (Priority: P2)

**Goal**: Feedback agent analyzes quiz performance and identifies error patterns for constructive feedback

**Independent Test**: Complete a quiz and verify detailed feedback beyond correct/incorrect

### Implementation for User Story 3

- [ ] T029 [P] [US3] Implement `analyze_error_patterns(quiz_responses, quiz_questions)` tool in `adk/quiz_tools.py` identifying conceptual/procedural/careless patterns
- [ ] T030 [P] [US3] Implement `generate_feedback_text(quiz_score, error_patterns, improvement_areas)` tool in `adk/quiz_tools.py` creating human-friendly feedback
- [ ] T031 [US3] Write instruction for FeedbackAgent in `adk/agent.py` to: read quiz state, analyze error patterns, identify improvement areas, update mastery, generate constructive feedback
- [ ] T032 [US3] Add feedback tools list to FeedbackAgent definition in `adk/agent.py`: analyze_error_patterns, generate_feedback_text, update_mastery, add_knowledge_gap
- [ ] T033 [US3] Configure FeedbackAgent output_key="feedback_result" in `adk/agent.py` for state sharing
- [ ] T034 [US3] Add ErrorPattern dataclass to `adk/quiz_tools.py` with fields: pattern_type, description, affected_questions, suggested_remediation

**Checkpoint**: User Story 3 complete - detailed feedback provided after quizzes

---

## Phase 6: User Story 4 - Learning Cycle Orchestration (Priority: P2)

**Goal**: System orchestrates Tutor -> Quiz -> Feedback sequence, repeating until mastery achieved (85%)

**Independent Test**: Start a learning session and verify automatic cycling through teach-quiz-feedback phases

### Implementation for User Story 4

- [ ] T035 [US4] Create `LearningSequence` SequentialAgent in `adk/orchestration.py` with sub_agents=[TutorAgent, QuizAgent, FeedbackAgent]
- [ ] T036 [US4] Create `MasteryChecker` BaseAgent in `adk/orchestration.py` that checks mastery_score vs mastery_threshold and yields Event with escalate=True when mastery achieved
- [ ] T037 [US4] Create `MasteryLoop` LoopAgent in `adk/orchestration.py` with sub_agents=[LearningSequence, MasteryChecker] and max_iterations=5
- [ ] T038 [US4] Implement `start_learning_cycle` tool in `adk/orchestration.py` to initialize cycle in learning_cycles table
- [ ] T039 [US4] Implement `complete_learning_cycle` tool in `adk/orchestration.py` to record cycle completion with score and mastery status
- [ ] T040 [US4] Add learning cycle state keys to session state in `adk/orchestration.py`: mastery_score, mastery_threshold (default 0.85), learning_cycle_count
- [ ] T041 [US4] Add TutorAgent tools in `adk/agent.py`: fetch_info (existing), preload_memory (existing)
- [ ] T042 [US4] Write instruction for TutorAgent in `adk/agent.py` to: read diagnostic results, adapt explanation to learner_level, provide examples, set explanation in state
- [ ] T043 [US4] Configure TutorAgent output_key="explanation" in `adk/agent.py`
- [ ] T044 [US4] Add QuizAgent tools in `adk/agent.py`: prepare_quiz, get_quiz_step, advance_quiz, get_quiz_source (existing)
- [ ] T045 [US4] Write instruction for QuizAgent in `adk/agent.py` to: generate questions based on explanation, evaluate answers, track score in state
- [ ] T046 [US4] Update CoordinatorAgent in `adk/agent.py` to include MasteryLoop as a sub_agent for topic learning requests

**Checkpoint**: User Story 4 complete - learning cycles run automatically until mastery

---

## Phase 7: User Story 5 - Adaptive Learning Path Updates (Priority: P3)

**Goal**: PathPlanner agent recommends optimal next topics based on progress, goals, and prerequisites

**Independent Test**: Complete several topics and verify contextually appropriate recommendations

### Implementation for User Story 5

- [ ] T047 [P] [US5] Implement `get_recommended_path(user_id, goal, max_topics)` tool in `adk/path_tools.py` generating ordered topic list with reasons
- [ ] T048 [P] [US5] Implement `get_next_topic(user_id)` tool in `adk/path_tools.py` returning single best next topic with alternatives
- [ ] T049 [US5] Write instruction for PathPlannerAgent in `adk/agent.py` to: consider mastery levels, time spent, learner goals, prerequisites; recommend optimal path
- [ ] T050 [US5] Add path tools list to PathPlannerAgent definition in `adk/agent.py`: get_recommended_path, get_next_topic, get_weak_concepts, get_learning_stats, get_relationships
- [ ] T051 [US5] Configure PathPlannerAgent output_key="learning_path" in `adk/agent.py` for state sharing
- [ ] T052 [US5] Add goal tracking to session state in `adk/path_tools.py`: goals list, learning_path list

**Checkpoint**: User Story 5 complete - adaptive learning paths generated based on progress

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final integration, cleanup, and validation

- [ ] T053 [P] Remove deprecated 3-agent definitions (tutor_agent, curriculum_planner_agent, assessor_agent) from `adk/agent.py` after verifying new agents work
- [ ] T054 [P] Add type hints to all new functions in `adk/diagnostic_tools.py`, `adk/path_tools.py`, `adk/orchestration.py`
- [ ] T055 [P] Add docstrings to all new agent definitions in `adk/agent.py`
- [ ] T056 Update CLAUDE.md with new agent architecture and tools documentation
- [ ] T057 Run quickstart.md validation scenarios to verify all interactions work
- [ ] T058 Verify agent transition logging captures all routing decisions (FR-013)
- [ ] T059 Verify SC-006: Agent transitions occur within 2 seconds using LoggingPlugin timing

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Phase 2 completion
- **User Story 2 (Phase 4)**: Depends on Phase 2 completion, benefits from US1 routing
- **User Story 3 (Phase 5)**: Depends on Phase 2 completion
- **User Story 4 (Phase 6)**: Depends on US1, US2, US3 (uses all specialist agents)
- **User Story 5 (Phase 7)**: Depends on Phase 2 completion
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Foundation only - implements routing infrastructure
- **User Story 2 (P1)**: Foundation only - can run parallel with US1
- **User Story 3 (P2)**: Foundation only - can run parallel with US1/US2
- **User Story 4 (P2)**: Depends on US1 (routing), US2 (diagnostic integration), US3 (feedback integration)
- **User Story 5 (P3)**: Foundation only - can run parallel with US1/US2/US3

### Within Each User Story

- Models/dataclasses before tools
- Tools before agent definitions
- Agent definitions before instructions
- Instructions before sub_agent wiring

### Parallel Opportunities

**Phase 1** (all in parallel):
- T001, T002, T003

**Phase 2** (must be sequential for DB schema):
- T004 → T005 → T006 → T007 → T008 → T009 → T010

**Phase 3 - US1** (T011-T015 in parallel, then sequential):
- T011, T012, T013, T014, T015 (all agent definitions)
- T016 (coordinator with sub_agents) → T017 (routing instruction)
- T018, T019 (transition tools)
- T020 (pause/resume) → T021 (run_dev update)

**Phase 4 - US2** (T022-T024 in parallel, then sequential):
- T022, T023, T024 (diagnostic tools)
- T025 (save tool) → T026 (instruction) → T027 (tools list) → T028 (output_key)

**Phase 5 - US3** (T029-T030 in parallel, then sequential):
- T029, T030 (feedback tools)
- T031 (instruction) → T032 (tools list) → T033 (output_key) → T034 (dataclass)

**Phase 6 - US4** (mostly sequential - orchestration patterns depend on each other):
- T035 → T036 → T037 (SequentialAgent → MasteryChecker → LoopAgent)
- T038, T039 (cycle tools)
- T040 (state keys) → T041-T045 (agent configurations)
- T046 (final integration)

**Phase 7 - US5** (T047-T048 in parallel, then sequential):
- T047, T048 (path tools)
- T049 → T050 → T051 → T052

**Phase 8** (T053-T055 in parallel, then sequential):
- T053, T054, T055 (cleanup tasks)
- T056 → T057 → T058 → T059 (validation)

---

## Parallel Example: User Story 1

```bash
# Launch all agent definitions together:
Task: "Define DiagnosticAgent LlmAgent in adk/agent.py"
Task: "Define TutorAgent LlmAgent in adk/agent.py"
Task: "Define QuizAgent LlmAgent in adk/agent.py"
Task: "Define FeedbackAgent LlmAgent in adk/agent.py"
Task: "Define PathPlannerAgent LlmAgent in adk/agent.py"

# Then create coordinator with all sub_agents:
Task: "Create CoordinatorAgent with sub_agents list"
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Routing)
4. Complete Phase 4: User Story 2 (Diagnostic)
5. **STOP and VALIDATE**: Test routing and diagnostic independently
6. Deploy/demo if ready - learners can ask questions, get diagnoses, but no automated cycles yet

### Incremental Delivery

1. Complete Setup + Foundational -> Foundation ready
2. Add US1 + US2 -> Test routing and diagnosis -> Deploy (MVP!)
3. Add US3 -> Test feedback after quizzes -> Deploy
4. Add US4 -> Test learning cycles -> Deploy (Full learning loop!)
5. Add US5 -> Test path recommendations -> Deploy (Complete system)
6. Each story adds value without breaking previous stories

### Recommended Order for Single Developer

1. Phase 1 (Setup): ~15 min
2. Phase 2 (Foundational): ~30 min
3. Phase 3 (US1 - Routing): ~45 min
4. Phase 4 (US2 - Diagnostic): ~30 min
5. Phase 5 (US3 - Feedback): ~30 min
6. Phase 6 (US4 - Learning Cycle): ~60 min (largest, most complex)
7. Phase 7 (US5 - PathPlanner): ~30 min
8. Phase 8 (Polish): ~30 min

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each phase completion
- Stop at any checkpoint to validate story independently
- Database migrations are additive (no destructive changes per data-model.md)
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
