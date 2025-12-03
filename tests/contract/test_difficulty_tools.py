"""
Contract tests for difficulty tool interfaces.

Tests verify ADK FunctionTool contracts match specifications:
- get_difficulty_level: Returns current level and metadata
- set_difficulty_level: Manually sets difficulty level
- record_performance: Records answer and triggers adjustment
- get_scaffolding: Returns scaffolding hints for struggle areas
"""

import pytest
from adk.difficulty import (
    _get_difficulty_level,
    _set_difficulty_level,
    _record_performance,
)
from adk.scaffolding import _get_scaffolding


class TestGetDifficultyLevelTool:
    """Contract tests for get_difficulty_level tool."""

    def test_returns_success_status(self, initialized_difficulty_context):
        """Should return success status when difficulty is initialized."""
        result = _get_difficulty_level(tool_context=initialized_difficulty_context)

        assert result["status"] == "success"
        assert "level" in result
        assert "name" in result
        assert "hint_allowance" in result
        assert "question_types" in result

    def test_returns_correct_difficulty_metadata(self, initialized_difficulty_context):
        """Should return correct metadata for level 3 (Application)."""
        result = _get_difficulty_level(tool_context=initialized_difficulty_context)

        assert result["level"] == 3
        assert result["name"] == "Application"
        assert result["hint_allowance"] == 1
        assert "scenario" in result["question_types"]

    def test_returns_error_when_not_initialized(self, mock_tool_context):
        """Should return error when difficulty not initialized."""
        result = _get_difficulty_level(tool_context=mock_tool_context)

        assert result["status"] == "error"
        assert "error_message" in result

    def test_returns_question_types_list(self, initialized_difficulty_context):
        """Should return question_types list for current difficulty level (US2)."""
        result = _get_difficulty_level(tool_context=initialized_difficulty_context)

        assert "question_types" in result
        assert isinstance(result["question_types"], list)
        assert len(result["question_types"]) > 0

        # Level 3 (Application) should have these types
        assert "scenario" in result["question_types"]
        assert "case_study" in result["question_types"]
        assert "problem_solving" in result["question_types"]


class TestSetDifficultyLevelTool:
    """Contract tests for set_difficulty_level tool."""

    def test_sets_difficulty_level_successfully(self, initialized_difficulty_context):
        """Should set difficulty level and return previous/new levels."""
        result = _set_difficulty_level(
            level=4,
            tool_context=initialized_difficulty_context
        )

        assert result["status"] == "success"
        assert result["previous_level"] == 3
        assert result["new_level"] == 4
        assert result["level_name"] == "Analysis"
        assert result["hint_allowance"] == 0

    def test_clamps_level_to_valid_range(self, initialized_difficulty_context):
        """Should clamp invalid levels to 1-6 range."""
        result = _set_difficulty_level(
            level=10,
            tool_context=initialized_difficulty_context
        )

        assert result["new_level"] == 6  # Clamped to maximum

        result = _set_difficulty_level(
            level=0,
            tool_context=initialized_difficulty_context
        )

        assert result["new_level"] == 1  # Clamped to minimum


