# Data Model: Adaptive Difficulty System

**Feature**: 001-adaptive-difficulty | **Date**: 2025-12-03

## Entities

### DifficultyLevel

Represents one of 6 difficulty levels with associated metadata.

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| level | int | Numeric level 1-6 | 1 ≤ level ≤ 6 |
| name | str | Human-readable name | Enum: Foundation, Understanding, Application, Analysis, Synthesis, Mastery |
| question_types | List[str] | Allowed question types for this level | Non-empty |
| hint_allowance | int | Max hints allowed per question | 0-3 |
| time_pressure | float | Expected answer time multiplier | 0.5-2.0 |
| description | str | What this level tests | Non-empty |

**Static Configuration** (immutable):

```python
DIFFICULTY_LEVELS = {
    1: DifficultyLevel(
        level=1,
        name="Foundation",
        question_types=["definition", "recognition", "true_false"],
        hint_allowance=3,
        time_pressure=1.5,
        description="Basic recall and recognition"
    ),
    2: DifficultyLevel(
        level=2,
        name="Understanding",
        question_types=["explanation", "comparison", "cause_effect"],
        hint_allowance=2,
        time_pressure=1.3,
        description="Comprehension and interpretation"
    ),
    3: DifficultyLevel(
        level=3,
        name="Application",
        question_types=["scenario", "case_study", "problem_solving"],
        hint_allowance=1,
        time_pressure=1.0,
        description="Apply knowledge to new situations"
    ),
    4: DifficultyLevel(
        level=4,
        name="Analysis",
        question_types=["breakdown", "pattern_recognition", "critique"],
        hint_allowance=0,
        time_pressure=0.9,
        description="Break down and analyze components"
    ),
    5: DifficultyLevel(
        level=5,
        name="Synthesis",
        question_types=["design", "integration", "hypothesis"],
        hint_allowance=0,
        time_pressure=0.8,
        description="Combine elements into new patterns"
    ),
    6: DifficultyLevel(
        level=6,
        name="Mastery",
        question_types=["teach_back", "edge_case", "meta_cognition"],
        hint_allowance=0,
        time_pressure=0.7,
        description="Expert-level teaching and edge cases"
    )
}
```

---

### PerformanceRecord

Captures a single answer's performance metrics.

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| id | int | Auto-incrementing primary key | Auto |
| user_id | str | User identifier | Foreign key |
| session_id | str | Session identifier | Not null |
| quiz_id | int | Related quiz | Foreign key to quiz_results |
| question_number | int | Question index in quiz | ≥ 1 |
| score | float | Score for this answer | 0.0-1.0 |
| response_time_ms | int | Time to answer in milliseconds | ≥ 0 |
| hints_used | int | Number of hints requested | ≥ 0 |
| difficulty_level | int | Difficulty at time of answer | 1-6 |
| concept_tested | str | Concept being assessed | Not null |
| question_type | str | Type of question asked | From difficulty level types |
| in_optimal_zone | bool | Whether score was in 60-85% range | Computed |
| timestamp | str | ISO timestamp | Not null |

**Indexes**: user_id, session_id, concept_tested

---

### PerformanceTrend

Aggregated analysis of recent answers for difficulty decisions.

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| user_id | str | User identifier | |
| window_size | int | Number of records analyzed | Default: 5 |
| avg_score | float | Average score in window | 0.0-1.0 |
| score_trend | str | Trend direction | Enum: improving, stable, declining |
| avg_response_time_ms | int | Average response time | ≥ 0 |
| time_trend | str | Time trend direction | Enum: faster, stable, slower |
| avg_hints_used | float | Average hints per question | ≥ 0.0 |
| consecutive_correct | int | Streak of correct answers | ≥ 0 |
| consecutive_incorrect | int | Streak of incorrect answers | ≥ 0 |
| optimal_zone_ratio | float | % of answers in optimal zone | 0.0-1.0 |

**Computed at runtime** (not persisted)

---

### DifficultyAdjustment

