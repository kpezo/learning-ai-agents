# Feature Specification: Adaptive Difficulty System

**Feature Branch**: `001-adaptive-difficulty`
**Created**: 2025-12-03
**Status**: Draft
**Input**: User description: "Implement the adaptive difficulty system for quizzes - a 6-level framework that dynamically adjusts question complexity based on real-time learner performance"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Automatic Difficulty Adjustment During Quiz (Priority: P1)

A learner takes a quiz on a topic. As they answer questions, the system automatically adjusts the difficulty level based on their performance. When they answer correctly and quickly, questions become more challenging. When they struggle (incorrect answers, needing hints), questions become easier with more scaffolding support.

**Why this priority**: This is the core value proposition - without automatic adjustment, there is no adaptive system. It directly addresses the problem of questions being too easy (boring) or too hard (frustrating) for learners.

**Independent Test**: Can be fully tested by starting a quiz and answering a mix of correct/incorrect responses, then verifying the difficulty level changes appropriately between questions.

**Acceptance Scenarios**:

1. **Given** a learner starting a quiz at difficulty level 3 (Application), **When** they answer 3 consecutive questions correctly with scores above 85%, **Then** the system increases difficulty to level 4 (Analysis).

2. **Given** a learner at difficulty level 4, **When** they answer 2 consecutive questions incorrectly (below 50%), **Then** the system decreases difficulty to level 3 and provides scaffolding hints.

3. **Given** a learner answering questions in the 60-85% score range, **When** their performance remains consistent, **Then** the system maintains the current difficulty level (optimal learning zone).

---

### User Story 2 - Difficulty-Appropriate Question Generation (Priority: P2)

When generating quiz questions, the system creates questions appropriate for the learner's current difficulty level. Foundation-level questions ask for definitions and recognition. Mastery-level questions require teaching back concepts and handling edge cases.

**Why this priority**: This enables the difficulty adjustment to have meaningful impact - without level-appropriate questions, changing the difficulty level would be meaningless.

**Independent Test**: Can be tested by setting a specific difficulty level and verifying generated questions match the expected question types for that level.

**Acceptance Scenarios**:

1. **Given** a learner at difficulty level 1 (Foundation), **When** a question is generated, **Then** the question type is one of: definition, recognition, or true/false.

2. **Given** a learner at difficulty level 3 (Application), **When** a question is generated, **Then** the question presents a scenario requiring application of the concept.

3. **Given** a learner at difficulty level 6 (Mastery), **When** a question is generated, **Then** the question asks the learner to teach the concept, identify edge cases, or critique an implementation.

---

### User Story 3 - Scaffolding Support When Struggling (Priority: P2)

When a learner's difficulty level decreases due to struggling, the system provides scaffolding support - structured hints and simplified explanations that help the learner build understanding step by step.

**Why this priority**: This completes the adaptive experience by not just making questions easier, but actively helping learners who are struggling. Equally important as P2 since it works hand-in-hand with question generation.

**Independent Test**: Can be tested by triggering a difficulty decrease and verifying that appropriate scaffolding hints are provided alongside the next question.

**Acceptance Scenarios**:

1. **Given** a learner who just had their difficulty decreased, **When** the next question is presented, **Then** scaffolding hints relevant to their struggle area are available.

2. **Given** a learner struggling with "definition" understanding, **When** scaffolding is provided, **Then** hints include strategies like "Let's start with the basic definition" and "The key word here is...".

3. **Given** a learner struggling with "process" understanding, **When** scaffolding is provided, **Then** hints break down the concept into sequential steps.

---

### User Story 4 - Performance Tracking and History (Priority: P3)

The system tracks each answer's performance data including score, response time, hints used, difficulty level, and concept tested. This history enables accurate trend analysis for difficulty adjustments.

**Why this priority**: While essential for the system to function well over time, basic difficulty adjustment can work with limited history. This enables more sophisticated adaptation.

**Independent Test**: Can be tested by answering several questions and then retrieving the performance history to verify all metrics are captured correctly.

**Acceptance Scenarios**:

1. **Given** a learner answers a question, **When** they submit their response, **Then** the system records: score, response time, hints used, difficulty level, concept tested, and timestamp.

2. **Given** a learner with 10+ answers recorded, **When** the system analyzes their performance trend, **Then** it identifies whether they are improving, stable, or declining.

3. **Given** performance data for a specific concept, **When** the system calculates concept-specific statistics, **Then** it provides average score and mastery level for that concept.

---

### User Story 5 - Hint System Based on Difficulty Level (Priority: P3)

Each difficulty level has a defined number of hints available. Foundation level allows 3 hints, Understanding allows 2, Application allows 1, and higher levels allow no hints. Hint usage affects difficulty adjustment decisions.

**Why this priority**: Enhances the learning experience but the core system can function without tiered hints initially.

**Independent Test**: Can be tested by checking available hints at each difficulty level and verifying hint count affects difficulty calculations.

**Acceptance Scenarios**:

1. **Given** a learner at difficulty level 1 (Foundation), **When** they request hints, **Then** up to 3 hints are available for the current question.

2. **Given** a learner at difficulty level 4 (Analysis), **When** they attempt to request a hint, **Then** no hints are available (0 allowed at this level).

