# Feature Specification: Advanced Pedagogical Metrics

**Feature Branch**: `008-pedagogical-metrics`
**Created**: 2025-12-03
**Status**: Draft
**Input**: User description: "Implement advanced pedagogical measurement with Bayesian Knowledge Tracing, Item Response Theory, Zone of Proximal Development metrics, and research-validated mastery thresholds"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Probabilistic Mastery Tracking (Priority: P1)

As a learner progresses through quizzes, the system calculates a mastery probability for each concept using Bayesian Knowledge Tracing (BKT). This probability updates after every answer, accounting for the chance of lucky guesses and careless slips, providing a more accurate measure of true understanding than simple percentage scores.

**Why this priority**: This is the foundation of adaptive learning - accurate mastery estimation drives all personalization decisions. Simple percentages don't account for guessing or slip errors.

**Independent Test**: Can be fully tested by answering a sequence of questions and verifying the mastery probability updates correctly according to BKT formulas.

**Acceptance Scenarios**:

1. **Given** a learner with 50% mastery probability, **When** they answer correctly, **Then** mastery probability increases (more for hard questions, less for easy ones).

2. **Given** a learner who guessed correctly on an easy question, **When** the system recalculates, **Then** mastery increase is modest (accounting for guess probability).

3. **Given** a learner who slipped on an easy question they know, **When** mastery is recalculated, **Then** decrease is modest (accounting for slip probability).

4. **Given** a learner reaches 95% mastery probability, **When** the system evaluates mastery, **Then** the concept is marked as mastered.

---

### User Story 2 - Question Difficulty Calibration (Priority: P1)

Each quiz question has calibrated difficulty parameters that allow the system to match questions to learner ability. When a learner struggles with appropriate-difficulty questions, the system correctly attributes this to skill gaps rather than question mismatch.

**Why this priority**: Equally critical - without calibrated questions, the system cannot accurately assess ability or provide appropriate challenge levels.

**Independent Test**: Can be tested by examining question difficulty parameters and verifying they predict learner success rates accurately.

**Acceptance Scenarios**:

1. **Given** a question with difficulty parameter 0 (average difficulty), **When** attempted by an average-ability learner, **Then** the expected success rate is approximately 50%.

2. **Given** a question with high discrimination parameter, **When** high-ability and low-ability learners attempt it, **Then** there is a clear difference in success rates.

3. **Given** a multiple-choice question, **When** calculating expected success, **Then** the system accounts for the guessing probability (e.g., 25% for 4-option questions).

---

### User Story 3 - Zone of Proximal Development Maintenance (Priority: P2)

The system keeps learners in their Zone of Proximal Development (ZPD) - the range where learning is optimally challenging. Questions are neither too easy (boring) nor too hard (frustrating). The system detects when learners exit the ZPD and adjusts accordingly.

**Why this priority**: ZPD maintenance optimizes learning efficiency but requires the foundational metrics (BKT, IRT) to function.

**Independent Test**: Can be tested by monitoring a learner's success rate over time and verifying it stays within the optimal 60-85% range.

**Acceptance Scenarios**:

1. **Given** a learner achieving 90%+ success rate, **When** the system detects boredom indicators, **Then** it increases question difficulty.

2. **Given** a learner achieving below 50% success rate, **When** the system detects frustration indicators, **Then** it decreases difficulty and offers scaffolding.

3. **Given** a learner in the 60-85% success range, **When** the system evaluates ZPD, **Then** it maintains current difficulty (optimal learning zone).

---

### User Story 4 - Frustration and Boredom Detection (Priority: P2)

The system monitors behavioral indicators beyond simple correctness: response time, help-seeking patterns, and abandonment rates. When patterns indicate frustration (too hard) or boredom (too easy), the system proactively adjusts.

**Why this priority**: Behavioral indicators catch problems earlier than pure accuracy metrics. Important for learner engagement and retention.

**Independent Test**: Can be tested by simulating frustration patterns (rapid incorrect attempts) and verifying the system responds appropriately.

**Acceptance Scenarios**:

1. **Given** a learner makes 3 rapid incorrect attempts within 10 seconds, **When** the system evaluates frustration indicators, **Then** it flags potential frustration.

2. **Given** a learner requests hints on 4+ consecutive problems, **When** frustration analysis runs, **Then** difficulty is reduced and scaffolding is activated.

3. **Given** a learner completes questions in less than half the expected time, **When** boredom analysis runs, **Then** difficulty is increased.

---

### User Story 5 - Domain-Specific Mastery Thresholds (Priority: P3)

Different subject areas have different mastery requirements. Medical training requires 90-95% accuracy for safety-critical content, while general knowledge might accept 80%. The system applies appropriate thresholds based on content domain.

