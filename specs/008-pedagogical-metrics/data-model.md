# Data Model: Advanced Pedagogical Metrics

**Feature**: 008-pedagogical-metrics
**Date**: 2025-12-03

---

## Entity Relationship Overview

```
User (1) ─────── (*) ConceptMastery
  │                    │
  │                    └── (1) BKTParameters
  │
  ├─────── (*) LearnerAbility
  │
  ├─────── (*) BehavioralEvent
  │
  └─────── (*) ZPDStatus

Question (1) ─────── (1) QuestionParameters

Domain (1) ─────── (1) DomainThreshold
```

---

## Entities

### 1. BKTParameters

Bayesian Knowledge Tracing parameters for a concept.

| Field | Type | Constraints | Default | Description |
|-------|------|-------------|---------|-------------|
| id | INTEGER | PRIMARY KEY | AUTO | Unique identifier |
| user_id | TEXT | NOT NULL, FK | - | References user |
| concept_name | TEXT | NOT NULL | - | Concept identifier |
| p_l0 | REAL | 0-1 | 0.1 | Initial knowledge probability |
| p_t | REAL | 0-1 | 0.3 | Learning rate (transit) |
| p_g | REAL | 0-0.5 | 0.2 | Guess probability |
| p_s | REAL | 0-0.3 | 0.1 | Slip probability |
| p_l_current | REAL | 0-1 | 0.1 | Current mastery probability |
| confidence_lower | REAL | 0-1 | 0.0 | 95% CI lower bound |
| confidence_upper | REAL | 0-1 | 1.0 | 95% CI upper bound |
| observations | INTEGER | >= 0 | 0 | Number of observations |
| last_updated | TEXT | ISO8601 | - | Last update timestamp |

**Validation Rules:**
- `p_g + p_s < 1` (prevents negative learning)
- `p_g < 0.5` (guess below chance)
- `p_s < 0.3` (slip should be low)
- UNIQUE(user_id, concept_name)

**State Transitions:**
- Created when concept first encountered
- Updated after every answer via BKT update equations
- `p_l_current >= 0.95` triggers mastery status

---

### 2. QuestionParameters

Item Response Theory parameters for a question.

| Field | Type | Constraints | Default | Description |
|-------|------|-------------|---------|-------------|
| id | INTEGER | PRIMARY KEY | AUTO | Unique identifier |
| question_id | TEXT | NOT NULL, UNIQUE | - | Question identifier |
| discrimination_a | REAL | 0.5-2.5 | 1.0 | Discrimination parameter |
| difficulty_b | REAL | -3 to +3 | 0.0 | Difficulty parameter |
| guessing_c | REAL | 0-0.35 | 0.25 | Guessing parameter |
| attempt_count | INTEGER | >= 0 | 0 | Total attempts |
| success_count | INTEGER | >= 0 | 0 | Correct responses |
| observed_rate | REAL | 0-1 | NULL | Empirical success rate |
| fisher_info | REAL | >= 0 | NULL | Information at theta=0 |
| calibrated | INTEGER | 0 or 1 | 0 | 1 if empirically calibrated |
| last_calibrated | TEXT | ISO8601 | NULL | Last calibration timestamp |

**Validation Rules:**
- `success_count <= attempt_count`
- `observed_rate = success_count / attempt_count` (when attempt_count > 0)
- Calibration triggered when `attempt_count >= 50`

**Initial Estimates (Cold Start):**
- Conceptual: a=0.9, b by complexity, c=0.25
- Procedural: a=1.2, b by complexity, c=0.20
- Application: a=1.5, b by complexity, c=0.25

---

### 3. LearnerAbility

Learner ability estimate (theta) for IRT matching.

| Field | Type | Constraints | Default | Description |
|-------|------|-------------|---------|-------------|
| id | INTEGER | PRIMARY KEY | AUTO | Unique identifier |
| user_id | TEXT | NOT NULL | - | References user |
| domain | TEXT | NOT NULL | 'general' | Domain/subject area |
| theta | REAL | -4 to +4 | 0.0 | Ability estimate |
| standard_error | REAL | > 0 | 1.0 | SE of theta estimate |
| responses_count | INTEGER | >= 0 | 0 | Responses used in estimate |
| last_updated | TEXT | ISO8601 | - | Last update timestamp |

**Validation Rules:**
- UNIQUE(user_id, domain)
- `standard_error` decreases as `responses_count` increases
- Minimum 5 responses for stable estimate

**Update Logic:**
- Newton-Raphson MLE after each response
- Use EAP (Expected A Posteriori) for few responses

---

### 4. ZPDStatus

Zone of Proximal Development tracking.

| Field | Type | Constraints | Default | Description |
|-------|------|-------------|---------|-------------|
| id | INTEGER | PRIMARY KEY | AUTO | Unique identifier |
| user_id | TEXT | NOT NULL | - | References user |
| concept_name | TEXT | NOT NULL | - | Concept identifier |
| status | TEXT | ENUM | 'optimal' | Current ZPD status |
| recent_success_rate | REAL | 0-1 | NULL | EMA of recent performance |
| consecutive_correct | INTEGER | >= 0 | 0 | Streak of correct answers |
| consecutive_incorrect | INTEGER | >= 0 | 0 | Streak of incorrect answers |
| recommended_difficulty | INTEGER | 1-6 | 3 | Suggested difficulty level |
| last_evaluated | TEXT | ISO8601 | - | Last evaluation timestamp |