Records a difficulty level change with reasoning.

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| id | int | Auto-incrementing primary key | Auto |
| user_id | str | User identifier | Foreign key |
| session_id | str | Session identifier | Not null |
| previous_level | int | Level before adjustment | 1-6 |
| new_level | int | Level after adjustment | 1-6 |
| adjustment_type | str | Type of change | Enum: increase, decrease, maintain |
| reason | str | Why adjustment was made | JSON: criteria met |
| triggered_by | str | What triggered evaluation | Enum: answer, manual, session_start |
| scaffolding_recommended | bool | Whether scaffolding should activate | |
| timestamp | str | ISO timestamp | Not null |

**Indexes**: user_id, session_id

---

### ScaffoldingSupport

Structured hints and strategies for a specific struggle area.

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| struggle_area | str | Type of struggle | Enum: definition, process, relationship, application |
| hint_templates | List[str] | Generic hint text templates | Non-empty |
| strategies | List[str] | Learning strategies to suggest | Non-empty |
| question_simplification | str | How to simplify questions | |
| example_prompts | List[str] | Example easier questions | |

**Static Configuration**:

```python
SCAFFOLDING_STRATEGIES = {
    "definition": ScaffoldingSupport(
        struggle_area="definition",
        hint_templates=[
            "Let's start with the basic definition of {concept}.",
            "The key word here is {keyword}.",
            "Think about what {concept} means in simple terms."
        ],
        strategies=[
            "Focus on the core meaning first",
            "Look for keywords that define the concept",
            "Connect to something you already know"
        ],
        question_simplification="Ask for recognition instead of recall",
        example_prompts=[
            "Which of these best describes {concept}?",
            "True or false: {simple_statement}"
        ]
    ),
    "process": ScaffoldingSupport(
        struggle_area="process",
        hint_templates=[
            "Let's break this down step by step.",
            "The first step is to {step1}.",
            "What needs to happen before {step}?"
        ],
        strategies=[
            "Identify the sequence of steps",
            "Focus on one step at a time",
            "Think about the order things happen"
        ],
        question_simplification="Ask about individual steps",
        example_prompts=[
            "What is the first step in {process}?",
            "What comes after {step}?"
        ]
    ),
    "relationship": ScaffoldingSupport(
        struggle_area="relationship",
        hint_templates=[
            "Think about how {concept1} and {concept2} are connected.",
            "What do these concepts have in common?",
            "How does {concept1} affect {concept2}?"
        ],
        strategies=[
            "Look for cause and effect",
            "Identify similarities and differences",
            "Map out how concepts connect"
        ],
        question_simplification="Focus on single relationships",
        example_prompts=[
            "How are {concept1} and {concept2} similar?",
            "Does {concept1} depend on {concept2}?"
        ]
    ),
    "application": ScaffoldingSupport(
        struggle_area="application",
        hint_templates=[
            "Think about a simpler example first.",
            "What concept from the lesson applies here?",
            "Have you seen a similar situation before?"
        ],
        strategies=[
            "Start with a simpler version of the problem",
            "Identify which concept to apply",
            "Think about real-world examples"
        ],
        question_simplification="Provide more context",
        example_prompts=[
            "In this simple case, what would you do?",
            "Which approach would work for {scenario}?"
        ]
    )
}
```

---

### ConceptStats (Extended)

Extension of existing ConceptMastery with difficulty-specific data.

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| concept_name | str | Concept identifier | Primary key with user_id |
| avg_difficulty_achieved | float | Average difficulty for correct answers | 1.0-6.0 |
| max_difficulty_achieved | int | Highest difficulty passed | 1-6 |
| difficulty_distribution | Dict[int, int] | Count of attempts per level | JSON |
| struggle_area | str | Identified struggle type | Nullable |
| complexity | int | Concept's inherent complexity | 1-5 (default 3) |

**Stored in existing concept_mastery table** (added columns)

---

## State Transitions

### Difficulty Level State Machine