**Why this priority**: Enhances accuracy but the system can function with a single default threshold initially.

**Independent Test**: Can be tested by completing quizzes in different domains and verifying mastery is evaluated against the correct threshold.

**Acceptance Scenarios**:

1. **Given** a learner in a general education context, **When** evaluating mastery, **Then** the 80% threshold is applied.

2. **Given** a learner in a STEM skills context, **When** evaluating mastery, **Then** the 85% threshold with 3 consecutive correct is applied.

3. **Given** a safety-critical domain, **When** evaluating mastery, **Then** the 95% threshold is applied.

---

### Edge Cases

- What happens when a learner has very few data points? System uses prior probabilities with high uncertainty; confidence intervals are wide.
- How does the system handle a learner who improves dramatically mid-session? BKT includes a learning rate parameter that allows for rapid skill acquisition.
- What happens when question difficulty parameters haven't been calibrated? System uses estimated difficulty based on concept complexity and Bloom's level.
- How does the system handle gaming behavior (e.g., intentional failing)? Anomaly detection flags unusual patterns for review.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST calculate mastery probability using Bayesian Knowledge Tracing for each concept.

- **FR-002**: System MUST use BKT parameters: initial knowledge probability (P_L0), learning rate (P_T), guess probability (P_G), and slip probability (P_S).

- **FR-003**: System MUST update mastery probability after every answer using Bayesian update rules.

- **FR-004**: System MUST consider a concept mastered when probability reaches 95% threshold.

- **FR-005**: System MUST store question difficulty parameters: discrimination (a), difficulty (b), and guessing (c).

- **FR-006**: System MUST calculate expected success probability based on learner ability and question parameters.

- **FR-007**: System MUST define optimal learning zone as 60-85% initial success rate.

- **FR-008**: System MUST detect frustration indicators: rapid incorrect attempts, excessive help requests, high abandonment rate.

- **FR-009**: System MUST detect boredom indicators: very fast completion times, high consecutive correct streaks, decreasing engagement.

- **FR-010**: System MUST adjust difficulty when learner exits the optimal learning zone.

- **FR-011**: System MUST support domain-specific mastery thresholds (80%, 85%, 90%, 95%).

- **FR-012**: System MUST track response time for each answer.

- **FR-013**: System MUST track hint/help request count per problem.

- **FR-014**: System MUST track problem abandonment events.

- **FR-015**: System MUST store BKT parameters per concept, allowing for concept-specific calibration.

- **FR-016**: System MUST provide learner ability estimate (theta) for IRT-based matching.

### Key Entities

- **MasteryProbability**: A learner's probability of having mastered a concept, calculated via BKT. Includes probability value (0-1), confidence interval, and last update timestamp.

- **BKTParameters**: The parameters for BKT calculation for a concept: P_L0 (initial knowledge), P_T (learning rate), P_G (guess probability), P_S (slip probability).

- **QuestionParameters**: IRT parameters for a question: discrimination (a), difficulty (b), guessing (c), plus observed success rate and attempt count.

- **LearnerAbility**: A learner's estimated ability level (theta), used for matching to appropriate question difficulty.

- **ZPDStatus**: The learner's current Zone of Proximal Development status: optimal, frustration-risk, or boredom-risk.

- **BehavioralIndicators**: Tracked behavioral metrics including response time, help requests, abandonment count, and engagement score.

- **DomainThreshold**: The mastery threshold configuration for a specific domain, including required probability and consistency requirement.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: BKT mastery predictions correlate with post-test performance at 0.7+ correlation coefficient.

- **SC-002**: Learners spend at least 60% of quiz time in the optimal learning zone (60-85% success rate).

- **SC-003**: Frustration indicators are detected within 3 problems of learner exhibiting frustration patterns.

- **SC-004**: Boredom indicators are detected within 5 problems of learner exhibiting boredom patterns.

- **SC-005**: Question difficulty parameters predict actual success rates with ±10% accuracy after 50+ attempts.

- **SC-006**: Mastery achievement (95% probability) predicts successful performance on new questions at 85%+ rate.

- **SC-007**: Learners who receive ZPD-based adjustments show 25% higher completion rates than fixed-difficulty baseline.

## Assumptions

- Initial BKT parameters (P_L0=0.1, P_T=0.3, P_G=0.2, P_S=0.1) are based on educational research literature.
- Question difficulty parameters will be calibrated over time from learner response data.
- Initial question difficulty estimates are derived from concept complexity and Bloom's taxonomy level.
- The system uses a single ability dimension (unidimensional IRT model) per concept domain.
- Behavioral indicators use time-based thresholds calibrated from initial testing.
- This feature extends (not replaces) the simpler percentage-based tracking in 001-adaptive-difficulty.
