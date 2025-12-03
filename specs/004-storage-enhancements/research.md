# Research: Storage Enhancements

**Feature**: 004-storage-enhancements
**Date**: 2025-12-03
**Status**: Complete

## 1. Session Persistence Strategy

### Decision: Use ADK `DatabaseSessionService` with SQLite

**Rationale**:
- ADK provides built-in `DatabaseSessionService` that handles all session/event serialization
- Directly supports SQLite via connection URL (e.g., `sqlite:///data/sessions.db`)
- Seamless integration with existing Runner pattern
- Handles session creation, retrieval, and event storage automatically

**Alternatives Considered**:
| Alternative | Rejected Because |
|-------------|------------------|
| Custom session table in existing storage.py | Duplicates ADK functionality; harder to maintain |
| InMemorySessionService + manual persistence | Requires complex serialization; doesn't support ADK event model |
| Third-party session store (Redis) | Over-engineered for local use; adds infrastructure complexity |

**Implementation Pattern** (from Day 3):
```python
from google.adk.sessions import DatabaseSessionService

db_url = "sqlite:///data/sessions.db"
session_service = DatabaseSessionService(db_url=db_url)

runner = Runner(
    agent=root_agent,
    app_name="education_app",
    session_service=session_service
)
```

---

## 2. Semantic Memory Strategy

### Decision: ADK `InMemoryMemoryService` for local, `VertexAiMemoryBankService` for production

**Rationale**:
- ADK's MemoryService provides semantic search out of the box
- `InMemoryMemoryService` works offline for development/testing
- `VertexAiMemoryBankService` adds LLM-powered consolidation for production
- Built-in `preload_memory` and `load_memory` tools reduce implementation effort

**Alternatives Considered**:
| Alternative | Rejected Because |
|-------------|------------------|
| Vector DB (Qdrant/Chroma) | Requires additional infrastructure; ADK MemoryService covers use case |
| Extend storage.py with embeddings | Custom solution when ADK provides native support |
| No semantic memory | User Story 2 explicitly requires cross-session personalization |

**Implementation Pattern**:
```python
from google.adk.memory import InMemoryMemoryService
from google.adk.tools import preload_memory

memory_service = InMemoryMemoryService()

agent = LlmAgent(
    tools=[preload_memory],  # Auto-loads relevant memories
    after_agent_callback=auto_save_to_memory  # Auto-saves session to memory
)

runner = Runner(
    agent=agent,
    app_name="education_app",
    session_service=session_service,
    memory_service=memory_service
)
```

---

## 3. Knowledge Graph Strategy

### Decision: Extend existing SQLite with graph query functions

**Rationale**:
- Existing `concept_relationships` table already stores relationships
- SQLite recursive CTEs handle prerequisite chains (FR-008 path queries)
- No need for dedicated graph DB at current scale (< 500 concepts)
- Keeps all data in single SQLite file for portability

**Alternatives Considered**:
| Alternative | Rejected Because |
|-------------|------------------|
| Neo4j/ArangoDB | Over-engineered; adds deployment complexity |
| In-memory graph (networkx) | Doesn't persist; reconstruction on every start |
| GraphQL layer | Adds API complexity; simple Python functions sufficient |

**Implementation Pattern**:
```python
# Recursive CTE for prerequisite chain
def get_prerequisites(self, concept_name: str, max_depth: int = 5) -> List[str]:
    with self._get_conn() as conn:
        rows = conn.execute("""
            WITH RECURSIVE prereq_chain(concept, depth) AS (
                SELECT target_concept, 1
                FROM concept_relationships
                WHERE source_concept = ? AND relationship_type = 'depends-on'
                UNION ALL
                SELECT cr.target_concept, pc.depth + 1
                FROM concept_relationships cr
                JOIN prereq_chain pc ON cr.source_concept = pc.concept
                WHERE cr.relationship_type = 'depends-on' AND pc.depth < ?
            )
            SELECT DISTINCT concept FROM prereq_chain ORDER BY depth
        """, (concept_name, max_depth)).fetchall()
        return [r[0] for r in rows]
```

---

## 4. Multi-Device Sync Strategy

### Decision: Tiered approach - SQLite local, Vertex AI Memory Bank for cloud sync

