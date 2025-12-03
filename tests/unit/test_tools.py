"""Unit tests for adk/tools.py

Tests _fetch_info and _get_quiz_source tool functions with mocked retriever.
"""

import pytest
from unittest.mock import patch, MagicMock
from adk.tools import _fetch_info, _get_quiz_source
from adk.rag_setup import Document


class TestFetchInfo:
    """Tests for _fetch_info tool function"""

    def test_fetch_info_success(self, mock_retriever):
        """Test fetching info with valid query"""
        with patch("adk.tools._retriever", mock_retriever):
            result = _fetch_info("Python programming")

            assert result["status"] == "success"
            assert "snippets" in result
            assert len(result["snippets"]) > 0
            assert isinstance(result["snippets"], list)

    def test_fetch_info_returns_text_content(self, mock_retriever):
        """Test that snippets contain expected content"""
        with patch("adk.tools._retriever", mock_retriever):
            result = _fetch_info("Python")

            # Should return relevant Python content
            snippets = result["snippets"]
            assert any("Python" in snippet for snippet in snippets)

    def test_fetch_info_with_empty_query(self, mock_retriever):
        """Test handling of empty query"""
        with patch("adk.tools._retriever", mock_retriever):
            result = _fetch_info("")

            assert result["status"] == "success"
            # Should still return snippets (even if not very relevant)
            assert "snippets" in result

    def test_fetch_info_no_retriever(self):
        """Test error handling when retriever not initialized"""
        with patch("adk.tools._retriever", None):
            result = _fetch_info("test query")

            assert result["status"] == "error"
            assert "error_message" in result
            assert "not initialized" in result["error_message"].lower()

    def test_fetch_info_strips_whitespace(self, mock_retriever):
        """Test that returned snippets are stripped of extra whitespace"""
        # Create retriever with snippets containing whitespace
        docs_with_whitespace = [
            Document(page_content="  Python is great  \n"),
            Document(page_content="\tIndented content\t"),
        ]
        mock_retriever.get_relevant_documents = MagicMock(return_value=docs_with_whitespace)

        with patch("adk.tools._retriever", mock_retriever):
            result = _fetch_info("Python")

            snippets = result["snippets"]
            # All snippets should be stripped
            assert all(snippet == snippet.strip() for snippet in snippets)


class TestGetQuizSource:
    """Tests for _get_quiz_source tool function"""

    def test_get_quiz_source_success(self, mock_retriever):
        """Test getting quiz source material"""
        with patch("adk.tools._retriever", mock_retriever):
            result = _get_quiz_source("Python Basics", max_chunks=3)

            assert result["status"] == "success"
            assert "snippets" in result
            assert len(result["snippets"]) <= 3

    def test_get_quiz_source_labeled_snippets(self, mock_retriever):
        """Test that snippets are labeled with numbers"""
        with patch("adk.tools._retriever", mock_retriever):
            result = _get_quiz_source("Python", max_chunks=2)

            snippets = result["snippets"]
            # Each snippet should start with "Snippet N:"
            assert snippets[0].startswith("Snippet 1:")
            assert snippets[1].startswith("Snippet 2:")

    def test_get_quiz_source_respects_max_chunks(self, mock_retriever):
        """Test that max_chunks parameter is respected"""
        with patch("adk.tools._retriever", mock_retriever):
            result = _get_quiz_source("Python", max_chunks=2)

            assert len(result["snippets"]) <= 2

    def test_get_quiz_source_truncates_long_content(self, mock_retriever):
        """Test that very long snippets are truncated to 600 chars"""
        # Create document with very long content
        long_content = "a" * 1000
        long_doc = Document(page_content=long_content)
        mock_retriever.get_relevant_documents = MagicMock(return_value=[long_doc])

        with patch("adk.tools._retriever", mock_retriever):
            result = _get_quiz_source("test", max_chunks=1)

            snippet = result["snippets"][0]
            # Should be truncated (including "Snippet 1: " prefix)
            assert len(snippet) < len(long_content)
            # Content part should be <= 600 chars
            content_part = snippet.split(": ", 1)[1]
            assert len(content_part) <= 600

    def test_get_quiz_source_with_max_chunks_zero(self, mock_retriever):
        """Test edge case: max_chunks=0"""
        with patch("adk.tools._retriever", mock_retriever):
            result = _get_quiz_source("Python", max_chunks=0)

            assert result["status"] == "success"
            assert len(result["snippets"]) == 0

    def test_get_quiz_source_no_retriever(self):
        """Test error handling when retriever not initialized"""
        with patch("adk.tools._retriever", None):
            result = _get_quiz_source("test topic")

            assert result["status"] == "error"
            assert "error_message" in result
            assert "not initialized" in result["error_message"].lower()


class TestToolIntegration:
    """Integration tests for tool functions"""

    def test_fetch_info_and_get_quiz_source_same_topic(self, mock_retriever):
        """Test that both tools return consistent content for same topic"""
        with patch("adk.tools._retriever", mock_retriever):
            fetch_result = _fetch_info("Python variables")
            quiz_result = _get_quiz_source("Python variables", max_chunks=3)

            # Both should succeed
            assert fetch_result["status"] == "success"
            assert quiz_result["status"] == "success"

            # Both should contain relevant content
            fetch_snippets = fetch_result["snippets"]
            quiz_snippets = quiz_result["snippets"]

            assert len(fetch_snippets) > 0
            assert len(quiz_snippets) > 0
