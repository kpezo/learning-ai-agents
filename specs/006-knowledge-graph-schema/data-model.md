# Data Model: Knowledge Graph Schema Enhancement

**Date**: 2025-12-03
**Branch**: `006-knowledge-graph-schema`

## Overview

This document defines the data model for the enhanced knowledge graph, including SQLite schema, entity definitions, and relationship constraints.

## Entities

### ConceptNode

A node in the knowledge graph representing a domain, course, module, topic, concept, skill, resource, or assessment.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique identifier |
| name | TEXT | NOT NULL | Human-readable name |
| node_type | TEXT | NOT NULL, CHECK in enum | One of: domain, course, module, topic, concept, skill, resource, assessment |
| hierarchy_level | INTEGER | NOT NULL, CHECK 1-5 | Position in hierarchy (1=domain, 5=leaf) |
| parent_id | INTEGER | REFERENCES concept_nodes(id) | Parent node for hierarchy |
| description | TEXT | | Detailed description |
| aliases | TEXT | | JSON array of alternative names |
| difficulty | TEXT | CHECK in enum | novice, beginner, intermediate, advanced, expert |
| bloom_level | TEXT | CHECK in enum | remember, understand, apply, analyze, evaluate, create |
| estimated_time_minutes | INTEGER | | Estimated learning time |
| importance_weight | REAL | CHECK 0.0-1.0 | Priority in learning paths |
| provenance | TEXT | | JSON with source tracking |
| created_at | TEXT | NOT NULL | ISO timestamp |
| updated_at | TEXT | | ISO timestamp |

**Node Type → Hierarchy Level Mapping**:
| Node Type | Typical Level | Description |
|-----------|---------------|-------------|
| domain | 1 | Broad subject area (e.g., "Machine Learning") |
| course | 2 | Full course or major section |
| module | 2-3 | Course module or chapter |
| topic | 3-4 | Specific topic within module |
| concept | 4-5 | Individual concept to learn |
| skill | 4-5 | Practical skill to develop |
| resource | 3-5 | Learning resource (any level) |
| assessment | 3-5 | Quiz, test, or evaluation |

### RelationshipEdge

A directed or undirected connection between two nodes.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique identifier |
| source_id | INTEGER | NOT NULL, FK concept_nodes | Starting node |
| target_id | INTEGER | NOT NULL, FK concept_nodes | Ending node |
| relationship_type | TEXT | NOT NULL, CHECK in enum | Type of relationship |
| is_directed | BOOLEAN | DEFAULT TRUE | Whether edge has direction |
| strength | TEXT | CHECK in enum | hard, soft, recommended (for prerequisites) |
| evidence_text | TEXT | | Supporting text from source |
| confidence | REAL | DEFAULT 1.0, CHECK 0.0-1.0 | Extraction confidence |
| provenance | TEXT | | JSON with source tracking |
| created_at | TEXT | NOT NULL | ISO timestamp |

**Relationship Types**:
| Type | Directed | Description | Example |
|------|----------|-------------|---------|
| prerequisite | Yes | A must be learned before B | "Algebra" → "Calculus" |
| enables | Yes | A makes B possible | "Variables" → "Functions" |
| part_of | Yes | A is a component of B | "Gradient" → "Gradient Descent" |
| contains | Yes | A contains B (inverse of part_of) | "Module" → "Topic" |
| similar_to | No | A and B are conceptually similar | "List" ↔ "Array" |
| related_to | No | A and B are loosely connected | "Python" ↔ "Data Science" |
| contradicts | No | A and B are conflicting | "Overfitting" ↔ "Underfitting" |
| exemplifies | Yes | A is an example of B | "MNIST" → "Dataset" |
| applies_to | Yes | A is applied in context B | "Backpropagation" → "Neural Networks" |
| extends | Yes | A builds upon B | "CNN" → "Neural Network" |
| teaches | Yes | Resource A teaches concept B | "Video1" → "Derivatives" |
| assesses | Yes | Assessment A evaluates concept B | "Quiz1" → "Linear Algebra" |

### Provenance (Embedded JSON)

Metadata tracking the origin of extracted data.

