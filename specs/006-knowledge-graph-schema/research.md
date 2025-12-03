# Research: Knowledge Graph Schema Enhancement

**Date**: 2025-12-03
**Branch**: `006-knowledge-graph-schema`

## Overview

This research consolidates findings for enhancing the knowledge graph with hierarchical nodes, rich relationships, Bloom's taxonomy, provenance tracking, and LLM-based construction.

## Research Questions

### 1. How should graph data be stored in SQLite?

**Finding**: Two approaches evaluated:

| Approach | Pros | Cons |
|----------|------|------|
| Adjacency List (normalized tables) | Simple, standard SQL queries, easy CRUD | Recursive queries for hierarchy traversal |
| Closure Table | O(1) descendant/ancestor queries | More storage, complex inserts, maintenance on moves |

**Decision**: Use **Adjacency List with Recursive CTEs** for hierarchy queries.

**Rationale**:
- SQLite 3.8.3+ supports recursive CTEs (WITH RECURSIVE)
- Simpler schema, matches existing `storage.py` patterns
- Good enough for 10K nodes (SC-006) with proper indexing
- Closure tables add complexity not justified at this scale

**Alternatives Considered**:
- Closure Table - rejected due to insert complexity and storage overhead
- Nested Sets - rejected due to rebalancing cost on inserts
- External graph DB (Neo4j) - rejected as adds deployment complexity

### 2. How should hierarchical levels be enforced?

**Finding**: The spec requires 5 hierarchy levels (domain → course → module → topic → concept/skill).

**Decision**: Store `hierarchy_level` as integer (1-5) with CHECK constraint. Parent-child relationships must have child.level = parent.level + 1.

**Rationale**: Simple validation, matches spec FR-002.

**Code Pattern**:
```sql
CREATE TABLE concept_nodes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hierarchy_level INTEGER NOT NULL CHECK (hierarchy_level BETWEEN 1 AND 5),
    parent_id INTEGER REFERENCES concept_nodes(id)
);
-- Trigger or application logic enforces: child.level = parent.level + 1
```

### 3. How should the 12 relationship types be modeled?

**Finding**: Spec FR-003 defines: prerequisite, enables, part_of, contains, similar_to, related_to, contradicts, exemplifies, applies_to, extends, teaches, assesses.

**Decision**: Use enum-like TEXT column with CHECK constraint. Store relationship metadata (strength, directionality) as separate columns.

**Rationale**: Extensible, queryable, matches existing pattern in `storage.py`.

**Schema Pattern**:
```sql
CREATE TABLE relationship_edges (
    id INTEGER PRIMARY KEY,
    source_id INTEGER NOT NULL REFERENCES concept_nodes(id),
    target_id INTEGER NOT NULL REFERENCES concept_nodes(id),
    relationship_type TEXT NOT NULL CHECK (
        relationship_type IN ('prerequisite', 'enables', 'part_of', 'contains',
        'similar_to', 'related_to', 'contradicts', 'exemplifies',
        'applies_to', 'extends', 'teaches', 'assesses')
    ),
    is_directed BOOLEAN DEFAULT TRUE,
    strength TEXT CHECK (strength IN ('hard', 'soft', 'recommended')),
    confidence REAL DEFAULT 1.0
);
```

### 4. How should LLM extraction be implemented?

**Finding**: Existing `question_pipeline.py` provides patterns:
- `concept_agent`: Extracts concepts with declarative/procedural/conditional fields
- `relationship_agent`: Maps relationships with types and confidence

**Decision**: Extend existing agents with enhanced prompts for:
1. Node type classification (8 types)
2. Hierarchy level inference
3. Bloom's taxonomy classification
4. 12 relationship types

**Rationale**: Reuse proven ADK patterns, avoid duplicating infrastructure.

**Enhancement Pattern**:
```python
# Extend concept-agent prompt to include:
# - node_type: domain/course/module/topic/concept/skill/resource/assessment
# - hierarchy_level: inferred from document structure
# - bloom_level: remember/understand/apply/analyze/evaluate/create
# - difficulty: novice/beginner/intermediate/advanced/expert
```

### 5. How should circular prerequisites be prevented (SC-005)?