```
                    ┌─────────────────────┐
                    │                     │
    ┌───────────────▼───────────────┐     │
    │                               │     │ Score ≥85%
    │         INCREASE              │     │ 3 consecutive
    │    (prev_level + 1)           │     │ no hints
    │                               │     │
    └───────────────┬───────────────┘     │
                    │                     │
                    ▼                     │
    ┌───────────────────────────────────┐ │
    │                                   │ │
    │        CURRENT LEVEL              │─┘
    │   (1-6, clamped at bounds)        │
    │                                   │◄─┐
    └───────────────┬───────────────────┘  │
                    │                      │
                    ▼                      │
    ┌───────────────────────────────┐      │
    │                               │      │ Score in
    │         MAINTAIN              │      │ 60-85%
    │    (same level)               │──────┘ optimal zone
    │                               │
    └───────────────┬───────────────┘
                    │
                    │ Score <50%
                    │ 2 consecutive
                    ▼
    ┌───────────────────────────────┐
    │                               │
    │         DECREASE              │
    │    (prev_level - 1)           │
    │    + scaffolding activated    │
    │                               │
    └───────────────────────────────┘
```

### Validation Rules

1. **Score validation**: 0.0 ≤ score ≤ 1.0
2. **Difficulty clamping**: 1 ≤ level ≤ 6
3. **Hint enforcement**: hints_used ≤ level.hint_allowance
4. **Streak reset**: Incorrect answer resets consecutive_correct (and vice versa)
5. **Scaffolding trigger**: Only on DECREASE transition

---

## Relationships

```
User (1) ────────< (N) PerformanceRecord
     │                       │
     │                       │
     └───< (N) DifficultyAdjustment
     │
     │
     └───< (N) ConceptMastery ───> DifficultyLevel (via avg_difficulty)
                    │
                    └───> ScaffoldingSupport (via struggle_area)
```

---

## SQLite Schema Extensions

```sql
-- Performance records for difficulty decisions
CREATE TABLE IF NOT EXISTS performance_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    session_id TEXT NOT NULL,
    quiz_id INTEGER,
    question_number INTEGER NOT NULL,
    score REAL NOT NULL,
    response_time_ms INTEGER DEFAULT 0,
    hints_used INTEGER DEFAULT 0,
    difficulty_level INTEGER NOT NULL,
    concept_tested TEXT NOT NULL,
    question_type TEXT,
    in_optimal_zone INTEGER DEFAULT 0,
    timestamp TEXT NOT NULL,
    FOREIGN KEY (quiz_id) REFERENCES quiz_results(id)
);
CREATE INDEX IF NOT EXISTS idx_perf_user ON performance_records(user_id);
CREATE INDEX IF NOT EXISTS idx_perf_session ON performance_records(session_id);
CREATE INDEX IF NOT EXISTS idx_perf_concept ON performance_records(concept_tested);

-- Difficulty adjustment history
CREATE TABLE IF NOT EXISTS difficulty_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    session_id TEXT NOT NULL,
    previous_level INTEGER NOT NULL,
    new_level INTEGER NOT NULL,
    adjustment_type TEXT NOT NULL,
    reason TEXT,
    triggered_by TEXT NOT NULL,
    scaffolding_recommended INTEGER DEFAULT 0,
    timestamp TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_diff_user ON difficulty_history(user_id);
CREATE INDEX IF NOT EXISTS idx_diff_session ON difficulty_history(session_id);

-- Add columns to concept_mastery (migration)
ALTER TABLE concept_mastery ADD COLUMN avg_difficulty_achieved REAL DEFAULT 3.0;
ALTER TABLE concept_mastery ADD COLUMN max_difficulty_achieved INTEGER DEFAULT 1;
ALTER TABLE concept_mastery ADD COLUMN difficulty_distribution TEXT DEFAULT '{}';
ALTER TABLE concept_mastery ADD COLUMN struggle_area TEXT;
ALTER TABLE concept_mastery ADD COLUMN complexity INTEGER DEFAULT 3;
```
