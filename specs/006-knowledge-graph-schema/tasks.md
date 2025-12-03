# Tasks: Knowledge Graph Schema Enhancement

**Input**: Design documents from `/specs/006-knowledge-graph-schema/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/
**Branch**: `006-knowledge-graph-schema`

**Tests**: Not explicitly requested in spec - test tasks omitted.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `adk/` at repository root (extending existing structure)
- Tests in `tests/unit/`, `tests/integration/`, `tests/contract/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and graph module structure

- [ ] T001 Create `adk/extraction/__init__.py` package init file
- [ ] T002 [P] Create `adk/graph.py` with module docstring and imports from contracts/graph-service.py
- [ ] T003 [P] Create `adk/graph_tools.py` with module docstring and imports from contracts/graph-tools.py
- [ ] T004 [P] Create `adk/extraction/concept_extractor.py` with module docstring
- [ ] T005 [P] Create `adk/extraction/relationship_extractor.py` with module docstring

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core schema and enum definitions that ALL user stories depend on

**CRITICAL**: No user story work can begin until this phase is complete

- [ ] T006 Add enum definitions (NodeType, RelationshipType, Difficulty, BloomLevel, PrerequisiteStrength, ExtractionMethod) to `adk/graph.py` per contracts/graph-service.py lines 18-83
- [ ] T007 Add dataclass definitions (Provenance, ConceptNode, RelationshipEdge, NodeWithChildren, LearningPath) to `adk/graph.py` per contracts/graph-service.py lines 90-153
- [ ] T008 Extend `adk/storage.py` with `concept_nodes` table schema per data-model.md lines 118-145 (CREATE TABLE with CHECK constraints and indexes)
- [ ] T009 Extend `adk/storage.py` with `relationship_edges` table schema per data-model.md lines 155-181 (CREATE TABLE with CHECK constraints and indexes)
- [ ] T010 Add table creation to `StorageService.__init__` in `adk/storage.py` to initialize graph tables on first access
- [ ] T011 Add JSON serialization helpers for Provenance dataclass in `adk/graph.py` (to_json, from_json methods)

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Hierarchical Concept Organization (Priority: P1)

**Goal**: Enable concepts organized into 5-level hierarchy (domain > course > module > topic > concept) with parent-child relationships and recursive traversal

**Independent Test**: Process a PDF and verify extracted concepts are organized into correct hierarchy levels with parent-child relationships

### Implementation for User Story 1

- [ ] T012 [US1] Implement `GraphService.__init__` in `adk/graph.py` initializing db connection and user_id
- [ ] T013 [US1] Implement `GraphService.create_node` in `adk/graph.py` with hierarchy_level validation (child.level = parent.level + 1)
- [ ] T014 [US1] Implement `GraphService.get_node` in `adk/graph.py` returning Optional[ConceptNode]
- [ ] T015 [US1] Implement `GraphService.get_node_by_name` in `adk/graph.py` searching name and aliases
- [ ] T016 [US1] Implement `GraphService.update_node` in `adk/graph.py` with hierarchy constraint validation
- [ ] T017 [US1] Implement `GraphService.delete_node` in `adk/graph.py` (CASCADE handled by FK)
- [ ] T018 [US1] Implement `GraphService.get_children` in `adk/graph.py` querying parent_id
- [ ] T019 [US1] Implement `GraphService.get_descendants` in `adk/graph.py` using recursive CTE per data-model.md lines 186-194
- [ ] T020 [US1] Implement `GraphService.get_ancestors` in `adk/graph.py` using recursive CTE per data-model.md lines 197-205
- [ ] T021 [US1] Implement `GraphService.get_node_with_children` in `adk/graph.py` combining node and children queries
- [ ] T022 [US1] Implement `get_concept` tool function in `adk/graph_tools.py` per contracts/graph-tools.py lines 15-38
- [ ] T023 [US1] Implement `get_descendants` tool function in `adk/graph_tools.py` per contracts/graph-tools.py lines 72-99
- [ ] T024 [US1] Implement `get_ancestors` tool function in `adk/graph_tools.py` per contracts/graph-tools.py lines 102-125
- [ ] T025 [US1] Implement `search_concepts` tool function in `adk/graph_tools.py` per contracts/graph-tools.py lines 196-229
- [ ] T026 [US1] Implement `get_graph_overview` tool function in `adk/graph_tools.py` per contracts/graph-tools.py lines 269-304
- [ ] T027 [US1] Add `GRAPH_TOOLS` list export in `adk/graph_tools.py` with FunctionTool wrappers for US1 tools

**Checkpoint**: User Story 1 complete - hierarchy queries work independently. Can navigate domain > course > module > topic > concept structure.

---

## Phase 4: User Story 2 - Rich Relationship Types (Priority: P1)

**Goal**: Enable 12 semantic relationship types (prerequisite, enables, part_of, contains, similar_to, related_to, contradicts, exemplifies, applies_to, extends, teaches, assesses) with direction and strength

