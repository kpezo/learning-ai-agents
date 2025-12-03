# Data Model: Tests & Evaluation Framework

**Feature**: 003-test-evaluation
**Date**: 2025-12-03

## Overview

This feature primarily uses test-specific data structures rather than persisted entities. The main data models are for evaluation scenarios and test reporting.

## Entities

### EvaluationScenario

Represents a single test scenario for agent behavior evaluation.

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| scenario_id | string | Unique identifier | Required, alphanumeric + underscore |
| agent | string | Target agent name | Required, one of: tutor, assessor, curriculum_planner |
| description | string | Human-readable scenario description | Required |
| input | string | User message to send to agent | Required |
| expected_patterns | string[] | Regex patterns to match in response | At least one required |
| required_tool_calls | string[] | Tools that must be called | Optional |
| forbidden_tool_calls | string[] | Tools that must NOT be called | Optional |
| max_response_time_ms | int | Maximum allowed response time | Optional, default 5000 |
| pass_threshold | float | Minimum pattern match ratio | 0.0-1.0, default 0.8 |

### EvaluationSet

A collection of scenarios for a specific agent or feature.

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| name | string | Evalset name | Required |
| version | string | Evalset version | Semver format |
| agent | string | Target agent | Required |
| scenarios | EvaluationScenario[] | List of scenarios | At least one required |
| pass_threshold | float | Minimum passing scenario ratio | 0.0-1.0, default 0.8 |

### EvaluationResult

Result from running a single scenario.

| Field | Type | Description |
|-------|------|-------------|
| scenario_id | string | Reference to scenario |
| passed | boolean | Whether scenario passed |
| response | string | Actual agent response |
| matched_patterns | string[] | Patterns that matched |
| missing_patterns | string[] | Expected patterns not found |
| tool_calls | string[] | Tools actually called |
| response_time_ms | int | Actual response time |
| error | string | Error message if failed |

### TestReport

Aggregate test execution summary.

| Field | Type | Description |
|-------|------|-------------|
| timestamp | datetime | When tests ran |
| total_tests | int | Total test count |
| passed | int | Passing tests |
| failed | int | Failing tests |
| skipped | int | Skipped tests |
| duration_seconds | float | Total execution time |
| coverage_percent | float | Line coverage percentage |
| failures | TestFailure[] | Details of failed tests |

### TestFailure

Details of a single test failure.

| Field | Type | Description |
|-------|------|-------------|
| test_name | string | Full test path |
| message | string | Failure message |
| traceback | string | Stack trace |
| file_path | string | Source file |
| line_number | int | Failure line |

## Relationships

```
EvaluationSet (1) --contains--> (*) EvaluationScenario
EvaluationScenario (1) --produces--> (1) EvaluationResult
TestReport (1) --contains--> (*) TestFailure
```

## State Transitions

### EvaluationScenario Lifecycle

```
[Created] -> [Loaded] -> [Running] -> [Completed]
                                   \-> [Failed]
                                   \-> [Timeout]
```

### Test Execution States

```
[Pending] -> [Running] -> [Passed]
                       \-> [Failed]
                       \-> [Skipped]
                       \-> [Error]
```

## File Storage

Evaluation scenarios are stored as JSON files, not in the SQLite database:

```
tests/evaluation/evalsets/
├── tutor_scenarios.json      # EvaluationSet for Tutor agent
├── assessor_scenarios.json   # EvaluationSet for Assessor agent
└── curriculum_scenarios.json # EvaluationSet for Curriculum Planner
```

Test results are ephemeral (stdout/XML reports) unless configured to persist.
