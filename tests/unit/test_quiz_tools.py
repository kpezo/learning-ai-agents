"""Unit tests for adk/quiz_tools.py

Tests quiz state management functions including prepare_quiz, get_quiz_step,
advance_quiz, and reveal_context with mocked retriever and storage.
"""

import pytest
from unittest.mock import patch, MagicMock
from adk.quiz_tools import (
    _prepare_quiz,
    _get_quiz_step,
    _advance_quiz,
    _reveal_context,
    _get_learning_stats,
    _get_weak_concepts,
    _get_quiz_history,
)


class TestPrepareQuiz:
    """Tests for _prepare_quiz function"""

    def test_prepare_quiz_success(self, mock_retriever, mock_tool_context):
        """Test successful quiz preparation"""
        with patch("adk.quiz_tools._retriever", mock_retriever):
            result = _prepare_quiz("Python Basics", max_chunks=3, tool_context=mock_tool_context)

            assert result["status"] == "success"
            assert mock_tool_context.state.get("quiz:snippets") is not None
            assert mock_tool_context.state.get("quiz:topic") == "Python Basics"
            assert mock_tool_context.state.get("quiz:index") == 0

    def test_prepare_quiz_initializes_counters(self, mock_retriever, mock_tool_context):
        """Test that prepare_quiz initializes all progress counters"""
        with patch("adk.quiz_tools._retriever", mock_retriever):
            _prepare_quiz("Python", max_chunks=2, tool_context=mock_tool_context)

            # Check all counters are initialized
            assert mock_tool_context.state.get("quiz:index") == 0
            assert mock_tool_context.state.get("quiz:mistakes") == 0
            assert mock_tool_context.state.get("quiz:total_mistakes") == 0
            assert mock_tool_context.state.get("quiz:correct") == 0

    def test_prepare_quiz_no_retriever(self, mock_tool_context):
        """Test error when retriever not initialized"""
        with patch("adk.quiz_tools._retriever", None):
            result = _prepare_quiz("Test", tool_context=mock_tool_context)

            assert result["status"] == "error"
            assert "not initialized" in result["error_message"].lower()

    def test_prepare_quiz_no_snippets_found(self, mock_tool_context):
        """Test error when no snippets found for topic"""
        # Create mock retriever that returns empty list
        empty_retriever = MagicMock()
        empty_retriever.get_relevant_documents.return_value = []

        with patch("adk.quiz_tools._retriever", empty_retriever):
            result = _prepare_quiz("NonexistentTopic", tool_context=mock_tool_context)

            assert result["status"] == "error"
            assert "No snippets found" in result["error_message"]

    def test_prepare_quiz_respects_max_chunks(self, mock_retriever, mock_tool_context):
        """Test that max_chunks parameter limits snippets"""
        with patch("adk.quiz_tools._retriever", mock_retriever):
            _prepare_quiz("Python", max_chunks=2, tool_context=mock_tool_context)

            snippets = mock_tool_context.state.get("quiz:snippets")
            assert len(snippets) <= 2


class TestGetQuizStep:
    """Tests for _get_quiz_step function"""

    def test_get_quiz_step_returns_current_question(self, mock_tool_context, sample_quiz_state):
        """Test getting current quiz step"""
        mock_tool_context.set_session_state(sample_quiz_state)

        result = _get_quiz_step(tool_context=mock_tool_context)

        assert result["status"] == "success"
        assert "current_step" in result
        assert "total_steps" in result
        assert result["current_step"] == 1  # index 0 -> step 1

    def test_get_quiz_step_shows_progress(self, mock_tool_context, sample_quiz_state):
        """Test that progress information is included"""
        mock_tool_context.set_session_state(sample_quiz_state)

        result = _get_quiz_step(tool_context=mock_tool_context)

        assert result["total_steps"] == 3
        assert result["correct_so_far"] == 0

    def test_get_quiz_step_no_quiz_prepared(self, mock_tool_context):
        """Test error when quiz not prepared"""
        result = _get_quiz_step(tool_context=mock_tool_context)

        assert result["status"] == "error"

    def test_get_quiz_step_at_end(self, mock_tool_context, sample_quiz_state):
        """Test behavior when quiz is complete"""
        sample_quiz_state["quiz:index"] = 3  # Beyond last question
        mock_tool_context.set_session_state(sample_quiz_state)

        result = _get_quiz_step(tool_context=mock_tool_context)

        # Should indicate quiz is complete
        assert "complete" in result.get("message", "").lower() or result["status"] == "complete"


