"""Shared pytest fixtures for testing the educational agent system.

This module provides:
- mock_retriever: SimpleRetriever with predefined chunks (mocks RAG system)
- test_storage: Isolated SQLite database using tmp_path (mocks storage)
- mock_tool_context: ADK ToolContext with mocked session state and LLM calls
"""

import os
import pytest
from pathlib import Path
from typing import Any, Dict
from unittest.mock import MagicMock, Mock

# Import from adk modules
from adk.rag_setup import SimpleRetriever, Document
from adk.storage import StorageService

try:
    from google.adk.tools.tool_context import ToolContext
    TOOL_CONTEXT_AVAILABLE = True
except ImportError:
    TOOL_CONTEXT_AVAILABLE = False


@pytest.fixture
def mock_retriever():
    """Fixture providing a SimpleRetriever with predefined test content.

    Mocks external dependencies: PDF loading, text extraction

    Returns:
        SimpleRetriever: Retriever with sample educational content
    """
    sample_chunks = [
        "Python is a high-level programming language known for its readability and simplicity.",
        "Variables in Python are dynamically typed, meaning you don't need to declare their type.",
        "Functions in Python are defined using the 'def' keyword followed by the function name.",
        "Loops allow you to repeat code multiple times. Python has 'for' and 'while' loops.",
        "Conditional statements like 'if', 'elif', and 'else' control program flow.",
        "Lists are ordered, mutable collections in Python, created with square brackets.",
        "Dictionaries store key-value pairs and are created with curly braces.",
        "Classes in Python define blueprints for creating objects with attributes and methods.",
        "Exception handling using try/except blocks prevents program crashes.",
        "Modules in Python are files containing Python code that can be imported.",
    ]
    return SimpleRetriever(chunks=sample_chunks)


@pytest.fixture
def test_storage(tmp_path):
    """Fixture providing isolated SQLite database for testing.

    Mocks external dependencies: Persistent storage, file system

    Args:
        tmp_path: pytest built-in fixture providing temporary directory

    Returns:
        StorageService: Storage instance with ephemeral database

    Notes:
        - Database is automatically cleaned up after test
        - Each test gets a fresh, isolated database
        - Uses explicit db_path to avoid module-level DATA_DIR caching issues
    """
    # Create temporary database path (unique per test via tmp_path)
    test_db_path = tmp_path / "test_user.db"

    # Create storage service with explicit db_path for proper isolation
    storage = StorageService(user_id="test_user", db_path=test_db_path)

    yield storage


@pytest.fixture
def mock_tool_context():
    """
    Creates a mock ADK ToolContext for testing tools without real session state.

    Mocks external dependencies: LLM API calls, ADK session state
    """
    if TOOL_CONTEXT_AVAILABLE:
        context = MagicMock(spec=ToolContext)
    else:
        context = MagicMock()

    context.state = {}
    context.session_id = "test_session_123"
    context.user_id = "test_user"

    # Helper method to configure session state
    def set_session_state(state_dict: Dict[str, Any]):
        """Configure session state for this test."""
        context.state.update(state_dict)

    context.set_session_state = set_session_state

    return context


@pytest.fixture
def initialized_difficulty_context(mock_tool_context):
    """
    ToolContext with difficulty system initialized.
    """
    mock_tool_context.state["difficulty:level"] = 3
    mock_tool_context.state["difficulty:history"] = []
    mock_tool_context.state["difficulty:scaffolding_active"] = False
    mock_tool_context.state["difficulty:hints_used_current"] = 0
    mock_tool_context.state["difficulty:consecutive_correct"] = 0
    mock_tool_context.state["difficulty:consecutive_incorrect"] = 0
    mock_tool_context.state["difficulty:last_adjustment"] = None
    return mock_tool_context


@pytest.fixture
def quiz_prepared_context(initialized_difficulty_context):
    """
    ToolContext with quiz prepared (extends difficulty initialization).
    """
    initialized_difficulty_context.state["quiz:prepared"] = True
    initialized_difficulty_context.state["quiz:topic"] = "test_topic"
    initialized_difficulty_context.state["quiz:current_step"] = 1
    initialized_difficulty_context.state["quiz:total_questions"] = 5
    # Add quiz snippets for advance_quiz to work
    initialized_difficulty_context.state["quiz:snippets"] = [
        "Test snippet 1",
        "Test snippet 2",
        "Test snippet 3",
        "Test snippet 4",
        "Test snippet 5",
    ]
    initialized_difficulty_context.state["quiz:index"] = 0
    initialized_difficulty_context.state["quiz:mistakes"] = 0
    initialized_difficulty_context.state["quiz:total_mistakes"] = 0
    initialized_difficulty_context.state["quiz:correct"] = 0
    initialized_difficulty_context.state["quiz:question_details"] = []
    return initialized_difficulty_context


@pytest.fixture
def performance_records_fixture():
    """
    Sample performance records for testing trend calculations.
    """
    return [
        {
            "score": 0.9,
            "response_time_ms": 10000,
            "hints_used": 0,
            "difficulty_level": 3,
            "concept_tested": "quadratic_equations",
            "in_optimal_zone": False,
        },
        {
            "score": 0.85,
            "response_time_ms": 12000,
            "hints_used": 0,
            "difficulty_level": 3,
            "concept_tested": "quadratic_equations",
            "in_optimal_zone": False,
        },
        {
            "score": 0.88,
            "response_time_ms": 11000,
            "hints_used": 0,
            "difficulty_level": 3,
            "concept_tested": "quadratic_equations",
            "in_optimal_zone": False,
        },
    ]


@pytest.fixture
def optimal_zone_records():
    """
    Performance records in optimal zone (60-85%).
    """
    return [
        {"score": 0.75, "hints_used": 1, "difficulty_level": 2, "in_optimal_zone": True},
        {"score": 0.68, "hints_used": 1, "difficulty_level": 2, "in_optimal_zone": True},
        {"score": 0.72, "hints_used": 0, "difficulty_level": 2, "in_optimal_zone": True},
    ]


@pytest.fixture
def struggling_records():
    """
    Performance records indicating struggle (<50%).
    """
    return [
        {"score": 0.40, "hints_used": 2, "difficulty_level": 3, "in_optimal_zone": False},
        {"score": 0.45, "hints_used": 3, "difficulty_level": 3, "in_optimal_zone": False},
    ]


@pytest.fixture
def sample_quiz_state():
    """
    Sample quiz state for testing quiz step functions.
    """
    return {
        "quiz:prepared": True,
        "quiz:topic": "Python Basics",
        "quiz:snippets": [
            "Python is a high-level programming language.",
            "Variables store data values.",
            "Functions are reusable blocks of code.",
        ],
        "quiz:index": 0,
        "quiz:mistakes": 0,
        "quiz:total_mistakes": 0,
        "quiz:correct": 0,
        "quiz:question_details": [],
    }