```json
{
  "source_document": "Intro.pdf",
  "page_numbers": [42, 43],
  "extraction_method": "llm_extracted",
  "confidence_score": 0.85,
  "extracted_by": "concept_agent",
  "extracted_at": "2025-12-03T10:30:00Z"
}
```

| Field | Type | Description |
|-------|------|-------------|
| source_document | string | Filename or URI of source |
| page_numbers | array[int] | Pages where content found |
| extraction_method | string | manual, llm_extracted, rule_based |
| confidence_score | float | Extraction confidence (0.0-1.0) |
| extracted_by | string | Agent or process name |
| extracted_at | string | ISO timestamp |

## SQLite Schema

```sql
-- ============================================================
-- Knowledge Graph Tables (extend existing storage.py schema)
-- ============================================================

-- Node types enum values
-- domain, course, module, topic, concept, skill, resource, assessment

-- Difficulty levels
-- novice, beginner, intermediate, advanced, expert

-- Bloom's taxonomy levels
-- remember, understand, apply, analyze, evaluate, create

CREATE TABLE IF NOT EXISTS concept_nodes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    node_type TEXT NOT NULL CHECK (
        node_type IN ('domain', 'course', 'module', 'topic',
                      'concept', 'skill', 'resource', 'assessment')
    ),
    hierarchy_level INTEGER NOT NULL CHECK (hierarchy_level BETWEEN 1 AND 5),
    parent_id INTEGER REFERENCES concept_nodes(id) ON DELETE SET NULL,
    description TEXT,
    aliases TEXT,  -- JSON array
    difficulty TEXT CHECK (
        difficulty IS NULL OR
        difficulty IN ('novice', 'beginner', 'intermediate', 'advanced', 'expert')
    ),
    bloom_level TEXT CHECK (
        bloom_level IS NULL OR
        bloom_level IN ('remember', 'understand', 'apply', 'analyze', 'evaluate', 'create')
    ),
    estimated_time_minutes INTEGER,
    importance_weight REAL CHECK (
        importance_weight IS NULL OR
        (importance_weight >= 0.0 AND importance_weight <= 1.0)
    ),
    provenance TEXT,  -- JSON
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT
);

-- Indexes for concept_nodes
CREATE INDEX IF NOT EXISTS idx_nodes_parent ON concept_nodes(parent_id);
CREATE INDEX IF NOT EXISTS idx_nodes_level ON concept_nodes(hierarchy_level);
CREATE INDEX IF NOT EXISTS idx_nodes_type ON concept_nodes(node_type);
CREATE INDEX IF NOT EXISTS idx_nodes_name ON concept_nodes(name);
CREATE INDEX IF NOT EXISTS idx_nodes_bloom ON concept_nodes(bloom_level);

-- Relationship types
CREATE TABLE IF NOT EXISTS relationship_edges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER NOT NULL REFERENCES concept_nodes(id) ON DELETE CASCADE,
    target_id INTEGER NOT NULL REFERENCES concept_nodes(id) ON DELETE CASCADE,
    relationship_type TEXT NOT NULL CHECK (
        relationship_type IN ('prerequisite', 'enables', 'part_of', 'contains',
                              'similar_to', 'related_to', 'contradicts', 'exemplifies',
                              'applies_to', 'extends', 'teaches', 'assesses')
    ),
    is_directed BOOLEAN NOT NULL DEFAULT TRUE,
    strength TEXT CHECK (
        strength IS NULL OR
        strength IN ('hard', 'soft', 'recommended')
    ),
    evidence_text TEXT,
    confidence REAL NOT NULL DEFAULT 1.0 CHECK (confidence >= 0.0 AND confidence <= 1.0),
    provenance TEXT,  -- JSON
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(source_id, target_id, relationship_type)  -- Prevent duplicate relationships
);

-- Indexes for relationship_edges
CREATE INDEX IF NOT EXISTS idx_edges_source ON relationship_edges(source_id);
CREATE INDEX IF NOT EXISTS idx_edges_target ON relationship_edges(target_id);
CREATE INDEX IF NOT EXISTS idx_edges_type ON relationship_edges(relationship_type);
CREATE INDEX IF NOT EXISTS idx_edges_strength ON relationship_edges(strength);

-- ============================================================
-- Hierarchy Query Support (Recursive CTE Examples)
-- ============================================================

-- Get all descendants of a node
-- WITH RECURSIVE descendants AS (
--     SELECT id, name, hierarchy_level, parent_id FROM concept_nodes WHERE id = ?
--     UNION ALL
--     SELECT cn.id, cn.name, cn.hierarchy_level, cn.parent_id
--     FROM concept_nodes cn
--     JOIN descendants d ON cn.parent_id = d.id
-- )
-- SELECT * FROM descendants WHERE id != ?;

-- Get all ancestors of a node
-- WITH RECURSIVE ancestors AS (
--     SELECT id, name, hierarchy_level, parent_id FROM concept_nodes WHERE id = ?
--     UNION ALL
--     SELECT cn.id, cn.name, cn.hierarchy_level, cn.parent_id
--     FROM concept_nodes cn
--     JOIN ancestors a ON cn.id = a.parent_id
-- )
-- SELECT * FROM ancestors WHERE id != ?;
```