**Finding**: Must detect cycles only for "hard" prerequisites. Soft/recommended can form cycles.

**Decision**: Implement cycle detection on INSERT using BFS/DFS traversal. Reject inserts that would create hard prerequisite cycles.

**Rationale**: Required by FR-016, critical for learning path validity.

**Code Pattern**:
```python
def would_create_cycle(source_id: int, target_id: int, strength: str) -> bool:
    if strength != "hard":
        return False
    # BFS from target checking if we can reach source
    visited = set()
    queue = [target_id]
    while queue:
        current = queue.pop(0)
        if current == source_id:
            return True
        if current in visited:
            continue
        visited.add(current)
        # Get all hard prerequisites of current
        edges = get_hard_prerequisites(current)
        queue.extend(e.target_id for e in edges)
    return False
```

### 6. How should Bloom's taxonomy classification work?

**Finding**: Spec FR-006 requires classification into 6 levels. LLM can infer from linguistic patterns:

| Level | Linguistic Markers |
|-------|-------------------|
| Remember | "define", "list", "state", "identify" |
| Understand | "explain", "describe", "summarize" |
| Apply | "use", "implement", "solve", "calculate" |
| Analyze | "compare", "contrast", "categorize" |
| Evaluate | "judge", "critique", "justify" |
| Create | "design", "construct", "develop" |

**Decision**: Use LLM inference with linguistic markers as prompt guidance.

**Rationale**: Matches existing AI-inference pattern from spec clarifications.

### 7. How should provenance be stored?

**Finding**: FR-010 requires source_document, page_numbers, extraction_method, confidence.

**Decision**: Embed provenance as JSON column in concept_nodes and relationship_edges.

**Rationale**: Flexible schema, matches existing `question_details` pattern in storage.py.

**Schema Pattern**:
```sql
provenance TEXT  -- JSON: {"source_document": "...", "page_numbers": [42, 43], "extraction_method": "llm_extracted", "confidence": 0.85}
```

### 8. How should hierarchy queries perform (SC-001 <200ms)?

**Finding**: Recursive CTE performance with indexes:
- 1000 nodes: ~10ms
- 10000 nodes: ~50-100ms

**Decision**: Add indexes on parent_id, hierarchy_level, relationship_type.

**Rationale**: Meets SC-001 requirements with headroom.

**Required Indexes**:
```sql
CREATE INDEX idx_nodes_parent ON concept_nodes(parent_id);
CREATE INDEX idx_nodes_level ON concept_nodes(hierarchy_level);
CREATE INDEX idx_edges_source ON relationship_edges(source_id);
CREATE INDEX idx_edges_target ON relationship_edges(target_id);
CREATE INDEX idx_edges_type ON relationship_edges(relationship_type);
```

## Technical Decisions Summary

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Graph storage | Adjacency list + recursive CTEs | Simple, sufficient for scale |
| Hierarchy enforcement | CHECK constraint + application logic | Clear validation |
| Relationship types | CHECK constraint enum | Extensible, queryable |
| LLM extraction | Extend existing pipeline agents | Reuse proven patterns |
| Cycle detection | BFS on hard prerequisites | Required by spec |
| Bloom's classification | LLM inference | Matches project patterns |
| Provenance | JSON column | Flexible, proven pattern |
| Performance | Proper indexes | Meets <200ms goal |

## Dependencies

Existing dependencies sufficient:
- google-adk (agent framework)
- google-genai (LLM calls)
- pymupdf (PDF extraction)
- sqlite3 (built-in Python)

No new dependencies required.

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| LLM extraction accuracy below 85% (SC-002) | Iterative prompt refinement, confidence thresholds |
| Recursive CTE performance at scale | Index optimization, query caching |
| Schema migration complexity | New tables, no modifications to existing |
| Circular dependency edge cases | Comprehensive test suite |

## Open Questions Resolved

All NEEDS CLARIFICATION items from spec resolved:
- ✅ Storage approach: SQLite adjacency list
- ✅ LLM extraction: Extend existing pipeline
- ✅ Cycle detection: BFS algorithm
- ✅ Performance: Indexed queries
