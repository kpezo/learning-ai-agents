# Data Model: Storage Enhancements

**Feature**: 004-storage-enhancements
**Date**: 2025-12-03
**Status**: Complete

## Overview

This document defines the data entities for enhanced storage capabilities. The design extends the existing `adk/storage.py` models while integrating with ADK's SessionService and MemoryService.

---

## Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           ADK Managed Layer                              │
│  ┌─────────────────────┐         ┌─────────────────────────────────┐    │
│  │   DatabaseSession   │         │         MemoryService           │    │
│  │   Service (ADK)     │◄───────►│  (InMemory/VertexAI)           │    │
│  │  - sessions.db      │         │  - Semantic search              │    │
│  │  - events table     │         │  - Consolidation                │    │
│  └─────────────────────┘         └─────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
                 │                              │
                 │ References                   │ Augments
                 ▼                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        Application Storage Layer                         │
│                          (adk/storage.py)                                │
│                                                                          │
│  ┌──────────────┐    ┌────────────────┐    ┌────────────────────────┐   │
│  │  QuizResult  │    │ ConceptMastery │    │    KnowledgeGap        │   │
│  │              │    │                │    │                        │   │
│  │ - id         │    │ - id           │    │ - id                   │   │
│  │ - user_id    │    │ - user_id      │    │ - user_id              │   │
│  │ - session_id◄├────┤ - concept_name │    │ - concept_name         │   │
│  │ - topic      │    │ - mastery_level│    │ - gap_type             │   │
│  │ - scores     │    │ - times_seen   │    │ - related_concepts     │   │
│  └──────────────┘    │ - knowledge_type│    └────────────────────────┘   │
│                      └────────────────┘                                  │
│         │                    │                                           │
│         │                    │ Tracks mastery of                         │
│         │                    ▼                                           │
│         │         ┌──────────────────┐     ┌─────────────────────────┐  │
│         │         │ ExtractedConcept │◄───►│  ConceptRelationship    │  │
│         │         │                  │     │                         │  │
│         │         │ - pdf_hash       │     │ - source_concept        │  │
│         │         │ - name           │     │ - target_concept        │  │
│         │         │ - knowledge types│     │ - relationship_type     │  │
│         │         └──────────────────┘     │ - direction             │  │
│         │                                  └─────────────────────────┘  │
│         │                                              │                 │
│         │ Links to ADK session                        │ Graph queries   │
│         ▼                                              ▼                 │
│  ┌──────────────┐                          ┌─────────────────────────┐  │
│  │  SessionLog  │                          │    GraphQuery (new)     │  │
│  │              │                          │                         │  │
│  │ - session_id │                          │ - get_prerequisites()   │  │
│  │ - role       │                          │ - get_enabled_concepts()│  │
│  │ - content    │                          │ - get_learning_path()   │  │
│  └──────────────┘                          └─────────────────────────┘  │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    NEW: UserMemory (FR-004)                       │   │
│  │                                                                    │   │
│  │  - id: int                    - preference_type: str              │   │
│  │  - user_id: str               - preference_value: str             │   │
│  │  - fact_type: enum            - source_session_id: str            │   │
│  │    (preference/interest/      - first_mentioned: datetime         │   │
│  │     difficulty/behavior)      - last_confirmed: datetime          │   │
│  │  - fact_key: str              - confidence: float                 │   │
│  │  - fact_value: str            - is_active: bool                   │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    NEW: SyncState (FR-009-011)                    │   │
│  │                                                                    │   │
│  │  - id: int                    - sync_status: enum                 │   │
│  │  - user_id: str                 (synced/pending/conflict)         │   │
│  │  - device_id: str             - last_sync_at: datetime            │   │
│  │  - last_local_change: datetime- conflict_data: json (nullable)   │   │
│  │  - last_remote_sync: datetime - retry_count: int                  │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    NEW: DataExport (FR-012-014)                   │   │
│  │                                                                    │   │
│  │  Export JSON Schema:                                               │   │
│  │  {                                                                 │   │
│  │    "version": "1.0.0",                                            │   │
│  │    "user_id": string,                                             │   │
│  │    "exported_at": ISO8601,                                        │   │
│  │    "stats": {...},                                                │   │
│  │    "quiz_history": [...],                                         │   │
│  │    "concept_mastery": [...],                                      │   │
│  │    "user_memories": [...],     # NEW                              │   │
│  │    "knowledge_gaps": [...],                                       │   │
│  │    "session_summaries": [...]  # NEW: digests, not full logs      │   │
│  │  }                                                                 │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Entity Definitions

