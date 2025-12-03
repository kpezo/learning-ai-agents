"""Report Service Contract

This module defines the public interface for the PDF Report Generator.
Implementation will be in adk/reports/.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional


# ===========================================================================
# Enums
# ===========================================================================


class MasteryTier(str, Enum):
    """Categorization of concept mastery level."""

    MASTERED = "mastered"  # >= 85%
    IN_PROGRESS = "in_progress"  # 50% - 84%
    NEEDS_PRACTICE = "needs_practice"  # < 50%


class TrendDirection(str, Enum):
    """Performance trend over recent period."""

    IMPROVING = "improving"
    STABLE = "stable"
    DECLINING = "declining"


class RecommendationType(str, Enum):
    """Type of learning recommendation."""

    REVIEW = "review"  # Review weak concept
    PRACTICE = "practice"  # More practice needed
    ADVANCE = "advance"  # Ready for harder content


# ===========================================================================
# Data Classes
# ===========================================================================


@dataclass
class DateRange:
    """Time period for report data."""

    start: datetime
    end: datetime


@dataclass
class ReportConfig:
    """Configuration for report generation request."""

    user_id: str
    date_range: Optional[DateRange] = None  # None = last 30 days
    include_charts: bool = True
    include_recommendations: bool = True
    page_format: str = "A4"  # or "LETTER"


@dataclass
class MasterySummary:
    """Executive summary statistics (FR-002)."""

    overall_mastery_pct: float  # 0.0 - 100.0
    total_quizzes: int
    total_time_minutes: int
    concepts_covered: int
    mastered_count: int  # >= 85%
    in_progress_count: int  # 50% - 84%
    needs_practice_count: int  # < 50%
    date_range: DateRange


@dataclass
class ConceptBreakdown:
    """Individual concept mastery details (FR-003, FR-004)."""

    concept_name: str
    mastery_level: float  # 0.0 - 1.0
    mastery_tier: MasteryTier
    times_practiced: int
    times_correct: int
    trend: TrendDirection
    last_practiced: datetime
    knowledge_type: str  # declarative/procedural/conditional


@dataclass
class ScorePoint:
    """Single data point for score progression chart."""

    date: date
    score: float  # 0.0 - 1.0
    topic: str
    quiz_id: int


@dataclass
class LearningAnalytics:
    """Time-series data for visualizations (FR-005, FR-006, FR-007)."""

    score_progression: List[ScorePoint]
    time_per_topic: Dict[str, int]  # topic -> minutes
    session_dates: List[date]  # for activity heatmap


@dataclass
class Recommendation:
    """Personalized learning suggestion (FR-008)."""

    type: RecommendationType
    priority: int  # 1-3, lower is more important
    target: str  # concept or topic name
    reasoning: str
    action: str


@dataclass
class ProgressReport:
    """Complete report data structure."""

    user_id: str
    generated_at: datetime
    summary: MasterySummary
    concepts: List[ConceptBreakdown]
    analytics: LearningAnalytics
    recommendations: List[Recommendation]


@dataclass
class ReportResult:
    """Result of report generation."""

    success: bool
    file_path: Optional[Path] = None
    error_message: Optional[str] = None
    report_data: Optional[ProgressReport] = None


# ===========================================================================
# Service Interface
# ===========================================================================


class ReportServiceInterface(ABC):
    """Abstract interface for report generation service."""

    @abstractmethod
    def generate_report(self, config: ReportConfig) -> ReportResult:
        """Generate a PDF progress report for the specified user.

        Args:
            config: Report configuration including user_id and options.

        Returns:
            ReportResult with file_path on success, error_message on failure.

        Raises:
            ValueError: If user_id doesn't exist or has no quiz data (FR-009).
        """
        pass

    @abstractmethod
    def collect_data(self, config: ReportConfig) -> ProgressReport:
        """Collect and aggregate data for report generation.

        Args:
            config: Report configuration.

        Returns:
            ProgressReport with all aggregated data.

        Raises:
            ValueError: If insufficient data for report.
        """
        pass

    @abstractmethod
    def get_report_history(
        self, user_id: str, limit: int = 10
    ) -> List[Dict]:
        """Get list of previously generated reports for user (FR-015).

        Args:
            user_id: User identifier.
            limit: Maximum reports to return.

        Returns:
            List of report metadata dicts.
        """
        pass


# ===========================================================================
# ADK Tool Interface
# ===========================================================================


def generate_report(user_id: str) -> dict:
    """ADK FunctionTool: Generate PDF progress report for a user.

    This tool integrates with the agent system to generate reports
    on demand. The PDF file path is returned for download/sharing.

    Args:
        user_id: The user identifier to generate report for.

    Returns:
        Dictionary with:
        - status: "success" or "error"
        - file_path: Path to generated PDF (on success)
        - message: Human-readable status message
        - summary: Quick stats (on success)
    """
    # Implementation will be in adk/reports/tools.py
    pass


def get_learning_summary(user_id: str) -> dict:
    """ADK FunctionTool: Get learning summary without PDF generation.

    Quick summary of user progress for agent responses.

    Args:
        user_id: The user identifier.

    Returns:
        Dictionary with mastery stats, weak concepts, recommendations.
    """
    # Implementation will be in adk/reports/tools.py
    pass
