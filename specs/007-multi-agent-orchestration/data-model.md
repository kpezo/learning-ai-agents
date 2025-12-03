# Data Model: Multi-Agent Orchestration Expansion

**Branch**: `007-multi-agent-orchestration`
**Date**: 2025-12-03
**Status**: Complete

## Overview

This document defines the data entities, relationships, and state conventions for the multi-agent orchestration system.

## Core Entities

### Agent Definitions

| Agent | Type | Description | State Keys (writes) |
|-------|------|-------------|---------------------|
| `coordinator` | `Agent` | Routes messages to appropriate specialists | `last_routed_to`, `routing_reason` |
| `diagnostic` | `LlmAgent` | Assesses prerequisites and knowledge gaps | `prerequisite_gaps`, `diagnostic_complete`, `learner_level` |
| `tutor` | `LlmAgent` | Explains concepts, answers questions | `explanation`, `examples_provided` |
| `quiz` | `LlmAgent` | Generates and evaluates quiz questions | `quiz_questions`, `quiz_responses`, `quiz_score` |
| `feedback` | `LlmAgent` | Analyzes performance, identifies patterns | `error_patterns`, `feedback_text`, `improvement_areas` |
| `pathplanner` | `LlmAgent` | Recommends learning paths | `learning_path`, `next_topic`, `path_reasoning` |

### Session State Schema

```python
@dataclass
class SessionState:
    """State shared across all agents via ctx.session.state"""

    # Identity
    user_id: str
    session_id: str

    # Diagnostic state
    current_topic: str = ""
    prerequisite_gaps: List[str] = field(default_factory=list)
    diagnostic_complete: bool = False
    learner_level: str = "unknown"  # beginner/intermediate/advanced

    # Learning cycle state
    explanation: str = ""
    examples_provided: List[str] = field(default_factory=list)

    # Quiz state
    quiz_questions: List[QuizQuestion] = field(default_factory=list)
    quiz_responses: List[QuizResponse] = field(default_factory=list)
    quiz_score: float = 0.0
    quiz_paused: bool = False
    quiz_question_index: int = 0

    # Mastery state
    mastery_score: float = 0.0
    mastery_threshold: float = 0.85
    learning_cycle_count: int = 0

    # Feedback state
    error_patterns: List[ErrorPattern] = field(default_factory=list)
    feedback_text: str = ""
    improvement_areas: List[str] = field(default_factory=list)

    # Path planning state
    goals: List[str] = field(default_factory=list)
    learning_path: List[str] = field(default_factory=list)
    next_topic: str = ""

    # Routing state
    last_routed_to: str = ""
    routing_reason: str = ""


@dataclass
class QuizQuestion:
    """Individual quiz question"""
    question_id: str
    question_text: str
    concept_name: str
    difficulty: str  # easy/medium/hard
    expected_answer: str
    source_context: str  # RAG snippet used to generate


@dataclass
class QuizResponse:
    """Learner's response to a question"""
    question_id: str
    learner_answer: str
    is_correct: bool
    time_taken_seconds: float
    attempt_number: int


@dataclass
class ErrorPattern:
    """Pattern identified in learner mistakes"""
    pattern_type: str  # conceptual/procedural/careless
    description: str
    affected_questions: List[str]  # question_ids
    suggested_remediation: str
```

### Database Extensions (storage.py)

```sql
-- New table: Agent transitions for debugging/analytics (FR-013)
CREATE TABLE IF NOT EXISTS agent_transitions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    from_agent TEXT NOT NULL,
    to_agent TEXT NOT NULL,
    reason TEXT,
    message_excerpt TEXT,  -- First 100 chars of triggering message
    timestamp TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_transitions_session ON agent_transitions(session_id);

-- New table: Learning cycle history
CREATE TABLE IF NOT EXISTS learning_cycles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    session_id TEXT NOT NULL,
    topic TEXT NOT NULL,
    cycle_number INTEGER NOT NULL,
    quiz_score REAL,
    mastery_achieved BOOLEAN,
    started_at TEXT NOT NULL,
    completed_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_cycles_user ON learning_cycles(user_id);
CREATE INDEX IF NOT EXISTS idx_cycles_topic ON learning_cycles(topic);

-- New table: Diagnostic results
CREATE TABLE IF NOT EXISTS diagnostic_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    session_id TEXT NOT NULL,
    topic TEXT NOT NULL,
    prerequisite_gaps TEXT,  -- JSON array of concept names
    learner_level TEXT,
    recommendations TEXT,  -- JSON array
    timestamp TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_diagnostic_user ON diagnostic_results(user_id);
```

