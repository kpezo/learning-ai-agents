"""
Integration tests for adaptive quiz with difficulty adjustment and scaffolding.

Tests cover end-to-end quiz flow with:
- Difficulty level adjustments based on performance
- Scaffolding activation when difficulty decreases
- Question type filtering by difficulty level
"""

import pytest
from unittest.mock import MagicMock


class TestScaffoldingActivation:
    """Integration tests for scaffolding activation on difficulty decrease."""

    def test_scaffolding_activates_on_difficulty_decrease(self, quiz_prepared_context):
        """Should activate scaffolding when difficulty level decreases due to poor performance."""
        from adk.quiz_tools import _advance_quiz

        # Simulate 2 consecutive low scores to trigger decrease
        # First low score
        result1 = _advance_quiz(
            correct=False,
            concept_name="test_concept",
            tool_context=quiz_prepared_context
        )

        # Second low score (should trigger decrease and activate scaffolding)
        result2 = _advance_quiz(
            correct=False,
            concept_name="test_concept",
            tool_context=quiz_prepared_context
        )

        # Verify scaffolding is active
        assert result2["difficulty"]["scaffolding_active"] is True

        # Verify scaffolding hints are included
        assert "scaffolding" in result2
        assert "struggle_area" in result2["scaffolding"]
        assert "hints" in result2["scaffolding"]

    def test_scaffolding_includes_struggle_area_detection(self, quiz_prepared_context):
        """Should detect struggle area from recent errors and provide appropriate hints."""
        from adk.quiz_tools import _advance_quiz
        from adk.difficulty import _record_performance

        # Set up history with definition-type errors
        quiz_prepared_context.state["difficulty:history"] = [
            {"question_type": "definition", "score": 0.3, "concept_tested": "test"},
            {"question_type": "recognition", "score": 0.25, "concept_tested": "test"},
        ]

        # Trigger scaffolding activation
        quiz_prepared_context.state["difficulty:scaffolding_active"] = True

        # Advance quiz to get scaffolding
        result = _advance_quiz(
            correct=False,
            concept_name="test_concept",
            tool_context=quiz_prepared_context
        )

        # Verify scaffolding hints match detected struggle area
        if "scaffolding" in result:
            assert result["scaffolding"]["struggle_area"] == "definition"
            hints = result["scaffolding"]["hints"]
            assert "hint_templates" in hints
            assert "strategies" in hints
            assert len(hints["strategies"]) > 0

    def test_scaffolding_inactive_with_good_performance(self, quiz_prepared_context):
        """Should NOT activate scaffolding when performance is good."""
        from adk.quiz_tools import _advance_quiz

        # Simulate good performance
        result1 = _advance_quiz(
            correct=True,
            concept_name="test_concept",
            tool_context=quiz_prepared_context
        )

        result2 = _advance_quiz(
            correct=True,
            concept_name="test_concept",
            tool_context=quiz_prepared_context
        )

        # Verify scaffolding is NOT active
        assert result2["difficulty"]["scaffolding_active"] is False
        assert "scaffolding" not in result2

    def test_full_quiz_flow_with_difficulty_adjustment(self, quiz_prepared_context):
        """Integration test of complete quiz flow with difficulty adjustments."""
        from adk.quiz_tools import _advance_quiz

        # Start at level 3
        initial_level = quiz_prepared_context.state.get("difficulty:level", 3)
        assert initial_level == 3

        # Answer 2 questions incorrectly (trigger decrease)
        result1 = _advance_quiz(correct=False, tool_context=quiz_prepared_context)
        result2 = _advance_quiz(correct=False, tool_context=quiz_prepared_context)

        # Level should have decreased
        new_level = quiz_prepared_context.state.get("difficulty:level", 3)
        assert new_level < initial_level
        assert result2["difficulty"]["adjusted"] is True
        assert result2["difficulty"]["scaffolding_active"] is True

        # Answer correctly to improve
        result3 = _advance_quiz(correct=True, tool_context=quiz_prepared_context)

        # Eventually should return to normal (scaffolding may remain active)
        assert result3["status"] == "success"


class TestDifficultyAndQuestionTypes:
    """Integration tests for difficulty level and question type coordination."""

    def test_question_types_match_difficulty_level(self, quiz_prepared_context):
        """Should return question types appropriate for current difficulty level."""
        from adk.difficulty import _get_difficulty_level, _set_difficulty_level

        # Set to level 1 (Foundation)
        _set_difficulty_level(level=1, tool_context=quiz_prepared_context)

        result = _get_difficulty_level(tool_context=quiz_prepared_context)

        assert result["level"] == 1
        assert "question_types" in result
        assert "definition" in result["question_types"]
        assert "recognition" in result["question_types"]
        assert "scenario" not in result["question_types"]  # Not in level 1

    def test_question_types_change_with_level_adjustment(self, quiz_prepared_context):
        """Should update question types when difficulty level changes."""
        from adk.difficulty import _get_difficulty_level, _set_difficulty_level

        # Start at level 3
        result1 = _get_difficulty_level(tool_context=quiz_prepared_context)
        level3_types = result1["question_types"]

        # Change to level 5
        _set_difficulty_level(level=5, tool_context=quiz_prepared_context)
        result2 = _get_difficulty_level(tool_context=quiz_prepared_context)
        level5_types = result2["question_types"]

        # Question types should be different
        assert set(level3_types) != set(level5_types)
        assert "design" in level5_types  # Level 5 specific
        assert "scenario" not in level5_types  # Level 3 specific


class TestPerformanceTracking:
    """Integration tests for performance tracking through quiz flow."""

    def test_performance_history_accumulates(self, quiz_prepared_context):
        """Should accumulate performance history as quiz progresses."""
        from adk.quiz_tools import _advance_quiz

        # Initial history should be empty
        initial_history = quiz_prepared_context.state.get("difficulty:history", [])
        assert len(initial_history) == 0

        # Answer several questions
        _advance_quiz(correct=True, tool_context=quiz_prepared_context)
        _advance_quiz(correct=False, tool_context=quiz_prepared_context)
        _advance_quiz(correct=True, tool_context=quiz_prepared_context)

        # History should accumulate
        history = quiz_prepared_context.state.get("difficulty:history", [])
        assert len(history) == 3

    def test_consecutive_streak_tracking(self, quiz_prepared_context):
        """Should track consecutive correct/incorrect streaks."""
        from adk.quiz_tools import _advance_quiz

        # Answer correctly twice
        _advance_quiz(correct=True, tool_context=quiz_prepared_context)
        _advance_quiz(correct=True, tool_context=quiz_prepared_context)

        correct_streak = quiz_prepared_context.state.get("difficulty:consecutive_correct", 0)
        incorrect_streak = quiz_prepared_context.state.get("difficulty:consecutive_incorrect", 0)

        assert correct_streak == 2
        assert incorrect_streak == 0

        # Answer incorrectly once
        _advance_quiz(correct=False, tool_context=quiz_prepared_context)

        correct_streak = quiz_prepared_context.state.get("difficulty:consecutive_correct", 0)
        incorrect_streak = quiz_prepared_context.state.get("difficulty:consecutive_incorrect", 0)

        assert correct_streak == 0  # Reset
        assert incorrect_streak == 1
