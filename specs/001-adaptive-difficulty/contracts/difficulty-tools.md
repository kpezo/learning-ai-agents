# Tool Contracts: Adaptive Difficulty System

**Feature**: 001-adaptive-difficulty | **Date**: 2025-12-03

## ADK FunctionTool Interfaces

These tools are exposed via Google ADK's `FunctionTool` wrapper and are callable by the agent.

---

### get_difficulty_level

Returns the current difficulty level and metadata for the session.

**Signature**:
```python
def _get_difficulty_level(tool_context: ToolContext = None) -> Dict[str, Any]
```

**Parameters**: None (uses session state)

**Returns**:
```json
{
  "status": "success",
  "level": 3,
  "name": "Application",
  "hint_allowance": 1,
  "hints_remaining": 1,
  "question_types": ["scenario", "case_study", "problem_solving"],
  "scaffolding_active": false
}
```

**Error Response**:
```json
{
  "status": "error",
  "error_message": "Quiz not prepared. Call prepare_quiz first."
}
```

---

### set_difficulty_level

Manually set difficulty level (used at session start or for testing).

**Signature**:
```python
def _set_difficulty_level(
    level: int,
    tool_context: ToolContext = None
) -> Dict[str, Any]
```

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| level | int | Yes | Target difficulty level (1-6) |

**Returns**:
```json
{
  "status": "success",
  "previous_level": 3,
  "new_level": 4,
  "level_name": "Analysis",
  "hint_allowance": 0
}
```

**Validation**: Level is clamped to 1-6 range.

---

### record_performance

Record performance metrics for the current answer and trigger difficulty evaluation.

**Signature**:
```python
def _record_performance(
    score: float,
    response_time_ms: int = 0,
    hints_used: int = 0,
    concept_name: str = "",
    question_type: str = "",
    tool_context: ToolContext = None
) -> Dict[str, Any]
```

**Parameters**:
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| score | float | Yes | - | Score for this answer (0.0-1.0) |
| response_time_ms | int | No | 0 | Time taken to answer in ms |
| hints_used | int | No | 0 | Number of hints used |
| concept_name | str | No | "" | Concept being tested |
| question_type | str | No | "" | Type of question asked |

**Returns**:
```json
{
  "status": "success",
  "performance_recorded": true,
  "in_optimal_zone": true,
  "difficulty_adjustment": {
    "type": "maintain",
    "previous_level": 3,
    "new_level": 3,
    "reason": "Performance in optimal zone (60-85%)"
  },
  "trend": {
    "avg_score": 0.72,
    "trend_direction": "stable",
    "consecutive_correct": 2
  }
}
```

**Adjustment triggered when**:
- 3 consecutive correct (≥85%): INCREASE
- 2 consecutive incorrect (<50%): DECREASE
- Otherwise: MAINTAIN

---

### get_difficulty_hint

Get a hint appropriate for the current difficulty level.

**Signature**:
```python
def _get_difficulty_hint(
    hint_number: int = 1,
    tool_context: ToolContext = None
) -> Dict[str, Any]
```

**Parameters**:
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| hint_number | int | No | 1 | Which hint to retrieve (1-based) |

**Returns** (success):
```json
{
  "status": "success",
  "hint_number": 1,
  "hint_text": "Think about the basic definition...",
  "hints_remaining": 2,
  "hints_allowed": 3
}
```

**Returns** (no hints available):
```json
{
  "status": "error",
  "error_message": "No hints available at difficulty level 4 (Analysis)"
}
```

**Returns** (hints exhausted):
```json
{
  "status": "error",
  "error_message": "All hints used for this question (3/3)"
}
```

---

### get_scaffolding

Get scaffolding support for a struggling learner.

**Signature**:
```python
def _get_scaffolding(
    struggle_area: str = "",
    concept_name: str = "",
    tool_context: ToolContext = None
) -> Dict[str, Any]
```

**Parameters**:
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| struggle_area | str | No | "" | Type: definition, process, relationship, application |
| concept_name | str | No | "" | Specific concept for context |

**Returns**:
```json
{
  "status": "success",
  "struggle_area": "definition",
  "hints": [
    "Let's start with the basic definition of the concept.",
    "The key word here is...",
    "Think about what this means in simple terms."
  ],
  "strategies": [
    "Focus on the core meaning first",
    "Look for keywords that define the concept",
    "Connect to something you already know"
  ],
  "simplified_question_suggestion": "Ask for recognition instead of recall",
  "active": true
}
```

**Auto-detection**: If `struggle_area` not provided, system infers from recent error patterns.

---

### get_performance_trend

Get aggregated performance trend analysis.

**Signature**:
```python
def _get_performance_trend(
    window_size: int = 5,
    tool_context: ToolContext = None
) -> Dict[str, Any]
```

**Parameters**:
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| window_size | int | No | 5 | Number of recent answers to analyze |

**Returns**:
```json
{
  "status": "success",
  "window_size": 5,
  "records_analyzed": 5,
  "avg_score": 0.78,
  "score_trend": "improving",
  "avg_response_time_ms": 12500,
  "time_trend": "faster",
  "avg_hints_used": 0.4,
  "consecutive_correct": 3,
  "consecutive_incorrect": 0,
  "optimal_zone_ratio": 0.6,
  "recommendation": "Consider increasing difficulty"
}
```

---

### get_concept_difficulty_stats

Get difficulty-specific statistics for a concept.

**Signature**:
```python
def _get_concept_difficulty_stats(
    concept_name: str,
    tool_context: ToolContext = None
) -> Dict[str, Any]
```

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| concept_name | str | Yes | Concept to analyze |

**Returns**:
```json
{
  "status": "success",
  "concept_name": "quadratic_equations",
  "avg_difficulty_achieved": 3.5,
  "max_difficulty_achieved": 4,
  "difficulty_distribution": {
    "1": 2,
    "2": 3,
    "3": 5,
    "4": 1
  },
  "struggle_area": "application",
  "complexity": 4,
  "mastery_level": 0.72
}
```

---

## Session State Keys

These keys are used in the ADK session state (`tool_context.state`):

| Key | Type | Description |
|-----|------|-------------|
| `difficulty:level` | int | Current difficulty level (1-6) |
| `difficulty:history` | List[Dict] | Recent performance records |
| `difficulty:scaffolding_active` | bool | Whether scaffolding is enabled |
| `difficulty:hints_used_current` | int | Hints used on current question |
| `difficulty:consecutive_correct` | int | Correct answer streak |
| `difficulty:consecutive_incorrect` | int | Incorrect answer streak |
| `difficulty:last_adjustment` | Dict | Last difficulty adjustment details |

---

## Integration with Existing Tools

### prepare_quiz (Extended)

**Additional behavior**:
1. Initialize `difficulty:level` to 3 (Application) or from user history
2. Reset hint and streak counters
3. Set `difficulty:scaffolding_active` to False

### advance_quiz (Extended)

**Additional behavior**:
1. Call `record_performance` internally with answer data
2. Include difficulty adjustment result in response
3. Trigger scaffolding if difficulty decreased

**Extended Response**:
```json
{
  "status": "success",
  "done": false,
  "next_question_number": 3,
  "difficulty": {
    "current_level": 3,
    "adjusted": false,
    "scaffolding_active": false
  }
}
```
