# Quickstart: ADK Implementation Guide

**Branch**: `009-adk-implementation-guide`
**Date**: 2025-12-03

## Purpose

This quickstart explains how to use the ADK Implementation Guide once it's created.

## Prerequisites

- Access to this repository
- Familiarity with markdown
- Basic understanding of ADK (Google Agent Development Kit)

## Using the Guide

### Finding the Guide

```bash
# The guide is located at:
cat planning/adk-guide.md

# Or view in your IDE/editor
code planning/adk-guide.md
```

### Looking Up Patterns by Feature Spec

1. Open `planning/adk-guide.md`
2. Find the section for your spec (e.g., "## Spec 001: Adaptive Difficulty")
3. Review the ADK Pattern Mapping table
4. Follow the implementation checklist

### Looking Up Patterns by ADK Concept

1. Open `planning/adk-guide.md`
2. Use the Cross-Reference Tables section
3. Find "Day X → Patterns" to see which patterns came from that day
4. Or find "Pattern → Specs" to see which specs use a pattern

### Copying Code Patterns

1. Navigate to the "Code Pattern Library" section
2. Find the pattern category (multi-agent, tool, memory, etc.)
3. Copy the code snippet
4. Adapt for your specific use case

### Making Architectural Decisions

1. Navigate to the "Decision Matrices" section
2. Find the relevant decision (e.g., "Which memory type to use?")
3. Review options and their trade-offs
4. Choose based on your requirements

## Quick Navigation

| If you want to... | Go to section... |
|-------------------|------------------|
| Implement a specific spec | `## Spec XXX: [Name]` |
| Learn about a Day's concepts | `## Cross-Reference: Day X` |
| Compare pattern options | `## Decision Matrices` |
| Copy code for a pattern | `## Code Pattern Library` |
| Understand when to use a pattern | Pattern's "When to Use" column |

## Verification Checklist

After using the guide to implement a feature:

- [ ] All recommended ADK patterns are imported correctly
- [ ] Code follows the patterns from the Code Pattern Library
- [ ] Architectural decisions align with Decision Matrix recommendations
- [ ] Implementation covers all checklist items for the spec

## Source Material References

If you need more detail than the guide provides:

| Topic | Source File |
|-------|-------------|
| Multi-Agent Patterns | `planning/kaggle-days/day1-explanation.md` |
| Tools | `planning/kaggle-days/day2-explanation.md` |
| Memory & Sessions | `planning/kaggle-days/day3-explanation.md` |
| Observability & Evaluation | `planning/kaggle-days/day4-explanation.md` |
| Deployment & A2A | `planning/kaggle-days/day5-explanation.md` |

## Project-Specific Examples

The existing `adk/` directory contains working examples:

| Concept | Example Location |
|---------|------------------|
| Hierarchical agents | `adk/agent.py:78-103` |
| FunctionTool | `adk/tools.py` |
| Stateful tools with ToolContext | `adk/quiz_tools.py` |
| Session management | `adk/run_dev.py` |
| Custom storage (SQLite) | `adk/storage.py` |

## Contributing to the Guide

If you find gaps or errors:

1. Reference the Kaggle Days source material
2. Update the guide with corrections
3. Ensure cross-references remain consistent
4. Verify code snippets are syntactically correct
