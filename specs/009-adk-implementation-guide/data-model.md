# Data Model: ADK Implementation Guide

**Branch**: `009-adk-implementation-guide`
**Date**: 2025-12-03

## Overview

Since this is a documentation-only feature, the "data model" describes the logical structure of the guide content rather than database entities or API schemas.

## Entities

### 1. ADKPattern

Represents a single ADK pattern or concept.

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| id | string | Unique pattern identifier | `sequential-agent` |
| name | string | Human-readable name | `SequentialAgent` |
| category | enum | Pattern category | `multi-agent`, `tool`, `memory`, `session`, `observability`, `deployment` |
| source_day | int | Kaggle Day number (1-5) | `1` |
| source_section | string | Section in source file | `Multi-Agent Patterns` |
| description | string | Brief explanation | `Executes sub-agents in sequence` |
| when_to_use | string | Conditional usage guidance | `When steps must complete before next` |
| code_snippet | string | Copy-pastable code | `SequentialAgent(name=..., sub_agents=[...])` |
| project_example | string | Reference to adk/ code | `adk/agent.py:78` |

### 2. FeatureSpec

Represents a feature specification (001-008).

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| id | string | Spec number | `001` |
| name | string | Feature name | `adaptive-difficulty` |
| title | string | Full title | `Adaptive Difficulty System` |
| primary_adk_patterns | string[] | Main patterns used | `["loop-agent", "function-tool", "session-state"]` |
| supporting_patterns | string[] | Secondary patterns | `["callbacks", "event-compaction"]` |

### 3. PatternMapping

Links ADK patterns to feature specs.

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| spec_id | string | Feature spec ID | `001` |
| pattern_id | string | ADK pattern ID | `loop-agent` |
| usage_context | string | How pattern is used | `Iterative difficulty adjustment until target mastery` |
| implementation_notes | string | Specific guidance | `Use `should_continue` callback to check mastery threshold` |

### 4. DecisionMatrix

Captures architectural choices between patterns.

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| decision_id | string | Decision identifier | `memory-type` |
| question | string | Decision question | `Which memory type to use?` |
| options | Option[] | Available choices | See below |
| default_recommendation | string | Default choice | `session-state` |

**Option sub-structure**:
| Field | Type | Description |
|-------|------|-------------|
| name | string | Option name |
| when_to_use | string | Conditions favoring this option |
| trade_offs | string | Pros/cons |

### 5. ImplementationChecklist

Step-by-step guidance for implementing a feature.

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| spec_id | string | Feature spec ID | `003` |
| steps | Step[] | Ordered implementation steps | See below |

**Step sub-structure**:
| Field | Type | Description |
|-------|------|-------------|
| order | int | Step number |
| action | string | What to do |
| pattern | string | ADK pattern reference |
| verification | string | How to verify completion |

## Relationships

```
FeatureSpec 1──M PatternMapping M──1 ADKPattern
     │                                    │
     │                                    │
     └──────────1 ImplementationChecklist │
                                          │
DecisionMatrix M──────────────────────────┘
```

- Each FeatureSpec has multiple PatternMappings
- Each ADKPattern can be used by multiple FeatureSpecs
- Each FeatureSpec has one ImplementationChecklist
- DecisionMatrices reference multiple ADKPatterns as options

## Content Categories

### ADK Pattern Categories

| Category | Patterns | Source Day |
|----------|----------|------------|
| multi-agent | SequentialAgent, ParallelAgent, LoopAgent, LlmAgent orchestration, sub_agents | Day 1 |
| tool | FunctionTool, AgentTool, MCP, long-running operations | Day 2 |
| memory | InMemoryMemoryService, load_memory, preload_memory, callbacks | Day 3 |
| session | InMemorySessionService, DatabaseSessionService, session state | Day 3 |
| observability | LoggingPlugin, custom plugins, tracing, metrics | Day 4 |
| evaluation | evalset, test_config, adk eval CLI, user simulation | Day 4 |
| deployment | Agent Engine, Cloud Run, A2A protocol, Memory Bank | Day 5 |

### Feature Spec Categories

| Spec | Primary Category | Secondary Categories |
|------|-----------------|---------------------|
| 001 | multi-agent | session, tool |
| 002 | tool | memory |
| 003 | evaluation | observability |
| 004 | memory | session |
| 005 | deployment | observability |
| 006 | tool | multi-agent |
| 007 | multi-agent | session |
| 008 | tool | memory |

## Validation Rules

1. **Pattern Completeness**: Every pattern mentioned in Kaggle Days must have an entry
2. **Spec Coverage**: Every spec (001-008) must have at least one PatternMapping
3. **Cross-Reference Integrity**: All pattern references in mappings must exist in ADKPattern table
4. **Code Snippet Validity**: All code snippets must be syntactically valid Python
5. **Project Example Accuracy**: All `adk/` references must point to existing files/lines

## Guide Document Structure

The entities above map to guide sections as follows:

```markdown
# ADK Implementation Guide

## Quick Reference Tables
- ADKPattern entries grouped by category

## Per-Spec Implementation Guides
For each FeatureSpec:
  - PatternMapping entries for that spec
  - ImplementationChecklist for that spec
  - Relevant DecisionMatrix entries

## Decision Matrices
- All DecisionMatrix entries organized by decision type

## Code Pattern Library
- ADKPattern code_snippets grouped by category

## Cross-Reference Index
- Day → Patterns (ADKPattern by source_day)
- Pattern → Specs (PatternMapping by pattern_id)
```
