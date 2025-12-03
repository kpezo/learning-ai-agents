# Feature Specification: ADK Implementation Guide

**Feature Branch**: `009-adk-implementation-guide`
**Created**: 2025-12-03
**Status**: Draft
**Input**: User description: "Create an ADK implementation guide that maps Kaggle Days course concepts (multi-agent patterns, tools, memory, sessions, observability, evaluation, deployment) to existing feature specs (001-008), providing code patterns, architectural decisions, and implementation references for developers building these features"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Pattern Lookup by Feature Spec (Priority: P1)

A developer working on a specific feature spec (e.g., 004-storage-enhancements) needs to find the relevant ADK patterns, code examples, and implementation approaches from the Kaggle Days content. They look up the spec number and get a curated list of applicable ADK concepts with references to specific day content.

**Why this priority**: This is the core value - developers need fast mapping from "what I'm building" to "how to build it with ADK."

**Independent Test**: Can be tested by selecting any spec (001-008) and verifying the guide returns relevant ADK patterns with day/section references.

**Acceptance Scenarios**:

1. **Given** a developer working on spec 007 (Multi-Agent Orchestration), **When** they consult the guide, **Then** they find references to Day 1 multi-agent patterns (Sequential, Parallel, Loop, LLM-based orchestration).

2. **Given** a developer working on spec 003 (Test Evaluation), **When** they consult the guide, **Then** they find references to Day 4 evaluation framework (evalset files, test_config.json, adk eval CLI).

3. **Given** a developer working on spec 004 (Storage Enhancements), **When** they consult the guide, **Then** they find references to Day 3 memory management (Sessions, Memory Bank, MemoryService).

---

### User Story 2 - Code Pattern Reference (Priority: P1)

A developer needs to implement a specific ADK feature (e.g., session persistence, tool creation) and wants example code patterns. The guide provides canonical code snippets from the Kaggle Days content that can be adapted to the project.

**Why this priority**: Equally critical - developers need working code examples, not just conceptual explanations.

**Independent Test**: Can be tested by looking up a pattern (e.g., "FunctionTool creation") and verifying working code with proper imports is provided.

**Acceptance Scenarios**:

1. **Given** a developer needs to create a custom tool, **When** they look up "FunctionTool," **Then** they find the pattern with type hints, docstrings, and return dict format from Day 2.

2. **Given** a developer needs to implement session state sharing, **When** they look up "output_key," **Then** they find the state passing pattern with `{variable}` syntax from Day 1.

3. **Given** a developer needs to add callbacks for auto-save, **When** they look up "callbacks," **Then** they find the after_agent_callback pattern from Day 3.

---

### User Story 3 - Architecture Decision Guidance (Priority: P2)

A developer faces an architectural decision (e.g., "should I use SequentialAgent or LoopAgent for the learning cycle?"). The guide provides decision criteria and trade-offs from the Kaggle Days content.

**Why this priority**: Reduces architectural mistakes by providing documented decision frameworks.

**Independent Test**: Can be tested by posing an architectural question and verifying the guide provides a decision matrix with pros/cons.

**Acceptance Scenarios**:

1. **Given** a developer choosing between orchestration patterns, **When** they consult the decision guide, **Then** they find the Day 1 decision framework (LLM-based for dynamic routing, Sequential for deterministic order, Parallel for independent tasks, Loop for iterative refinement).

2. **Given** a developer choosing memory strategy, **When** they consult the guide, **Then** they find the Day 3 comparison (load_memory vs preload_memory, InMemoryMemoryService vs VertexAiMemoryBankService).

3. **Given** a developer choosing deployment target, **When** they consult the guide, **Then** they find the Day 5 deployment matrix (Agent Engine vs Cloud Run vs GKE).

---

### User Story 4 - Spec-to-Day Content Cross-Reference (Priority: P2)

The guide provides a comprehensive mapping table showing which Kaggle Days content is relevant to each spec, enabling developers to study the right material before implementation.

**Why this priority**: Provides structured learning path for developers new to the codebase.

**Independent Test**: Can be tested by selecting any day (1-5) and verifying the reverse mapping to applicable specs is accurate.

**Acceptance Scenarios**:

1. **Given** the cross-reference table, **When** a developer looks at Day 1 mappings, **Then** they see it applies to 007 (orchestration patterns), 001 (agent tools for difficulty), and the base agent architecture.