## Validation Rules

### Node Validation

1. **Hierarchy Consistency**: If parent_id is set, child.hierarchy_level MUST equal parent.hierarchy_level + 1
2. **Root Nodes**: Nodes with hierarchy_level = 1 MUST have parent_id = NULL
3. **Required Fields**: name, node_type, hierarchy_level are required
4. **Bloom's Classification**: All concept and skill nodes SHOULD have bloom_level set (SC-004)

### Relationship Validation

1. **No Self-Loops**: source_id != target_id
2. **No Circular Hard Prerequisites**: Inserting prerequisite with strength='hard' must not create a cycle
3. **Symmetric Relationships**: similar_to, related_to, contradicts should have is_directed=FALSE
4. **Type-Appropriate Strength**: Only prerequisite relationships use the strength field

## State Transitions

### Node Lifecycle

```
┌─────────┐     create()      ┌──────────┐
│ (none)  │ ─────────────────>│  active  │
└─────────┘                   └──────────┘
                                   │
                               update()
                                   │
                                   v
                              ┌──────────┐
                              │ updated  │ (updated_at set)
                              └──────────┘
                                   │
                               delete()
                                   │
                                   v
                              ┌──────────┐
                              │ deleted  │ (CASCADE on edges)
                              └──────────┘
```

### Extraction Pipeline State

```
┌─────────────┐     ingest()     ┌────────────┐
│  PDF file   │ ────────────────>│  passages  │
└─────────────┘                  └────────────┘
                                      │
                                extract_concepts()
                                      │
                                      v
                                ┌────────────┐     extract_relationships()     ┌───────────────┐
                                │  concepts  │ ────────────────────────────────>│ relationships │
                                └────────────┘                                  └───────────────┘
                                      │                                              │
                                      └──────────────── persist() ──────────────────┘
                                                           │
                                                           v
                                                    ┌────────────┐
                                                    │   graph    │ (in SQLite)
                                                    └────────────┘
```

## Query Patterns

### Get Node with Children

```python
def get_node_with_children(node_id: int) -> NodeWithChildren:
    """Return node and its immediate children."""
    # 1. Get the node
    # 2. Get children where parent_id = node_id
    # 3. Return combined result
```

### Get All Prerequisites (Transitive)

```python
def get_all_prerequisites(node_id: int, strength: str = None) -> List[Node]:
    """Return all prerequisite nodes (transitive closure)."""
    # Use recursive CTE following prerequisite edges
    # Optionally filter by strength (hard/soft/recommended)
```

### Get Related by Type

```python
def get_related_by_type(node_id: int, relationship_type: str) -> List[Node]:
    """Return all nodes related by specific type."""
    # Query relationship_edges where source_id or target_id = node_id
    # Filter by relationship_type
```

## Integration Points

### Existing Tables (storage.py)

The graph tables coexist with existing tables:
- `quiz_results` - can reference concept_nodes via concept_name
- `concept_mastery` - can be linked to concept_nodes.id
- `extracted_concepts` - migration path to concept_nodes

### ADK Tools

New tools expose graph queries:
- `get_concept(name)` - lookup concept by name
- `get_prerequisites(concept_id)` - transitive prerequisites
- `get_descendants(concept_id)` - hierarchy traversal
- `find_learning_path(start_id, end_id)` - pathfinding between concepts