## Entity Relationships

```
                    ┌─────────────────┐
                    │   Coordinator   │
                    │     (Agent)     │
                    └────────┬────────┘
                             │ routes to
          ┌──────────────────┼──────────────────┐
          │                  │                  │
          ▼                  ▼                  ▼
   ┌──────────┐      ┌──────────────────┐  ┌────────────┐
   │Diagnostic│      │  LearningCycle   │  │PathPlanner │
   │(LlmAgent)│      │(SequentialAgent) │  │ (LlmAgent) │
   └────┬─────┘      └────────┬─────────┘  └──────┬─────┘
        │                     │                   │
        │            ┌────────┴────────┐          │
        │            │                 │          │
        ▼            ▼                 ▼          │
   writes to    ┌────────┐      ┌──────────┐     │
   diagnostic_  │ Tutor  │ ──►  │   Quiz   │     │
   results      │(LlmAgent)     │(LlmAgent)│     │
                └────────┘      └────┬─────┘     │
                                     │           │
                                     ▼           │
                               ┌──────────┐      │
                               │ Feedback │      │
                               │(LlmAgent)│      │
                               └────┬─────┘      │
                                    │            │
                                    ▼            ▼
                              writes to     reads from
                              quiz_results  concept_mastery
                              concept_mastery learning_path
```

## State Transitions

### Routing State Machine

```
                    ┌──────────────┐
    New session ──► │  AWAITING    │
                    │   INPUT      │
                    └──────┬───────┘
                           │ user message
                           ▼
                    ┌──────────────┐
                    │  CLASSIFY    │ (Coordinator LLM)
                    │   INTENT     │
                    └──────┬───────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
    ┌───────────┐   ┌───────────┐   ┌───────────┐
    │ DIAGNOSE  │   │   LEARN   │   │   PLAN    │
    │           │   │           │   │           │
    └─────┬─────┘   └─────┬─────┘   └─────┬─────┘
          │               │               │
          ▼               ▼               ▼
    Diagnostic ─►  Learning Cycle ─► PathPlanner
         │               │               │
         └───────────────┴───────────────┘
                         │
                         ▼
                  ┌──────────────┐
                  │  AWAITING    │
                  │   INPUT      │ (loop)
                  └──────────────┘
```

### Learning Cycle State Machine

```
                    ┌──────────────┐
    Start topic ──► │   TUTOR      │
                    │  EXPLAINING  │
                    └──────┬───────┘
                           │ explanation complete
                           ▼
                    ┌──────────────┐
                    │    QUIZ      │
                    │   ACTIVE     │
                    └──────┬───────┘
                           │ quiz complete
                           ▼
                    ┌──────────────┐
                    │  FEEDBACK    │
                    │  ANALYZING   │
                    └──────┬───────┘
                           │
            ┌──────────────┴──────────────┐
            │ mastery < 85%               │ mastery >= 85%
            ▼                             ▼
     ┌─────────────┐               ┌─────────────┐
     │ LOOP AGAIN  │               │  MASTERED   │
     │ (increment  │               │ (escalate)  │
     │  cycle_count)               └─────────────┘
     └──────┬──────┘
            │
            ▼
     Back to TUTOR EXPLAINING
```

## Validation Rules

### Agent Name Constraints
- Must be lowercase, alphanumeric + underscores
- Max 30 characters
- Must be unique within `sub_agents` list

### Mastery Threshold
- Range: 0.0 to 1.0
- Default: 0.85
- Configurable via `mastery_threshold` state key

### Learning Cycle Limits
- Max iterations: 5 (configurable via LoopAgent)
- If mastery not achieved after 5 cycles, suggest PathPlanner remediation

### Quiz Question Limits
- Per session: 3-10 questions (configurable)
- Per concept: minimum 1, maximum 3

## Migration Notes

### From Existing 3-Agent System

| Old Agent | New Agent(s) | Notes |
|-----------|--------------|-------|
| `tutor` | `tutor` | Keep as-is, update instruction |
| `curriculum_planner` | `diagnostic`, `pathplanner` | Split responsibilities |
| `assessor` | `quiz`, `feedback` | Split responsibilities |
| `education_supervisor` | `coordinator` | Rename, update routing instruction |

### Database Migration

```sql
-- No destructive migrations - all changes are additive
-- Existing tables remain unchanged:
--   quiz_results, concept_mastery, knowledge_gaps,
--   session_logs, extracted_concepts, concept_relationships
```