2. **Given** the cross-reference table, **When** a developer looks at Day 4 mappings, **Then** they see it applies to 003 (evaluation framework) and 008 (pedagogical metrics validation).

3. **Given** the cross-reference table, **When** a developer looks at Day 5 mappings, **Then** they see it applies to 005 (deployment) and 004 (Memory Bank for cloud sync).

---

### User Story 5 - Implementation Checklist by Spec (Priority: P3)

For each spec, the guide provides a checklist of ADK implementation steps derived from the Kaggle Days content, ensuring developers don't miss important patterns.

**Why this priority**: Nice to have for ensuring completeness, but developers can work from the pattern references.

**Independent Test**: Can be tested by selecting a spec and verifying the checklist covers all relevant ADK patterns.

**Acceptance Scenarios**:

1. **Given** spec 004 (Storage Enhancements), **When** viewing the checklist, **Then** it includes: configure SessionService, implement state tools with ToolContext, set up MemoryService, add memory tools to agents.

2. **Given** spec 007 (Multi-Agent Orchestration), **When** viewing the checklist, **Then** it includes: define sub_agents, choose orchestration pattern, configure output_key for state passing, implement exit conditions for loops.

3. **Given** spec 003 (Test Evaluation), **When** viewing the checklist, **Then** it includes: create test_config.json, write evalset.json files, add LoggingPlugin, configure adk eval command.

---

### Edge Cases

- What if a spec has no direct ADK pattern mapping? Guide identifies the gaps and suggests general Python approaches or external libraries.
- How does the guide handle conflicting patterns? Guide notes when multiple approaches exist and provides selection criteria.
- What if Kaggle Days content is updated? Guide includes version references and links to source day content.
- What if a learner keeps getting a concept wrong? After 3 failed attempts, system provides scaffolded help (simpler explanation, hints, or breaks concept into sub-concepts).
- What if concepts cannot be extracted from PDF? System logs extraction failure, notifies user, and allows manual concept entry as fallback.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Guide MUST provide a spec-to-ADK-pattern mapping for all specs (001-008).

- **FR-002**: Guide MUST include code patterns with proper ADK imports for each mapped concept.

- **FR-003**: Guide MUST reference specific Kaggle Days content (day number and section) for each pattern.

- **FR-004**: Guide MUST provide decision matrices for architectural choices (orchestration, memory, deployment).

- **FR-005**: Guide MUST include a cross-reference table: Day → Applicable Specs and Spec → Applicable Days.

- **FR-006**: Guide MUST provide implementation checklists for each spec.

- **FR-007**: Guide MUST document the 4 orchestration patterns: LLM-Based, Sequential, Parallel, Loop.

- **FR-008**: Guide MUST document tool creation patterns: FunctionTool, AgentTool, MCP Tools.

- **FR-009**: Guide MUST document session management: InMemorySessionService, DatabaseSessionService, session state.

- **FR-010**: Guide MUST document memory patterns: MemoryService, load_memory, preload_memory, callbacks for auto-save.

- **FR-011**: Guide MUST document observability patterns: LoggingPlugin, custom plugins, debug logging.

- **FR-012**: Guide MUST document evaluation patterns: evalset files, test_config.json, adk eval CLI, user simulation.

- **FR-013**: Guide MUST document deployment patterns: to_a2a(), Agent Engine configuration, container setup.

- **FR-014**: Guide MUST include copy-pastable code snippets that work with the project's existing structure.

- **FR-015**: Guide MUST be stored in a developer-accessible location (planning/adk-guide.md or similar).

### Key Entities

- **SpecMapping**: A mapping entry linking a spec number to relevant ADK patterns, with day references and code snippets.

- **PatternReference**: A documented ADK pattern including name, description, code example, and Kaggle Days source.

- **DecisionMatrix**: A structured comparison of architectural options with criteria, pros, cons, and recommendation triggers.

- **CrossReferenceTable**: Bidirectional mapping between Kaggle Days content and spec numbers.

- **ImplementationChecklist**: An ordered list of ADK implementation steps for a specific spec.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Every spec (001-008) has at least 3 mapped ADK patterns with code references.

- **SC-002**: Developers can find relevant ADK content for any spec within 30 seconds using the cross-reference table.

- **SC-003**: Code snippets in the guide compile without errors when pasted into the project (given proper imports).