### 1. UserMemory (NEW - FR-004, FR-005)

Stores learned facts about users for personalization across sessions.

```python
@dataclass
class UserMemory:
    """Long-term facts about a user for personalization."""

    id: Optional[int] = None
    user_id: str = ""
    fact_type: str = ""  # preference, interest, difficulty_area, learning_style
    fact_key: str = ""   # e.g., "explanation_style", "favorite_topic"
    fact_value: str = "" # e.g., "step-by-step", "machine_learning"
    source_session_id: str = ""  # Where this was learned
    first_mentioned: str = ""    # ISO8601 timestamp
    last_confirmed: str = ""     # Last time user confirmed this fact
    confidence: float = 1.0      # 0.0-1.0, decreases if contradicted
    is_active: bool = True       # False if user explicitly changed preference
```

**Validation Rules**:
- `fact_type` must be one of: `preference`, `interest`, `difficulty_area`, `learning_style`, `behavior`
- `confidence` must be between 0.0 and 1.0
- `fact_key` + `user_id` should be unique (upsert on conflict)

**State Transitions**:
- Created when agent detects user preference (e.g., "I prefer visual explanations")
- Updated when user confirms or repeats preference (confidence increases)
- Deactivated when user explicitly changes preference (is_active = False)

---

### 2. ConceptRelationship (ENHANCED - FR-006, FR-007, FR-008)

Extended to support graph queries for prerequisite chains and learning paths.

```python
@dataclass
class ConceptRelationship:
    """Relationship between concepts with graph query support."""

    id: Optional[int] = None
    pdf_hash: str = ""
    source_concept: str = ""
    target_concept: str = ""
    relationship_type: str = ""  # depends-on, enables, part-of, similar-to, builds-on
    direction: str = ""          # unidirectional, bidirectional
    rationale: str = ""
    confidence: float = 0.0
    # NEW fields for graph traversal
    weight: float = 1.0          # For weighted path algorithms
    learning_order: int = 0      # Suggested learning sequence within type
```

**Relationship Types** (FR-006):
| Type | Meaning | Example |
|------|---------|---------|
| `depends-on` | Must learn A before B | "algebra" depends-on "arithmetic" |
| `enables` | Learning A unlocks B | "calculus" enables "differential equations" |
| `part-of` | A is a component of B | "derivatives" part-of "calculus" |
| `similar-to` | A and B are related concepts | "gradient" similar-to "derivative" |
| `builds-on` | A extends/deepens B | "multivariate calculus" builds-on "calculus" |

---

### 3. SyncState (NEW - FR-009, FR-010, FR-011)

Tracks synchronization state for multi-device access.

```python
@dataclass
class SyncState:
    """Per-device synchronization metadata."""

    id: Optional[int] = None
    user_id: str = ""
    device_id: str = ""          # UUID generated per device
    device_name: str = ""        # User-friendly name (e.g., "John's Laptop")
    last_local_change: str = ""  # ISO8601 timestamp of last local modification
    last_remote_sync: str = ""   # ISO8601 timestamp of last successful sync
    sync_status: str = "synced"  # synced, pending, conflict, error
    pending_changes: str = ""    # JSON array of change records
    conflict_data: Optional[str] = None  # JSON with conflicting versions
    retry_count: int = 0
    last_error: Optional[str] = None
```

**Sync Status Values**:
| Status | Meaning | Action |
|--------|---------|--------|
| `synced` | All changes pushed and pulled | None |
| `pending` | Local changes not yet synced | Push on next connection |
| `conflict` | Same data modified on multiple devices | Apply last-write-wins, log conflict |
| `error` | Sync failed | Retry with exponential backoff |

