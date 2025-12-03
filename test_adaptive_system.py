#!/usr/bin/env python3
"""
Manual test script for the adaptive difficulty system.

This script demonstrates:
1. Difficulty level adjustment based on performance
2. Question type filtering by difficulty
3. Scaffolding activation when struggling

Run with: python test_adaptive_system.py
"""

from unittest.mock import MagicMock
from google.adk.tools.tool_context import ToolContext

from adk.difficulty import (
    _get_difficulty_level,
    _set_difficulty_level,
    _record_performance,
    get_allowed_question_types,
    DIFFICULTY_LEVELS,
)
from adk.scaffolding import (
    detect_struggle_area,
    get_scaffolding_hints,
    _get_scaffolding,
    SCAFFOLDING_STRATEGIES,
)


def create_test_context():
    """Create a mock tool context for testing."""
    context = MagicMock(spec=ToolContext)
    context.state = {
        "difficulty:level": 3,
        "difficulty:history": [],
        "difficulty:scaffolding_active": False,
        "difficulty:hints_used_current": 0,
        "difficulty:consecutive_correct": 0,
        "difficulty:consecutive_incorrect": 0,
    }
    context.session_id = "test_session"
    context.user_id = "test_user"
    return context


def print_section(title):
    """Print a formatted section header."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def test_difficulty_levels():
    """Test 1: Display all difficulty levels and their properties."""
    print_section("TEST 1: Difficulty Level Configuration")

    for level, config in DIFFICULTY_LEVELS.items():
        print(f"Level {level}: {config.name}")
        print(f"  Question Types: {', '.join(config.question_types)}")
        print(f"  Hint Allowance: {config.hint_allowance}")
        print(f"  Time Pressure: {config.time_pressure}x")
        print(f"  Description: {config.description}")
        print()


def test_difficulty_adjustment():
    """Test 2: Simulate difficulty adjustment based on performance."""
    print_section("TEST 2: Difficulty Adjustment Simulation")

    context = create_test_context()

    print("Starting at Level 3 (Application)\n")

    # Simulate poor performance (2 low scores)
    print("Simulating 2 consecutive low scores (trigger decrease)...")
    result1 = _record_performance(
        score=0.40,
        response_time_ms=15000,
        hints_used=2,
        concept_name="test_concept",
        question_type="scenario",
        tool_context=context,
    )
    print(f"  Score 1: 0.40 (40%)")

    result2 = _record_performance(
        score=0.35,
        response_time_ms=18000,
        hints_used=3,
        concept_name="test_concept",
        question_type="scenario",
        tool_context=context,
    )
    print(f"  Score 2: 0.35 (35%)")

    adjustment = result2["difficulty_adjustment"]
    print(f"\nDifficulty Adjustment:")
    print(f"  Type: {adjustment['type']}")
    print(f"  Previous Level: {adjustment['previous_level']}")
    print(f"  New Level: {adjustment['new_level']}")
    print(f"  Reason: {adjustment['reason']}")
    print(f"  Scaffolding Active: {context.state['difficulty:scaffolding_active']}")

    # Now simulate good performance (3 high scores)
    print("\n" + "-"*70)
    print("\nSimulating 3 consecutive high scores (trigger increase)...")

    # Reset to level 3 for demonstration
    _set_difficulty_level(3, tool_context=context)
    context.state["difficulty:history"] = []

    for i in range(3):
        result = _record_performance(
            score=0.90,
            response_time_ms=8000,
            hints_used=0,
            concept_name="test_concept",
            question_type="scenario",
            tool_context=context,
        )
        print(f"  Score {i+1}: 0.90 (90%), no hints")

    adjustment = result["difficulty_adjustment"]
    print(f"\nDifficulty Adjustment:")
    print(f"  Type: {adjustment['type']}")
    print(f"  Previous Level: {adjustment['previous_level']}")
    print(f"  New Level: {adjustment['new_level']}")
    print(f"  Reason: {adjustment['reason']}")


def test_question_types():
    """Test 3: Show how question types change with difficulty level."""
    print_section("TEST 3: Question Type Filtering by Level")

    context = create_test_context()

    for level in [1, 3, 6]:
        _set_difficulty_level(level, tool_context=context)
        result = _get_difficulty_level(tool_context=context)

        print(f"Level {level} ({result['name']}):")
        print(f"  Allowed Question Types: {', '.join(result['question_types'])}")
        print(f"  Hint Allowance: {result['hint_allowance']}")
        print()


def test_scaffolding_strategies():
    """Test 4: Display all scaffolding strategies."""
    print_section("TEST 4: Scaffolding Support Strategies")

    for area, strategy in SCAFFOLDING_STRATEGIES.items():
        print(f"{area.upper()} Struggle:")
        print(f"  Hint Examples:")
        for hint in strategy.hint_templates[:2]:
            print(f"    - {hint}")
        print(f"  Learning Strategies:")
        for strat in strategy.strategies:
            print(f"    - {strat}")
        print(f"  Question Simplification: {strategy.question_simplification}")
        print()


def test_scaffolding_detection():
    """Test 5: Test struggle area detection from error patterns."""
    print_section("TEST 5: Struggle Area Detection")

    test_cases = [
        {
            "name": "Definition Struggle",
            "errors": [
                {"question_type": "definition", "score": 0.3},
                {"question_type": "recognition", "score": 0.25},
            ]
        },
        {
            "name": "Process Struggle",
            "errors": [
                {"question_type": "problem_solving", "score": 0.35},
                {"question_type": "breakdown", "score": 0.40},
            ]
        },
        {
            "name": "Relationship Struggle",
            "errors": [
                {"question_type": "comparison", "score": 0.30},
                {"question_type": "cause_effect", "score": 0.35},
            ]
        },
        {
            "name": "Application Struggle",
            "errors": [
                {"question_type": "scenario", "score": 0.35},
                {"question_type": "case_study", "score": 0.40},
            ]
        },
    ]

    for test_case in test_cases:
        struggle_area = detect_struggle_area(test_case["errors"])
        hints = get_scaffolding_hints(struggle_area)

        print(f"{test_case['name']}:")
        print(f"  Detected Area: {struggle_area}")
        print(f"  First Hint: {hints['hint_templates'][0]}")
        print(f"  Simplification: {hints['simplification']}")
        print()


def test_end_to_end_flow():
    """Test 6: Simulate complete adaptive quiz flow."""
    print_section("TEST 6: End-to-End Adaptive Quiz Flow")

    context = create_test_context()

    print("Quiz Session Simulation:")
    print(f"Starting difficulty: Level {context.state['difficulty:level']}\n")

    # Simulate a struggling learner
    scenarios = [
        {"score": 0.75, "desc": "Question 1: Decent performance"},
        {"score": 0.45, "desc": "Question 2: Struggling (low score)"},
        {"score": 0.40, "desc": "Question 3: Still struggling (triggers decrease)"},
        {"score": 0.70, "desc": "Question 4: Improving (with scaffolding)"},
        {"score": 0.80, "desc": "Question 5: Recovering"},
    ]

    for i, scenario in enumerate(scenarios, 1):
        print(f"{scenario['desc']}: {scenario['score']*100:.0f}%")

        result = _record_performance(
            score=scenario["score"],
            response_time_ms=12000,
            hints_used=1 if scenario["score"] < 0.60 else 0,
            concept_name="test_concept",
            question_type="scenario",
            tool_context=context,
        )

        adjustment = result["difficulty_adjustment"]
        current_level = context.state["difficulty:level"]
        scaffolding_active = context.state["difficulty:scaffolding_active"]

        if adjustment["type"] != "maintain":
            print(f"  → Difficulty {adjustment['type']}d: Level {adjustment['previous_level']} → {adjustment['new_level']}")

        if scaffolding_active:
            print(f"  → Scaffolding ACTIVATED")
            scaffolding_result = _get_scaffolding(tool_context=context)
            if scaffolding_result["status"] == "success":
                print(f"  → Struggle Area: {scaffolding_result['struggle_area']}")

        print()

    print(f"Final difficulty level: {context.state['difficulty:level']}")
    print(f"Total questions answered: {len(context.state['difficulty:history'])}")


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("  ADAPTIVE DIFFICULTY SYSTEM - MANUAL TEST SUITE")
    print("="*70)

    try:
        test_difficulty_levels()
        test_difficulty_adjustment()
        test_question_types()
        test_scaffolding_strategies()
        test_scaffolding_detection()
        test_end_to_end_flow()

        print("\n" + "="*70)
        print("  ALL MANUAL TESTS COMPLETED SUCCESSFULLY")
        print("="*70 + "\n")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