**Independent Test**: Query relationships between concepts and verify correct relationship type, direction, and strength returned

### Implementation for User Story 2

- [ ] T028 [US2] Implement `GraphService.create_relationship` in `adk/graph.py` with duplicate prevention (UNIQUE constraint)
- [ ] T029 [US2] Implement `GraphService.would_create_cycle` in `adk/graph.py` using BFS per research.md lines 109-127 (only for hard prerequisites)
- [ ] T030 [US2] Add cycle check to `create_relationship` in `adk/graph.py` raising ValueError for circular hard prerequisites
- [ ] T031 [US2] Implement `GraphService.get_relationships` in `adk/graph.py` with type and direction filtering
- [ ] T032 [US2] Implement `GraphService.delete_relationship` in `adk/graph.py`
- [ ] T033 [US2] Implement `GraphService.get_prerequisites` in `adk/graph.py` with strength filtering and transitive closure via recursive CTE
- [ ] T034 [US2] Implement `get_prerequisites` tool function in `adk/graph_tools.py` per contracts/graph-tools.py lines 41-69
- [ ] T035 [US2] Implement `get_related_concepts` tool function in `adk/graph_tools.py` per contracts/graph-tools.py lines 127-161
- [ ] T036 [US2] Implement `find_learning_path` tool function in `adk/graph_tools.py` per contracts/graph-tools.py lines 164-193
- [ ] T037 [US2] Implement `GraphService.find_learning_path` in `adk/graph.py` traversing prerequisites in reverse
- [ ] T038 [US2] Update `GRAPH_TOOLS` list in `adk/graph_tools.py` to include US2 tools

**Checkpoint**: User Story 2 complete - relationships work independently. Can query prerequisites, find learning paths, get related concepts.

---

## Phase 5: User Story 3 - Bloom's Taxonomy Classification (Priority: P2)

**Goal**: Classify concepts by Bloom's level (remember, understand, apply, analyze, evaluate, create) for cognitive-appropriate question generation

**Independent Test**: Retrieve concept and verify bloom_level is set, then confirm generated questions match that cognitive level

### Implementation for User Story 3

- [ ] T039 [US3] Implement `classify_bloom_level` method in `adk/extraction/concept_extractor.py` using linguistic markers per research.md lines 129-145
- [ ] T040 [US3] Add bloom_level inference to concept extraction prompt in `adk/extraction/concept_extractor.py`
- [ ] T041 [US3] Implement `GraphService.search_nodes` in `adk/graph.py` with bloom_level filter parameter
- [ ] T042 [US3] Implement `get_concept_details` tool function in `adk/graph_tools.py` per contracts/graph-tools.py lines 232-265 including bloom_level
- [ ] T043 [US3] Update `search_concepts` tool in `adk/graph_tools.py` to support bloom_level filter
- [ ] T044 [US3] Add `GraphService.get_concepts_by_bloom_level` convenience method in `adk/graph.py`

**Checkpoint**: User Story 3 complete - Bloom's classification works independently. Can filter and query concepts by cognitive level.

---

## Phase 6: User Story 4 - Provenance Tracking (Priority: P2)

**Goal**: Track source document, page numbers, extraction method, and confidence for all extracted concepts and relationships

**Independent Test**: Query concept's provenance and verify source_document, page_numbers, extraction_method, and confidence_score returned

### Implementation for User Story 4

- [ ] T045 [US4] Add provenance JSON column handling in `GraphService.create_node` in `adk/graph.py` (serialize Provenance to JSON)
- [ ] T046 [US4] Add provenance deserialization in `GraphService.get_node` in `adk/graph.py` (parse JSON to Provenance)
- [ ] T047 [US4] Add provenance handling in `GraphService.create_relationship` in `adk/graph.py`
- [ ] T048 [US4] Add provenance to extraction output in `adk/extraction/concept_extractor.py` (source_document, page_numbers)
- [ ] T049 [US4] Add confidence_score tracking in `adk/extraction/concept_extractor.py` and `relationship_extractor.py`
- [ ] T050 [US4] Implement low-confidence concept detection in `GraphService.search_nodes` in `adk/graph.py` (min_confidence, max_confidence params)
- [ ] T051 [US4] Update `get_concept_details` tool in `adk/graph_tools.py` to include full provenance object

**Checkpoint**: User Story 4 complete - provenance works independently. Can trace any concept/relationship back to source document.

---

## Phase 7: User Story 5 - LLM-Based Graph Construction (Priority: P2)

**Goal**: Automatically extract concepts and relationships from educational PDFs using Gemini LLM with structured prompts

**Independent Test**: Process new PDF and verify extracted concepts match expected content with names, types, and difficulty levels

### Implementation for User Story 5

