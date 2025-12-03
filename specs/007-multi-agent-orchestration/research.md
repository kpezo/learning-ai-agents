# Research: Multi-Agent Orchestration Expansion

**Branch**: `007-multi-agent-orchestration`
**Date**: 2025-12-03
**Status**: Complete

## Overview

This research consolidates findings for the Multi-Agent Orchestration Expansion feature. The feature expands from 3 agents to 5 specialists with LLM-driven routing and ADK orchestration patterns (SequentialAgent, LoopAgent).

## Research Tasks

### Task 1: ADK SequentialAgent Pattern

**Question**: How to implement SequentialAgent for the Tutor → Quiz → Feedback learning cycle?

**Finding**: ADK provides `SequentialAgent` that executes sub-agents in fixed order, passing the same `InvocationContext` through each step. Key characteristics:
- Same context flows through all agents sequentially
- Enables state accumulation via `output_key` property
- Later agents access earlier results via template syntax: `{state_key}`

```python
from google.adk.agents import SequentialAgent, LlmAgent

tutor = LlmAgent(name="Tutor", output_key="explanation")
quiz = LlmAgent(name="Quiz", instruction="Quiz on {explanation}", output_key="quiz_result")
feedback = LlmAgent(name="Feedback", instruction="Analyze {quiz_result}")

learning_sequence = SequentialAgent(
    name="LearningCycle",
    sub_agents=[tutor, quiz, feedback]
)
```

**Decision**: Use `SequentialAgent` for the Tutor → Quiz → Feedback pipeline.
**Rationale**: Native ADK pattern; deterministic execution order; automatic state passing.
**Alternatives Rejected**: Custom orchestration logic would duplicate ADK functionality.

---

### Task 2: ADK LoopAgent Pattern for Mastery

**Question**: How to implement LoopAgent that repeats until learner achieves mastery (85%)?

**Finding**: ADK provides `LoopAgent` that iteratively executes sub-agents until:
1. `max_iterations` is reached, or
2. A sub-agent signals escalation via `Event` with `escalate=True`

```python
from google.adk.agents import LoopAgent, BaseAgent
from google.adk.events import Event, EventActions

class MasteryChecker(BaseAgent):
    async def _run_async_impl(self, ctx):
        mastery = ctx.session.state.get("mastery_score", 0.0)
        threshold = ctx.session.state.get("mastery_threshold", 0.85)
        is_mastered = mastery >= threshold
        yield Event(
            author=self.name,
            actions=EventActions(escalate=is_mastered)
        )

mastery_loop = LoopAgent(
    name="MasteryLoop",
    max_iterations=5,
    sub_agents=[learning_sequence, MasteryChecker(name="MasteryChecker")]
)
```

**Decision**: Use `LoopAgent` wrapping `SequentialAgent` with custom `MasteryChecker`.
**Rationale**: Combines sequential flow with iterative refinement; configurable threshold.
**Alternatives Rejected**: Manual iteration tracking in tools would be more complex.

---

### Task 3: LLM-Driven Routing (Coordinator Agent)

**Question**: How should the Coordinator agent route messages to appropriate specialists?

**Finding**: ADK supports LLM-driven delegation where the parent `LlmAgent` selects sub-agents:
- Parent LLM generates `transfer_to_agent(agent_name='target')` calls
- Sub-agents need clear `description` fields for LLM selection
- Scope configurable: can transfer to sub-agents, parent, or siblings

```python
from google.adk.agents import Agent, LlmAgent

diagnostic = LlmAgent(
    name="diagnostic",
    description="Assesses learner's existing knowledge and identifies prerequisite gaps"
)
tutor = LlmAgent(
    name="tutor",
    description="Explains concepts and answers questions about the material"
)
# ... other specialists

coordinator = Agent(
    name="coordinator",
    instruction="""Route learner requests to the appropriate specialist:
    - Questions about topics → tutor
    - Quiz requests → quiz
    - Progress inquiries → pathplanner
    - New topic starts → diagnostic (to check prerequisites first)
    - After quiz completion → feedback
    If unclear, ask the learner to clarify.""",
    sub_agents=[diagnostic, tutor, quiz, feedback, pathplanner]
)
```