- **SC-004**: Decision matrices cover all major architectural choices identified in specs (orchestration, memory, deployment, evaluation).

- **SC-005**: Implementation checklists for each spec achieve 90% coverage of required ADK patterns.

- **SC-006**: Guide references all 5 Kaggle Days with at least 5 patterns from each day.

## Clarifications

### Session 2025-12-03

- Q: How should the system classify extracted concepts into knowledge types? → A: AI infers from text patterns (automatic classification using linguistic markers: "X is..." → declarative, "To do X..." → procedural, "If X then Y" → conditional)
- Q: How should mastery score be calculated, and should different knowledge types have different weights? → A: Simple ratio (correct_answers / total_questions) with equal weight across all knowledge types
- Q: What triggers the transition from one learning phase to the next? → A: Mastery-based transitions (auto-advance when score ≥ 0.8 threshold)
- Q: How should concept relationships (prerequisite, builds_on, related) be discovered? → A: Use existing Relationship Agent from adk/question_pipeline.py
- Q: What happens when a learner keeps getting a concept wrong? → A: After 3 failed attempts, provide scaffolded help (simpler explanation, hints, or break into sub-concepts)

## Assumptions

- The Kaggle Days content (day1-day5-explanation.md) is the authoritative source for ADK patterns.
- Code examples will be adapted to match the project's existing import paths and conventions (e.g., `adk/` structure).
- The guide is a static document; dynamic tooling for lookup is out of scope.
- Patterns are indexed by both spec number and concept name for flexible lookup.
- The guide complements (not replaces) the detailed spec documents.
- Knowledge type classification uses AI inference from linguistic patterns (no manual annotation required).
- Mastery scoring uses simple ratio (correct/total) with equal weight across knowledge types.
- Learning phase transitions are mastery-gated at 0.8 threshold.
- Concept relationships are discovered via existing Relationship Agent in adk/question_pipeline.py.
- Scaffolded help triggers after 3 consecutive failures on a concept.

---

## Spec-to-ADK Pattern Mapping

### 001-adaptive-difficulty

| ADK Concept | Day | Section | Code Pattern |
|-------------|-----|---------|--------------|
| FunctionTool | Day 2 | Custom Function Tools | Create `adjust_difficulty(performance, current_level)` tool |
| Session State | Day 3 | Session.State | Store difficulty level in `tool_context.state["user:difficulty_level"]` |
| output_key | Day 1 | State Management | Pass performance data between agents via output_key |
| Callbacks | Day 3 | Automating Memory | Use `after_tool_callback` to trigger difficulty recalculation |

**Implementation Checklist:**
- [ ] Create FunctionTool for difficulty adjustment logic
- [ ] Store performance metrics in session state with `user:` prefix
- [ ] Use output_key for passing data if using multi-agent pattern
- [ ] Add callback to auto-update difficulty after quiz answers

---

### 002-pdf-reports

| ADK Concept | Day | Section | Code Pattern |
|-------------|-----|---------|--------------|
| FunctionTool | Day 2 | Custom Function Tools | Create `generate_report(user_id)` tool returning PDF bytes |
| Session State | Day 3 | Session.State | Read user progress from `tool_context.state` |
| Manual Memory Search | Day 3 | Memory Operations | Use `memory_service.search_memory()` for historical data |

**Implementation Checklist:**
- [ ] Create FunctionTool wrapping PDF generation library
- [ ] Access learning history via session state or storage
- [ ] Query MemoryService for cross-session data aggregation

---

### 003-test-evaluation

| ADK Concept | Day | Section | Code Pattern |
|-------------|-----|---------|--------------|
| Evaluation Framework | Day 4 | Systematic Evaluation | Create `.evalset.json` files for agent scenarios |
| test_config.json | Day 4 | Evaluation Configuration | Define thresholds: `response_match_score`, `tool_trajectory_avg_score` |
| adk eval CLI | Day 4 | CLI Evaluation | Run `adk eval agent/ tests/ --config_file_path=config.json` |
| LoggingPlugin | Day 4 | Production Logging | Add `plugins=[LoggingPlugin()]` to Runner |
| Custom Plugin | Day 4 | Plugins and Callbacks | Create `CountInvocationPlugin` for test metrics |
| User Simulation | Day 4 | User Simulation | Use `UserSimulationEvaluator` for conversation testing |

