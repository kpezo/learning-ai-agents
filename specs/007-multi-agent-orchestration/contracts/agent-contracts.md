# Agent Contracts: Multi-Agent Orchestration

**Branch**: `007-multi-agent-orchestration`
**Date**: 2025-12-03

## Overview

This document defines the input/output contracts for each agent in the multi-agent system. These contracts enable testing, validation, and clear interfaces between agents.

---

## Coordinator Agent

### Contract: Route Message

**Purpose**: Classify user intent and route to appropriate specialist agent.

**Input**:
```python
{
    "user_message": str,           # The user's input message
    "session_state": {             # Current session context
        "current_topic": str | None,
        "quiz_paused": bool,
        "last_routed_to": str | None
    }
}
```

**Output**:
```python
{
    "target_agent": str,           # One of: diagnostic, tutor, quiz, feedback, pathplanner
    "routing_reason": str,         # Why this agent was chosen
    "context_for_agent": dict      # Additional context to pass
}
```

**Routing Rules**:
| User Intent | Target Agent | Trigger Patterns |
|-------------|--------------|------------------|
| New topic start | `diagnostic` | "teach me X", "I want to learn X" |
| Question about content | `tutor` | "explain", "why", "how does" |
| Quiz request | `quiz` | "quiz me", "test my knowledge" |
| After quiz completion | `feedback` | Automatic after quiz |
| Progress inquiry | `pathplanner` | "what's next", "my progress" |
| Resume paused quiz | `quiz` | "continue quiz", "resume" when `quiz_paused=True` |
| Unclear | `tutor` | Default fallback |

---

## Diagnostic Agent

### Contract: Assess Prerequisites

**Purpose**: Check learner's prerequisite knowledge before starting a topic.

**Input**:
```python
{
    "topic": str,                  # Topic learner wants to study
    "user_id": str,                # For mastery lookup
}
```

**Output**:
```python
{
    "diagnostic_complete": True,
    "prerequisite_gaps": [         # List of missing prerequisites
        {
            "concept": str,
            "current_mastery": float,  # 0.0-1.0
            "required_mastery": float  # Typically 0.5
        }
    ],
    "learner_level": str,          # beginner | intermediate | advanced
    "recommendation": str          # "proceed" | "remediate" | "skip_ahead"
}
```

**State Written**:
- `diagnostic_complete`: True
- `prerequisite_gaps`: List of gap objects
- `learner_level`: Classification string

**Tools Used**:
- `get_prerequisites(topic)` - Queries concept_relationships table
- `get_mastery(concept)` - Checks user's mastery level

---

## Tutor Agent

### Contract: Explain Concept

**Purpose**: Provide personalized explanation of a concept.

**Input**:
```python
{
    "topic": str,
    "learner_level": str,          # From diagnostic
    "prerequisite_gaps": list,     # Concepts to be careful about
    "specific_question": str | None  # If asking about something specific
}
```

**Output**:
```python
{
    "explanation": str,            # Main explanation text
    "examples_provided": [str],    # Concrete examples used
    "key_points": [str],          # Summary bullets
    "next_action": str            # "quiz" | "continue_explaining" | "ask_question"
}
```

**State Written**:
- `explanation`: The explanation text
- `examples_provided`: List of examples

**Tools Used**:
- `fetch_info(query)` - RAG retrieval for context
- `preload_memory` - Load relevant past interactions

---

## Quiz Agent

### Contract: Generate and Run Quiz

**Purpose**: Create quiz questions and evaluate answers.

### Sub-Contract: Prepare Quiz

**Input**:
```python
{
    "topic": str,
    "num_questions": int,          # Default 5
    "difficulty": str              # easy | medium | hard | adaptive
}
```

**Output**:
```python
{
    "quiz_questions": [
        {
            "question_id": str,
            "question_text": str,
            "concept_name": str,
            "difficulty": str,
            "expected_answer": str,
            "source_context": str
        }
    ],
    "quiz_question_index": 0
}
```

### Sub-Contract: Evaluate Answer

**Input**:
```python
{
    "question_id": str,
    "learner_answer": str
}
```

**Output**:
```python
{
    "is_correct": bool,
    "feedback": str,               # Immediate feedback
    "quiz_score": float,           # Running score
    "quiz_complete": bool
}
```