**Decision**: Use ADK's native LLM delegation via `sub_agents` with descriptive agent descriptions.
**Rationale**: Leverages Gemini's understanding; no explicit routing rules needed.
**Alternatives Rejected**:
- Keyword matching: Too brittle, fails on rephrased requests
- Separate classifier model: Adds latency, complexity

---

### Task 4: Session State Sharing Between Agents

**Question**: How do agents share state (diagnostic results, quiz scores, mastery levels)?

**Finding**: ADK agents share state via `session.state` dictionary:
- Agents write via `output_key` property or direct `ctx.session.state[key] = value`
- Subsequent agents read via template syntax `{key}` or `ctx.session.state.get(key)`
- In `SequentialAgent`, state accumulates through the pipeline
- In `ParallelAgent`, agents share state but use distinct keys to avoid races

State keys convention for this feature:
```python
# Diagnostic phase
"prerequisite_gaps": List[str]       # Concepts learner is missing
"diagnostic_complete": bool          # Whether diagnostic ran
"learner_level": str                 # "beginner"/"intermediate"/"advanced"

# Learning cycle
"current_topic": str                 # Topic being studied
"explanation": str                   # Tutor's explanation
"quiz_questions": List[dict]         # Generated quiz questions
"quiz_responses": List[dict]         # Learner's answers
"quiz_score": float                  # Score from 0.0-1.0
"mastery_score": float              # Rolling mastery level
"mastery_threshold": float          # Target (default 0.85)

# Feedback phase
"error_patterns": List[dict]         # Identified mistake patterns
"feedback_text": str                 # Constructive feedback

# Path planning
"learning_path": List[str]           # Recommended topic sequence
"goals": List[str]                   # Learner's stated goals
```

**Decision**: Use ADK session state with documented key conventions.
**Rationale**: Native pattern; enables state accumulation in sequences; persistent across agent switches.
**Alternatives Rejected**: Database-per-agent would fragment state; custom event bus adds complexity.

---

### Task 5: Agent Transition Tracking (FR-013)

**Question**: How to track which agent handled each message for debugging and analytics?

**Finding**: ADK provides agent attribution via:
1. `Event.author` field contains agent name
2. `LoggingPlugin` in runner exposes all events including transfers
3. Session logs can capture transitions

Implementation approach:
```python
from adk.storage import get_storage

def log_transition(ctx, from_agent: str, to_agent: str, reason: str):
    storage = get_storage(ctx.session.user_id)
    storage.log_transition(
        session_id=ctx.session.session_id,
        from_agent=from_agent,
        to_agent=to_agent,
        reason=reason,
        timestamp=datetime.utcnow().isoformat()
    )
```

Add to `storage.py`:
```python
# agent_transitions table
CREATE TABLE IF NOT EXISTS agent_transitions (
    id INTEGER PRIMARY KEY,
    session_id TEXT NOT NULL,
    from_agent TEXT NOT NULL,
    to_agent TEXT NOT NULL,
    reason TEXT,
    timestamp TEXT NOT NULL
);
```

**Decision**: Add `agent_transitions` table to SQLite storage; log transitions via runner events.
**Rationale**: Enables debugging ("why did it go to X?") and analytics (routing accuracy).
**Alternatives Rejected**: In-memory only would lose data on restart.

---

### Task 6: Mid-Conversation Agent Switching (FR-011)

**Question**: How to handle user interruptions (e.g., question during quiz)?

**Finding**: ADK's design naturally supports interruption:
1. Coordinator always receives messages first
2. Coordinator can redirect mid-stream based on intent
3. Quiz state persists in session.state, allowing resume

Implementation pattern:
```python
# In coordinator instruction:
"""If the learner asks a question during a quiz session:
1. Note quiz is paused (set session state quiz_paused=True)
2. Route to tutor for the question
3. After tutor responds, ask if learner wants to resume quiz

If quiz_paused is True and learner wants to continue:
1. Route back to quiz agent
2. Quiz reads quiz_state from session to resume"""
```