**Implementation Checklist:**
- [ ] Create test_config.json with pass thresholds
- [ ] Write evalset.json files for each agent scenario
- [ ] Configure adk eval in CI pipeline
- [ ] Add LoggingPlugin to Runner for observability
- [ ] Create custom metrics plugin if needed

---

### 004-storage-enhancements

| ADK Concept | Day | Section | Code Pattern |
|-------------|-----|---------|--------------|
| SessionService | Day 3 | Session Management | Use `DatabaseSessionService(db_url="sqlite:///data.db")` |
| Session Persistence | Day 3 | DatabaseSessionService | Persist sessions to SQLite |
| MemoryService | Day 3 | Memory - Long-Term | Use `InMemoryMemoryService` or `VertexAiMemoryBankService` |
| load_memory / preload_memory | Day 3 | Agent-Based Retrieval | Add memory tools: `tools=[load_memory]` or `tools=[preload_memory]` |
| auto_save_to_memory | Day 3 | Automating Memory Storage | Implement `after_agent_callback` for auto-save |
| Session State | Day 3 | Session.State | Store user preferences in `tool_context.state["user:*"]` |
| Memory Bank | Day 5 | Memory Bank | Configure for cross-session persistence |

**Implementation Checklist:**
- [ ] Replace InMemorySessionService with DatabaseSessionService
- [ ] Configure MemoryService for long-term storage
- [ ] Add load_memory or preload_memory tool to agents
- [ ] Implement after_agent_callback for automatic memory saves
- [ ] Define session state key conventions (`user:`, `app:`, `temp:`)

---

### 005-production-deployment

| ADK Concept | Day | Section | Code Pattern |
|-------------|-----|---------|--------------|
| to_a2a() | Day 5 | Exposing Agent via A2A | `app = to_a2a(root_agent, port=8001)` |
| FastAPI Integration | Day 5 | A2A Protocol | A2A creates FastAPI app automatically |
| Agent Card | Day 5 | Agent Cards | Served at `/.well-known/agent-card.json` |
| Health Check | Day 4 | ADK Web UI | Implement `/health` endpoint pattern |
| LoggingPlugin | Day 4 | Production Logging | Add `plugins=[LoggingPlugin()]` for production observability |
| Container | Day 5 | Cloud Run Deployment | Create Dockerfile with `adk api_server` command |

**Implementation Checklist:**
- [ ] Wrap agent with to_a2a() for HTTP API
- [ ] Create Dockerfile based on Day 5 pattern
- [ ] Add LoggingPlugin for production logging
- [ ] Implement /health endpoint
- [ ] Configure environment variables (GOOGLE_API_KEY, etc.)

---

### 006-knowledge-graph-schema

| ADK Concept | Day | Section | Code Pattern |
|-------------|-----|---------|--------------|
| FunctionTool | Day 2 | Custom Function Tools | Create `get_prerequisites(concept)`, `get_descendants(concept)` tools |
| AgentTool | Day 1 | Agent Tools | Create specialist `ConceptExtractorAgent` for LLM extraction |
| SequentialAgent | Day 1 | Sequential Workflow | Chain: IngestAgent → ConceptAgent → RelationshipAgent |
| Session State | Day 3 | Session.State | Cache extracted concepts in state during processing |

**Implementation Checklist:**
- [ ] Create FunctionTools for graph queries
- [ ] Use SequentialAgent for extraction pipeline
- [ ] Store intermediate extraction results via output_key
- [ ] Create specialist agents for concept and relationship extraction

---

### 007-multi-agent-orchestration

| ADK Concept | Day | Section | Code Pattern |
|-------------|-----|---------|--------------|
| sub_agents | Day 1 | Multi-Agent Systems | `Agent(..., sub_agents=[specialist_agents])` |
| AgentTool | Day 1 | AgentTool | `tools=[AgentTool(specialist_agent)]` |
| SequentialAgent | Day 1 | Sequential Workflow | `SequentialAgent(sub_agents=[tutor, quiz, feedback])` |
| LoopAgent | Day 1 | Loop Workflow | `LoopAgent(sub_agents=[...], max_iterations=5)` |
| ParallelAgent | Day 1 | Parallel Workflow | `ParallelAgent(sub_agents=[...])` for independent tasks |
| output_key | Day 1 | State Management | Share data: `output_key="diagnostic_results"` → `{diagnostic_results}` |
| FunctionTool exit_loop | Day 1 | Loop Workflow | Create exit function for loop termination |
| LLM-Based Routing | Day 1 | LLM-Based Orchestration | Coordinator instruction guides delegation |

