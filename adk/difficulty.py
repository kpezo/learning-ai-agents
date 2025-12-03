"""
Adaptive difficulty system for educational quiz flow.

Provides 6-level difficulty adjustment based on real-time learner performance,
with automatic level transitions, hint management, and performance tracking.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime


@dataclass
class DifficultyLevel:
    """
    Represents one difficulty level with associated metadata.

    Attributes:
        level: Numeric difficulty (1-6)
        name: Human-readable level name
        question_types: Allowed question types for this level
        hint_allowance: Maximum hints per question (0-3)
        time_pressure: Expected answer time multiplier
        description: What this level tests
    """
    level: int
    name: str
    question_types: List[str]
    hint_allowance: int
    time_pressure: float
    description: str


# Static difficulty level configuration (1-6)
DIFFICULTY_LEVELS = {
    1: DifficultyLevel(
        level=1,
        name="Foundation",
        question_types=["definition", "recognition", "true_false"],
        hint_allowance=3,
        time_pressure=1.5,
        description="Basic recall and recognition"
    ),
    2: DifficultyLevel(
        level=2,
        name="Understanding",
        question_types=["explanation", "comparison", "cause_effect"],
        hint_allowance=2,
        time_pressure=1.3,
        description="Comprehension and interpretation"
    ),
    3: DifficultyLevel(
        level=3,
        name="Application",
        question_types=["scenario", "case_study", "problem_solving"],
        hint_allowance=1,
        time_pressure=1.0,
        description="Apply knowledge to new situations"
    ),
    4: DifficultyLevel(
        level=4,
        name="Analysis",
        question_types=["breakdown", "pattern_recognition", "critique"],
        hint_allowance=0,
        time_pressure=0.9,
        description="Break down and analyze components"
    ),
    5: DifficultyLevel(
        level=5,
        name="Synthesis",
        question_types=["design", "integration", "hypothesis"],
        hint_allowance=0,
        time_pressure=0.8,
        description="Combine elements into new patterns"
    ),
    6: DifficultyLevel(
        level=6,
        name="Mastery",
        question_types=["teach_back", "edge_case", "meta_cognition"],
        hint_allowance=0,
        time_pressure=0.7,
        description="Expert-level teaching and edge cases"
    )
}


@dataclass
class PerformanceRecord:
    """
    Captures a single answer's performance metrics.

    Attributes:
        user_id: User identifier
        session_id: Session identifier
        quiz_id: Related quiz ID
        question_number: Question index
        score: Score for this answer (0.0-1.0)
        response_time_ms: Time to answer in milliseconds
        hints_used: Number of hints requested
        difficulty_level: Difficulty at time of answer
        concept_tested: Concept being assessed
        question_type: Type of question asked
        in_optimal_zone: Whether score was in 60-85% range
        timestamp: ISO timestamp
    """
    user_id: str
    session_id: str
    quiz_id: Optional[int]
    question_number: int
    score: float
    response_time_ms: int
    hints_used: int
    difficulty_level: int
    concept_tested: str
    question_type: str
    in_optimal_zone: bool
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class PerformanceTrend:
    """
    Aggregated analysis of recent answers for difficulty decisions.

    Attributes:
        user_id: User identifier
        window_size: Number of records analyzed
        avg_score: Average score in window
        score_trend: Trend direction (improving/stable/declining)
        avg_response_time_ms: Average response time
        time_trend: Time trend direction (faster/stable/slower)
        avg_hints_used: Average hints per question
        consecutive_correct: Streak of correct answers
        consecutive_incorrect: Streak of incorrect answers
        optimal_zone_ratio: Percentage of answers in optimal zone
    """
    user_id: str
    window_size: int
    avg_score: float
    score_trend: str  # improving, stable, declining
    avg_response_time_ms: int
    time_trend: str  # faster, stable, slower
    avg_hints_used: float
    consecutive_correct: int
    consecutive_incorrect: int
    optimal_zone_ratio: float


@dataclass
class DifficultyAdjustment:
    """
    Records a difficulty level change with reasoning.

    Attributes:
        user_id: User identifier
        session_id: Session identifier
        previous_level: Level before adjustment
        new_level: Level after adjustment
        adjustment_type: Type of change (increase/decrease/maintain)
        reason: Why adjustment was made
        triggered_by: What triggered evaluation
        scaffolding_recommended: Whether scaffolding should activate
        timestamp: ISO timestamp
    """
    user_id: str
    session_id: str
    previous_level: int
    new_level: int
    adjustment_type: str  # increase, decrease, maintain
    reason: str
    triggered_by: str  # answer, manual, session_start
    scaffolding_recommended: bool
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


# =============================================================================
# Core Logic Functions
# =============================================================================

def get_allowed_question_types(level: int) -> List[str]:
    """
    Get allowed question types for a difficulty level.

    Args:
        level: Difficulty level (1-6)

    Returns:
        List of allowed question type strings
    """
    clamped_level = max(1, min(6, level))
    return DIFFICULTY_LEVELS[clamped_level].question_types


def get_concept_complexity(concept_name: str, user_id: str) -> int:
    """
    Retrieve concept complexity from storage.

    Args:
        concept_name: Name of the concept
        user_id: User identifier

    Returns:
        Complexity level (1-5), defaults to 3 if not found
    """
    from adk.storage import get_storage

    try:
        storage = get_storage(user_id)
        with storage._get_conn() as conn:
            row = conn.execute(
                """
                SELECT complexity FROM concept_mastery
                WHERE user_id = ? AND concept_name = ?
            """,
                (user_id, concept_name),
            ).fetchone()
            return row[0] if row and row[0] is not None else 3
    except Exception:
        return 3  # Default complexity


def calculate_performance_trend(
    records: List[Dict[str, Any]], user_id: str, window_size: int = 5
) -> PerformanceTrend:
    """
    Calculate performance trend from recent records.

    Args:
        records: List of performance record dicts (most recent first)
        user_id: User identifier
        window_size: Number of records to analyze

    Returns:
        PerformanceTrend with aggregated analysis
    """
    if not records:
        return PerformanceTrend(
            user_id=user_id,
            window_size=0,
            avg_score=0.0,
            score_trend="stable",
            avg_response_time_ms=0,
            time_trend="stable",
            avg_hints_used=0.0,
            consecutive_correct=0,
            consecutive_incorrect=0,
            optimal_zone_ratio=0.0,
        )

    records = records[:window_size]
    scores = [r["score"] for r in records]
    times = [r.get("response_time_ms", 0) for r in records]
    hints = [r.get("hints_used", 0) for r in records]

    avg_score = sum(scores) / len(scores)
    avg_time = sum(times) / len(times) if times else 0
    avg_hints = sum(hints) / len(hints)

    # Determine score trend (compare first half vs second half)
    if len(scores) >= 2:
        mid = len(scores) // 2
        first_half_avg = sum(scores[:mid]) / mid
        second_half_avg = sum(scores[mid:]) / (len(scores) - mid)
        if second_half_avg > first_half_avg + 0.05:
            score_trend = "improving"
        elif second_half_avg < first_half_avg - 0.05:
            score_trend = "declining"
        else:
            score_trend = "stable"
    else:
        score_trend = "stable"

    # Determine time trend
    if len(times) >= 2 and all(t > 0 for t in times):
        mid = len(times) // 2
        first_half_time = sum(times[:mid]) / mid
        second_half_time = sum(times[mid:]) / (len(times) - mid)
        if second_half_time < first_half_time * 0.9:
            time_trend = "faster"
        elif second_half_time > first_half_time * 1.1:
            time_trend = "slower"
        else:
            time_trend = "stable"
    else:
        time_trend = "stable"

    # Calculate consecutive streaks (from most recent)
    consecutive_correct = 0
    consecutive_incorrect = 0
    for score in scores:
        if score >= 0.60:
            consecutive_correct += 1
            break
        else:
            consecutive_incorrect += 1

    # Count how many in optimal zone
    optimal_count = sum(1 for s in scores if 0.60 <= s <= 0.85)
    optimal_zone_ratio = optimal_count / len(scores)

    return PerformanceTrend(
        user_id=user_id,
        window_size=len(records),
        avg_score=avg_score,
        score_trend=score_trend,
        avg_response_time_ms=int(avg_time),
        time_trend=time_trend,
        avg_hints_used=avg_hints,
        consecutive_correct=consecutive_correct,
        consecutive_incorrect=consecutive_incorrect,
        optimal_zone_ratio=optimal_zone_ratio,
    )


def calculate_difficulty_adjustment(
    current_level: int,
    performance_records: List[Dict[str, Any]],
    user_id: str,
    session_id: str,
    concept_name: str = "",
) -> DifficultyAdjustment:
    """
    Calculate difficulty adjustment based on performance.

    Rules:
    - INCREASE: 3 consecutive scores ≥85%, no hints used
    - DECREASE: 2 consecutive scores <50%
    - MAINTAIN: Otherwise (optimal zone 60-85%)

    Complexity modifier: effective_threshold = base_threshold * (complexity / 3.0)

    Args:
        current_level: Current difficulty level (1-6)
        performance_records: Recent performance records (most recent first)
        user_id: User identifier
        session_id: Session identifier
        concept_name: Optional concept name for complexity adjustment

    Returns:
        DifficultyAdjustment with decision and reasoning
    """
    if len(performance_records) < 2:
        return DifficultyAdjustment(
            user_id=user_id,
            session_id=session_id,
            previous_level=current_level,
            new_level=current_level,
            adjustment_type="maintain",
            reason="Insufficient data for adjustment",
            triggered_by="answer",
            scaffolding_recommended=False,
        )

    # Get concept complexity for threshold adjustment
    complexity = 3
    if concept_name:
        complexity = get_concept_complexity(concept_name, user_id)

    # Calculate complexity modifier
    complexity_modifier = complexity / 3.0
    increase_threshold = 0.85 * complexity_modifier
    decrease_threshold = 0.50 * complexity_modifier

    # Clamp thresholds to reasonable bounds
    increase_threshold = min(increase_threshold, 0.95)
    decrease_threshold = max(decrease_threshold, 0.30)

    # Check for INCREASE (3 consecutive high, no hints)
    if len(performance_records) >= 3:
        recent_3 = performance_records[:3]
        if all(r["score"] >= increase_threshold and r.get("hints_used", 0) == 0 for r in recent_3):
            new_level = min(current_level + 1, 6)
            return DifficultyAdjustment(
                user_id=user_id,
                session_id=session_id,
                previous_level=current_level,
                new_level=new_level,
                adjustment_type="increase" if new_level > current_level else "maintain",
                reason=f"3 consecutive scores ≥{increase_threshold:.0%} with no hints",
                triggered_by="answer",
                scaffolding_recommended=False,
            )

    # Check for DECREASE (2 consecutive low)
    recent_2 = performance_records[:2]
    if all(r["score"] < decrease_threshold for r in recent_2):
        new_level = max(current_level - 1, 1)
        return DifficultyAdjustment(
            user_id=user_id,
            session_id=session_id,
            previous_level=current_level,
            new_level=new_level,
            adjustment_type="decrease" if new_level < current_level else "maintain",
            reason=f"2 consecutive scores <{decrease_threshold:.0%}",
            triggered_by="answer",
            scaffolding_recommended=(new_level < current_level),
        )

    # MAINTAIN (default case)
    return DifficultyAdjustment(
        user_id=user_id,
        session_id=session_id,
        previous_level=current_level,
        new_level=current_level,
        adjustment_type="maintain",
        reason="Performance in acceptable range",
        triggered_by="answer",
        scaffolding_recommended=False,
    )


# =============================================================================
# ADK Tool Functions
# =============================================================================

def _get_difficulty_level(tool_context=None) -> Dict[str, Any]:
    """
    Get current difficulty level and metadata.

    Args:
        tool_context: ADK ToolContext with session state

    Returns:
        Dict with status, level, metadata
    """
    if tool_context is None or "difficulty:level" not in tool_context.state:
        return {
            "status": "error",
            "error_message": "Quiz not prepared. Call prepare_quiz first.",
        }

    current_level = tool_context.state["difficulty:level"]
    level_data = DIFFICULTY_LEVELS[current_level]
    hints_used = tool_context.state.get("difficulty:hints_used_current", 0)

    return {
        "status": "success",
        "level": current_level,
        "name": level_data.name,
        "hint_allowance": level_data.hint_allowance,
        "hints_remaining": max(0, level_data.hint_allowance - hints_used),
        "question_types": level_data.question_types,
        "scaffolding_active": tool_context.state.get("difficulty:scaffolding_active", False),
    }


def _set_difficulty_level(level: int, tool_context=None) -> Dict[str, Any]:
    """
    Manually set difficulty level.

    Args:
        level: Target difficulty level (1-6)
        tool_context: ADK ToolContext with session state

    Returns:
        Dict with status, previous_level, new_level, metadata
    """
    if tool_context is None:
        return {"status": "error", "error_message": "No tool context provided"}

    # Clamp level to valid range
    new_level = max(1, min(6, level))
    previous_level = tool_context.state.get("difficulty:level", 3)

    # Update state
    tool_context.state["difficulty:level"] = new_level
    tool_context.state["difficulty:hints_used_current"] = 0

    level_data = DIFFICULTY_LEVELS[new_level]

    return {
        "status": "success",
        "previous_level": previous_level,
        "new_level": new_level,
        "level_name": level_data.name,
        "hint_allowance": level_data.hint_allowance,
    }


def _record_performance(
    score: float,
    response_time_ms: int = 0,
    hints_used: int = 0,
    concept_name: str = "",
    question_type: str = "",
    tool_context=None,
) -> Dict[str, Any]:
    """
    Record performance and trigger difficulty adjustment.

    Args:
        score: Score for this answer (0.0-1.0)
        response_time_ms: Time taken to answer
        hints_used: Number of hints used
        concept_name: Concept being tested
        question_type: Type of question asked
        tool_context: ADK ToolContext with session state

    Returns:
        Dict with status, adjustment details, trend analysis
    """
    if tool_context is None:
        return {"status": "error", "error_message": "No tool context provided"}

    user_id = getattr(tool_context, "user_id", "unknown_user")
    session_id = getattr(tool_context, "session_id", "unknown_session")
    current_level = tool_context.state.get("difficulty:level", 3)

    # Determine if in optimal zone
    in_optimal_zone = 0.60 <= score <= 0.85

    # Create performance record
    perf_record = {
        "score": score,
        "response_time_ms": response_time_ms,
        "hints_used": hints_used,
        "difficulty_level": current_level,
        "concept_tested": concept_name,
        "question_type": question_type,
        "in_optimal_zone": in_optimal_zone,
    }

    # Add to history
    history = tool_context.state.get("difficulty:history", [])
    history.insert(0, perf_record)
    tool_context.state["difficulty:history"] = history[:10]  # Keep last 10

    # Calculate adjustment
    adjustment = calculate_difficulty_adjustment(
        current_level=current_level,
        performance_records=history,
        user_id=user_id,
        session_id=session_id,
        concept_name=concept_name,
    )

    # Apply adjustment
    if adjustment.new_level != current_level:
        tool_context.state["difficulty:level"] = adjustment.new_level

    # Update scaffolding flag
    tool_context.state["difficulty:scaffolding_active"] = adjustment.scaffolding_recommended

    # Reset hint counter for next question
    tool_context.state["difficulty:hints_used_current"] = 0

    # Update streaks
    if score >= 0.60:
        tool_context.state["difficulty:consecutive_correct"] = (
            tool_context.state.get("difficulty:consecutive_correct", 0) + 1
        )
        tool_context.state["difficulty:consecutive_incorrect"] = 0
    else:
        tool_context.state["difficulty:consecutive_incorrect"] = (
            tool_context.state.get("difficulty:consecutive_incorrect", 0) + 1
        )
        tool_context.state["difficulty:consecutive_correct"] = 0

    # Store last adjustment
    tool_context.state["difficulty:last_adjustment"] = {
        "type": adjustment.adjustment_type,
        "previous_level": adjustment.previous_level,
        "new_level": adjustment.new_level,
        "reason": adjustment.reason,
    }

    # Calculate trend
    trend = calculate_performance_trend(history, user_id, window_size=5)

    return {
        "status": "success",
        "performance_recorded": True,
        "in_optimal_zone": in_optimal_zone,
        "difficulty_adjustment": {
            "type": adjustment.adjustment_type,
            "previous_level": adjustment.previous_level,
            "new_level": adjustment.new_level,
            "reason": adjustment.reason,
        },
        "trend": {
            "avg_score": trend.avg_score,
            "trend_direction": trend.score_trend,
            "consecutive_correct": trend.consecutive_correct,
        },
    }


# =============================================================================
# ADK FunctionTool Wrappers
# =============================================================================

try:
    from google.adk.tools import FunctionTool

    get_difficulty_level_tool = FunctionTool(func=_get_difficulty_level)
    set_difficulty_level_tool = FunctionTool(func=_set_difficulty_level)
    record_performance_tool = FunctionTool(func=_record_performance)

except ImportError:
    # ADK not installed, tools will be None
    get_difficulty_level_tool = None
    set_difficulty_level_tool = None
    record_performance_tool = None
