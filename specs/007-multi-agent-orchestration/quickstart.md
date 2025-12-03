# Quickstart: Multi-Agent Orchestration

**Branch**: `007-multi-agent-orchestration`
**Date**: 2025-12-03

## Prerequisites

- Python 3.11+
- Google API key with Gemini access
- Existing `adk/` package installed

```bash
# Verify prerequisites
python --version  # Should be 3.11+
pip list | grep google-adk  # Should show google-adk installed
```

## Quick Setup

```bash
# 1. Ensure you're on the feature branch
git checkout 007-multi-agent-orchestration

# 2. Install any new dependencies (if added)
pip install -r adk/requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env and ensure GOOGLE_API_KEY is set
```

## Running the Multi-Agent System

```bash
# Start the interactive agent session
python -m adk.run_dev
```

## Example Interactions

### 1. Start with Diagnostic (New Topic)

```
User: I want to learn about calculus

Agent: [Coordinator routes to Diagnostic]
I'll first check if you're ready for calculus. Let me assess your
prerequisites...

Based on your mastery data:
- Algebra: 85% ✓
- Trigonometry: 45% ⚠️

Recommendation: You should strengthen your trigonometry before
diving into calculus. Would you like to start with a trig refresher?
```

### 2. Ask a Question (Routes to Tutor)

```
User: Can you explain what a derivative is?

Agent: [Coordinator routes to Tutor]
A derivative measures how a function changes as its input changes.
Think of it as the "instantaneous rate of change"...

[Examples provided]
[Key points summarized]

Ready to test your understanding? I can quiz you on derivatives.
```

### 3. Request a Quiz (Routes to Quiz → Feedback)

```
User: Quiz me on derivatives

Agent: [Coordinator routes to Quiz]
Starting a 5-question quiz on derivatives...

Question 1: What is the derivative of f(x) = x²?

User: 2x

Agent: Correct! ✓

[... more questions ...]

Agent: [Quiz completes, routes to Feedback]
Quiz Score: 4/5 (80%)

I noticed a pattern in your incorrect answer:
- Error type: Procedural
- You correctly identified the rule but made a calculation error
- Suggestion: Practice the chain rule with more complex examples

Your mastery is now at 78%. One more round should help you reach 85%.
Would you like to continue the learning cycle?
```

### 4. Check Progress (Routes to PathPlanner)

```
User: What should I learn next?

Agent: [Coordinator routes to PathPlanner]
Based on your progress:

Recommended Path:
1. Trigonometry Review (addresses weak area)
2. Calculus: Limits (next logical step)
3. Calculus: Derivatives (current focus)
4. Calculus: Integrals (after derivatives mastery)

Next recommended topic: Trigonometry Review
Reason: Strengthening this will make calculus easier.

Shall I start the trigonometry review?
```

### 5. Mid-Quiz Interruption

```
User: [During a quiz] Wait, can you explain what sine means again?

Agent: [Coordinator pauses quiz, routes to Tutor]
Quiz paused. I'll explain sine first.

Sine is a trigonometric function that relates an angle to the
ratio of sides in a right triangle...

[Explanation continues]

Would you like to resume your quiz?
```

## Key Files to Modify

When implementing this feature, you'll work with:

```
adk/
├── agent.py              # Add 5 new specialist agents
├── orchestration.py      # NEW: SequentialAgent, LoopAgent patterns
├── diagnostic_tools.py   # NEW: Prerequisite checking
├── path_tools.py         # NEW: Learning path recommendations
├── quiz_tools.py         # Add feedback integration
└── storage.py            # Add agent_transitions table
```

## Testing the Changes

```bash
# Run unit tests
pytest tests/unit/test_agents.py -v

# Run integration tests
pytest tests/integration/test_routing.py -v

# Test the full learning cycle
pytest tests/integration/test_learning_cycle.py -v
```

## Verifying Success Criteria

| Criteria | How to Verify |
|----------|---------------|
| SC-001: 90% routing accuracy | Review sample conversations |
| SC-002: 80% mastery completion | Check `learning_cycles` table |
| SC-005: 90% coherent conversations | User feedback |
| SC-006: <2s transitions | Observe via LoggingPlugin |

## Common Issues

### "Module not found" error
```bash
# Make sure you're in the project root
cd /path/to/learning-ai-agents
pip install -e .
```

### "No prerequisites found" for topic
The `concept_relationships` table may be empty. Run the question pipeline first:
```bash
python -m adk.question_pipeline
```

### Quiz not advancing
Check session state:
```python
# In debug mode, print session state
print(ctx.session.state)
```

## Next Steps

After implementing this feature:
1. Run `/speckit.tasks` to generate implementation tasks
2. Follow TDD: write tests first, then implement
3. Validate against acceptance scenarios in spec.md
