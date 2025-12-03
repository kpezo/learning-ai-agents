# Feature Specification: Knowledge Graph Schema Enhancement

**Feature Branch**: `006-knowledge-graph-schema`
**Created**: 2025-12-03
**Status**: Draft
**Input**: User description: "Enhance knowledge graph with hierarchical concept nodes, 12 relationship types, Bloom's taxonomy levels, provenance tracking, and LLM-based graph construction from educational PDFs"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Hierarchical Concept Organization (Priority: P1)

An educator uploads educational content (PDF), and the system automatically extracts concepts organized into a three-level hierarchy: domains/chapters at level 1, topics/sections at level 2, and concepts/keywords at level 3. This structure enables learners to navigate from broad topics to specific concepts.

**Why this priority**: This is the foundation of the knowledge graph - without hierarchical organization, concepts are flat and unnavigable, making adaptive learning paths impossible to construct.

**Independent Test**: Can be fully tested by processing a PDF and verifying the extracted concepts are organized into the correct hierarchy levels with parent-child relationships.

**Acceptance Scenarios**:

1. **Given** an educational PDF on "Machine Learning," **When** the system processes it, **Then** it creates hierarchy: "Machine Learning" (level 1) → "Supervised Learning" (level 2) → "Linear Regression" (level 3).

2. **Given** a concept at level 3, **When** querying its parents, **Then** the system returns its level 2 topic and level 1 domain.

3. **Given** a domain at level 1, **When** querying its descendants, **Then** the system returns all topics and concepts within that domain.

---

### User Story 2 - Rich Relationship Types (Priority: P1)

Concepts are connected through semantically meaningful relationships that capture educational dependencies. The system supports 12 relationship types including prerequisites, enables, part_of, similar_to, contradicts, exemplifies, and assesses.

**Why this priority**: Equally critical - relationships enable learning path generation, prerequisite checking, and identifying conceptually similar (and potentially confusable) topics.

**Independent Test**: Can be tested by querying relationships between concepts and verifying the correct relationship type and direction is returned.

**Acceptance Scenarios**:

1. **Given** concepts "Algebra" and "Calculus," **When** querying their relationship, **Then** the system returns "prerequisite" with Algebra as the source.

2. **Given** a concept "Gradient Descent," **When** querying for similar concepts, **Then** the system returns related optimization methods with "similar_to" relationships.

3. **Given** a concept "Derivative," **When** querying for examples, **Then** the system returns concrete instances connected via "exemplifies" relationships.

---

### User Story 3 - Bloom's Taxonomy Classification (Priority: P2)

Each concept is classified by its Bloom's taxonomy level (remember, understand, apply, analyze, evaluate, create), enabling the system to generate questions at appropriate cognitive levels.

**Why this priority**: Enhances question generation quality by aligning questions with cognitive complexity, but basic quiz functionality works without this classification.

**Independent Test**: Can be tested by retrieving a concept and verifying its Bloom's level is set, then generating questions that match that level.

**Acceptance Scenarios**:

1. **Given** a factual concept like "Definition of a derivative," **When** extracted, **Then** it is classified as "remember" level.

2. **Given** a procedural concept like "Solving quadratic equations," **When** extracted, **Then** it is classified as "apply" level.

3. **Given** a concept classified at "analyze" level, **When** generating a question, **Then** the question requires comparison or categorization.

---

### User Story 4 - Provenance Tracking (Priority: P2)

Each concept and relationship includes provenance metadata showing where it came from: source document, page numbers, extraction method (manual, LLM, rule-based), and confidence score.

**Why this priority**: Important for verification and debugging but not essential for core graph functionality.

**Independent Test**: Can be tested by querying a concept's provenance and verifying source document and extraction details are returned.

**Acceptance Scenarios**:

1. **Given** a concept extracted from page 42 of "Intro.pdf," **When** querying its provenance, **Then** the system returns source_document, page_numbers, and extraction_method.

2. **Given** LLM-extracted relationships, **When** viewing provenance, **Then** confidence scores are included (0.0-1.0).

3. **Given** manually added concepts, **When** viewing provenance, **Then** extraction_method shows "manual" with confidence 1.0.

---

### User Story 5 - LLM-Based Graph Construction (Priority: P2)

The system uses LLM prompts to automatically extract concepts and relationships from educational PDFs, reducing manual curation effort while maintaining educational accuracy.