**Decision**: Handle via coordinator instruction + session state flags.
**Rationale**: No special infrastructure; LLM handles naturally with state persistence.
**Alternatives Rejected**: Separate "interrupt handler" agent adds unnecessary complexity.

---

### Task 7: Refactoring Existing 3-Agent System

**Question**: How to migrate from current (Tutor, Curriculum Planner, Assessor) to new 5-agent system?

**Finding**: Current system in `adk/agent.py`:
- `tutor_agent` → Maps to new `TutorAgent` (keep)
- `curriculum_planner_agent` → Responsibilities split:
  - Learning path → new `PathPlannerAgent`
  - Prerequisites → new `DiagnosticAgent`
- `assessor_agent` → Responsibilities split:
  - Quiz generation → new `QuizAgent`
  - Feedback → new `FeedbackAgent`

Migration strategy:
1. Create new agent definitions without removing old ones
2. Update `root_agent` to use new agents as sub_agents
3. Deprecate but don't delete old agent definitions initially
4. Once tests pass, remove deprecated code

**Decision**: Incremental migration with parallel agent definitions.
**Rationale**: Reduces risk; allows A/B testing; maintains backward compatibility.
**Alternatives Rejected**: Big-bang replacement risks breaking working system.

---

### Task 8: Diagnostic Agent Prerequisites Lookup

**Question**: How does DiagnosticAgent determine prerequisites for a topic?

**Finding**: Options considered:

1. **Hardcoded prerequisite map** - Maintain `{topic: [prerequisites]}` dict
   - Pros: Fast, predictable
   - Cons: Manual maintenance, doesn't scale

2. **RAG + LLM inference** - Query knowledge graph for relationships
   - Pros: Dynamic, uses existing concept relationships from storage
   - Cons: May hallucinate prerequisites

3. **Hybrid approach** - Use concept_relationships table + LLM verification
   - Pros: Data-grounded but flexible
   - Cons: Requires well-populated relationship data

Current codebase has `concept_relationships` table in `storage.py`:
```python
@dataclass
class ConceptRelationship:
    source_concept: str
    target_concept: str
    relationship_type: str  # "depends-on", "enables", "part-of"
    direction: str
```

**Decision**: Use existing `concept_relationships` table with "depends-on" relationship type.
**Rationale**: Leverages existing infrastructure; grounded in extracted data.
**Alternatives Rejected**: Pure LLM would be slower and less reliable.

---

## Key Findings Summary

| Topic | Decision | Source |
|-------|----------|--------|
| Learning Sequence | `SequentialAgent(Tutor → Quiz → Feedback)` | ADK docs |
| Mastery Loop | `LoopAgent` + custom `MasteryChecker` | ADK docs |
| Routing | LLM-driven via `sub_agents` descriptions | ADK docs |
| State Sharing | `session.state` with documented key conventions | ADK pattern |
| Transition Tracking | New `agent_transitions` table in storage | Custom extension |
| Interruption Handling | Coordinator instruction + state flags | ADK pattern |
| Migration | Incremental with parallel definitions | Best practice |
| Prerequisites | Query `concept_relationships` table | Existing storage |

## Dependencies Identified

| Dependency | Status | Notes |
|------------|--------|-------|
| `google.adk.agents.SequentialAgent` | Available | Part of google-adk package |
| `google.adk.agents.LoopAgent` | Available | Part of google-adk package |
| `concept_relationships` table | Available | Already in `storage.py` |
| pytest fixtures for agents | Needs creation | Per spec 003-test-evaluation |

## Implementation Notes

1. **No NEEDS CLARIFICATION items** - All technical context resolved
2. **ADK patterns validated** - SequentialAgent, LoopAgent, LLM delegation confirmed
3. **State key conventions defined** - Ready for data-model.md
4. **Migration path clear** - Incremental approach minimizes risk

## Next Steps

Proceed to Phase 1: Generate design artifacts (data-model.md, contracts/, quickstart.md)
