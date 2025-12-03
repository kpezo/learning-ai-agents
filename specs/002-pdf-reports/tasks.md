# Tasks: PDF Report Generator

**Input**: Design documents from `/specs/002-pdf-reports/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Not explicitly requested in specification - omitting test-first tasks.

**Organization**: Tasks grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, etc.)
- All paths are relative to repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency setup

- [ ] T001 Create `adk/reports/` package directory structure per plan.md
- [ ] T002 Add ReportLab, svglib, matplotlib dependencies to `adk/requirements.txt`
- [ ] T003 [P] Create `adk/reports/__init__.py` with public API exports
- [ ] T004 [P] Create data models in `adk/reports/models.py` (ReportConfig, DateRange, MasterySummary, ConceptBreakdown, LearningAnalytics, Recommendation enums)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure required before ANY user story can begin

- [ ] T005 Implement `DataCollector` class in `adk/reports/data_collector.py` with `collect_data(user_id, date_range)` method reading from StorageService
- [ ] T006 Implement quiz prerequisite check in `adk/reports/data_collector.py` (FR-009: require at least 1 completed quiz)
- [ ] T007 Implement active session exclusion in `adk/reports/data_collector.py` (FR-010: exclude incomplete quiz sessions)
- [ ] T008 [P] Create PDF document template in `adk/reports/templates.py` with header/footer callbacks
- [ ] T009 [P] Create base `ReportGenerator` class in `adk/reports/generator.py` with `generate_report(config) -> GenerateReportResult`

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Generate Progress Report on Demand (Priority: P1)

**Goal**: Generate a basic PDF with executive summary when user requests a progress report

**Independent Test**: Complete one quiz, request report, verify PDF contains mastery summary

### Implementation for User Story 1

- [ ] T010 [US1] Implement `MasterySummary` calculation in `adk/reports/data_collector.py` (overall_mastery_pct, total_quizzes, total_time_minutes, concepts_covered)
- [ ] T011 [US1] Implement `render_executive_summary()` in `adk/reports/templates.py` using ReportLab Platypus (FR-002)
- [ ] T012 [US1] Wire summary rendering into `ReportGenerator.generate_report()` in `adk/reports/generator.py`
- [ ] T013 [US1] Implement error handling for no-quiz-data case in `adk/reports/generator.py` returning ReportError(NO_QUIZ_DATA)
- [ ] T014 [US1] Add report file saving logic with path `data/reports/{user_id}_{timestamp}.pdf` in `adk/reports/generator.py`
- [ ] T015 [US1] Add `generate_report` tool function in `adk/report_tools.py` for ADK agent integration

**Checkpoint**: User Story 1 complete - basic report generation works

---

## Phase 4: User Story 2 - Concept Mastery Breakdown (Priority: P1)

**Goal**: Add detailed concept mastery breakdown section with tier grouping and trend indicators

**Independent Test**: Complete quizzes on multiple concepts, verify PDF shows each concept with mastery level and trend

### Implementation for User Story 2

- [ ] T016 [US2] Implement `ConceptBreakdown` list generation in `adk/reports/data_collector.py` with mastery tier assignment
- [ ] T017 [US2] Implement trend calculation in `adk/reports/data_collector.py` (compare mastery over last 7 days: improving/stable/declining)
- [ ] T018 [US2] Implement `render_mastery_breakdown()` in `adk/reports/templates.py` with tier-grouped tables (FR-003, FR-004)
- [ ] T019 [US2] Add visual progress bars (text-based: filled/empty blocks) for mastery levels in `adk/reports/templates.py`
- [ ] T020 [US2] Add trend indicators (arrows) to mastery table in `adk/reports/templates.py`
- [ ] T021 [US2] Wire mastery breakdown into report generation flow in `adk/reports/generator.py`

**Checkpoint**: User Story 2 complete - concept breakdown with tiers and trends works

---

## Phase 5: User Story 3 - Learning Analytics Visualization (Priority: P2)

**Goal**: Add visual charts showing score progression, difficulty trends, and time distribution

**Independent Test**: Complete quizzes over multiple days, verify PDF contains readable charts

### Implementation for User Story 3

- [ ] T022 [US3] Implement `LearningAnalytics` data collection in `adk/reports/data_collector.py` (score_progression, difficulty_changes, time_per_topic)
- [ ] T023 [P] [US3] Create `adk/reports/charts.py` with grayscale matplotlib styling (plt.style.use('grayscale'))
- [ ] T024 [US3] Implement `render_score_progression_chart()` in `adk/reports/charts.py` using line styles and markers for differentiation (FR-005)
- [ ] T025 [US3] Implement `render_difficulty_trend_chart()` in `adk/reports/charts.py` (FR-006)
- [ ] T026 [US3] Implement `render_time_distribution_chart()` in `adk/reports/charts.py` as pie/bar chart (FR-007)
- [ ] T027 [US3] Implement SVG-to-PDF embedding using svglib in `adk/reports/charts.py`
- [ ] T028 [US3] Wire analytics charts into report generation flow in `adk/reports/generator.py`

**Checkpoint**: User Story 3 complete - visualizations render in PDF

---

## Phase 6: User Story 4 - Personalized Recommendations (Priority: P2)

**Goal**: Generate personalized learning recommendations based on performance patterns

**Independent Test**: Complete quizzes with varying mastery levels, verify recommendations target weak concepts

### Implementation for User Story 4

- [ ] T029 [P] [US4] Create `adk/reports/recommendations.py` with `RecommendationEngine` class
- [ ] T030 [US4] Implement review recommendation logic: identify concepts below 50% mastery in `adk/reports/recommendations.py`
- [ ] T031 [US4] Implement practice recommendation logic: identify concepts with declining trends in `adk/reports/recommendations.py`
- [ ] T032 [US4] Implement advance recommendation logic: suggest new content when all concepts above 85% in `adk/reports/recommendations.py`
- [ ] T033 [US4] Implement priority ordering (1-3) for recommendations in `adk/reports/recommendations.py`
- [ ] T034 [US4] Implement `render_recommendations()` in `adk/reports/templates.py` with prioritized list (FR-008)
- [ ] T035 [US4] Wire recommendations into report generation flow in `adk/reports/generator.py`

**Checkpoint**: User Story 4 complete - recommendations appear in report

---

## Phase 7: User Story 5 - Shareable and Printable Format (Priority: P3)

**Goal**: Ensure PDF is well-formatted for both digital viewing and physical printing

**Independent Test**: Open PDF in viewer and print - verify layout integrity and grayscale readability

### Implementation for User Story 5

- [ ] T036 [US5] Add A4/LETTER page size support to document template in `adk/reports/templates.py` (FR-011)
- [ ] T037 [US5] Implement `KeepTogether` wrapping for sections to prevent mid-section page breaks in `adk/reports/templates.py` (FR-012)
- [ ] T038 [US5] Configure accessible fonts (Helvetica, minimum 10pt) in `adk/reports/templates.py` (FR-013)
- [ ] T039 [US5] Validate grayscale chart compatibility - ensure all series distinguishable in `adk/reports/charts.py` (FR-014)
- [ ] T040 [US5] Add page numbering to footer in `adk/reports/templates.py`

**Checkpoint**: User Story 5 complete - PDF prints correctly

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Performance optimization, persistence, and final integration

- [ ] T041 [P] Implement report metadata persistence in `adk/storage.py` (add generated_reports table) (FR-015)
- [ ] T042 Add `preview_report(config) -> ProgressReport` function in `adk/reports/generator.py` for data preview without PDF
- [ ] T043 Add performance optimization: disable ReportLab shape checking in production in `adk/reports/generator.py`
- [ ] T044 Add date range default (last 30 days) and validation in `adk/reports/data_collector.py`
- [ ] T045 Add edge case handling: limited data message when only 1 quiz in `adk/reports/templates.py`
- [ ] T046 Run quickstart.md validation - test CLI and Python API usage examples

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Phase 2 completion
  - US1 and US2 are both P1 - can proceed in parallel if staffed
  - US3 depends on US1 (needs base report structure)
  - US4 depends on US1 (needs base report structure)
  - US5 can proceed in parallel with US3/US4
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

| Story | Depends On | Can Run With |
|-------|------------|--------------|
| US1 (P1) | Phase 2 | US2 |
| US2 (P1) | Phase 2 | US1 |
| US3 (P2) | US1 | US4, US5 |
| US4 (P2) | US1 | US3, US5 |
| US5 (P3) | US1 | US3, US4 |

### Within Each User Story

- Data collection before templates
- Templates before generator integration
- Core implementation before edge cases

### Parallel Opportunities

Within Phase 1:
- T003 and T004 can run in parallel (different files)

Within Phase 2:
- T008 and T009 can run in parallel (templates vs generator)

Within Phase 5 (US3):
- T023 can start immediately (new file, no dependencies)

Within Phase 6 (US4):
- T029 can start immediately (new file)

Within Phase 8:
- T041 can run in parallel with other polish tasks

---

## Parallel Example: Phase 1 Setup

```bash
# After T001-T002 complete, launch in parallel:
Task: "T003 - Create adk/reports/__init__.py with public API exports"
Task: "T004 - Create data models in adk/reports/models.py"
```

## Parallel Example: User Story 3

```bash
# T023 can start immediately (new charts.py file):
Task: "T023 - Create adk/reports/charts.py with grayscale matplotlib styling"

# While T022 progresses (data_collector changes):
Task: "T022 - Implement LearningAnalytics data collection"
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1 (basic report)
4. Complete Phase 4: User Story 2 (mastery breakdown)
5. **STOP and VALIDATE**: Test report generation with real data
6. Deploy/demo if ready

### Incremental Delivery

1. Setup + Foundational ’ Foundation ready
2. Add US1 ’ Test ’ Basic MVP with executive summary
3. Add US2 ’ Test ’ Full P1 scope with concept breakdown
4. Add US3 ’ Test ’ Visual analytics
5. Add US4 ’ Test ’ Recommendations
6. Add US5 ’ Test ’ Print-ready quality
7. Polish ’ Production-ready

---

## Notes

- All paths relative to repository root
- [P] tasks = different files, no dependencies within phase
- [Story] label maps task to user story for traceability
- Commit after each task or logical group
- Each user story checkpoint is a deployable increment