**State Written**:
- `quiz_questions`: Generated questions
- `quiz_responses`: Learner answers with correctness
- `quiz_score`: Final score (0.0-1.0)
- `quiz_question_index`: Current position

**Tools Used**:
- `get_quiz_source(topic, max_chunks)` - Get RAG context
- `prepare_quiz(topic)` - Initialize quiz session
- `get_quiz_step()` - Get current question
- `advance_quiz(correct, concept_name)` - Move to next

---

## Feedback Agent

### Contract: Analyze Performance

**Purpose**: Provide constructive feedback on quiz results.

**Input**:
```python
{
    "quiz_questions": list,        # From quiz agent
    "quiz_responses": list,        # Learner's answers
    "quiz_score": float
}
```

**Output**:
```python
{
    "error_patterns": [
        {
            "pattern_type": str,   # conceptual | procedural | careless
            "description": str,
            "affected_questions": [str],
            "suggested_remediation": str
        }
    ],
    "feedback_text": str,          # Human-friendly feedback
    "improvement_areas": [str],    # Concepts to focus on
    "mastery_score": float,        # Updated mastery
    "mastery_achieved": bool       # True if >= threshold
}
```

**State Written**:
- `error_patterns`: Identified patterns
- `feedback_text`: Narrative feedback
- `mastery_score`: Updated mastery level
- `improvement_areas`: List of weak concepts

**Tools Used**:
- `update_mastery(concept, correct)` - Update concept mastery
- `add_knowledge_gap(concept, gap_type)` - Record gaps

---

## PathPlanner Agent

### Contract: Recommend Learning Path

**Purpose**: Suggest next steps based on progress and goals.

**Input**:
```python
{
    "user_id": str,
    "goals": [str] | None,         # Learner's stated goals
    "current_topic": str | None,
    "mastery_data": dict           # From storage
}
```

**Output**:
```python
{
    "learning_path": [             # Ordered list of topics
        {
            "topic": str,
            "reason": str,         # Why recommended
            "estimated_effort": str # low | medium | high
        }
    ],
    "next_topic": str,             # Immediate next recommendation
    "path_reasoning": str,         # Explanation of path logic
    "alternative_paths": [str]     # Other options
}
```

**State Written**:
- `learning_path`: Recommended sequence
- `next_topic`: Immediate next topic
- `path_reasoning`: Why this path

**Tools Used**:
- `get_weak_concepts(threshold)` - Find weak areas
- `get_learning_stats()` - Overall progress
- `get_relationships(pdf_hash)` - Concept dependencies

---

## Orchestration Contracts

### LearningCycle (SequentialAgent)

**Purpose**: Execute Tutor → Quiz → Feedback sequence.

**Input**:
```python
{
    "topic": str,
    "learner_level": str,
    "mastery_threshold": float     # Default 0.85
}
```

**Output**:
```python
{
    "explanation": str,            # From Tutor
    "quiz_score": float,           # From Quiz
    "feedback_text": str,          # From Feedback
    "mastery_achieved": bool,
    "cycle_number": int
}
```

### MasteryLoop (LoopAgent)

**Purpose**: Repeat LearningCycle until mastery achieved.

**Input**:
```python
{
    "topic": str,
    "max_iterations": int          # Default 5
}
```

**Output**:
```python
{
    "final_mastery": float,
    "total_cycles": int,
    "mastery_achieved": bool,
    "recommendation": str          # "mastered" | "needs_remediation"
}
```

**Escalation Condition**:
- `mastery_score >= mastery_threshold` → escalate=True
- `cycle_count >= max_iterations` → escalate=True (max reached)

---

## Error Handling

All agents follow this error contract:

```python
{
    "success": False,
    "error": {
        "code": str,               # e.g., "INVALID_INPUT", "RAG_EMPTY"
        "message": str,
        "recoverable": bool,
        "fallback_action": str     # What coordinator should do
    }
}
```

| Error Code | Meaning | Fallback |
|------------|---------|----------|
| `INVALID_INPUT` | Missing required field | Ask user to clarify |
| `RAG_EMPTY` | No content found for topic | Suggest related topics |
| `TIMEOUT` | Agent took too long | Retry or route to tutor |
| `STATE_MISSING` | Required state not set | Run diagnostic first |
