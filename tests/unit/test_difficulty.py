"""
Unit tests for difficulty adjustment logic.

Tests cover:
- Difficulty increase logic (3 consecutive ≥85%)
- Difficulty decrease logic (2 consecutive <50%)
- Difficulty maintain logic (60-85% optimal zone)
- Difficulty level clamping (1-6 bounds)
"""

import pytest
from adk.difficulty import (
    DIFFICULTY_LEVELS,
    DifficultyLevel,
    PerformanceRecord,
    PerformanceTrend,
    DifficultyAdjustment,
    calculate_performance_trend,
    calculate_difficulty_adjustment,
    get_concept_complexity,
)


class TestDifficultyIncrease:
    """Tests for difficulty level increase logic."""

    def test_increase_on_three_consecutive_high_scores(self):
        """Should increase difficulty after 3 consecutive scores ≥85% with no hints."""
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

        assert adjustment.adjustment_type == "increase"
        assert adjustment.new_level == 4
        assert adjustment.previous_level == 3

    def test_no_increase_with_hints_used(self):
        """Should NOT increase difficulty if hints were used."""
        records = [
            {"score": 0.90, "hints_used": 1, "difficulty_level": 3},
            {"score": 0.88, "hints_used": 0, "difficulty_level": 3},
            {"score": 0.86, "hints_used": 0, "difficulty_level": 3},
        ]

        adjustment = calculate_difficulty_adjustment(
            current_level=3,
            performance_records=records,
            user_id="test_user",
            session_id="test_session"
        )

        assert adjustment.adjustment_type != "increase"

    def test_no_increase_with_only_two_consecutive(self):
        """Should NOT increase difficulty with only 2 consecutive high scores."""
        records = [
            {"score": 0.90, "hints_used": 0, "difficulty_level": 3},
            {"score": 0.88, "hints_used": 0, "difficulty_level": 3},
        ]

        adjustment = calculate_difficulty_adjustment(
            current_level=3,
            performance_records=records,
            user_id="test_user",
            session_id="test_session"
        )

        assert adjustment.adjustment_type != "increase"


class TestDifficultyDecrease:
    """Tests for difficulty level decrease logic."""

    def test_decrease_on_two_consecutive_low_scores(self):
        """Should decrease difficulty after 2 consecutive scores <50%."""
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

        assert adjustment.adjustment_type == "decrease"
        assert adjustment.new_level == 3
        assert adjustment.previous_level == 4
        assert adjustment.scaffolding_recommended is True

    def test_no_decrease_with_one_low_score(self):
        """Should NOT decrease difficulty with only 1 low score."""
        records = [
            {"score": 0.40, "hints_used": 2, "difficulty_level": 3},
        ]

        adjustment = calculate_difficulty_adjustment(
            current_level=3,
            performance_records=records,
            user_id="test_user",
            session_id="test_session"
        )

        assert adjustment.adjustment_type != "decrease"


class TestDifficultyMaintain:
    """Tests for difficulty level maintain logic."""

    def test_maintain_in_optimal_zone(self):
        """Should maintain difficulty when scores are in 60-85% range."""
        records = [
            {"score": 0.75, "hints_used": 1, "difficulty_level": 3},
            {"score": 0.68, "hints_used": 0, "difficulty_level": 3},
            {"score": 0.72, "hints_used": 1, "difficulty_level": 3},
        ]

        adjustment = calculate_difficulty_adjustment(
            current_level=3,
            performance_records=records,
            user_id="test_user",
            session_id="test_session"
        )

        assert adjustment.adjustment_type == "maintain"
        assert adjustment.new_level == 3
        assert adjustment.previous_level == 3

    def test_maintain_with_mixed_performance(self):
        """Should maintain difficulty with mixed performance."""
        records = [
            {"score": 0.80, "hints_used": 0, "difficulty_level": 2},
            {"score": 0.55, "hints_used": 1, "difficulty_level": 2},
        ]

        adjustment = calculate_difficulty_adjustment(
            current_level=2,
            performance_records=records,
            user_id="test_user",
            session_id="test_session"
        )

        assert adjustment.adjustment_type == "maintain"
        assert adjustment.new_level == 2