**Rationale**:
- P3 priority means cloud sync is optional enhancement
- Vertex AI Memory Bank provides managed cloud storage with sync
- SQLite remains default for offline/local operation (FR-010)
- Last-write-wins conflict resolution matches FR-011

**Alternatives Considered**:
| Alternative | Rejected Because |
|-------------|------------------|
| Custom cloud sync (Firebase/Supabase) | Adds authentication complexity; Vertex AI integrates with ADK |
| CRDTs for conflict resolution | Over-engineered for educational app; last-write-wins sufficient |
| No cloud sync | User Story 4 requires multi-device access |

**Implementation Pattern**:
```python
# Environment-based service selection
import os
from google.adk.memory import InMemoryMemoryService

def get_memory_service():
    if os.getenv("VERTEX_AI_PROJECT"):
        from google.adk.memory import VertexAiMemoryBankService
        return VertexAiMemoryBankService(
            project=os.getenv("VERTEX_AI_PROJECT"),
            location=os.getenv("VERTEX_AI_LOCATION", "us-central1")
        )
    return InMemoryMemoryService()
```

---

## 5. Data Export/Import Strategy

### Decision: JSON export with version metadata, schema migration on import

**Rationale**:
- Existing `export_progress()` method returns JSON-serializable dict
- Add version field for forward/backward compatibility (FR-014)
- Import validates version and applies migrations as needed

**Alternatives Considered**:
| Alternative | Rejected Because |
|-------------|------------------|
| SQLite dump | Not portable; version differences hard to handle |
| Protobuf/MessagePack | Binary format harder to debug; JSON human-readable |
| No versioning | FR-014 requires handling version differences |

**Implementation Pattern**:
```python
EXPORT_VERSION = "1.0.0"

def export_progress(self) -> Dict[str, Any]:
    return {
        "version": EXPORT_VERSION,
        "user_id": self.user_id,
        "exported_at": datetime.utcnow().isoformat(),
        # ... existing export data
    }

def import_progress(self, data: Dict[str, Any]):
    version = data.get("version", "0.0.0")
    if version != EXPORT_VERSION:
        data = self._migrate_export_data(data, version)
    # ... import logic
```

---

## 6. Migration Strategy

### Decision: Automatic migration on first startup with rollback capability

**Rationale**:
- FR-015 requires migration without data loss
- FR-016 requires rollback capability
- Backup existing database before migration
- Apply migrations in version order

**Implementation Pattern**:
```python
def _migrate_if_needed(self):
    current_version = self._get_schema_version()
    if current_version < CURRENT_SCHEMA_VERSION:
        # Backup before migration
        backup_path = self.db_path.with_suffix('.db.backup')
        shutil.copy(self.db_path, backup_path)

        try:
            self._apply_migrations(current_version)
        except Exception as e:
            # Rollback on failure
            shutil.copy(backup_path, self.db_path)
            raise MigrationError(f"Migration failed: {e}")
```

---

## 7. Session State Key Conventions

### Decision: Adopt ADK prefix conventions for session state

**Rationale**:
- Matches Day 3 best practices
- Clear separation between user data, app config, and temporary state
- Consistent across all tools

**Key Prefixes**:
| Prefix | Purpose | Example |
|--------|---------|---------|
| `user:` | User-specific preferences and data | `user:difficulty_level`, `user:preferred_explanation_style` |
| `app:` | Application configuration | `app:theme`, `app:language` |
| `temp:` | Temporary state (cleared on session end) | `temp:current_quiz_id` |
| `quiz:` | Quiz-specific state (existing) | `quiz:snippets`, `quiz:index` |

---

## Summary of Decisions

| Component | Decision | Key Benefit |
|-----------|----------|-------------|
| Session Persistence | `DatabaseSessionService` | Built-in, zero custom code |
| Semantic Memory | `MemoryService` + tools | Automatic consolidation, semantic search |
| Knowledge Graph | SQLite + recursive CTEs | Single database, portable |
| Multi-Device Sync | Vertex AI Memory Bank (opt-in) | Managed cloud sync |
| Export Format | JSON with version | Human-readable, migratable |
| Migration | Auto-migrate with backup | Zero data loss, rollback |