**Why this priority**: Automation is valuable but manual graph construction can work initially. LLM extraction accelerates content onboarding.

**Independent Test**: Can be tested by processing a new PDF and verifying extracted concepts match expected content.

**Acceptance Scenarios**:

1. **Given** an educational PDF, **When** processed through LLM extraction, **Then** concepts are extracted with names, types, and difficulty levels.

2. **Given** extracted text chunks, **When** relationship extraction runs, **Then** prerequisite and part_of relationships are identified between concepts.

3. **Given** ambiguous content, **When** extraction confidence is below 0.7, **Then** the concept is flagged for manual review.

---

### Edge Cases

- What happens when a concept appears in multiple documents? System merges metadata and tracks all sources in provenance.
- How does the system handle circular prerequisites? Validation prevents circular prerequisite chains during insertion.
- What happens when LLM extraction fails? System falls back to rule-based extraction and logs the failure for investigation.
- How does the system handle conflicting relationship types (e.g., both prerequisite and contradicts)? Both relationships are stored; queries return all relationships with types.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST support 8 node types: domain, course, module, topic, concept, skill, resource, and assessment.

- **FR-002**: System MUST enforce hierarchy levels (1-5) for organizing concepts from broad to specific.

- **FR-003**: System MUST support 12 relationship types: prerequisite, enables, part_of, contains, similar_to, related_to, contradicts, exemplifies, applies_to, extends, teaches, and assesses.

- **FR-004**: System MUST store relationship directionality (is_directed flag) for asymmetric relationships like prerequisite.

- **FR-005**: System MUST store prerequisite strength as "hard," "soft," or "recommended."

- **FR-006**: System MUST classify concepts by Bloom's taxonomy level (remember, understand, apply, analyze, evaluate, create).

- **FR-007**: System MUST store difficulty level for each concept (novice, beginner, intermediate, advanced, expert).

- **FR-008**: System MUST store estimated learning time (in minutes) for each concept.

- **FR-009**: System MUST store importance weight (0.0-1.0) for prioritizing concepts in learning paths.

- **FR-010**: System MUST track provenance for each node: source document, page numbers, extraction method, and confidence score.

- **FR-011**: System MUST support querying all descendants of a concept (children, grandchildren, etc.).

- **FR-012**: System MUST support querying all ancestors of a concept (parents, grandparents, etc.).

- **FR-013**: System MUST support querying concepts by relationship type (e.g., all prerequisites of concept X).

- **FR-014**: System MUST provide LLM-based extraction from PDF documents using structured prompts.

- **FR-015**: System MUST store concept aliases (alternative names) for flexible querying.

- **FR-016**: System MUST validate relationship consistency (no circular hard prerequisites).

### Key Entities

- **ConceptNode**: A node in the knowledge graph with id, name, node_type (domain/topic/concept/etc.), hierarchy_level, description, aliases, difficulty, bloom_taxonomy_level, estimated_learning_time, importance_weight, and provenance.

- **RelationshipEdge**: A connection between nodes with id, source_id, target_id, relationship_type, is_directed, strength, prerequisite_type (for prerequisites), evidence_text, and confidence.

- **Provenance**: Metadata tracking origin of extracted data including source_document, page_numbers, extraction_method (manual/llm_extracted/rule_based), and confidence_score.

- **ExtractionPrompt**: The structured prompt used for LLM-based concept and relationship extraction.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Concept hierarchy queries return results in under 200ms for graphs with up to 1000 nodes.

- **SC-002**: LLM-based extraction achieves 85% accuracy for concept identification (validated against manual annotation).

- **SC-003**: Relationship extraction achieves 75% accuracy for prerequisite relationships.

- **SC-004**: 100% of concepts have a valid Bloom's taxonomy classification after extraction.

- **SC-005**: Zero circular hard prerequisites exist in the graph (validation prevents insertion).

- **SC-006**: Graph supports at least 10,000 concepts with sub-second query performance.

## Assumptions

- The existing SQLite storage will be extended with graph-optimized tables or a graph database integration.
- LLM extraction uses the Gemini model already configured in the system.
- Extraction prompts are stored as markdown files in the codebase for easy modification.
- Manual review queue for low-confidence extractions is out of scope for this spec (future feature).
- Graph visualization is out of scope; this spec covers data model and query capabilities only.