**Conflict Resolution** (FR-011):
- Compare `last_local_change` timestamps
- Keep version with latest timestamp
- Store losing version in `conflict_data` for audit
- Log conflict for user visibility

---

### 4. DataExport (ENHANCED - FR-012, FR-013, FR-014)

Enhanced export schema with version metadata for forward/backward compatibility.

```python
EXPORT_VERSION = "1.0.0"

@dataclass
class DataExport:
    """Complete export of user data with version metadata."""

    version: str = EXPORT_VERSION
    user_id: str = ""
    exported_at: str = ""  # ISO8601

    # Core data
    stats: Dict[str, Any] = field(default_factory=dict)
    quiz_history: List[Dict] = field(default_factory=list)
    concept_mastery: List[Dict] = field(default_factory=list)
    knowledge_gaps: List[Dict] = field(default_factory=list)

    # NEW in v1.0.0
    user_memories: List[Dict] = field(default_factory=list)
    session_summaries: List[Dict] = field(default_factory=list)  # Digests, not full logs

    # Metadata
    source_app_version: str = ""
    checksum: str = ""  # SHA256 for integrity verification
```

**Version Compatibility Matrix**:
| Export Version | Min Import Version | Notes |
|----------------|-------------------|-------|
| 1.0.0 | 1.0.0 | Current version |
| 0.x.x (legacy) | 1.0.0 | Auto-migrates; missing fields get defaults |

---

### 5. PersistedSession (ADK-Managed)

Sessions are managed by ADK's `DatabaseSessionService`. The schema is controlled by ADK:

```sql
-- ADK's internal events table (for reference)
CREATE TABLE events (
    id INTEGER PRIMARY KEY,
    app_name TEXT NOT NULL,
    user_id TEXT NOT NULL,
    session_id TEXT NOT NULL,
    author TEXT,
    content TEXT,  -- JSON serialized
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Integration with Application Storage**:
- `quiz_results.session_id` references ADK session IDs
- `session_logs` table provides additional logging beyond ADK events
- `user_memories.source_session_id` tracks where facts were learned

---

## Database Schema Updates

### New Tables

```sql
-- User long-term memories for personalization
CREATE TABLE IF NOT EXISTS user_memories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    fact_type TEXT NOT NULL,
    fact_key TEXT NOT NULL,
    fact_value TEXT NOT NULL,
    source_session_id TEXT,
    first_mentioned TEXT NOT NULL,
    last_confirmed TEXT NOT NULL,
    confidence REAL DEFAULT 1.0,
    is_active INTEGER DEFAULT 1,
    UNIQUE(user_id, fact_key)
);
CREATE INDEX IF NOT EXISTS idx_user_memories_user ON user_memories(user_id);
CREATE INDEX IF NOT EXISTS idx_user_memories_type ON user_memories(fact_type);

-- Sync state for multi-device
CREATE TABLE IF NOT EXISTS sync_state (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    device_id TEXT NOT NULL UNIQUE,
    device_name TEXT,
    last_local_change TEXT,
    last_remote_sync TEXT,
    sync_status TEXT DEFAULT 'synced',
    pending_changes TEXT,
    conflict_data TEXT,
    retry_count INTEGER DEFAULT 0,
    last_error TEXT
);
CREATE INDEX IF NOT EXISTS idx_sync_user ON sync_state(user_id);