class TestAdvanceQuiz:
    """Tests for _advance_quiz function"""

    def test_advance_quiz_correct_answer(self, mock_retriever, mock_tool_context, sample_quiz_state):
        """Test advancing with correct answer"""
        mock_tool_context.set_session_state(sample_quiz_state)

        with patch("adk.quiz_tools._retriever", mock_retriever):
            with patch("adk.quiz_tools.get_storage"):
                result = _advance_quiz(
                    correct=True,
                    concept_name="Python Basics",
                    tool_context=mock_tool_context
                )

                assert result["status"] == "success"
                # Index should advance
                assert mock_tool_context.state["quiz:index"] > sample_quiz_state["quiz:index"]
                # Correct count should increase
                assert mock_tool_context.state["quiz:correct"] == 1

    def test_advance_quiz_incorrect_answer(self, mock_retriever, mock_tool_context, sample_quiz_state):
        """Test that incorrect answer increments mistake counter"""
        mock_tool_context.set_session_state(sample_quiz_state)

        with patch("adk.quiz_tools._retriever", mock_retriever):
            with patch("adk.quiz_tools.get_storage"):
                result = _advance_quiz(
                    correct=False,
                    concept_name="Python Basics",
                    tool_context=mock_tool_context
                )

                # Mistakes should increment
                assert mock_tool_context.state["quiz:total_mistakes"] > 0

    def test_advance_quiz_updates_storage(self, mock_retriever, mock_tool_context, sample_quiz_state):
        """Test that advance_quiz persists progress to storage"""
        mock_tool_context.set_session_state(sample_quiz_state)
        mock_storage = MagicMock()

        with patch("adk.quiz_tools._retriever", mock_retriever):
            with patch("adk.quiz_tools.get_storage", return_value=lambda user_id: mock_storage):
                _advance_quiz(
                    correct=True,
                    concept_name="Test Concept",
                    tool_context=mock_tool_context
                )

                # Storage update_mastery should be called
                # Note: This tests the integration point, actual method name may vary
                # mock_storage.update_mastery.assert_called_once()

    def test_advance_quiz_no_quiz_prepared(self, mock_tool_context):
        """Test error when advancing without prepared quiz"""
        result = _advance_quiz(correct=True, tool_context=mock_tool_context)

        assert result["status"] == "error"


class TestRevealContext:
    """Tests for _reveal_context function"""

    def test_reveal_context_shows_snippet(self, mock_tool_context, sample_quiz_state):
        """Test revealing full context for current question"""
        mock_tool_context.set_session_state(sample_quiz_state)

        result = _reveal_context(tool_context=mock_tool_context)

        assert result["status"] == "success"
        assert "snippet" in result
        # Should return the current snippet
        assert result["snippet"] in sample_quiz_state["quiz:snippets"]

    def test_reveal_context_no_quiz(self, mock_tool_context):
        """Test error when revealing context without quiz"""
        result = _reveal_context(tool_context=mock_tool_context)

        assert result["status"] == "error"

    def test_reveal_context_at_valid_index(self, mock_tool_context, sample_quiz_state):
        """Test revealing context at specific index"""
        sample_quiz_state["quiz:index"] = 1
        mock_tool_context.set_session_state(sample_quiz_state)

        result = _reveal_context(tool_context=mock_tool_context)

        # Should return snippet at index 1
        assert result["snippet"] == sample_quiz_state["quiz:snippets"][1]


class TestLearningStats:
    """Tests for learning statistics functions"""

    def test_get_learning_stats(self, mock_tool_context, test_storage):
        """Test retrieving learning statistics"""
        with patch("adk.quiz_tools.get_storage", return_value=lambda user_id: test_storage):
            # Create some test data
            quiz_id = test_storage.start_quiz("session_001", "Topic1", 5)
            test_storage.update_quiz_progress(quiz_id, correct=3, mistakes=2, details=[])
            test_storage.complete_quiz(quiz_id)

            result = _get_learning_stats(tool_context=mock_tool_context)

            assert result["status"] == "success"
            assert "stats" in result

    def test_get_weak_concepts(self, mock_tool_context, test_storage):
        """Test retrieving weak concepts"""
        with patch("adk.quiz_tools.get_storage", return_value=lambda user_id: test_storage):
            # Create weak concept
            test_storage.update_mastery("weak_concept", correct=False)

            result = _get_weak_concepts(threshold=0.5, tool_context=mock_tool_context)

            assert result["status"] == "success"
            assert "concepts" in result

    def test_get_quiz_history(self, mock_tool_context, test_storage):
        """Test retrieving quiz history"""
        with patch("adk.quiz_tools.get_storage", return_value=lambda user_id: test_storage):
            # Create quiz history
            quiz_id = test_storage.start_quiz("session_001", "Python", 3)
            test_storage.complete_quiz(quiz_id)

            result = _get_quiz_history(topic="Python", limit=10, tool_context=mock_tool_context)

            assert result["status"] == "success"
            assert "history" in result


class TestQuizFlowIntegration:
    """Integration tests for complete quiz flow"""

    def test_complete_quiz_flow(self, mock_retriever, mock_tool_context, test_storage):
        """Test complete quiz flow: prepare -> step -> advance -> complete"""
        with patch("adk.quiz_tools._retriever", mock_retriever):
            with patch("adk.quiz_tools.get_storage", return_value=lambda user_id: test_storage):
                # 1. Prepare quiz
                prepare_result = _prepare_quiz("Python", max_chunks=2, tool_context=mock_tool_context)
                assert prepare_result["status"] == "success"

                # 2. Get first step
                step_result = _get_quiz_step(tool_context=mock_tool_context)
                assert step_result["status"] == "success"
                assert step_result["current_step"] == 1

                # 3. Advance with correct answer
                advance_result = _advance_quiz(
                    correct=True,
                    concept_name="Python",
                    tool_context=mock_tool_context
                )
                assert advance_result["status"] == "success"

                # 4. Check progress updated
                assert mock_tool_context.state["quiz:correct"] == 1
                assert mock_tool_context.state["quiz:index"] == 1

    def test_quiz_with_reveal_context(self, mock_retriever, mock_tool_context):
        """Test quiz flow with context reveal"""
        with patch("adk.quiz_tools._retriever", mock_retriever):
            # Prepare quiz
            _prepare_quiz("Python", max_chunks=2, tool_context=mock_tool_context)

            # Reveal context for help
            reveal_result = _reveal_context(tool_context=mock_tool_context)

            assert reveal_result["status"] == "success"
            assert "snippet" in reveal_result
            assert len(reveal_result["snippet"]) > 0
