# Research: Advanced Pedagogical Metrics

**Feature**: 008-pedagogical-metrics
**Date**: 2025-12-03

## Overview

This document consolidates research findings for implementing Bayesian Knowledge Tracing (BKT), Item Response Theory (IRT), and Zone of Proximal Development (ZPD) metrics in the educational agent system.

---

## 1. Bayesian Knowledge Tracing (BKT)

### Decision
Use standard BKT with 4-parameter Hidden Markov Model for probabilistic mastery estimation.

### Rationale
BKT provides theoretically grounded mastery estimates that account for guessing and slip errors, unlike simple percentage-based tracking. It's well-established in educational research with known convergence properties.

### Core Formulas

**Update after correct answer:**
```
P(L_t | correct) = P(L_t) * (1 - P_S) / [P(L_t) * (1 - P_S) + (1 - P(L_t)) * P_G]
```

**Update after incorrect answer:**
```
P(L_t | incorrect) = P(L_t) * P_S / [P(L_t) * P_S + (1 - P(L_t)) * (1 - P_G)]
```

**Learning transition:**
```
P(L_t+1) = P(L_t | obs) + (1 - P(L_t | obs)) * P_T
```

### Parameters

| Parameter | Symbol | Default | Description |
|-----------|--------|---------|-------------|
| Prior | P(L0) | 0.1 | Initial knowledge probability |
| Learn | P(T) | 0.3 | Probability of learning after each attempt |
| Guess | P(G) | 0.2 | Probability of correct guess when not knowing |
| Slip | P(S) | 0.1 | Probability of error despite knowing |

### Constraints
- `0 <= all parameters <= 1`
- `P(G) + P(S) < 1` (prevents negative learning)
- `P(G) < 0.5` (guess should be below chance for binary)
- `P(S) < 0.1` (slips should be rare)

### Mastery Threshold
- Standard threshold: **95%** probability indicates mastery
- Spec requirement: 95% threshold (FR-004)

### Alternatives Considered
- **Simple ratio tracking**: Current approach, doesn't account for guessing/slipping
- **Deep Knowledge Tracing (DKT)**: Requires large datasets, overkill for current scale
- **pyBKT library**: Could import, but simple implementation preferred for transparency

---

## 2. Item Response Theory (IRT)

### Decision
Use 3-Parameter Logistic (3PL) model for question difficulty calibration.

### Rationale
3PL accounts for discrimination, difficulty, and guessing - essential for accurate matching of questions to learner ability. Simpler than full IRT packages but sufficient for our needs.

### Core Formula (3PL)

```
P(correct | theta, a, b, c) = c + (1 - c) / (1 + exp(-a * (theta - b)))
```

### Parameters

| Parameter | Symbol | Range | Default | Description |
|-----------|--------|-------|---------|-------------|
| Discrimination | a | 0.5-2.5 | 1.0 | How well question differentiates ability |
| Difficulty | b | -3 to +3 | 0.0 | Ability level for 50% success |
| Guessing | c | 0-0.35 | 0.25 | Probability of guessing correctly |

### Initial Parameter Estimates (Cold Start)

**Discrimination (a):**
- Conceptual questions: 0.8-1.0
- Procedural questions: 1.0-1.5
- Application questions: 1.2-2.0

**Difficulty (b):**
- Easy: -1.0
- Medium: 0.0
- Hard: 1.0
- Very Hard: 2.0

**Guessing (c):**
- 4-option multiple choice: 0.25
- 5-option multiple choice: 0.20
- Free response: 0.0

### Learner Ability Estimation (theta)

Use Maximum Likelihood Estimation with Newton-Raphson iteration:

```
theta_(n+1) = theta_n - [dL/dtheta] / [d2L/dtheta2]
```

Converge when `|theta_(n+1) - theta_n| < 0.001`

**Initial theta:** 0.0 (population mean)

### Fisher Information

```
I(theta) = a^2 * P_star * (1 - P_star) / (P * Q)
```

Where `P_star = (P - c) / (1 - c)`

Use information for:
- Selecting maximally informative questions
- Calculating standard error of ability estimate

