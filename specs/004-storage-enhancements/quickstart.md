# Quickstart: Storage Enhancements

**Feature**: 004-storage-enhancements
**Time to First Working Example**: ~10 minutes

## Prerequisites

- Python 3.11+
- Existing ADK setup from CLAUDE.md
- `GOOGLE_API_KEY` environment variable set

## 1. Session Persistence (5 minutes)

Replace `InMemorySessionService` with `DatabaseSessionService` for persistent sessions.

### Before (current)
```python
# adk/run_dev.py - current implementation
from google.adk.sessions import InMemorySessionService
session_service = InMemorySessionService()
```

### After (enhanced)
```python
# adk/run_dev.py - with persistence
from google.adk.sessions import DatabaseSessionService
import os

DATA_DIR = os.getenv("DATA_DIR", "./data")
session_service = DatabaseSessionService(db_url=f"sqlite:///{DATA_DIR}/sessions.db")
```

### Test It
```bash
# Start a session
python -m adk.run_dev
> Hi, I'm learning about agents

# Close the app (Ctrl+C), then restart
python -m adk.run_dev
> What was I learning about?
# Agent should remember the conversation!
```

## 2. Memory Integration (5 minutes)

Add cross-session memory with `MemoryService`.

### Code Changes
```python
# adk/agent.py - add memory service and tools
from google.adk.memory import InMemoryMemoryService
from google.adk.tools import preload_memory

# Create memory service
memory_service = InMemoryMemoryService()

# Auto-save callback
async def auto_save_to_memory(callback_context):
    """Automatically save session to memory after each agent turn."""
    await callback_context._invocation_context.memory_service.add_session_to_memory(
        callback_context._invocation_context.session
    )

# Update specialist creation to include memory
def _make_specialist(role: str, extra_tools: List = None) -> LlmAgent:
    tools = [
        fetch_info_tool,
        get_quiz_source_tool,
        # ... existing tools ...
        preload_memory,  # ADD THIS
    ]
    if extra_tools:
        tools.extend(extra_tools)

    return LlmAgent(
        name=role.lower().replace(" ", "_"),
        description=f"{role} agent for education tasks.",
        model=_gemini_model(),
        instruction=_base_instruction(role),
        tools=tools,
        after_agent_callback=auto_save_to_memory,  # ADD THIS
    )
```

### Update Runner
```python
# adk/run_dev.py
from adk.agent import root_agent, memory_service

runner = Runner(
    agent=root_agent,
    app_name="education_app",
    session_service=session_service,
    memory_service=memory_service,  # ADD THIS
)
```

### Test It
```bash
python -m adk.run_dev
> I prefer step-by-step explanations

# In a NEW session (different session_id)
python -m adk.run_dev
> Explain what an agent is
# Agent should use step-by-step format based on memory!
```

## 3. Knowledge Graph Queries (5 minutes)

Add graph traversal functions to `StorageService`.

### Add to storage.py
```python
# adk/storage.py - add after existing methods

def get_prerequisites(self, concept_name: str, max_depth: int = 5) -> List[Dict]:
    """Get all prerequisite concepts in learning order."""
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
            SELECT DISTINCT concept, MIN(depth) as depth
            FROM prereq_chain
            GROUP BY concept
            ORDER BY depth DESC
        """, (concept_name, max_depth)).fetchall()
        return [{"concept": r[0], "depth": r[1]} for r in rows]

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

### Create Tool
```python
# adk/graph_tools.py (NEW FILE)
from google.adk.tools import FunctionTool
from google.adk.tools.tool_context import ToolContext
from adk.storage import get_storage

def _get_prerequisites(concept: str, tool_context: ToolContext = None) -> dict:
    """Get prerequisite concepts for a topic."""
    user_id = tool_context.user_id if tool_context else "default_user"
    storage = get_storage(user_id)
    prereqs = storage.get_prerequisites(concept)
    return {"status": "success", "prerequisites": prereqs}

get_prerequisites_tool = FunctionTool(func=_get_prerequisites)
```

### Test It
```python
from adk.storage import get_storage

storage = get_storage("test_user")
prereqs = storage.get_prerequisites("machine_learning")
print(prereqs)
# [{"concept": "linear_algebra", "depth": 2}, {"concept": "statistics", "depth": 1}]
```

## 4. User Memories (5 minutes)

Store learned facts about users for personalization.

### Add to storage.py
```python
# adk/storage.py - add UserMemory dataclass and methods

@dataclass
class UserMemory:
    """Long-term facts about a user for personalization."""
    id: Optional[int] = None
    user_id: str = ""
    fact_type: str = ""  # preference, interest, difficulty_area, learning_style
    fact_key: str = ""
    fact_value: str = ""
    source_session_id: str = ""
    first_mentioned: str = ""
    last_confirmed: str = ""
    confidence: float = 1.0
    is_active: bool = True

# Add to _init_db():
conn.executescript("""
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
""")

# Add methods:
def save_user_memory(self, fact_type: str, fact_key: str, fact_value: str,
                     source_session_id: str = "") -> int:
    """Save a learned fact about the user."""
    now = datetime.utcnow().isoformat()
    with self._get_conn() as conn:
        cursor = conn.execute("""
            INSERT INTO user_memories
            (user_id, fact_type, fact_key, fact_value, source_session_id,
             first_mentioned, last_confirmed)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id, fact_key) DO UPDATE SET
                fact_value = excluded.fact_value,
                last_confirmed = excluded.last_confirmed,
                confidence = MIN(confidence + 0.1, 1.0)
        """, (self.user_id, fact_type, fact_key, fact_value,
              source_session_id, now, now))
        return cursor.lastrowid

def get_user_memories(self, fact_type: str = None) -> List[UserMemory]:
    """Get user memories, optionally filtered by type."""
    with self._get_conn() as conn:
        if fact_type:
            rows = conn.execute("""
                SELECT * FROM user_memories
                WHERE user_id = ? AND fact_type = ? AND is_active = 1
            """, (self.user_id, fact_type)).fetchall()
        else:
            rows = conn.execute("""
                SELECT * FROM user_memories
                WHERE user_id = ? AND is_active = 1
            """, (self.user_id,)).fetchall()
        return [UserMemory(**dict(row)) for row in rows]
```

### Test It
```python
from adk.storage import get_storage

storage = get_storage("test_user")
storage.save_user_memory(
    fact_type="preference",
    fact_key="explanation_style",
    fact_value="step-by-step with examples",
    source_session_id="session-001"
)

memories = storage.get_user_memories(fact_type="preference")
print(memories)
# [UserMemory(fact_key='explanation_style', fact_value='step-by-step with examples', ...)]
```

## Environment Variables

```bash
# .env file
GOOGLE_API_KEY=your-key-here
DATA_DIR=./data                    # Where SQLite databases are stored
PDF_PATH=Intro.pdf                 # Educational content PDF
GEMINI_MODEL=gemini-2.5-flash-lite # Model to use

# Optional: Enable cloud sync
VERTEX_AI_PROJECT=your-project-id
VERTEX_AI_LOCATION=us-central1
```

## Verification Checklist

- [ ] Session persists across app restarts
- [ ] Memory tools available to agents (`preload_memory`)
- [ ] Auto-save callback triggers after each turn
- [ ] Graph queries return prerequisite chains
- [ ] User memories stored and retrievable
- [ ] Export/import preserves all data

## Next Steps

1. Run `/speckit.tasks` to generate implementation tasks
2. Implement in order: Session → Memory → Graph → Sync → Export
3. Write tests for each component before implementation (TDD)