**Implementation Checklist:**
- [ ] Define 5 specialist agents (Diagnostic, Tutor, Quiz, Feedback, PathPlanner)
- [ ] Create Coordinator agent with sub_agents
- [ ] Choose orchestration pattern for learning cycle (LoopAgent recommended)
- [ ] Define output_key for each agent's state contribution
- [ ] Create exit_loop FunctionTool for mastery completion
- [ ] Configure max_iterations as safety limit

---

### 008-pedagogical-metrics

| ADK Concept | Day | Section | Code Pattern |
|-------------|-----|---------|--------------|
| FunctionTool | Day 2 | Custom Function Tools | Create BKT calculation tools |
| Session State | Day 3 | Session.State | Store mastery probabilities in state |
| Evaluation | Day 4 | Agent Evaluation | Create evalset for metric accuracy validation |
| Callbacks | Day 3 | Callbacks | Use callbacks to update metrics after each answer |

**Implementation Checklist:**
- [ ] Create FunctionTools for BKT, IRT, ZPD calculations
- [ ] Store metric state with appropriate key prefixes
- [ ] Write evaluation scenarios to validate metric predictions
- [ ] Add callbacks for real-time metric updates

---

## Decision Matrices

### Orchestration Pattern Selection (Day 1)

| Pattern | Use When | Example in This Project |
|---------|----------|------------------------|
| **LLM-Based** | Dynamic routing based on content | Coordinator routing to specialists (007) |
| **Sequential** | Fixed order, each step builds on previous | Learning cycle: Tutor → Quiz → Feedback (007) |
| **Parallel** | Independent tasks, speed matters | Multi-topic research (not currently in specs) |
| **Loop** | Iterative refinement until condition | Quiz until mastery achieved (007, 001) |

### Memory Strategy Selection (Day 3)

| Strategy | Use When | Applicable Specs |
|----------|----------|-----------------|
| **Session State** | Within-session, short-term | All specs (difficulty level, quiz state) |
| **load_memory** | On-demand cross-session | 002 (report generation) |
| **preload_memory** | Always-needed context | 004 (personalization) |
| **DatabaseSessionService** | Persist across restarts | 004, 005 |
| **MemoryService** | Long-term knowledge | 004 (semantic memory) |

### SessionService Selection (Day 3)

| Service | Persistence | Use Case |
|---------|-------------|----------|
| **InMemorySessionService** | None (dev only) | Testing, prototyping |
| **DatabaseSessionService** | SQLite/PostgreSQL | Production single-machine |
| **Vertex AI Memory Bank** | Cloud | Multi-device, production |

---

## Code Pattern Reference

### Creating a FunctionTool (Day 2)

```python
from google.adk.tools import FunctionTool

def adjust_difficulty(
    current_level: int,
    score: float,
    hints_used: int
) -> dict:
    """Adjusts quiz difficulty based on learner performance.

    Args:
        current_level: Current difficulty level (1-6)
        score: Score on last question (0.0-1.0)
        hints_used: Number of hints used

    Returns:
        Dictionary with new difficulty and adjustment reason.
    """
    if score >= 0.85 and hints_used == 0:
        new_level = min(current_level + 1, 6)
        reason = "Excellent performance, increasing difficulty"
    elif score < 0.50:
        new_level = max(current_level - 1, 1)
        reason = "Struggling, decreasing difficulty"
    else:
        new_level = current_level
        reason = "Maintaining current level"

    return {
        "status": "success",
        "previous_level": current_level,
        "new_level": new_level,
        "reason": reason
    }

# Add to agent
agent = LlmAgent(
    ...,
    tools=[adjust_difficulty]  # ADK auto-wraps as FunctionTool
)
```

### Session State Access (Day 3)

```python
from google.adk.tools.tool_context import ToolContext

def save_difficulty_level(
    tool_context: ToolContext,
    level: int
) -> dict:
    """Save current difficulty level to session state."""
    tool_context.state["user:difficulty_level"] = level
    return {"status": "saved", "level": level}

def get_difficulty_level(tool_context: ToolContext) -> dict:
    """Retrieve current difficulty level from session state."""
    level = tool_context.state.get("user:difficulty_level", 3)  # Default: 3
    return {"status": "success", "level": level}
```