-- Schema version tracking for migrations
CREATE TABLE IF NOT EXISTS schema_version (
    version TEXT PRIMARY KEY,
    applied_at TEXT NOT NULL,
    description TEXT
);
```

### Enhanced Tables

```sql
-- Add graph traversal fields to concept_relationships
ALTER TABLE concept_relationships ADD COLUMN weight REAL DEFAULT 1.0;
ALTER TABLE concept_relationships ADD COLUMN learning_order INTEGER DEFAULT 0;
```

---

## Graph Query Functions

### FR-007: Get Prerequisites

```python
def get_prerequisites(self, concept_name: str, max_depth: int = 5) -> List[Dict]:
    """Get all prerequisite concepts in learning order."""
    with self._get_conn() as conn:
        rows = conn.execute("""
            WITH RECURSIVE prereq_chain(concept, depth, path) AS (
                SELECT target_concept, 1, source_concept || ' -> ' || target_concept
                FROM concept_relationships
                WHERE source_concept = ? AND relationship_type = 'depends-on'
                UNION ALL
                SELECT cr.target_concept, pc.depth + 1, pc.path || ' -> ' || cr.target_concept
                FROM concept_relationships cr
                JOIN prereq_chain pc ON cr.source_concept = pc.concept
                WHERE cr.relationship_type = 'depends-on' AND pc.depth < ?
            )
            SELECT DISTINCT concept, MIN(depth) as depth, path
            FROM prereq_chain
            GROUP BY concept
            ORDER BY depth DESC
        """, (concept_name, max_depth)).fetchall()
        return [{"concept": r[0], "depth": r[1], "path": r[2]} for r in rows]
```

### FR-007: Get Enabled Concepts

```python
def get_enabled_concepts(self, concept_name: str) -> List[Dict]:
    """Get concepts that are unlocked after mastering this one."""
    with self._get_conn() as conn:
        rows = conn.execute("""
            SELECT source_concept, relationship_type, rationale
            FROM concept_relationships
            WHERE target_concept = ?
            AND relationship_type IN ('depends-on', 'builds-on')
        """, (concept_name,)).fetchall()
        return [{"concept": r[0], "relationship": r[1], "rationale": r[2]} for r in rows]
```

### FR-008: Get Learning Path

```python
def get_learning_path(
    self,
    from_concept: str,
    to_concept: str,
    max_depth: int = 10
) -> Optional[List[str]]:
    """Find shortest learning path between two concepts."""
    with self._get_conn() as conn:
        rows = conn.execute("""
            WITH RECURSIVE path_finder(concept, path, depth) AS (
                SELECT ?, ?, 0
                UNION ALL
                SELECT cr.target_concept,
                       pf.path || ',' || cr.target_concept,
                       pf.depth + 1
                FROM concept_relationships cr
                JOIN path_finder pf ON cr.source_concept = pf.concept
                WHERE cr.relationship_type IN ('depends-on', 'enables', 'builds-on')
                AND pf.depth < ?
                AND cr.target_concept NOT IN (SELECT value FROM json_each(pf.path))
            )
            SELECT path
            FROM path_finder
            WHERE concept = ?
            ORDER BY depth
            LIMIT 1
        """, (from_concept, from_concept, max_depth, to_concept)).fetchone()
        return rows[0].split(',') if rows else None
```

---

## Session State Key Conventions

For use with ADK's `tool_context.state`:

| Prefix | Scope | Persistence | Examples |
|--------|-------|-------------|----------|
| `user:` | User preferences | Saved to UserMemory | `user:preferred_style`, `user:difficulty_level` |
| `app:` | Application config | Session only | `app:theme`, `app:language` |
| `temp:` | Temporary values | Cleared on end | `temp:retry_count`, `temp:current_topic` |
| `quiz:` | Quiz state | Session + storage | `quiz:index`, `quiz:snippets` |
| `memory:` | Memory retrieval | Transient | `memory:recent_facts`, `memory:context` |

---

## Migration Plan

### Version 0.x → 1.0.0

1. Create new tables (`user_memories`, `sync_state`, `schema_version`)
2. Add columns to `concept_relationships` (`weight`, `learning_order`)
3. Migrate existing data (no data loss - additive changes only)
4. Update export/import to handle version differences

```python
MIGRATIONS = [
    ("1.0.0", """
        CREATE TABLE IF NOT EXISTS user_memories (...);
        CREATE TABLE IF NOT EXISTS sync_state (...);
        CREATE TABLE IF NOT EXISTS schema_version (...);
        ALTER TABLE concept_relationships ADD COLUMN weight REAL DEFAULT 1.0;
        ALTER TABLE concept_relationships ADD COLUMN learning_order INTEGER DEFAULT 0;
    """),
]
```
