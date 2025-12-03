#!/usr/bin/env python3
"""
Manual smoke test for MVP Adaptive Difficulty System.
Tests core functionality without requiring pytest.
"""

import sys
sys.path.insert(0, '/Users/kpezo/Development/Privat/learning-ai-agents')

from adk.difficulty import (
    DIFFICULTY_LEVELS,
    calculate_performance_trend,
    calculate_difficulty_adjustment,
    get_concept_complexity,
)

def test_difficulty_levels():
    """Test that difficulty levels are properly configured."""
    print("Testing difficulty levels configuration...")
    assert len(DIFFICULTY_LEVELS) == 6, "Should have 6 difficulty levels"
    assert DIFFICULTY_LEVELS[1].name == "Foundation"
    assert DIFFICULTY_LEVELS[3].name == "Application"
    assert DIFFICULTY_LEVELS[6].name == "Mastery"
    assert DIFFICULTY_LEVELS[1].hint_allowance == 3
    assert DIFFICULTY_LEVELS[6].hint_allowance == 0
    print("✓ Difficulty levels configured correctly")

def test_increase_logic():
    """Test difficulty increase on 3 consecutive high scores."""
    print("\nTesting difficulty increase logic...")
    records = [
        {"score": 0.90, "hints_used": 0, "difficulty_level": 3},
        {"score": 0.88, "hints_used": 0, "difficulty_level": 3},
        {"score": 0.86, "hints_used": 0, "difficulty_level": 3},
    ]

    adjustment = calculate_difficulty_adjustment(
        current_level=3,
        performance_records=records,
        user_id="test_user",
        session_id="test_session"
    )

    assert adjustment.adjustment_type == "increase", f"Expected increase, got {adjustment.adjustment_type}"
    assert adjustment.new_level == 4, f"Expected level 4, got {adjustment.new_level}"
    print(f"✓ Difficulty increased from {adjustment.previous_level} to {adjustment.new_level}")

def test_decrease_logic():
    """Test difficulty decrease on 2 consecutive low scores."""
    print("\nTesting difficulty decrease logic...")
    records = [
        {"score": 0.40, "hints_used": 2, "difficulty_level": 4},
        {"score": 0.45, "hints_used": 3, "difficulty_level": 4},
    ]

    adjustment = calculate_difficulty_adjustment(
        current_level=4,
        performance_records=records,
        user_id="test_user",
        session_id="test_session"
    )

    assert adjustment.adjustment_type == "decrease", f"Expected decrease, got {adjustment.adjustment_type}"
    assert adjustment.new_level == 3, f"Expected level 3, got {adjustment.new_level}"
    assert adjustment.scaffolding_recommended is True, "Scaffolding should be recommended"
    print(f"✓ Difficulty decreased from {adjustment.previous_level} to {adjustment.new_level}")
    print(f"✓ Scaffolding recommended: {adjustment.scaffolding_recommended}")

def test_maintain_logic():
    """Test difficulty maintain in optimal zone."""
    print("\nTesting difficulty maintain logic...")
    records = [
        {"score": 0.75, "hints_used": 1, "difficulty_level": 3},
        {"score": 0.68, "hints_used": 0, "difficulty_level": 3},
    ]

    adjustment = calculate_difficulty_adjustment(
        current_level=3,
        performance_records=records,
        user_id="test_user",
        session_id="test_session"
    )

    assert adjustment.adjustment_type == "maintain", f"Expected maintain, got {adjustment.adjustment_type}"
    assert adjustment.new_level == 3, f"Expected level 3, got {adjustment.new_level}"
    print(f"✓ Difficulty maintained at level {adjustment.new_level}")

def test_level_clamping():
    """Test difficulty level bounds (1-6)."""
    print("\nTesting level clamping...")

    # Test upper bound
    records_high = [
        {"score": 0.95, "hints_used": 0, "difficulty_level": 6},
        {"score": 0.92, "hints_used": 0, "difficulty_level": 6},
        {"score": 0.90, "hints_used": 0, "difficulty_level": 6},
    ]

    adjustment = calculate_difficulty_adjustment(
        current_level=6,
        performance_records=records_high,
        user_id="test_user",
        session_id="test_session"
    )

    assert adjustment.new_level == 6, f"Should clamp at level 6, got {adjustment.new_level}"
    print(f"✓ Upper bound clamping works (level 6)")

    # Test lower bound
    records_low = [
        {"score": 0.30, "hints_used": 3, "difficulty_level": 1},
        {"score": 0.40, "hints_used": 3, "difficulty_level": 1},
    ]

    adjustment = calculate_difficulty_adjustment(
        current_level=1,
        performance_records=records_low,
        user_id="test_user",
        session_id="test_session"
    )

    assert adjustment.new_level == 1, f"Should clamp at level 1, got {adjustment.new_level}"
    print(f"✓ Lower bound clamping works (level 1)")

def test_performance_trend():
    """Test performance trend calculation."""
    print("\nTesting performance trend analysis...")
    records = [
        {"score": 0.80, "response_time_ms": 10000, "hints_used": 0},
        {"score": 0.75, "response_time_ms": 12000, "hints_used": 1},
        {"score": 0.70, "response_time_ms": 13000, "hints_used": 1},
    ]

    trend = calculate_performance_trend(
        records=records,
        user_id="test_user",
        window_size=3
    )

    assert trend.window_size == 3
    assert trend.avg_score > 0.7
    assert trend.score_trend in ["improving", "stable", "declining"]
    print(f"✓ Performance trend calculated: {trend.score_trend} (avg score: {trend.avg_score:.2f})")

def test_concept_complexity():
    """Test concept complexity retrieval."""
    print("\nTesting concept complexity...")
    complexity = get_concept_complexity("unknown_concept", "test_user")
    assert complexity == 3, f"Expected default complexity 3, got {complexity}"
    print(f"✓ Default complexity returned: {complexity}")

def main():
    """Run all smoke tests."""
    print("="*60)
    print("MVP ADAPTIVE DIFFICULTY SYSTEM - SMOKE TEST")
    print("="*60)

    try:
        test_difficulty_levels()
        test_increase_logic()
        test_decrease_logic()
        test_maintain_logic()
        test_level_clamping()
        test_performance_trend()
        test_concept_complexity()

        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED - MVP IS WORKING!")
        print("="*60)
        return 0

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
