# Tool Contracts: Multi-Agent Orchestration

**Branch**: `007-multi-agent-orchestration`
**Date**: 2025-12-03

## Overview

This document defines contracts for new tools added to support multi-agent orchestration.

---

## Diagnostic Tools (`adk/diagnostic_tools.py`)

### get_prerequisites

**Purpose**: Get prerequisite concepts for a topic from concept relationships.

```python
@FunctionTool
def get_prerequisites(topic: str) -> dict:
    """
    Get prerequisite concepts for a topic.

    Args:
        topic: The topic to find prerequisites for

    Returns:
        {
            "topic": str,
            "prerequisites": [
                {
                    "concept": str,
                    "relationship": str,  # "depends-on"
                    "confidence": float
                }
            ],
            "found_in_db": bool
        }
    """
```

### check_prerequisites_mastery

**Purpose**: Check if learner has mastery of all prerequisites.

```python
@FunctionTool
def check_prerequisites_mastery(
    topic: str,
    user_id: str,
    threshold: float = 0.5
) -> dict:
    """
    Check if learner has sufficient mastery of prerequisites.

    Args:
        topic: The target topic
        user_id: Learner's user ID
        threshold: Minimum mastery required (default 0.5)

    Returns:
        {
            "all_met": bool,
            "gaps": [
                {
                    "concept": str,
                    "current_mastery": float,
                    "required": float
                }
            ],
            "ready_for_topic": bool
        }
    """
```

### classify_learner_level

**Purpose**: Determine learner's level based on mastery data.

```python
@FunctionTool
def classify_learner_level(user_id: str) -> dict:
    """
    Classify learner as beginner/intermediate/advanced.

    Args:
        user_id: Learner's user ID

    Returns:
        {
            "level": str,  # beginner | intermediate | advanced
            "reasoning": str,
            "stats": {
                "concepts_mastered": int,
                "average_mastery": float,
                "topics_completed": int
            }
        }
    """
```

---

## Path Planning Tools (`adk/path_tools.py`)

### get_recommended_path

**Purpose**: Generate a learning path based on goals and progress.

```python
@FunctionTool
def get_recommended_path(
    user_id: str,
    goal: str | None = None,
    max_topics: int = 5
) -> dict:
    """
    Generate personalized learning path.

    Args:
        user_id: Learner's user ID
        goal: Optional learning goal (e.g., "machine learning")
        max_topics: Maximum topics to recommend

    Returns:
        {
            "path": [
                {
                    "topic": str,
                    "reason": str,
                    "prerequisite_met": bool,
                    "estimated_time": str  # "short" | "medium" | "long"
                }
            ],
            "goal_aligned": bool,
            "weak_areas_addressed": int
        }
    """
```

### get_next_topic

**Purpose**: Get the single best next topic.

```python
@FunctionTool
def get_next_topic(user_id: str) -> dict:
    """
    Get the most appropriate next topic for the learner.

    Args:
        user_id: Learner's user ID

    Returns:
        {
            "topic": str,
            "confidence": float,
            "reason": str,
            "alternatives": [str]
        }
    """
```

---

## Feedback Tools (extensions to `adk/quiz_tools.py`)

### analyze_error_patterns

**Purpose**: Identify patterns in quiz mistakes.

```python
@FunctionTool
def analyze_error_patterns(
    quiz_responses: list,
    quiz_questions: list
) -> dict:
    """
    Analyze quiz responses for error patterns.

    Args:
        quiz_responses: List of {question_id, learner_answer, is_correct}
        quiz_questions: List of {question_id, concept_name, expected_answer}

    Returns:
        {
            "patterns": [
                {
                    "type": str,  # conceptual | procedural | careless
                    "description": str,
                    "questions": [str],  # question_ids
                    "confidence": float
                }
            ],
            "most_common_type": str,
            "unique_concepts_missed": int
        }
    """
```

### generate_feedback_text

**Purpose**: Generate human-friendly feedback narrative.

```python
@FunctionTool
def generate_feedback_text(
    quiz_score: float,
    error_patterns: list,
    improvement_areas: list
) -> dict:
    """
    Generate constructive feedback text.

    Args:
        quiz_score: Score from 0.0 to 1.0
        error_patterns: From analyze_error_patterns
        improvement_areas: List of concepts to focus on

    Returns:
        {
            "feedback": str,  # Full feedback paragraph
            "tone": str,  # encouraging | neutral | supportive
            "action_items": [str]  # Specific suggestions
        }
    """
```

---

## Transition Tracking Tools (extensions to `adk/storage.py`)

### log_agent_transition

**Purpose**: Record agent routing for debugging/analytics.

```python
@FunctionTool
def log_agent_transition(
    session_id: str,
    from_agent: str,
    to_agent: str,
    reason: str,
    message_excerpt: str = ""
) -> dict:
    """
    Log an agent transition event.

    Args:
        session_id: Current session ID
        from_agent: Agent that was active
        to_agent: Agent being routed to
        reason: Why this routing decision
        message_excerpt: First 100 chars of triggering message

    Returns:
        {
            "logged": True,
            "transition_id": int
        }
    """
```

### get_session_transitions

**Purpose**: Retrieve transition history for a session.

```python
@FunctionTool
def get_session_transitions(
    session_id: str,
    limit: int = 50
) -> dict:
    """
    Get agent transitions for a session.

    Args:
        session_id: Session to query
        limit: Maximum transitions to return

    Returns:
        {
            "transitions": [
                {
                    "from_agent": str,
                    "to_agent": str,
                    "reason": str,
                    "timestamp": str
                }
            ],
            "total_count": int,
            "unique_agents_used": [str]
        }
    """
```

---

## Learning Cycle Tools (`adk/orchestration.py`)

### start_learning_cycle

**Purpose**: Initialize a new learning cycle for a topic.

```python
@FunctionTool
def start_learning_cycle(
    session_id: str,
    user_id: str,
    topic: str,
    mastery_threshold: float = 0.85
) -> dict:
    """
    Start a new learning cycle session.

    Args:
        session_id: Current session
        user_id: Learner's ID
        topic: Topic to learn
        mastery_threshold: Target mastery (default 0.85)

    Returns:
        {
            "cycle_id": int,
            "topic": str,
            "initial_mastery": float,
            "threshold": float,
            "status": "started"
        }
    """
```

### complete_learning_cycle

**Purpose**: Record completion of a learning cycle.

```python
@FunctionTool
def complete_learning_cycle(
    cycle_id: int,
    quiz_score: float,
    mastery_achieved: bool
) -> dict:
    """
    Complete a learning cycle with results.

    Args:
        cycle_id: Cycle to complete
        quiz_score: Final quiz score
        mastery_achieved: Whether mastery threshold met

    Returns:
        {
            "cycle_id": int,
            "completed": True,
            "recommendation": str  # "continue" | "mastered" | "needs_help"
        }
    """
```

---

## Tool Dependencies

| Tool | Depends On | State Accessed |
|------|------------|----------------|
| `get_prerequisites` | `storage.get_relationships` | concept_relationships |
| `check_prerequisites_mastery` | `storage.get_mastery` | concept_mastery |
| `classify_learner_level` | `storage.get_user_stats` | quiz_results, concept_mastery |
| `get_recommended_path` | `storage.get_weak_concepts`, `get_prerequisites` | All mastery data |
| `analyze_error_patterns` | None (pure computation) | Passed as args |
| `log_agent_transition` | `storage._get_conn` | agent_transitions |