class TestRecordPerformanceTool:
    """Contract tests for record_performance tool."""

    def test_records_performance_successfully(self, quiz_prepared_context):
        """Should record performance and return adjustment details."""
        result = _record_performance(
            score=0.75,
            response_time_ms=12000,
            hints_used=1,
            concept_name="test_concept",
            question_type="scenario",
            tool_context=quiz_prepared_context
        )

        assert result["status"] == "success"
        assert result["performance_recorded"] is True
        assert "in_optimal_zone" in result
        assert "difficulty_adjustment" in result
        assert "trend" in result

    def test_detects_optimal_zone(self, quiz_prepared_context):
        """Should correctly identify optimal zone (60-85%)."""
        result = _record_performance(
            score=0.72,
            response_time_ms=10000,
            hints_used=0,
            concept_name="test_concept",
            question_type="scenario",
            tool_context=quiz_prepared_context
        )

        assert result["in_optimal_zone"] is True

        result = _record_performance(
            score=0.95,
            response_time_ms=8000,
            hints_used=0,
            concept_name="test_concept",
            question_type="scenario",
            tool_context=quiz_prepared_context
        )

        assert result["in_optimal_zone"] is False

    def test_triggers_difficulty_adjustment(self, quiz_prepared_context):
        """Should trigger difficulty adjustment and include details."""
        # Record 3 high scores to trigger increase
        for _ in range(3):
            result = _record_performance(
                score=0.90,
                response_time_ms=10000,
                hints_used=0,
                concept_name="test_concept",
                question_type="scenario",
                tool_context=quiz_prepared_context
            )

        # Last result should show increase
        adjustment = result["difficulty_adjustment"]
        assert adjustment["type"] in ["increase", "maintain", "decrease"]
        assert "previous_level" in adjustment
        assert "new_level" in adjustment
        assert "reason" in adjustment

    def test_includes_performance_trend(self, quiz_prepared_context):
        """Should include trend analysis in response."""
        result = _record_performance(
            score=0.85,
            response_time_ms=11000,
            hints_used=0,
            concept_name="test_concept",
            question_type="scenario",
            tool_context=quiz_prepared_context
        )

        trend = result["trend"]
        assert "avg_score" in trend
        assert "trend_direction" in trend
        assert "consecutive_correct" in trend


class TestGetScaffoldingTool:
    """Contract tests for get_scaffolding tool."""

    def test_returns_success_with_scaffolding_active(self, initialized_difficulty_context):
        """Should return scaffolding hints when scaffolding is active."""
        # Enable scaffolding
        initialized_difficulty_context.state["difficulty:scaffolding_active"] = True
        initialized_difficulty_context.state["difficulty:history"] = [
            {"question_type": "definition", "score": 0.3}
        ]

        result = _get_scaffolding(tool_context=initialized_difficulty_context)

        assert result["status"] == "success"
        assert result["scaffolding_active"] is True
        assert "struggle_area" in result
        assert "hints" in result
        assert "hint_templates" in result["hints"]
        assert "strategies" in result["hints"]
        assert "simplification" in result["hints"]

    def test_returns_inactive_when_scaffolding_disabled(self, initialized_difficulty_context):
        """Should return inactive status when scaffolding is disabled."""
        initialized_difficulty_context.state["difficulty:scaffolding_active"] = False

        result = _get_scaffolding(tool_context=initialized_difficulty_context)

        assert result["status"] == "success"
        assert result["scaffolding_active"] is False
        assert result.get("hints") is None

    def test_detects_struggle_area_from_history(self, initialized_difficulty_context):
        """Should detect struggle area from performance history."""
        initialized_difficulty_context.state["difficulty:scaffolding_active"] = True
        initialized_difficulty_context.state["difficulty:history"] = [
            {"question_type": "comparison", "score": 0.25},
            {"question_type": "cause_effect", "score": 0.35},
        ]

        result = _get_scaffolding(tool_context=initialized_difficulty_context)

        assert result["status"] == "success"
        assert result["struggle_area"] == "relationship"

    def test_includes_all_required_hint_fields(self, initialized_difficulty_context):
        """Should include all required fields in hint response."""
        initialized_difficulty_context.state["difficulty:scaffolding_active"] = True
        initialized_difficulty_context.state["difficulty:history"] = [
            {"question_type": "scenario", "score": 0.3}
        ]

        result = _get_scaffolding(tool_context=initialized_difficulty_context)

        hints = result["hints"]
        assert isinstance(hints["hint_templates"], list)
        assert len(hints["hint_templates"]) > 0
        assert isinstance(hints["strategies"], list)
        assert len(hints["strategies"]) > 0
        assert isinstance(hints["simplification"], str)
        assert len(hints["simplification"]) > 0
        assert isinstance(hints["example_prompts"], list)
        assert len(hints["example_prompts"]) > 0

    def test_returns_error_with_no_context(self):
        """Should return error when tool context is missing."""
        result = _get_scaffolding(tool_context=None)

        assert result["status"] == "error"
        assert "error_message" in result