- [ ] T052 [US5] Implement `ExtractionService.__init__` in `adk/extraction/concept_extractor.py` with model configuration
- [ ] T053 [US5] Implement `ExtractionService.extract_concepts_from_pdf` in `adk/extraction/concept_extractor.py` using existing rag_setup patterns
- [ ] T054 [US5] Create concept extraction prompt in `adk/extraction/concept_extractor.py` requesting node_type, hierarchy_level, difficulty, bloom_level
- [ ] T055 [US5] Implement `ExtractionService.infer_hierarchy` in `adk/extraction/concept_extractor.py` setting parent_id based on document structure
- [ ] T056 [US5] Implement `ExtractionService.extract_relationships` in `adk/extraction/relationship_extractor.py` for 12 relationship types
- [ ] T057 [US5] Create relationship extraction prompt in `adk/extraction/relationship_extractor.py` with confidence scoring
- [ ] T058 [US5] Add fallback to rule-based extraction when LLM confidence < 0.7 in `adk/extraction/concept_extractor.py`
- [ ] T059 [US5] Add extraction integration function combining concept and relationship extraction in `adk/extraction/__init__.py`
- [ ] T060 [US5] Implement `GraphService.get_graph_stats` in `adk/graph.py` per contracts/graph-service.py lines 410-416

**Checkpoint**: User Story 5 complete - LLM extraction works end-to-end. Can process PDFs and populate graph automatically.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Integration, validation, and performance optimization across all stories

- [ ] T061 [P] Add graph tools to tutor specialist agent in `adk/agent.py` following existing tool integration pattern
- [ ] T062 [P] Add graph tools to curriculum planner agent in `adk/agent.py`
- [ ] T063 Implement `GraphService.validate` in `adk/graph.py` checking hierarchy consistency and circular prerequisites
- [ ] T064 Implement `migrate_concepts` helper function in `adk/graph.py` to migrate from old extracted_concepts table
- [ ] T065 Add performance indexes verification in `adk/storage.py` for <200ms hierarchy queries (SC-001)
- [ ] T066 Run quickstart.md validation scenarios in `specs/006-knowledge-graph-schema/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational (Phase 2)
- **User Story 2 (Phase 4)**: Depends on Foundational (Phase 2) - can run parallel with US1
- **User Story 3 (Phase 5)**: Depends on Foundational (Phase 2) - can run parallel with US1/US2
- **User Story 4 (Phase 6)**: Depends on Foundational (Phase 2) and partial US1 (create_node exists)
- **User Story 5 (Phase 7)**: Depends on Foundational (Phase 2) and partial US4 (provenance exists)
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational - foundation for all graph operations
- **User Story 2 (P1)**: Can start after Foundational - relationship logic is independent
- **User Story 3 (P2)**: Can start after Foundational - extends node attributes
- **User Story 4 (P2)**: Requires US1 create_node to exist for provenance integration
- **User Story 5 (P2)**: Requires US3 bloom_level and US4 provenance for complete extraction

### Within Each User Story

- GraphService methods before tool functions
- Core operations before convenience methods
- Tool functions after service implementation

### Parallel Opportunities

- T002, T003, T004, T005 can run in parallel (different files)
- T061, T062 can run in parallel (different agents)
- After Phase 2: US1, US2, US3 can be worked on in parallel by different developers

---

## Parallel Example: Phase 1 Setup

```bash
# Launch all setup tasks together:
Task: "Create adk/extraction/__init__.py package init file"
Task: "Create adk/graph.py with module docstring and imports"
Task: "Create adk/graph_tools.py with module docstring and imports"
Task: "Create adk/extraction/concept_extractor.py with module docstring"
Task: "Create adk/extraction/relationship_extractor.py with module docstring"
```

---

## Parallel Example: User Stories After Foundation

```bash
# After Phase 2 completes, these user stories can run in parallel:
# Developer A: User Story 1 (T012-T027) - Hierarchy
# Developer B: User Story 2 (T028-T038) - Relationships
# Developer C: User Story 3 (T039-T044) - Bloom's Taxonomy
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 - Hierarchy
4. Complete Phase 4: User Story 2 - Relationships
5. **STOP and VALIDATE**: Test hierarchy and relationship queries independently
6. Deploy/demo if ready - core graph functionality works

### Incremental Delivery

1. Complete Setup + Foundational -> Foundation ready
2. Add User Story 1 -> Test hierarchy queries -> MVP has navigation
3. Add User Story 2 -> Test relationships -> MVP has learning paths
4. Add User Story 3 -> Test Bloom's -> Enhanced question quality
5. Add User Story 4 -> Test provenance -> Full traceability
6. Add User Story 5 -> Test extraction -> Automated content ingestion

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (hierarchy)
   - Developer B: User Story 2 (relationships)
   - Developer C: User Story 3 (Bloom's)
3. US4 and US5 after initial stories complete (have dependencies)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Performance target: <200ms for hierarchy queries (SC-001) with 10,000 concepts (SC-006)
- No circular hard prerequisites allowed (SC-005)