**Status Values:**
- `frustration_risk`: success_rate < 0.50 for 2+ consecutive
- `below_zpd`: success_rate < 0.60
- `optimal`: success_rate 0.60-0.85
- `above_zpd`: success_rate > 0.85
- `boredom_risk`: success_rate > 0.90 for 3+ consecutive

**Validation Rules:**
- UNIQUE(user_id, concept_name)
- Status determined by thresholds + behavioral indicators

---

### 5. BehavioralEvent

Behavioral indicator tracking for frustration/boredom detection.

| Field | Type | Constraints | Default | Description |
|-------|------|-------------|---------|-------------|
| id | INTEGER | PRIMARY KEY | AUTO | Unique identifier |
| user_id | TEXT | NOT NULL | - | References user |
| session_id | TEXT | NOT NULL | - | Session identifier |
| event_type | TEXT | NOT NULL | - | Event type |
| timestamp | TEXT | ISO8601 | - | Event timestamp |
| question_id | TEXT | NULL | - | Related question |
| concept_name | TEXT | NULL | - | Related concept |
| response_time_ms | INTEGER | >= 0 | NULL | Time to respond |
| expected_time_ms | INTEGER | > 0 | NULL | Expected response time |
| hints_used | INTEGER | >= 0 | 0 | Hints requested |
| attempts | INTEGER | >= 1 | 1 | Attempts on this question |
| correct | INTEGER | 0 or 1 | NULL | Final correctness |

**Event Types:**
- `answer`: Standard answer event
- `hint_request`: Hint requested
- `abandon`: Question abandoned
- `rapid_attempt`: < 3 seconds between attempts
- `timeout`: Exceeded time limit

**Derived Metrics:**
- `response_ratio = response_time_ms / expected_time_ms`
- Fast: ratio < 0.5
- Normal: ratio 0.5-2.0
- Slow: ratio > 2.0

---

### 6. DomainThreshold

Domain-specific mastery thresholds.

| Field | Type | Constraints | Default | Description |
|-------|------|-------------|---------|-------------|
| id | INTEGER | PRIMARY KEY | AUTO | Unique identifier |
| domain | TEXT | NOT NULL, UNIQUE | - | Domain name |
| mastery_threshold | REAL | 0-1 | 0.80 | Required mastery probability |
| consistency_count | INTEGER | >= 0 | 0 | Required consecutive correct |
| description | TEXT | NULL | - | Domain description |

**Preset Domains:**
- `general`: threshold=0.80, consistency=0
- `stem`: threshold=0.85, consistency=3
- `medical`: threshold=0.95, consistency=5
- `safety`: threshold=0.95, consistency=5

---

## Extended ConceptMastery

Extends existing `concept_mastery` table from `adk/storage.py`:

| Field | Type | Description |
|-------|------|-------------|
| *existing fields* | ... | From current schema |
| bkt_mastery | REAL | BKT probability (replaces simple ratio) |
| mastery_source | TEXT | 'simple' or 'bkt' |
| domain | TEXT | For threshold lookup |

**Migration:**
- Add columns with defaults
- Existing `mastery_level` preserved for backward compatibility
- New `bkt_mastery` used for BKT-based mastery

---

## Indexes

```sql
-- BKT Parameters
CREATE INDEX idx_bkt_user ON bkt_parameters(user_id);
CREATE INDEX idx_bkt_concept ON bkt_parameters(user_id, concept_name);

-- Question Parameters
CREATE INDEX idx_question_id ON question_parameters(question_id);
CREATE INDEX idx_question_calibrated ON question_parameters(calibrated);

-- Learner Ability
CREATE INDEX idx_ability_user ON learner_ability(user_id);
CREATE INDEX idx_ability_domain ON learner_ability(user_id, domain);

-- ZPD Status
CREATE INDEX idx_zpd_user ON zpd_status(user_id);
CREATE INDEX idx_zpd_status ON zpd_status(status);

-- Behavioral Events
CREATE INDEX idx_behavior_user ON behavioral_events(user_id);
CREATE INDEX idx_behavior_session ON behavioral_events(session_id);
CREATE INDEX idx_behavior_type ON behavioral_events(event_type);
CREATE INDEX idx_behavior_time ON behavioral_events(timestamp);
```

---

## Session State Keys

For ADK ToolContext state (extends `adk/quiz_tools.py`):

| Key | Type | Description |
|-----|------|-------------|
| `quiz:response_times` | List[int] | Response times (ms) for current quiz |
| `quiz:zpd_status` | str | Current ZPD status |
| `quiz:theta` | float | Current ability estimate |
| `quiz:theta_se` | float | Standard error of theta |
| `quiz:consecutive_correct` | int | Consecutive correct streak |
| `quiz:consecutive_incorrect` | int | Consecutive incorrect streak |
| `quiz:hint_count` | int | Hints used this quiz |
| `quiz:last_response_time` | int | Last response timestamp (ms) |
