# Implementation Plan: Advanced Pedagogical Metrics

**Branch**: `008-pedagogical-metrics` | **Date**: 2025-12-03 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/008-pedagogical-metrics/spec.md`

## Summary

Implement research-validated pedagogical measurement systems including Bayesian Knowledge Tracing (BKT) for probabilistic mastery estimation, Item Response Theory (IRT) for question difficulty calibration, Zone of Proximal Development (ZPD) tracking for optimal learning zone maintenance, and behavioral indicators for frustration/boredom detection. This extends the existing simple percentage-based tracking in `adk/storage.py` and `adk/quiz_tools.py`.

## Technical Context

**Language/Version**: Python 3.11+ (matching existing ADK codebase)
**Primary Dependencies**: google-adk, google-genai, numpy (for BKT/IRT calculations)
**Storage**: SQLite via `adk/storage.py` (extends existing per-user databases)
**Testing**: pytest, pytest-cov, pytest-asyncio (existing testing framework)
**Target Platform**: Cross-platform Python (CLI-based educational system)
**Project Type**: Single project (extends existing `adk/` module structure)
**Performance Goals**: Real-time mastery updates (<100ms per calculation)
**Constraints**: Must integrate with existing ADK session state and storage patterns
**Scale/Scope**: Per-user metrics, ~10-100 concepts per domain

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Note**: Constitution file contains placeholder template values only. Proceeding with standard best practices:

| Principle | Status | Notes |
|-----------|--------|-------|
| Extends existing patterns | ✅ PASS | Builds on `adk/storage.py` and `adk/quiz_tools.py` |
| Testable components | ✅ PASS | Pure functions for BKT/IRT calculations |
| Single responsibility | ✅ PASS | Separate modules for metrics types |
| Backward compatible | ✅ PASS | Extends ConceptMastery, doesn't break existing API |

## Project Structure

### Documentation (this feature)

```text
specs/008-pedagogical-metrics/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
adk/
├── storage.py           # EXTEND: Add BKT, IRT, ZPD tables
├── quiz_tools.py        # EXTEND: Use BKT for mastery calculations
├── metrics/             # NEW: Pedagogical metrics module
│   ├── __init__.py
│   ├── bkt.py           # Bayesian Knowledge Tracing
│   ├── irt.py           # Item Response Theory
│   ├── zpd.py           # Zone of Proximal Development
│   └── behavioral.py    # Frustration/boredom detection
└── metrics_tools.py     # NEW: ADK tools wrapping metrics

tests/
├── test_bkt.py          # Unit tests for BKT
├── test_irt.py          # Unit tests for IRT
├── test_zpd.py          # Unit tests for ZPD
├── test_behavioral.py   # Unit tests for behavioral indicators
└── test_metrics_integration.py  # Integration tests
```

**Structure Decision**: Extend existing `adk/` module structure. New metrics functionality lives in `adk/metrics/` submodule with dedicated files for each algorithm. Storage schema extensions go in `adk/storage.py`.

## Complexity Tracking

No complexity violations. Design follows existing patterns.

---

## Phase 0 Output: Research

**Completed**: See [research.md](./research.md)

Key decisions:
- **BKT**: Standard 4-parameter model with defaults P(L0)=0.1, P(T)=0.3, P(G)=0.2, P(S)=0.1
- **IRT**: 3PL model for question calibration with cold-start estimates
- **ZPD**: 60-85% optimal zone, behavioral indicators for exit detection
- **Thresholds**: Domain-specific (80% general, 85% STEM, 95% safety-critical)

---

## Phase 1 Output: Design Artifacts

### Data Model
**Completed**: See [data-model.md](./data-model.md)

New entities:
- `BKTParameters`: Per-concept BKT state and parameters
- `QuestionParameters`: IRT a, b, c per question
- `LearnerAbility`: Theta estimates per user per domain
- `ZPDStatus`: Zone tracking with recommendations
- `BehavioralEvent`: Response time, hints, abandonment tracking
- `DomainThreshold`: Configurable mastery thresholds

### API Contracts
**Completed**: See [contracts/](./contracts/)

Files:
- `metrics_api.py`: Python ABC contracts for BKT, IRT, ZPD, Behavioral services
- `storage_schema.sql`: SQLite schema extensions

### Integration Guide
**Completed**: See [quickstart.md](./quickstart.md)

Covers:
- Basic usage of each metrics module
- Integration with quiz_tools.py
- Storage persistence patterns
- ADK tool wrappers
- Migration from simple mastery

---

## Implementation Phases

### Phase 1: Core Algorithms (P1 stories)

1. **BKT Module** (`adk/metrics/bkt.py`)
   - BKTCalculator class with update() method
   - Bayesian update formulas
   - Confidence interval calculation
   - Mastery threshold checking

2. **IRT Module** (`adk/metrics/irt.py`)
   - 3PL probability calculation
   - Newton-Raphson ability estimation
   - Fisher information calculation
   - Optimal question selection

### Phase 2: ZPD and Behavioral (P2 stories)

3. **ZPD Module** (`adk/metrics/zpd.py`)
   - Zone evaluation from recent results
   - Difficulty recommendation logic
   - Exit detection triggers

4. **Behavioral Module** (`adk/metrics/behavioral.py`)
   - Frustration detection
   - Boredom detection
   - Response time analysis

### Phase 3: Integration (P2/P3 stories)

5. **Storage Extensions** (`adk/storage.py`)
   - New table initialization
   - BKT CRUD operations
   - Question parameter storage
   - Behavioral event logging

6. **Quiz Tools Integration** (`adk/quiz_tools.py`)
   - Replace simple mastery with BKT
   - Add response time tracking
   - ZPD-based difficulty adjustment

7. **ADK Tool Wrappers** (`adk/metrics_tools.py`)
   - FunctionTool wrappers for agent access
   - Tool context integration

### Phase 4: Testing and Domain Config (P3)

8. **Domain Thresholds**
   - Configurable threshold table
   - Per-concept domain assignment

9. **Comprehensive Tests**
   - Unit tests for each algorithm
   - Integration tests with storage
   - Acceptance scenario validation

---

## Dependencies Between Tasks

```
BKT Module ─────────────────┬──> Storage Extensions ──> Quiz Tools Integration
                            │
IRT Module ─────────────────┤
                            │
ZPD Module ──────────────── ┼──> ADK Tool Wrappers
                            │
Behavioral Module ──────────┘
```

- BKT and IRT are independent, can be parallel
- ZPD depends on success rate calculations
- Behavioral depends on response time infrastructure
- Storage extensions needed before quiz tools integration
- All core modules needed before ADK tool wrappers

---

## Constitution Check (Post-Design)

| Principle | Status | Notes |
|-----------|--------|-------|
| Extends existing patterns | ✅ PASS | Uses existing StorageService pattern |
| Testable components | ✅ PASS | Pure functions with no external deps |
| Single responsibility | ✅ PASS | Each metric type in separate module |
| Backward compatible | ✅ PASS | Existing API preserved, new columns added |

---

## Next Steps

Run `/speckit.tasks` to generate tasks.md with implementation tasks.