### Alternatives Considered
- **2PL model**: Simpler but doesn't account for guessing
- **Rasch model (1PL)**: Too restrictive, assumes equal discrimination
- **Full IRT package (pyirt)**: Overkill for current scale

---

## 3. Zone of Proximal Development (ZPD)

### Decision
Use success rate thresholds with behavioral indicators for ZPD tracking.

### Rationale
Research-validated thresholds (60-85% success rate) provide clear boundaries for optimal learning zone. Behavioral indicators enable earlier detection of zone exit.

### Success Rate Thresholds

| Zone | Success Rate | Status |
|------|--------------|--------|
| Frustration | < 50% | Below ZPD |
| Learning | 50-60% | Lower ZPD boundary |
| Optimal | 60-85% | Within ZPD (target: 75%) |
| Near Mastery | 85-90% | Upper ZPD boundary |
| Boredom | > 90% | Above ZPD |

**Spec alignment:** FR-007 specifies 60-85% as optimal zone.

### ZPD Exit Detection

**Frustration triggers (exit below):**
- Success rate < 50% for 2+ consecutive attempts
- 3+ rapid incorrect attempts within 10 seconds (FR-008)
- Hint requests on 4+ consecutive problems

**Boredom triggers (exit above):**
- Success rate > 90% for 3+ consecutive attempts
- Completion time < 50% expected
- Zero hints used consistently

### Behavioral Indicators

**Frustration markers:**
- Response time: Initially slower, then rushing
- Error pattern: Repeated mistakes on similar items
- Engagement: Random guessing, giving up

**Boredom markers:**
- Response time: Faster than average (< 50% expected)
- Engagement: Minimal cognitive investment
- Pattern: High success without effort

### Response Time Thresholds

From research on flow vs frustration:
- Flow state: ~491ms average
- Boredom: ~459ms average (faster)
- Frustration: Variable, often slower then rushed

**Practical thresholds:**
- Expected time per question: Calibrated per question type
- Fast completion: < 50% expected time
- Slow completion: > 200% expected time

### Alternatives Considered
- **Fixed difficulty**: No adaptation, doesn't maintain ZPD
- **Random selection**: Inefficient, may frustrate or bore
- **Only success-rate based**: Misses behavioral signals

---

## 4. Domain-Specific Thresholds

### Decision
Support configurable mastery thresholds per domain.

### Rationale
Different content domains have different accuracy requirements. Safety-critical domains need higher thresholds.

### Threshold Configuration

| Domain | Threshold | Consistency | Rationale |
|--------|-----------|-------------|-----------|
| General Education | 80% | None | Standard learning |
| STEM Skills | 85% | 3 consecutive | Procedural accuracy |
| Medical/Safety | 90-95% | 5 consecutive | Error minimization |
| Language Learning | 80% | Spaced repetition | Retention focused |

**Default:** 80% for general content (FR-011)

---

## 5. Integration with Existing System

### Current State

**`adk/storage.py`:**
- Simple mastery: `mastery_level = times_correct / times_seen`
- No probabilistic estimation
- No question difficulty parameters
- No behavioral tracking

**`adk/quiz_tools.py`:**
- Tracks: correct count, mistakes, question index
- No response time tracking
- No ZPD detection
- No ability estimation

### Required Extensions

**Storage (new tables):**
- `bkt_parameters`: Per-concept BKT parameters
- `question_parameters`: IRT a, b, c per question
- `learner_ability`: theta estimate per user
- `behavioral_events`: Response times, hint usage

**Quiz Tools (new state keys):**
- `quiz:response_times`: Timestamp per answer
- `quiz:zpd_status`: Current zone status
- `quiz:theta`: Learner ability estimate

### Migration Path
1. Add new tables without modifying existing
2. BKT replaces simple ratio in `update_mastery()`
3. IRT parameters populated from cold-start estimates
4. Behavioral tracking added to `advance_quiz()`

---

## References

- Pardos & Heffernan (2010): BKT parameter initialization
- Baker et al. (2008): BKT degeneracy constraints
- Van de Sande: Properties of BKT model
- Item Response Theory literature: 3PL model
- Vygotsky (1978): Zone of Proximal Development theory
- Research on optimal success rates: 85% rule for learning
- Flow state research: Response time correlates
