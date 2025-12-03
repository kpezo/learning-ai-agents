# Research: Adaptive Difficulty System

**Feature**: 001-adaptive-difficulty | **Date**: 2025-12-03

## Technical Decisions

### 1. Difficulty Level Data Structure

**Decision**: Use an enum-like dataclass with level metadata.

**Rationale**: Each difficulty level (1-6) has associated properties: name, allowed question types, hint allowance, and time pressure factor. A dataclass provides type safety and easy serialization.

**Alternatives considered**:
- Dict-based configuration: Rejected due to lack of type checking
- Class inheritance per level: Over-engineered for 6 static levels

### 2. Performance Trend Algorithm

**Decision**: Use exponential moving average (EMA) with configurable window size.

**Rationale**: EMA gives more weight to recent performance while smoothing out individual question variance. This aligns with FR-002 (3-answer threshold) and FR-003 (2-answer threshold).

**Alternatives considered**:
- Simple moving average: Less responsive to recent changes
- Raw last-N average: Too volatile, single outliers cause false adjustments

**Implementation**:
```python
# Increase: EMA > 85% over 3 answers, no hints used
# Decrease: 2 consecutive < 50%
# Maintain: Otherwise (60-85% optimal zone)
```

### 3. Session State Management

**Decision**: Extend existing `quiz:*` session state keys with `difficulty:*` namespace.

**Rationale**: The current quiz_tools.py uses session state for quiz progress. Difficulty state should follow the same pattern for consistency.

**State keys**:
- `difficulty:level` - Current difficulty (1-6)
- `difficulty:history` - List of recent performance records
- `difficulty:scaffolding_active` - Whether scaffolding hints are enabled
- `difficulty:hints_used` - Hints used on current question

### 4. Storage Schema Extension

**Decision**: Add new tables to existing SQLite schema in storage.py.

**Rationale**: The existing StorageService pattern handles schema initialization cleanly. New tables maintain separation of concerns.

**New tables**:
- `performance_records` - Per-answer metrics (score, time, hints, difficulty, concept)
- `difficulty_history` - Tracks difficulty adjustments with reasons
- `scaffolding_usage` - Records scaffolding hint effectiveness

### 5. Scaffolding Strategy Selection

**Decision**: Map struggle areas to hint strategies via lookup table.

**Rationale**: The spec defines 4 struggle areas (definition, process, relationship, application). Each maps to specific hint strategies that can be selected based on question type and error pattern.

**Struggle area detection**:
- Definition: Errors on recognition/definition questions
- Process: Errors on sequential/procedural questions
- Relationship: Errors on comparison/connection questions
- Application: Errors on scenario/case study questions

### 6. Question Type to Difficulty Mapping

**Decision**: Define allowed question types per difficulty level in configuration.

**Rationale**: This mapping enables the assessor agent to generate appropriate questions. The LLM prompt will include the allowed types for the current level.

**Mapping** (from spec FR-005):
| Level | Name | Question Types |
|-------|------|----------------|
| 1 | Foundation | definition, recognition, true/false |
| 2 | Understanding | explanation, comparison, cause-effect |
| 3 | Application | scenario, case-study, problem-solving |
| 4 | Analysis | breakdown, pattern-recognition, critique |
| 5 | Synthesis | design, integration, hypothesis |
| 6 | Mastery | teach-back, edge-case, meta-cognition |

### 7. Hint Allowance Enforcement

**Decision**: Track hints at session level, enforce limits in get_hint tool.

**Rationale**: Hint limits (3/2/1/0/0/0 for levels 1-6) are enforced when requesting hints. Usage is tracked for difficulty adjustment.

### 8. Integration Approach

**Decision**: Create new `difficulty.py` and `scaffolding.py` modules; extend quiz_tools.py.

**Rationale**: New modules encapsulate complexity. Existing quiz flow is extended rather than replaced, maintaining backward compatibility.

**Integration points**:
- `prepare_quiz`: Initialize difficulty level (default 3 or from history)
- `advance_quiz`: Record performance, calculate adjustment
- New `get_difficulty_hint`: Provide level-appropriate hints
- New `get_scaffolding`: Provide scaffolding when difficulty decreases

## Dependencies Research

### Google ADK Session State

- Session state is a dict-like object accessed via `tool_context.state`
- State persists within a session, cleared on session end
- Lists and dicts are stored/retrieved correctly
- No size limits observed for typical use cases

### Gemini Model for Question Generation

- Model receives difficulty level and allowed types in system prompt
- Can generate questions with specific Bloom's taxonomy levels
- Prompt template should include explicit examples for each level

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| Question generation doesn't match difficulty | Include explicit examples in prompt |
| Performance history lost on session end | Persist to SQLite after each answer |
| Scaffolding hints too generic | Use concept-specific templates |
| Response time measurement inaccurate | Accept browser-side timing limitations |