3. **Given** a learner who used 2+ hints consecutively, **When** the system calculates optimal difficulty, **Then** this contributes to a potential difficulty decrease.

---

### Edge Cases

- What happens when a learner starts their first quiz with no performance history? System starts at a default difficulty level (level 3 - Application) as a balanced starting point.
- How does the system handle a learner at maximum difficulty (level 6) who continues to excel? System maintains level 6 and may indicate mastery achievement.
- How does the system handle a learner at minimum difficulty (level 1) who continues to struggle? System maintains level 1 with maximum scaffolding support and may suggest prerequisite concept review.
- What happens when concept complexity is very high but learner is struggling? System factors concept complexity into difficulty calculation, allowing lower effective difficulty for complex concepts.
- How does the system handle rapid answer submissions (potential guessing)? Very short response times with incorrect answers are weighted more heavily toward difficulty decrease.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST support 6 distinct difficulty levels: Foundation (1), Understanding (2), Application (3), Analysis (4), Synthesis (5), and Mastery (6).

- **FR-002**: System MUST automatically increase difficulty by 1 level when a learner achieves 85%+ average score over the last 3 answers without using hints.

- **FR-003**: System MUST automatically decrease difficulty by 1 level when a learner scores below 50% on 2 consecutive answers.

- **FR-004**: System MUST maintain current difficulty when learner scores are in the 60-85% range (optimal learning zone).

- **FR-005**: System MUST generate questions appropriate to the current difficulty level, matching defined question types for each level.

- **FR-006**: System MUST provide scaffolding hints when difficulty is decreased, tailored to the learner's identified struggle area.

- **FR-007**: System MUST track performance data for each answer: score, response time, hints used, difficulty level, concept tested, and timestamp.

- **FR-008**: System MUST limit available hints based on difficulty level: 3 hints for level 1, 2 for level 2, 1 for level 3, and 0 for levels 4-6.

- **FR-009**: System MUST factor hint usage into difficulty adjustment calculations (heavy hint usage contributes to difficulty decrease).

- **FR-010**: System MUST clamp difficulty level within valid range (1-6), preventing invalid values.

- **FR-011**: System MUST provide a default starting difficulty level for new learners with no performance history.

- **FR-012**: System MUST factor concept complexity (1-5 scale) into difficulty calculations, allowing complexity-adjusted effective difficulty.

- **FR-013**: System MUST identify the learner's struggle area (definition, process, relationship, or application) when providing scaffolding.

#### Struggle Area Detection Algorithm (FR-013)

The system identifies struggle area based on **question type failure patterns**:

| If recent failures are mostly... | Detected Struggle Area |
|----------------------------------|------------------------|
| definition, recognition, true_false | `definition` |
| explanation, comparison, cause_effect | `relationship` |
| scenario, case_study, problem_solving | `application` |
| breakdown, pattern_recognition | `process` |

**Detection Logic**:
1. Retrieve last 5 incorrect answers for the current concept
2. Count occurrences of each question_type
3. Map dominant question_type category to struggle_area
4. If no clear pattern (tie or <3 records), default to `definition` (most foundational)

- **FR-014**: System MUST persist difficulty history across quiz sessions for the same user.

### Key Entities

- **DifficultyLevel**: Represents one of 6 levels (1-6), each with a name, allowed question types, hint allowance, and time pressure setting.

- **PerformanceRecord**: Captures a single answer's metrics including score, response time, hints used, difficulty level, concept tested, timestamp, and whether it was in the optimal learning zone.

- **PerformanceTrend**: Aggregated analysis of recent answers showing average score, score trend (improving/stable/declining), time trend, and average hints used.

- **DifficultyAdjustment**: The calculated change to difficulty level, including previous level, new level, adjustment reasons, and recommended scaffolding if decreasing.

- **ScaffoldingSupport**: Structured hints and strategies for a specific struggle area, including hint text options and simplified question templates.

- **ConceptStats**: Per-concept performance tracking including attempts, total score, average, last difficulty, and mastery level.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Learners spend at least 50% of their quiz time in the optimal learning zone (60-85% scores).

- **SC-002**: Average difficulty adjustment accuracy: when difficulty increases, learner's next 3 answers average below 85%; when difficulty decreases, learner's next 3 answers average above 50%.

- **SC-003**: Learners who receive scaffolding support after difficulty decrease show improved scores (10%+ increase) within the next 3 questions on the same concept.

- **SC-004**: System correctly identifies struggle area (verified by learner feedback or subsequent performance improvement after targeted scaffolding) in at least 70% of cases.

- **SC-005**: Learners complete 20% more questions per session compared to non-adaptive quiz sessions (engagement increase).

- **SC-006**: Learner mastery of concepts (reaching 85%+ average) is achieved in 15% fewer attempts compared to fixed-difficulty quizzes.

## Assumptions

- The existing quiz system (prepare_quiz, get_quiz_step, advance_quiz) will be extended rather than replaced.
- Performance data will be stored using the existing SQLite storage infrastructure.
- The Gemini LLM will generate questions based on difficulty-level instructions in the agent prompt.
- Initial concept complexity ratings will be derived from the existing concept extraction pipeline or default to medium (3).
- Response time is measured from when the question is displayed to when the answer is submitted.
- The optimal learning zone (60-85%) is based on established educational research on desirable difficulty.