class TestDifficultyLevelClamping:
    """Tests for difficulty level bounds enforcement (1-6)."""

    def test_clamp_at_maximum_level_6(self):
        """Should clamp difficulty at level 6."""
        records = [
            {"score": 0.95, "hints_used": 0, "difficulty_level": 6},
            {"score": 0.92, "hints_used": 0, "difficulty_level": 6},
            {"score": 0.90, "hints_used": 0, "difficulty_level": 6},
        ]

        adjustment = calculate_difficulty_adjustment(
            current_level=6,
            performance_records=records,
            user_id="test_user",
            session_id="test_session"
        )

        # Should want to increase but clamp at 6
        assert adjustment.new_level == 6
        assert adjustment.previous_level == 6

    def test_clamp_at_minimum_level_1(self):
        """Should clamp difficulty at level 1."""
        records = [
            {"score": 0.30, "hints_used": 3, "difficulty_level": 1},
            {"score": 0.40, "hints_used": 3, "difficulty_level": 1},
        ]

        adjustment = calculate_difficulty_adjustment(
            current_level=1,
            performance_records=records,
            user_id="test_user",
            session_id="test_session"
        )

        # Should want to decrease but clamp at 1
        assert adjustment.new_level == 1
        assert adjustment.previous_level == 1


class TestPerformanceTrendCalculation:
    """Tests for performance trend analysis."""

    def test_improving_trend(self):
        """Should detect improving score trend."""
        records = [
            {"score": 0.60, "response_time_ms": 15000, "hints_used": 2},
            {"score": 0.70, "response_time_ms": 12000, "hints_used": 1},
            {"score": 0.80, "response_time_ms": 10000, "hints_used": 0},
        ]

        trend = calculate_performance_trend(
            records=records,
            user_id="test_user",
            window_size=3
        )

        assert trend.score_trend == "improving"
        assert trend.avg_score > 0.65
        assert trend.consecutive_correct > 0

    def test_declining_trend(self):
        """Should detect declining score trend."""
        records = [
            {"score": 0.45, "response_time_ms": 15000, "hints_used": 2},
            {"score": 0.40, "response_time_ms": 13000, "hints_used": 1},
            {"score": 0.35, "response_time_ms": 10000, "hints_used": 0},
        ]

        trend = calculate_performance_trend(
            records=records,
            user_id="test_user",
            window_size=3
        )

        assert trend.score_trend == "declining"
        assert trend.consecutive_incorrect > 0


class TestConceptComplexity:
    """Tests for concept complexity integration."""

    def test_get_concept_complexity_default(self):
        """Should return default complexity of 3 when not found."""
        complexity = get_concept_complexity("unknown_concept", "test_user")
        assert complexity == 3

    def test_complexity_affects_thresholds(self):
        """Should adjust difficulty thresholds based on concept complexity."""
        # High complexity concept (5) should have harder thresholds
        # This test will verify the modifier is applied
        # Implementation detail: effective_threshold = base_threshold * (complexity / 3.0)

        # For complexity 5: 0.85 * (5/3) = 1.42 (clamped), harder to increase
        # For complexity 1: 0.85 * (1/3) = 0.28, easier to increase

        # This will be fully testable once the implementation is complete
        pass


class TestQuestionTypeMapping:
    """Tests for question type mapping per difficulty level (US2)."""

    def test_level_1_question_types(self):
        """Should return Foundation level question types."""
        from adk.difficulty import get_allowed_question_types

        types = get_allowed_question_types(1)
        assert "definition" in types
        assert "recognition" in types
        assert "true_false" in types

    def test_level_3_question_types(self):
        """Should return Application level question types."""
        from adk.difficulty import get_allowed_question_types

        types = get_allowed_question_types(3)
        assert "scenario" in types
        assert "case_study" in types
        assert "problem_solving" in types

    def test_level_6_question_types(self):
        """Should return Mastery level question types."""
        from adk.difficulty import get_allowed_question_types

        types = get_allowed_question_types(6)
        assert "teach_back" in types
        assert "edge_case" in types
        assert "meta_cognition" in types

    def test_question_types_clamping(self):
        """Should clamp invalid levels and return appropriate types."""
        from adk.difficulty import get_allowed_question_types

        # Test upper bound
        types = get_allowed_question_types(10)
        assert types == DIFFICULTY_LEVELS[6].question_types

        # Test lower bound
        types = get_allowed_question_types(0)
        assert types == DIFFICULTY_LEVELS[1].question_types
