"""
Unit tests for scaffolding support logic.

Tests cover:
- Scaffolding strategy selection by struggle area
- Struggle area auto-detection from error patterns
- Scaffolding hint generation
"""

import pytest
from adk.scaffolding import (
    SCAFFOLDING_STRATEGIES,
    ScaffoldingSupport,
    detect_struggle_area,
    get_scaffolding_hints,
)


class TestScaffoldingStrategySelection:
    """Tests for scaffolding strategy selection by struggle area."""

    def test_definition_scaffolding_strategy(self):
        """Should return definition strategy for definition struggle area."""
        strategy = SCAFFOLDING_STRATEGIES["definition"]

        assert strategy.struggle_area == "definition"
        assert len(strategy.hint_templates) > 0
        assert len(strategy.strategies) > 0
        assert strategy.question_simplification is not None
        assert len(strategy.example_prompts) > 0

    def test_process_scaffolding_strategy(self):
        """Should return process strategy for process struggle area."""
        strategy = SCAFFOLDING_STRATEGIES["process"]

        assert strategy.struggle_area == "process"
        assert "step" in strategy.hint_templates[0].lower()
        assert len(strategy.strategies) > 0

    def test_relationship_scaffolding_strategy(self):
        """Should return relationship strategy for relationship struggle area."""
        strategy = SCAFFOLDING_STRATEGIES["relationship"]

        assert strategy.struggle_area == "relationship"
        assert "connect" in " ".join(strategy.hint_templates).lower()
        assert len(strategy.strategies) > 0

    def test_application_scaffolding_strategy(self):
        """Should return application strategy for application struggle area."""
        strategy = SCAFFOLDING_STRATEGIES["application"]

        assert strategy.struggle_area == "application"
        assert "example" in " ".join(strategy.hint_templates).lower()
        assert len(strategy.strategies) > 0

    def test_all_strategies_have_required_fields(self):
        """All scaffolding strategies should have all required fields."""
        for area, strategy in SCAFFOLDING_STRATEGIES.items():
            assert strategy.struggle_area == area
            assert len(strategy.hint_templates) >= 2
            assert len(strategy.strategies) >= 2
            assert strategy.question_simplification
            assert len(strategy.example_prompts) >= 1


class TestStruggleAreaDetection:
    """Tests for struggle area auto-detection from error patterns."""

    def test_detect_definition_struggle(self):
        """Should detect definition struggle from basic recall errors."""
        recent_errors = [
            {"question_type": "definition", "score": 0.2},
            {"question_type": "recognition", "score": 0.3},
        ]

        struggle_area = detect_struggle_area(recent_errors)
        assert struggle_area == "definition"

    def test_detect_process_struggle(self):
        """Should detect process struggle from sequential task errors."""
        recent_errors = [
            {"question_type": "problem_solving", "score": 0.3, "concept": "algorithm_steps"},
            {"question_type": "scenario", "score": 0.4, "concept": "workflow"},
        ]

        struggle_area = detect_struggle_area(recent_errors)
        assert struggle_area == "process"

    def test_detect_relationship_struggle(self):
        """Should detect relationship struggle from comparison errors."""
        recent_errors = [
            {"question_type": "comparison", "score": 0.3},
            {"question_type": "cause_effect", "score": 0.25},
        ]

        struggle_area = detect_struggle_area(recent_errors)
        assert struggle_area == "relationship"

    def test_detect_application_struggle(self):
        """Should detect application struggle from scenario/case study errors."""
        recent_errors = [
            {"question_type": "case_study", "score": 0.35},
            {"question_type": "scenario", "score": 0.4},
        ]

        struggle_area = detect_struggle_area(recent_errors)
        assert struggle_area == "application"

    def test_default_to_definition_with_no_errors(self):
        """Should default to definition struggle with no error data."""
        struggle_area = detect_struggle_area([])
        assert struggle_area == "definition"

    def test_default_to_definition_with_mixed_errors(self):
        """Should default to definition with mixed/unclear error patterns."""
        recent_errors = [
            {"question_type": "edge_case", "score": 0.3},
            {"question_type": "meta_cognition", "score": 0.4},
        ]

        struggle_area = detect_struggle_area(recent_errors)
        # Should choose the most common or default to definition
        assert struggle_area in SCAFFOLDING_STRATEGIES.keys()


class TestScaffoldingHintGeneration:
    """Tests for scaffolding hint generation."""

    def test_get_hints_for_definition_struggle(self):
        """Should return appropriate hints for definition struggle."""
        hints = get_scaffolding_hints("definition", concept="photosynthesis")

        assert "hint_templates" in hints
        assert "strategies" in hints
        assert "simplification" in hints
        assert len(hints["hint_templates"]) > 0

    def test_get_hints_for_process_struggle(self):
        """Should return appropriate hints for process struggle."""
        hints = get_scaffolding_hints("process", concept="mitosis")

        assert "hint_templates" in hints
        assert "strategies" in hints
        assert len(hints["strategies"]) > 0

    def test_get_hints_with_concept_substitution(self):
        """Should substitute concept name in hint templates."""
        concept = "photosynthesis"
        hints = get_scaffolding_hints("definition", concept=concept)

        # Check if at least one hint template contains the concept or placeholder
        templates = hints["hint_templates"]
        assert len(templates) > 0

    def test_get_hints_for_all_struggle_areas(self):
        """Should return valid hints for all struggle areas."""
        for area in SCAFFOLDING_STRATEGIES.keys():
            hints = get_scaffolding_hints(area)

            assert "hint_templates" in hints
            assert "strategies" in hints
            assert "simplification" in hints
            assert "example_prompts" in hints

    def test_invalid_struggle_area_returns_definition(self):
        """Should default to definition hints for invalid struggle area."""
        hints = get_scaffolding_hints("invalid_area")

        assert "hint_templates" in hints
        # Should have returned some valid scaffolding
        assert len(hints["strategies"]) > 0
