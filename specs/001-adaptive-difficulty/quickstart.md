# Quickstart: Adaptive Difficulty System

**Feature**: 001-adaptive-difficulty | **Date**: 2025-12-03

## Overview

The adaptive difficulty system extends the existing quiz flow with automatic difficulty adjustment based on learner performance. It tracks performance metrics, adjusts question difficulty (1-6 levels), and provides scaffolding support when learners struggle.

## Quick Integration

### 1. Import the new tools

```python
from adk.difficulty import (
    get_difficulty_level_tool,
    set_difficulty_level_tool,
    record_performance_tool,
    get_difficulty_hint_tool,
    get_performance_trend_tool,
)
from adk.scaffolding import get_scaffolding_tool
```

### 2. Add tools to your agent

```python
from adk.agent import _make_specialist

assessor = _make_specialist(
    "assessor",
    extra_tools=[
        get_difficulty_level_tool,
        set_difficulty_level_tool,
        record_performance_tool,
        get_difficulty_hint_tool,
        get_scaffolding_tool,
        get_performance_trend_tool,
    ],
)
```

### 3. Update agent instructions

Add to the assessor agent's instruction:

```text
You have access to an adaptive difficulty system. Before generating questions:
1. Call get_difficulty_level to get the current level and allowed question types
2. Generate questions ONLY from the allowed types for that level
3. After the learner answers, call record_performance with their score

Difficulty levels:
- Level 1 (Foundation): definition, recognition, true/false questions
- Level 2 (Understanding): explanation, comparison questions
- Level 3 (Application): scenario, problem-solving questions
- Level 4 (Analysis): breakdown, pattern recognition questions
- Level 5 (Synthesis): design, integration questions
- Level 6 (Mastery): teach-back, edge case questions

If scaffolding is active (after difficulty decrease), provide the scaffolding
hints to help the learner before the next question.
```

## Basic Usage Flow

### Starting a Quiz

```python
# Existing prepare_quiz will now initialize difficulty
result = prepare_quiz_tool.run(topic="algebra", tool_context=ctx)
# difficulty:level is set to 3 (Application) by default

# Or explicitly set starting difficulty
set_difficulty_level_tool.run(level=2, tool_context=ctx)
```

### During the Quiz

```python
# 1. Get current difficulty before generating question
difficulty = get_difficulty_level_tool.run(tool_context=ctx)
# Returns: {"level": 3, "question_types": ["scenario", "case_study", "problem_solving"], ...}

# 2. Generate appropriate question (done by agent using the question_types)

# 3. Learner answers, record performance
result = record_performance_tool.run(
    score=0.85,
    response_time_ms=15000,
    hints_used=0,
    concept_name="quadratic_equations",
    question_type="scenario",
    tool_context=ctx
)
# Returns: {"difficulty_adjustment": {"type": "maintain", ...}, ...}
```

### Handling Hints

```python
# Check if hints are available
difficulty = get_difficulty_level_tool.run(tool_context=ctx)
if difficulty["hint_allowance"] > 0:
    hint = get_difficulty_hint_tool.run(hint_number=1, tool_context=ctx)
    # Returns: {"hint_text": "...", "hints_remaining": 2}
```

### When Difficulty Decreases

```python
# After difficulty decrease, get scaffolding
scaffolding = get_scaffolding_tool.run(
    struggle_area="definition",  # or auto-detected
    concept_name="quadratic_equations",
    tool_context=ctx
)
# Returns hints, strategies, and simplified question suggestions
```

## Difficulty Levels Reference

| Level | Name | Question Types | Hints |
|-------|------|----------------|-------|
| 1 | Foundation | definition, recognition, true/false | 3 |
| 2 | Understanding | explanation, comparison, cause-effect | 2 |
| 3 | Application | scenario, case-study, problem-solving | 1 |
| 4 | Analysis | breakdown, pattern-recognition, critique | 0 |
| 5 | Synthesis | design, integration, hypothesis | 0 |
| 6 | Mastery | teach-back, edge-case, meta-cognition | 0 |

## Adjustment Rules

**Increase difficulty** when:
- 3 consecutive answers score ≥85%
- No hints used on those answers

**Decrease difficulty** when:
- 2 consecutive answers score <50%
- Scaffolding activates automatically

**Maintain difficulty** when:
- Scores are in 60-85% range (optimal learning zone)

## Common Patterns

### Check if learner is struggling

```python
trend = get_performance_trend_tool.run(window_size=5, tool_context=ctx)
if trend["consecutive_incorrect"] >= 2:
    # Difficulty will decrease, prepare scaffolding
    pass
```

### Get concept-specific recommendations

```python
from adk.quiz_tools import get_weak_concepts_tool

weak = get_weak_concepts_tool.run(threshold=0.5, tool_context=ctx)
# Focus on concepts with low mastery at appropriate difficulty
```

### Persist and restore difficulty across sessions

```python
# Difficulty history is automatically persisted to SQLite
# On new session, check user's historical difficulty:
from adk.storage import get_storage

storage = get_storage(user_id)
# Query difficulty_history for last session's final level
```

## Testing

```bash
# Run unit tests
pytest tests/unit/test_difficulty.py -v

# Run integration tests
pytest tests/integration/test_adaptive_quiz.py -v

# Test specific scenario
pytest tests/unit/test_difficulty.py::test_difficulty_increase -v
```