### Sequential Agent Pattern (Day 1)

```python
from google.adk.agents import Agent, SequentialAgent

# Step 1: Tutor explains
tutor_agent = Agent(
    name="TutorAgent",
    instruction="Explain the concept: {topic}",
    output_key="explanation"
)

# Step 2: Quiz assesses
quiz_agent = Agent(
    name="QuizAgent",
    instruction="Based on: {explanation}, create a quiz question",
    output_key="quiz_result"
)

# Step 3: Feedback analyzes
feedback_agent = Agent(
    name="FeedbackAgent",
    instruction="Analyze quiz result: {quiz_result}. Provide feedback.",
    output_key="feedback"
)

# Combine in sequence
learning_cycle = SequentialAgent(
    name="LearningCycle",
    sub_agents=[tutor_agent, quiz_agent, feedback_agent]
)
```

### Loop Agent with Exit Condition (Day 1)

```python
from google.adk.agents import Agent, LoopAgent
from google.adk.tools import FunctionTool

def exit_on_mastery():
    """Exit the learning loop when mastery is achieved."""
    return {"status": "mastery_achieved", "message": "Congratulations!"}

mastery_checker = Agent(
    name="MasteryChecker",
    instruction="""Check if score in {quiz_result} is >= 85%.
    If mastered, call exit_on_mastery function.
    Otherwise, provide encouragement to continue.""",
    tools=[FunctionTool(exit_on_mastery)]
)

mastery_loop = LoopAgent(
    name="MasteryLoop",
    sub_agents=[tutor_agent, quiz_agent, mastery_checker],
    max_iterations=5  # Safety limit
)
```

### Memory Auto-Save Callback (Day 3)

```python
async def auto_save_to_memory(callback_context):
    """Automatically save session to memory after each agent turn."""
    await callback_context._invocation_context.memory_service.add_session_to_memory(
        callback_context._invocation_context.session
    )

agent = LlmAgent(
    name="MemoryAgent",
    tools=[preload_memory],
    after_agent_callback=auto_save_to_memory
)
```

### Evaluation Set Structure (Day 4)

```json
{
  "eval_set_id": "tutor_agent_tests",
  "eval_cases": [
    {
      "eval_id": "explain_derivative",
      "conversation": [
        {
          "user_content": {
            "parts": [{"text": "Explain what a derivative is"}]
          },
          "final_response": {
            "parts": [{"text": "A derivative measures the rate of change..."}]
          },
          "intermediate_data": {
            "tool_uses": []
          }
        }
      ]
    }
  ]
}
```

### A2A Server Setup (Day 5)

```python
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from adk.agent import root_agent

# Convert agent to A2A-compatible server
app = to_a2a(root_agent, port=8000)

# Run with: uvicorn server:app --host 0.0.0.0 --port 8000
```

---

## Cross-Reference Table

### Day → Applicable Specs

| Day | Primary Topics | Applicable Specs |
|-----|---------------|------------------|
| **Day 1** | Agent basics, multi-agent patterns, orchestration | 007, 001 (agent structure) |
| **Day 2** | Tools (Function, Code Execution, MCP, LRO) | All specs (tools are fundamental) |
| **Day 3** | Sessions, Memory, Context Compaction | 004, 001, 002, 008 |
| **Day 4** | Observability, Evaluation | 003, 008 (validation) |
| **Day 5** | A2A Protocol, Deployment, Memory Bank | 005, 004 (cloud sync) |

### Spec → Primary Day References

| Spec | Primary Days | Key Concepts |
|------|--------------|--------------|
| **001** | Day 2, Day 3 | FunctionTool, session state, callbacks |
| **002** | Day 2, Day 3 | FunctionTool, memory search |
| **003** | Day 4 | Evaluation framework, plugins, observability |
| **004** | Day 3, Day 5 | SessionService, MemoryService, Memory Bank |
| **005** | Day 5, Day 4 | A2A, deployment, logging |
| **006** | Day 1, Day 2 | Sequential pipeline, custom tools |
| **007** | Day 1 | All orchestration patterns |
| **008** | Day 2, Day 3, Day 4 | Tools, state, evaluation |
