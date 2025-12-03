import pytest
from unittest.mock import MagicMock
from google.adk.tools.tool_context import ToolContext


@pytest.fixture
def mock_tool_context():
    """
    Creates a mock ADK ToolContext for testing tools without real session state.
    """
    context = MagicMock(spec=ToolContext)
    context.state = {}
    context.session_id = "test_session_123"
    context.user_id = "test_user"
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
